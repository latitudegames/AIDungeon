from __future__ import division
from __future__ import print_function
import sys
sys.path.append('../')
import tensorflow as tf
import os
import numpy as np
tf.enable_eager_execution()
import transformer
import argparse
import pdb
import re
from collections import Counter
from tensorflow.python import debug as tf_debug
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import embedding_ops
import fastBPE
import platform

use_py3 = platform.python_version()[0] == '3'

parser = argparse.ArgumentParser(description='TensorFlow code for generating from CTRL')
parser.add_argument('--model_dir', type=str, required=True,
                                        help='location of model checkpoint')
parser.add_argument('--seed', type=int, default=1337,
                                        help='random seed for TensorFlow, numpy and PythonHash')
parser.add_argument('--sequence_len', type=int, default=256,
                                        help='sequence len of model being fine-tuned (must match also the TFRecords)')
parser.add_argument('--iterations', type=int, default=1000,
                                        help='random seed for TensorFlow, numpy and PythonHash')

args = parser.parse_args()
tf.random.set_random_seed(args.seed)
os.environ['PYTHONHASHSEED'] = str(args.seed)
np.random.seed(args.seed)

# load the vocabulary from file
vocab = open('../vocab').read().decode(encoding='utf-8').split('\n') if not use_py3 else open('../vocab', encoding='utf-8').read().split('\n')
vocab = list(map(lambda x: x.split(' ')[0], vocab)) + ['<unk>'] + ['\n']
print ('{} unique words'.format(len(vocab)))

# length of the vocabulary
vocab_size = len(vocab)

# define the numericalization map
# idx2word maps the numericalized ID to the word
# word2idx maps the word to the numericalized ID
word2idx = {u:i for i, u in enumerate(vocab)}
idx2word = np.array(vocab)



# sequence length to use for the transformer
# must match the model being fine-tuned
seq_length = args.sequence_len

def input_fn(params=None):
    print('READING!', params)
    dataset = tf.data.Dataset.list_files(tf.io.gfile.glob('./*.tfrecords'), shuffle=True)

    tf_data = tf.data.TFRecordDataset(dataset)
    myfeatures = {
        'input': tf.io.FixedLenFeature([256], tf.int64),
        'output': tf.io.FixedLenFeature([256], tf.int64)
        }

    def _parse_text_function(example_proto):
        blah = tf.io.parse_single_example(example_proto, myfeatures)
        return blah['input'], blah['output']
    
    train_data = tf_data.map(_parse_text_function).batch(params['batch_size'], drop_remainder=True).repeat().shuffle(10000)#.prefetch(tf.contrib.data.AUTOTUNE)
    
    return train_data


# the dimension of the transformer
embedding_dim = 1280


# Now, we begin defining the model
# we defer the transformer definition to transformer.py
# here, we only define the tied softmax layer
# this layer ties the softmax weights to the input embeddings
class TiedEmbeddingSoftmax(tf.keras.layers.Layer):

  def __init__(self, vocab_size=vocab_size, embedding_size=embedding_dim, **kwargs):
    super(TiedEmbeddingSoftmax, self).__init__()
    self.w = self.add_weight(name='w', shape=(vocab_size, embedding_size),
                             initializer='random_normal',
                             trainable=True)
    self.b = self.add_weight(name='b', shape=(vocab_size,),
                             initializer='zeros',
                             trainable=True)

  def call(self, inputs, embed=True):
    if embed:
      dtype = tf.keras.backend.dtype(inputs)
      if dtype != 'int32' and dtype != 'int64':
        inputs = math_ops.cast(inputs, 'int32')
      return embedding_ops.embedding_lookup(self.w, inputs)
    else:
      return tf.tensordot(inputs, tf.transpose(self.w), 1) + self.b

# input for the keras model
tokens = tf.keras.layers.Input(shape=(seq_length,), dtype='int32')

# instantiates a tied softmax class
tied_embedding_softmax = TiedEmbeddingSoftmax()

# embedded tokens, before passing it to the transformer
embedded = tied_embedding_softmax(tokens, embed=True)

# the activations after passing it from the transformer
# for some odd reason, TPUs don't play well with specifying the arguments of the Encoder() function
# so you have to leave them at their defaults
transformed = transformer.Encoder()(embedded, training=False)


# pass the activations from our tiedsoftmax class
# this time with embed=False denoting that we are doing the softmax operation
# and not a lookup
logits = tied_embedding_softmax(transformed, embed=False)


# finally, define the Keras model with inputs as tokens and outputs as the logits we just computed
model = tf.keras.Model(inputs=tokens, outputs=logits)


# the loss function is a simple categorical crossentropy between the logits and the labels
def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

# the optimizer is not used since this code only supports inference
# however, to compile the model, we still define it
optimizer = tf.contrib.estimator.clip_gradients_by_norm(
        tf.train.AdagradOptimizer(learning_rate=1e-2), 0.25)


# compile the model with the optimizer and loss            
model.compile(optimizer=optimizer, loss=loss)
print(model.summary())


# IMPORTANT
# this is where the saved model is presented to the code
# the model directory should have the model checkpoint and
# a checkpoint file
run_config = tf.contrib.tpu.RunConfig(
        model_dir=args.model_dir)


# this converts the Keras model to a TensorFlow estimator
# this step is critical
# remember to patch the TF 1.14 file before running the code, else you're going to see errors here

run_config = tf.contrib.tpu.RunConfig(
        model_dir=args.model_dir,
        session_config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=True),
        tpu_config=tf.contrib.tpu.TPUConfig(iterations_per_loop=100, num_cores_per_replica=1, input_partition_dims=[[1, 1], [1, 1]], per_host_input_for_training=3))
tf.logging.set_verbosity(tf.logging.INFO)

estimator_model = tf.keras.estimator.model_to_estimator(keras_model=model, config=run_config)

estimator_model.train(input_fn=input_fn, steps=args.iterations)
