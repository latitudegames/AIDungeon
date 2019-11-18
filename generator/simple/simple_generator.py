from story.utils import *
import warnings
warnings.filterwarnings("ignore")
import gpt_2_simple as gpt2
import os
import requests
import sys
import tensorflow as tf
import requests
from tqdm import tqdm
from gpt_2_simple.src import model, sample, encoder, memory_saving_gradients
from gpt_2_simple.src.load_dataset import load_dataset, Sampler
from gpt_2_simple.src.accumulate import AccumulatingOptimizer
import json
import numpy as np

tf.logging.set_verbosity(tf.logging.ERROR)

class SimpleGenerator:

    def __init__(self,  generate_num=80, temperature=0.3, top_k=40, top_p=0.8):
        self.generate_num=generate_num
        self.temp = temperature
        self.top_k = top_k
        self.top_p = top_p

        self.model_name = "run1"
        self.model_dir = "generator/simple/checkpoint"
        self.checkpoint_path = os.path.join(self.model_dir, self.model_name)
        if not os.path.isdir(os.path.join(self.model_dir, self.model_name)):
            print(f"Downloading {self.model_name} model...")

            subdir = os.path.join(self.model_dir, self.model_name)
            if not os.path.exists(subdir):
                os.makedirs(subdir)
            subdir = subdir.replace('\\', '/')  # needed for Windows

            for filename in ['checkpoint', 'encoder.json', 'hparams.json', 'model.ckpt.data-00000-of-00001',
                             'model.ckpt.index', 'model.ckpt.meta', 'vocab.bpe']:

                r = requests.get("https://storage.googleapis.com/gpt-2/" + subdir + "/" + filename, stream=True)

                with open(os.path.join(subdir, filename), 'wb') as f:
                    file_size = int(r.headers["content-length"])
                    chunk_size = 1000
                    with tqdm(ncols=100, desc="Fetching " + filename, total=file_size, unit_scale=True) as pbar:
                        # 1k for chunk_size, since Ethernet packet size is around 1500 bytes
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            f.write(chunk)
                            pbar.update(chunk_size)

        self.sess = gpt2.start_tf_sess()
        gpt2.load_gpt2(self.sess, model_dir=self.model_dir, model_name=self.model_name)


    def prompt_replace(self, prompt):
        # print("\n\nBEFORE PROMPT_REPLACE:")
        # print(repr(prompt))
        if len(prompt) > 0 and prompt[-1] == " ":
            prompt = prompt[:-1]

        #prompt = second_to_first_person(prompt)
        
        # print("\n\nAFTER PROMPT_REPLACE")
        # print(repr(prompt))
        return prompt

    def result_replace(self, result):
        # print("\n\nBEFORE RESULT_REPLACE:")
        # print(repr(result))

        result = cut_trailing_sentence(result)
        if len(result) == 0:
            return ""
        first_letter_capitalized = result[0].isupper()
        result = result.replace('."', '".')
        result = result.replace("#", "")
        result = result.replace("*", "")
        #result = first_to_second_person(result)
        result = remove_profanity(result)

        if not first_letter_capitalized:
            result = result[0].lower() + result[1:]

        #
        # print("\n\nAFTER RESULT_REPLACE:")
        # print(repr(result))

        return result

    def generate(self, prompt, options=None, seed=1):

        debug_print=False
        prefix = self.prompt_replace(prompt)

        if debug_print:
            print("******DEBUG******")
            print("Prompt is: ", repr(prefix))


        enc = encoder.get_encoder(self.checkpoint_path)
        hparams = model.default_hparams()
        batch_size = 1
        nsamples = 1
        with open(os.path.join(self.checkpoint_path, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))

        context = tf.compat.v1.placeholder(tf.int32, [batch_size, None])
        context_tokens = enc.encode(prefix)

        #np.random.seed(seed)
        #tf.compat.v1.set_random_seed(seed)

        output = sample.sample_sequence(
            hparams=hparams,
            length=min(self.generate_num, 1023 - (len(context_tokens) if prefix else 0)),
            start_token=enc.encoder['<|endoftext|>'] if not prefix else None,
            context=context if prefix else None,
            batch_size=batch_size,
            temperature=self.temp, top_p=self.top_p
        )[:, 1:]

        generated = 0
        gen_texts = []
        while generated < nsamples:
            if not prefix:
                out = self.sess.run(output)
            else:
                out = self.sess.run(output, feed_dict={
                    context: batch_size * [context_tokens]
                })
            for i in range(batch_size):
                generated += 1
                gen_text = enc.decode(out[i])
                if prefix:
                    gen_text = enc.decode(context_tokens[:1]) + gen_text
                gen_text = gen_text.lstrip('\n')
                gen_texts.append(gen_text)
        if debug_print:
            print("Generated result is: ", repr(gen_texts[0]))
            print("******END DEBUG******")
        result = gen_texts[0][len(prefix):]

        result = self.result_replace(result)
        if len(result) == 0:
            return self.generate(prompt)
        return result
