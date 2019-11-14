import tarfile
import os
import json
import requests
import sys
import shutil
import re
from tqdm import tqdm, trange
import numpy as np
import tensorflow as tf
from tensorflow.core.protobuf import rewriter_config_pb2
from tensorflow.python.client import device_lib
import time
from datetime import datetime
import csv
import argparse

# if in Google Colaboratory
try:
    from google.colab import drive
except:
    pass

import gpt_2_simple as gpt2

from gpt_2_simple.src import model, sample, encoder, memory_saving_gradients
from gpt_2_simple.src.load_dataset import load_dataset, Sampler
from gpt_2_simple.src.accumulate import AccumulatingOptimizer


def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']


def finetune(sess,
             dataset,
             steps=-1,
             model_name='124M',
             model_dir='models',
             combine=50000,
             batch_size=1,
             learning_rate=0.0001,
             accumulate_gradients=5,
             restore_from='latest',
             run_name='run1',
             checkpoint_dir='checkpoint',
             sample_every=100,
             sample_length=1023,
             sample_num=1,
             save_every=1000,
             print_every=1,
             max_checkpoints=1,
             use_memory_saving_gradients=False,
             only_train_transformer_layers=False,
             optimizer='adam',
             overwrite=False):
    """Finetunes the model on the given dataset.
    Adapted from https://github.com/nshepperd/gpt-2/blob/finetuning/train.py.
    See that file for parameter definitions.
    """

    SAMPLE_DIR = 'samples'

    checkpoint_path = os.path.join(checkpoint_dir, run_name)

    def maketree(path):
        try:
            os.makedirs(path)
        except:
            pass

    maketree(checkpoint_path)
    files = [f for f in os.listdir(checkpoint_path)]
    for file in ['hparams.json', 'encoder.json', 'vocab.bpe']:
        try:
            shutil.copyfile(os.path.join(model_dir, model_name, file),
                            os.path.join(checkpoint_path, file))
        except FileNotFoundError as fnf_error:
            print("You need to download the GPT-2 model first via download_gpt2()")
            raise (fnf_error)

    enc = encoder.get_encoder(checkpoint_path)
    hparams = model.default_hparams()
    with open(os.path.join(checkpoint_path, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if sample_length > hparams.n_ctx:
        raise ValueError(
            "Can't get samples longer than window size: %s" % hparams.n_ctx)

    if model_name not in ['117M', '124M']:
        use_memory_saving_gradients = True
        only_train_transformer_layers = True
        accumulate_gradients = 1

    context = tf.compat.v1.placeholder(tf.int32, [batch_size, None])
    output = model.model(hparams=hparams, X=context)
    loss = tf.reduce_mean(
        input_tensor=tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=context[:, 1:], logits=output['logits'][:, :-1]))

    tf_sample = sample.sample_sequence(
        hparams=hparams,
        length=sample_length,
        context=context,
        batch_size=batch_size,
        temperature=1.0,
        top_k=40)

    all_vars = [v for v in tf.compat.v1.trainable_variables() if 'model' in v.name]
    train_vars = [v for v in all_vars if '/h' in v.name] if only_train_transformer_layers else all_vars

    if optimizer == 'adam':
        opt = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate)
    elif optimizer == 'sgd':
        opt = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=learning_rate)

    if accumulate_gradients > 1:
        if use_memory_saving_gradients:
            exit("Memory saving gradients are not implemented for gradient accumulation yet.")
        opt = AccumulatingOptimizer(
            opt=opt,
            var_list=train_vars)
        opt_reset = opt.reset()
        opt_compute = opt.compute_gradients(loss)
        opt_apply = opt.apply_gradients()
        summary_loss = tf.compat.v1.summary.scalar('loss', opt_apply)
    else:
        if use_memory_saving_gradients:
            opt_grads = memory_saving_gradients.gradients(loss, train_vars)
        else:
            opt_grads = tf.gradients(ys=loss, xs=train_vars)
        opt_grads = list(zip(opt_grads, train_vars))
        opt_apply = opt.apply_gradients(opt_grads)
        summary_loss = tf.compat.v1.summary.scalar('loss', loss)

    summary_log = tf.compat.v1.summary.FileWriter(checkpoint_path)

    saver = tf.compat.v1.train.Saver(
        var_list=all_vars,
        max_to_keep=max_checkpoints)
    sess.run(tf.compat.v1.global_variables_initializer())

    if restore_from == 'latest':
        ckpt = tf.train.latest_checkpoint(checkpoint_path)
        if ckpt is None:
            # Get fresh GPT weights if new run.
            ckpt = tf.train.latest_checkpoint(
                os.path.join(model_dir, model_name))
    elif restore_from == 'fresh':
        ckpt = tf.train.latest_checkpoint(
            os.path.join(model_dir, model_name))
    else:
        ckpt = tf.train.latest_checkpoint(restore_from)
    print('Loading checkpoint', ckpt)
    saver.restore(sess, ckpt)

    print('Loading dataset...')
    chunks = load_dataset(enc, dataset, combine)
    data_sampler = Sampler(chunks)
    print('dataset has', data_sampler.total_size, 'tokens')
    print('Training...')

    counter = 1
    counter_path = os.path.join(checkpoint_path, 'counter')
    if os.path.exists(counter_path) and restore_from == 'latest':
        # Load the step number if we're resuming a run
        # Add 1 so we don't immediately try to save again
        with open(counter_path, 'r') as fp:
            counter = int(fp.read()) + 1
    counter_base = counter

    def save():
        maketree(checkpoint_path)
        print(
            'Saving',
            os.path.join(checkpoint_path,
                         'model-{}').format(counter - 1))
        saver.save(
            sess,
            os.path.join(checkpoint_path, 'model'),
            global_step=counter - 1)
        with open(counter_path, 'w') as fp:
            fp.write(str(counter - 1) + '\n')

    def generate_samples():
        context_tokens = data_sampler.sample(1)
        all_text = []
        index = 0
        while index < sample_num:
            out = sess.run(
                tf_sample,
                feed_dict={context: batch_size * [context_tokens]})
            for i in range(min(sample_num - index, batch_size)):
                text = enc.decode(out[i])
                text = '======== SAMPLE {} ========\n{}\n'.format(
                    index + 1, text)
                all_text.append(text)
                index += 1
        print(text)
        maketree(os.path.join(SAMPLE_DIR, run_name))
        with open(
                os.path.join(SAMPLE_DIR, run_name,
                             'samples-{}').format(counter), 'w') as fp:
            fp.write('\n'.join(all_text))

    def sample_batch():
        return [data_sampler.sample(1024) for _ in range(batch_size)]

    if overwrite and restore_from == 'latest':
        for file in files:
            if file.startswith('model') or file.startswith('events'):
                os.remove(os.path.join(checkpoint_path, file))
        save()

    avg_loss = (0.0, 0.0)
    start_time = time.time()

    if steps:
        steps = int(steps)

    try:
        while True:
            if steps > 0 and counter == (counter_base + steps):
                save()
                return
            if (counter - 1) % save_every == 0 and counter > 1:
                save()
            if (counter - 1) % sample_every == 0 and counter > 1:
                generate_samples()

            if accumulate_gradients > 1:
                sess.run(opt_reset)
                for _ in range(accumulate_gradients):
                    sess.run(
                        opt_compute, feed_dict={context: sample_batch()})
                (v_loss, v_summary) = sess.run((opt_apply, summary_loss))
            else:
                (_, v_loss, v_summary) = sess.run(
                    (opt_apply, loss, summary_loss),
                    feed_dict={context: sample_batch()})

            summary_log.add_summary(v_summary, counter)

            if counter % print_every == 0:
                avg_loss = (avg_loss[0] * 0.99 + v_loss,
                            avg_loss[1] * 0.99 + 1.0)

                print(
                    '[{counter} | {time:2.2f}] loss={loss:2.2f} avg={avg:2.2f}'
                        .format(
                        counter=counter,
                        time=time.time() - start_time,
                        loss=v_loss,
                        avg=avg_loss[0] / avg_loss[1]))

            counter += 1
    except KeyboardInterrupt:
        print('interrupted')
        save()

model_name = "1558M"
if not os.path.isdir(os.path.join("models", model_name)):
    print("Downloading ", model_name, " model...")
    gpt2.download_gpt2(model_name=model_name)  # model is saved into current directory under /models/124M/

file_name = "merged_first_person.txt"

sess = gpt2.start_tf_sess()
finetune(sess,
              file_name,
              model_name=model_name,
              steps=10000)

gpt2.generate(sess)