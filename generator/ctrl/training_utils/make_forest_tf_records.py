import numpy as np
import os
import tensorflow as tf
import tqdm
import pdb
import glob
import time
import sys
import re
import argparse
import fastBPE
import platform
import json
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../../..')
from story.utils import *

def make_samples_helper(context, story_block, action_results, path, tree_id):

    samples = []

    for i, action_result in enumerate(action_results):
        new_path = path[:]
        new_path.append(i)
        if action_result["result"] is not None:
            sample = [context, story_block, action_result["action"], action_result["result"]]
            samples.append(sample)
        if len(action_result["action_results"]) is not 0:
            sub_result = make_samples_helper(context, action_result["result"], action_result["action_results"], new_path, tree_id)
            samples += sub_result

    return samples


def make_samples(tree):
    # Traverse to the bottom levels of each tree
    first_story_block = tree["first_story_block"]
    samples = make_samples_helper(tree["context"], first_story_block, tree["action_results"], [], tree["tree_id"])
    return samples


def build_tokenized_samples(bpe, tree):
    samples = make_samples(tree)
    string_samples = []

    for sample in samples:
        sample = [string.strip() for string in sample]

        sample[2] = sample[2][0].lower() + sample[2][1:]
        sample[2] = "You " + sample[2]

        new_sample = []

        for item in sample:
            new_sample.append(second_to_first_person(item))

        string_samples.append(" ".join(new_sample))

    tokenized_samples = [bpe.apply([sample.encode('ascii', errors='ignore') if not use_py3 else sample])[0] for sample in
                         string_samples]  # will NOT work for non-English texts
    tokenized_samples = [re.findall(r'\S+|\n', sample) for sample in tokenized_samples]
    tokenized_samples = [list(filter(lambda x: x != u'@@', sample)) for sample in tokenized_samples]

    # Fill samples up to seq_len
    for sample in tokenized_samples:
        pad_len = seq_length - len(sample)
        for _ in range(pad_len):
            sample.append("\n")

    return tokenized_samples


use_py3 = platform.python_version()[0] == '3'

paths_to_train_files = ["apoc_seed1.json","apoc_seed2.json","apoc_seed3.json","apoc_seed4.json"]
seq_length = 256
domain = ["Apocalypse"]


# Build sequences from JSON
bpe = fastBPE.fastBPE('../codes', '../vocab')
tokenized_samples = []
for fname in paths_to_train_files:
    with open(fname, 'r') as fp:
        tree = json.load(fp)

        tokenized_samples += build_tokenized_samples(bpe, tree)
        string_samples = []

# load the vocabulary from file
vocab = open('../vocab').read().decode(encoding='utf-8').split('\n') if not use_py3 else open('../vocab', encoding='utf-8').read().split('\n')
vocab = list(map(lambda x: x.split(' ')[0], vocab)) + ['<unk>'] + ['\n']
print ('{} unique words'.format(len(vocab)))
    
# Creating a mapping from unique characters to indices
word2idx = {u:i for i, u in enumerate(vocab)}
idx2word = np.array(vocab)

seq_length = seq_length-1

def numericalize(x):
    count = 0
    for i in x:
        if i not in word2idx:
            print(i)
            count += 1
    return count>1, [word2idx.get(i, word2idx['<unk>'])  for i in x]

tfrecords_fname = 'action_results.tfrecords'

total = 0
skipped = 0
with tf.io.TFRecordWriter(tfrecords_fname) as writer:
    for sample in tokenized_samples:
        domain_seq = (domain+sample)[:256+1]
        flag_input, inputs = numericalize(domain_seq[:-1])
        flag_output, outputs = numericalize(domain_seq[1:])
        total += 1
        if flag_input or flag_output:
            skipped += 1
            continue

        if len(inputs)!=seq_length+1 or len(outputs)!=seq_length+1:
            break
        example_proto = tf.train.Example(features=tf.train.Features(feature={'input': tf.train.Feature(int64_list=tf.train.Int64List(value=inputs)),
                                                                             'output': tf.train.Feature(int64_list=tf.train.Int64List(value=outputs))}))
        writer.write(example_proto.SerializeToString())
print('Done')
print('Skipped', skipped, 'of', total)
