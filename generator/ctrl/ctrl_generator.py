import tensorflow as tf
import numpy as np

tf.enable_eager_execution()
import generator.ctrl.model.transformer as transformer
import re
from collections import Counter
from tensorflow.python import debug as tf_debug
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import embedding_ops
import fastBPE
from story.utils import *
import warnings
warnings.filterwarnings("ignore")

# the loss function is a simple categorical crossentropy between the logits and the labels
def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)


class CTRLGenerator():

    def __init__(self, control_code="Apocalypse ", generate_num=28, temperature=0.4, topk=40, nucleus_prob=0):

        self.generate_num=generate_num
        model_dir = "generator/ctrl/model/aidungeon2model/"
        self.control_code = control_code
        vocab_file = 'generator/ctrl/model/vocab'
        code_file = 'generator/ctrl/model/codes'

        self.max_new_lines = 5

        # load the vocabulary from file
        vocab = open(vocab_file, encoding='utf-8').read().split('\n')
        vocab = list(map(lambda x: x.split(' ')[0], vocab)) + ['<unk>'] + ['\n']
        print('{} unique words'.format(len(vocab)))

        # length of the vocabulary
        vocab_size = len(vocab)

        # define the numericalization map
        # idx2word maps the numericalized ID to the word
        # word2idx maps the word to the numericalized ID
        self.word2idx = {u: i for i, u in enumerate(vocab)}
        self.idx2word = np.array(vocab)

        # sequence length to use for the transformer
        # the model is trained with a self.seq_length of 512
        # so, any value <= 512 should work
        self.seq_length = min(self.generate_num, 256)

        # the dimension of the transformer
        embedding_dim = 1280

        # input for the keras model
        tokens = tf.keras.layers.Input(shape=(self.seq_length,), dtype='int32')

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
            model_dir=model_dir)

        # this converts the Keras model to a TensorFlow estimator
        # this step is critical
        # remember to patch the TF 1.14 file before running the code, else you're going to see errors here
        estimator_model = tf.keras.estimator.model_to_estimator(keras_model=model, config=run_config)

        # we now create a serving function from this estimator
        # this enables us to load the model once and easily query it multiple times
        def serving_input_fn():
            inputs = {'input_1': tf.placeholder(tf.int32, [1, self.seq_length])}
            return tf.estimator.export.ServingInputReceiver(inputs, inputs)

        self.predict_fn = tf.contrib.predictor.from_estimator(estimator_model, serving_input_fn)

        # almost there, we now take the user prompt and tokenize with BPE
        # load BPE codes
        self.bpe = fastBPE.fastBPE(code_file, vocab_file)

        self.temperature=temperature
        self.nucleusprob = nucleus_prob
        self.penalty = 1.2
        self.topk=topk

    def configure_verb_probs(self, probabilities, options):

        # Make sure only a possible verb is chosen.
        for word in get_possible_verbs():
                probabilities[self.word2idx[word]] += 100

        # Disallow used verbs
        if "used_verbs" in options:
            for verb in options["used_verbs"]:
                if verb in self.word2idx:
                    probabilities[self.word2idx[verb]] = -1e8

        return probabilities

    def prompt_replace(self, prompt):
        # print("\n\nBEFORE PROMPT_REPLACE:")
        # print(repr(prompt))
        if prompt[-1] != " ":
            prompt = prompt + " "

        prompt = second_to_first_person(prompt)

        prompt = self.control_code + prompt
        # print("\n\nAFTER PROMPT_REPLACE")
        # print(repr(prompt))
        return prompt

    def result_replace(self, result):
        # print("\n\nBEFORE RESULT_REPLACE:")
        # print(repr(result))

        result = cut_trailing_sentence(result)
        first_letter_capitalized = result[0].isupper()
        result = result.replace('."', '".')
        result = result.replace("#", "")
        result = result.replace("*", "")
        result = first_to_second_person(result)
        result = remove_profanity(result)

        if not first_letter_capitalized:
            result = result[0].lower() + result[1:]

        #
        # print("\n\nAFTER RESULT_REPLACE:")
        # print(repr(result))

        return result

    def generate_next_token(self, token, tokens_generated, options, num_new_lines, token_num, first_token=False, forbid_newline=False):

        # get the logits from the prediction function
        # the logic here is a bit convoluted because we are allowing generation past 512 tokens
        # this is done by sliding the window over (past 512 tokens) and continuing prediction
        # I'm sure this can be simplified (TODO)
        if token <= self.seq_length:
            prompt_logits = self.predict_fn({'input_1': tokens_generated[:, :self.seq_length]})[
                                'tied_embedding_softmax'].squeeze() / (self.temperature if self.temperature > 0 else 1.)
            _token = token if token < self.seq_length else -1
        else:
            _token = -1
            end = token + 1
            start = token - self.seq_length + 2
            prompt_logits = \
                self.predict_fn({'input_1': np.hstack((tokens_generated[:, 0:1], tokens_generated[:, start:end]))})[
                    'tied_embedding_softmax'].squeeze() / (self.temperature if self.temperature > 0 else 1.)

        # if penalty (for repetition) is non-zero,
        # discount the logits from already generated tokens
        if self.penalty > 0:
            penalized_so_far = set()
            for _ in range(token + 1):
                generated_token = tokens_generated[0][_]
                if generated_token not in penalized_so_far:
                    penalized_so_far.add(generated_token)
                    prompt_logits[_token][generated_token] /= self.penalty

        # disallow some tokens
        forbidden_tokens = ['<unk>', 'Sco@@', "&amp@@", "1]@@", "2]@@", "3]@@", "4]@@", "https://www.@@", "[@@", ":@@",
                            "Edit", "&@@", "2:","1:", ":", "Edit@@", "EDI@@", "EDIT@@", "edit", "TL@@", "tl@@", ";@@",
                            '**', "http://@@", "Redd@@", "UP@@", "mom", "Up@@", "Me:", "Update", "mom@@", "Part",
                            "http://www.@@", "edit@@", "*@@", "Writing", "Text@@", "\\@@", "<br>@@", "<div", "|@@", '...',
                            '..','…', 'https://@@', '...@@', "http://gutenberg@@"]

        #encourage_tokens = ["zombie", "radiation", "fallout", "undead", "corpse", "vampire", "virus", "plague"]
        encourage_tokens = []
        for encourage_token in encourage_tokens:
            prompt_logits[_token][self.word2idx[encourage_token]] *= 1.2

        for forbidden_token in forbidden_tokens:
            prompt_logits[_token][self.word2idx[forbidden_token]] = -1e8

        last_ind = tokens_generated[0][token]

        if forbid_newline:
            prompt_logits[_token][self.word2idx['\n']] = -1e8
        else:
            prompt_logits[_token][self.word2idx['\n']] *= 1.0

        # Set whitelist
        if "word_whitelist" in options and token_num in options["word_whitelist"].keys():
            for word in options["word_whitelist"][token_num]:
                prompt_logits[_token][self.word2idx[word]] += 100

        # Set blacklist, overwrites whitelist
        if "word_blacklist" in options and token_num in options["word_blacklist"].keys():
            for word in options["word_blacklist"][token_num]:
                prompt_logits[_token][self.word2idx[word]] = -1e8

        # compute probabilities from logits
        prompt_probs = np.exp(prompt_logits[_token])
        prompt_probs = prompt_probs / sum(prompt_probs)
        pruned_list = np.argsort(prompt_probs)[::-1]
        # if you are using nucleus prob, then compute the nucleus probability size
        if self.nucleusprob > 0.:
            minimum_topk = 1
            nucleus = max(np.where(np.cumsum(np.sort(prompt_probs)[::-1]) > self.nucleusprob)[0][0], minimum_topk)
        elif self.topk > 0:
            nucleus = self.topk
        else:
            nucleus = len(pruned_list)

        pruned_list = pruned_list[:nucleus]

        # if temperature is 0
        # just pick the first (most probable) token
        if self.temperature == 0:
            idx = pruned_list[0]
        else:
            # else,
            # sample from the pruned_list with the logits
            chosen_idx = int(
                tf.random.categorical(np.expand_dims(prompt_logits[_token][pruned_list], 0), num_samples=1).numpy())
            idx = pruned_list[chosen_idx]

        return idx

    def generate(self, prompt, options=None):
        prompt = self.prompt_replace(prompt)

        debug_print = True

        if debug_print:
            print("\n\n*****DEBUG*****")
            print("Prompt is:")
            print(prompt + "\n\n")

        if options is None: options = dict()
        if "used_verbs" not in options:
            options["used_verbs"] = set()

        first_token = True

        # tokenize provided prompt
        split_prompt = self.bpe.apply([prompt])[0].split()
        text = [self.word2idx[i] for i in split_prompt]
        total_text_len = len(text) + self.generate_num

        # pad with 0s and create a mini-batch of 2 (arbitrary, for ease of code)
        padded_text = text + [0] * (total_text_len - len(text))
        tokens_generated = np.tile(padded_text, (1, 1))
        result = ""

        token_num = 0
        num_new_lines = 0
        for token in range(len(text) - 1, total_text_len - 1):
            idx = self.generate_next_token(token, tokens_generated, options, num_new_lines, token_num, first_token=first_token, forbid_newline=False)
            is_nothing = len(cut_trailing_sentence(result)) == 0 or len(cut_trailing_quotes(result)) == 0
            if self.idx2word[idx] == '\n' and token_num > 7 and not is_nothing:
                return self.result_replace(result)
            elif self.idx2word[idx] == '\n':
                idx = self.generate_next_token(token, tokens_generated, options, num_new_lines, token_num,
                                               first_token=first_token, forbid_newline=True)
            # assign the token for generation

            tokens_generated[0][token + 1] = idx
            if debug_print:
                print(repr(self.idx2word[idx]), end="_")

            tokens_generated_so_far = ' '.join([self.idx2word[c] for c in tokens_generated[0][len(text):token+2]])
            tokens_generated_so_far = re.sub('(@@ )', '', string=tokens_generated_so_far)
            tokens_generated_so_far = re.sub('(@@ ?$)', '', string=tokens_generated_so_far)
            result = tokens_generated_so_far

            token_num += 1
        if debug_print:
            print("\n****END DEBUG*****\n")
        return self.result_replace(result)