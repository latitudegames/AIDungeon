from __future__ import print_function
import torch
import os
import tqdm
import pdb
import numpy as np
import platform
import hashlib
import pytorch_transformer
import re
import argparse
import tensorflow as tf
import fastBPE
from tensorflow.python import pywrap_tensorflow

use_py3 = platform.python_version()[0] == '3'

parser = argparse.ArgumentParser(description='TensorFlow code for generating from CTRL')
parser.add_argument('--model_path', type=str, required=True,
                                        help='location of model *data* checkpoint; this is NOT the directory but rather the model checkpoint')
parser.add_argument('--seed', type=int, default=1337,
                                        help='random seed for TensorFlow, numpy and PythonHash')
parser.add_argument('--generate_num', type=int, default=256,
                                        help='number of tokens to generate')
parser.add_argument('--temperature', type=float, default=0,
                                        help='temperature for sampling distribution; 0 means greedy')
parser.add_argument('--nucleus', type=float, default=0.,
                                        help='cumulative probability cutoff for nucleus sampling; 0 means no nucleus sampling')
parser.add_argument('--topk', type=int, default=0,
                                        help='topk value for sampling from the softmax distribution ; 0 means no topk preferred')
parser.add_argument('--penalty', type=float, default=1.2,
                                        help='repetition penalty for greedy sampling')
parser.add_argument('--print_once', action='store_true',
                                        help='the completion is printed only at the end; not every word')
parser.add_argument('--topn', type=int, default=0,
                                        help='print top-n candidates during generations; defaults to 0 which is no printing')

args = parser.parse_args()
torch.manual_seed(args.seed)
torch.cuda.manual_seed_all(args.seed)
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
embedding_dim = 1280

class TiedEmbeddingSoftmax(torch.nn.Module):

  def __init__(self, vocab_size=vocab_size, embedding_size=embedding_dim, **kwargs):
    super(TiedEmbeddingSoftmax, self).__init__()
    self.w = torch.nn.Parameter(torch.zeros(vocab_size, embedding_size))
    self.b = torch.nn.Parameter(torch.zeros(vocab_size))

  def forward(self, inputs, embed=True):
    if embed:
      return torch.nn.functional.embedding(inputs, self.w)
    else:
      return torch.tensordot(inputs, self.w.t(), 1) + self.b


test_softmax = TiedEmbeddingSoftmax()
test_encoder = pytorch_transformer.Encoder()

def predict_fn(inputs):
  with torch.no_grad():
    embedded = torch.tensor(inputs['input_1']).cuda()
    embedded = test_softmax(embedded, embed=True)
    embedded = test_encoder(embedded)
    embedded = test_softmax(embedded, embed=False)
  return embedded






bpe = fastBPE.fastBPE('codes', 'vocab')
seq_length = min(args.generate_num, 256)
pytorch_model_hash = hashlib.md5(args.model_path.encode('utf-8')).hexdigest()
temperature = args.temperature
nucleusprob = args.nucleus
penalty = args.penalty
topk = args.topk

# try to load the model from a (cached) PyTorch checkpoint
# if one is not available, then create it by converting the weights
if os.path.exists(pytorch_model_hash):
  print('Found PyTorch checkpoint @', pytorch_model_hash)
  print('Loading instead of converting from TensorFlow')
  checkpoint = torch.load(pytorch_model_hash)
  test_softmax.load_state_dict(checkpoint['softmax'])
  test_encoder.load_state_dict(checkpoint['encoder'])

  test_softmax.to('cuda')
  test_encoder.to('cuda')

else:
  print('Could not find PyTorch checkpoint')
  print('Converting weights and will store the PyTorch checkpoint as ', pytorch_model_hash)
  chkpt_for_reader = '.'.join(args.model_path.split('.')[:-1])
  reader = pywrap_tensorflow.NewCheckpointReader(chkpt_for_reader)
  test_softmax.w = torch.nn.Parameter(torch.tensor(reader.get_tensor('w')).to('cuda'))
  test_softmax.b = torch.nn.Parameter(torch.tensor(reader.get_tensor('b')).to('cuda'))

  list_of_variables = list(filter(lambda x: 'Adagrad' not in x, reader.get_variable_to_shape_map().keys()))

  str2parameter = lambda x: torch.nn.Parameter(torch.tensor(reader.get_tensor(x)).t().to('cuda'))

  test_encoder.layernorm.weight = str2parameter('encoder/layer_normalization_96/gamma')
  test_encoder.layernorm.bias = str2parameter('encoder/layer_normalization_96/beta')
  for i in tqdm.tqdm(range(48)):
    if i==0:
      layer_variables = sorted(filter(lambda x: 'layer/' in x, list_of_variables))
    else:
      layer_variables = sorted(filter(lambda x: 'layer_'+str(i)+'/' in x, list_of_variables))

    current_layer = getattr(test_encoder, 'layer'+str(i))

    current_layer.layernorm1.bias = str2parameter(layer_variables[0])
    current_layer.layernorm1.weight = str2parameter(layer_variables[1])

    current_layer.layernorm2.bias = str2parameter(layer_variables[2])
    current_layer.layernorm2.weight = str2parameter(layer_variables[3])


    current_layer.multi_head_attention.Wq.bias = str2parameter(layer_variables[4])
    current_layer.multi_head_attention.Wq.weight = str2parameter(layer_variables[5])
    current_layer.multi_head_attention.Wk.bias = str2parameter(layer_variables[6])
    current_layer.multi_head_attention.Wk.weight = str2parameter(layer_variables[7])
    current_layer.multi_head_attention.Wv.bias = str2parameter(layer_variables[8])
    current_layer.multi_head_attention.Wv.weight = str2parameter(layer_variables[9])
    current_layer.multi_head_attention.dense.bias = str2parameter(layer_variables[10])
    current_layer.multi_head_attention.dense.weight = str2parameter(layer_variables[11])
    current_layer.ffn[0].bias = str2parameter(layer_variables[12])
    current_layer.ffn[0].weight = str2parameter(layer_variables[13])
    current_layer.ffn[2].bias = str2parameter(layer_variables[14])
    current_layer.ffn[2].weight = str2parameter(layer_variables[15])
  torch.save({
    'softmax': test_softmax.state_dict(),
    'encoder': test_encoder.state_dict(),
  }, pytorch_model_hash)

test_softmax.eval()
test_encoder.eval()




while True:
  prompt = raw_input('ENTER PROMPT: ') if not use_py3 else input('ENTER PROMPT: ')

  # tokenize provided prompt
  split_prompt = bpe.apply([prompt])[0].split()
  text = [word2idx[i] for i in split_prompt]


  # pad with 0s and create a mini-batch of 2 (arbitrary, for ease of code)
  padded_text = text + [0] * (args.generate_num - len(text))
  tokens_generated = np.tile(padded_text, (1,1))
  try:
    for token in range(len(text)-1, args.generate_num-1):
      # get the logits from the prediction function
      # the logic here is a bit convoluted because we are allowing generation past 512 tokens
      # this is done by sliding the window over (past 512 tokens) and continuing prediction
      # I'm sure this can be simplified (TODO)
      if token <= seq_length:
        prompt_logits = predict_fn({'input_1':tokens_generated[:, :seq_length]}).squeeze() / (temperature if temperature>0 else 1.)
        _token = token if token < seq_length else -1
      else:
        _token = -1
        end = token + 1
        start = token - seq_length + 2
        prompt_logits = predict_fn({'input_1':np.hstack((tokens_generated[:,0:1], tokens_generated[:,start:end]))}).squeeze() / (temperature if temperature>0 else 1.)

      prompt_logits = prompt_logits.cpu().detach().numpy()

      # if penalty (for repetition) is non-zero,
      # discount the logits from already generated tokens
      if penalty>0:
          penalized_so_far = set()
          for _ in range(token+1):
             generated_token = tokens_generated[0][_]
             # don't penalize newlines
             # you could also choose not to penalize frequent words
             # (which incidentally are sorted in the vocab file)
             # but I don't do that
             # if it prints too many new lines instead of continuing generating text,
             # you might want to comment this out
             #if idx2word[generated_token] == '\n':
             #    continue
             if generated_token in penalized_so_far:
                 continue
             penalized_so_far.add(generated_token)
             prompt_logits[_token][generated_token] /= penalty

      # disallow some tokens
      prompt_logits[_token][word2idx['<unk>']] = -1e8

      # sometimes, when generating from reddit,
      # it tries to generate the Score (reddit Karma) immediately after generating the Title:
      # to disallow this, we can just prevent it from generating Score
      prompt_logits[_token][word2idx['Sco@@']] = -1e8


      # compute probabilities from logits
      prompt_probs = np.exp(prompt_logits[_token])
      prompt_probs = prompt_probs / sum(prompt_probs)
      pruned_list = np.argsort(prompt_probs)[::-1]
      # if you are using nucleus prob, then compute the nucleus probability size
      if nucleusprob > 0.:
        minimum_topk = 1
        nucleus = max(np.where(np.cumsum(np.sort(prompt_probs)[::-1])>nucleusprob)[0][0], minimum_topk)
      elif topk > 0:
        # we are over-loading notation here
        # if you choose to specify a topk instead of a nucleus,
        # we will hardcode the nucleus to be just that
        nucleus = topk
      else:
        # if you specify neither nucleus or topk,
        # then we will use the whole list
        nucleus = len(pruned_list)

      pruned_list = pruned_list[:nucleus]  
      # if you want to disallow more complex tokens, you can do so here
      # for instance, if you want to disallow anything with the phrase `http`,
      # you can delete theme from the pruned_list
      # you can comment this out, I'm keeping it in for demonstration purpose
      tokens_to_disallow = []
      for _ in range(len(pruned_list)):
          if 'http' in idx2word[pruned_list[_]]:
              tokens_to_disallow.append(_)
      pruned_list = np.delete(pruned_list, tokens_to_disallow)

      if args.topn > 0 :
        print('TOPN :: top-n alternatives:', [idx2word[_] for _ in pruned_list[:args.topn]])

      # if temperature is 0
      # just pick the first (most probable) token
      if temperature==0:
          idx = pruned_list[0]
      else:
        # else,
        # sample from the pruned_list with the logits
        chosen_idx = torch.distributions.categorical.Categorical(torch.tensor(np.expand_dims(prompt_logits[_token][pruned_list],0))).sample().numpy()[0]
        idx = pruned_list[chosen_idx]

      if args.topn > 0 :
        print('TOPN :: chosen word:', idx2word[idx])

      # assign the token for generation
      tokens_generated[0][token+1] = idx

      # clear screen if you want to
      # os.system("clear")


      tokens_generated_so_far = ' '.join([idx2word[c] for c in tokens_generated[0].squeeze()[:token+2]])
      tokens_generated_so_far = re.sub('(@@ )', '', string=tokens_generated_so_far)
      tokens_generated_so_far = re.sub('(@@ ?$)', '', string=tokens_generated_so_far)              

      if not args.print_once:
        print('---------------------------------------')
        print(tokens_generated_so_far)
        print()
    print('---------------------------------------')            
    print(tokens_generated_so_far)
    print()
    
  except KeyboardInterrupt: #Exception as e:
    print('Continuing')

