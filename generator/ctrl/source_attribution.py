from __future__ import division
from __future__ import print_function
import tensorflow as tf
import os
import numpy as np
tf.enable_eager_execution()
import transformer
import argparse
import pdb
import sys
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

args = parser.parse_args()
tf.random.set_random_seed(args.seed)
os.environ['PYTHONHASHSEED'] = str(args.seed)
np.random.seed(args.seed)

# load the vocabulary from file
vocab = open('vocab').read().decode(encoding='utf-8').split('\n') if not use_py3 else open('vocab', encoding='utf-8').read().split('\n')
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
# the model is trained with a seq_length of 512
# so, any value <= 512 should work
seq_length = 256




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
optimizer = tf.contrib.tpu.CrossShardOptimizer(
    tf.contrib.estimator.clip_gradients_by_norm(
        tf.train.AdagradOptimizer(learning_rate=1e-2), 0.25)
    )        

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
estimator_model = tf.keras.estimator.model_to_estimator(keras_model=model, config=run_config)

# we now create a serving function from this estimator
# this enables us to load the model once and easily query it multiple times
def serving_input_fn():
    inputs = {'input_1': tf.placeholder(tf.int32, [2,seq_length])}
    return tf.estimator.export.ServingInputReceiver(inputs, inputs)
predict_fn = tf.contrib.predictor.from_estimator(estimator_model, serving_input_fn)

# almost there, we now take the user prompt and tokenize with BPE
# load BPE codes
bpe = fastBPE.fastBPE('codes', 'vocab')

domains = []
with open('control_codes.txt', 'r') as f:
    domains = [line.split() for line in f.readlines()]
    domains = [(t[1], float(t[0])) for t in domains]

    
while True:
    _prompt = raw_input('ENTER PROMPT: ') if not use_py3 else input('ENTER PROMPT: ')

    ppls = {}
    # loop over all domains and compute perplexity
    for domain, domain_prior in domains:
       print(u'computing for domain: {}'.format(domain))
       # tokenize data and add domain tag to it
       prompt = domain + u' ' + _prompt
       split_prompt = bpe.apply([prompt])[0].split()

       # numericalize data and pad to the seq_len dimension
       text = [word2idx[i] for i in split_prompt]
       padding_text = text + [0] * (seq_length - len(text))
       tokens_generated = np.tile(padding_text, (2,1)) 
       output_scores = predict_fn({'input_1':tokens_generated})['tied_embedding_softmax'].squeeze()[0]
       token_scores = output_scores[:-1]

       # compute the perplexity for this sequence
       xent = 0
       for sequence_idx, token_idx in enumerate(text[1:]):
           token = idx2word[token_idx]

           # compute the probability of this token
           Z = np.exp(token_scores[sequence_idx]).sum()
           token_prob = np.exp(token_scores[sequence_idx, token_idx]) / Z 
           xent -= np.log(token_prob) / len(text[1:])
           
       ppls[domain] = round(np.exp(xent), 6)
       #print(u'{} ppl = {}'.format(domain, ppls[domain]))

    # sort the domains based on perplexities and print
    ppls = [(k, v) for k, v in ppls.items()]
    ppls.sort(key=lambda x: x[1])
    print('PROMPT: {}'.format(_prompt))
    for t in ppls:
        domain, ppl = t
        print(u'{} ppl = {}'.format(domain, ppl))
