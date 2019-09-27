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

use_py3 = platform.python_version()[0] == '3'

parser = argparse.ArgumentParser(description='TensorFlow code for creating TFRecords data')
parser.add_argument('--text_file', type=str, required=True,
                                        help='location of text file to convert to TFRecords')
parser.add_argument('--control_code', type=str, required=True,
                                        help='control code to use for this file. must be in the vocabulary, else it will error out.')
parser.add_argument('--sequence_len', type=int, required=True,
                                        help='sequence length of model being fine-tuned (256 or 512)')

args = parser.parse_args()


path_to_train_file = fname = args.text_file
domain = [args.control_code]

train_text = open(path_to_train_file, 'rb').read().decode(encoding='utf-8')
bpe = fastBPE.fastBPE('../codes', '../vocab')
tokenized_train_text = bpe.apply([train_text.encode('ascii', errors='ignore') if not use_py3 else train_text])[0] # will NOT work for non-English texts 
# if you want to run non-english text, please tokenize separately using ./fast applybpe and then run this script on the .bpe file with utf8 encoding

tokenized_train_text = re.findall(r'\S+|\n', tokenized_train_text)
tokenized_train_text = list(filter(lambda x: x != u'@@', tokenized_train_text))

# load the vocabulary from file
vocab = open('../vocab').read().decode(encoding='utf-8').split('\n') if not use_py3 else open('../vocab', encoding='utf-8').read().split('\n')
vocab = list(map(lambda x: x.split(' ')[0], vocab)) + ['<unk>'] + ['\n']
print ('{} unique words'.format(len(vocab)))

if args.control_code not in vocab:
    print('Provided control code is not in the vocabulary')
    print('Please provide a different one; refer to the vocab file for allowable tokens')
    sys.exit(1)
    
# Creating a mapping from unique characters to indices
word2idx = {u:i for i, u in enumerate(vocab)}
idx2word = np.array(vocab)

seq_length = args.sequence_len-1

def numericalize(x):
    count = 0
    for i in x:
        if i not in word2idx:
            print(i)
            count += 1
    return count>1, [word2idx.get(i, word2idx['<unk>'])  for i in x]

tfrecords_fname = fname.lower()+'.tfrecords'

total = 0
skipped = 0
with tf.io.TFRecordWriter(tfrecords_fname) as writer:
    for i in tqdm.tqdm(range(0, len(tokenized_train_text), seq_length)):
        flag_input, inputs = numericalize(domain+tokenized_train_text[i:i+seq_length])
        flag_output, outputs = numericalize(tokenized_train_text[i:i+seq_length+1])
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
