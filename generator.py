import json
import os
import numpy as np
import tensorflow as tf

import gpt2.src.model as model
import gpt2.src.sample as sample
import gpt2.src.encoder as encoder
from utils import *

pos_action_starts = ["You attack", "You tell", "You use", "You go"]


class StoryGenerator():

    def __init__(self, sess, length=100, temperature=0.9, top_k=40):
    
        seed = None
        batch_size=1
        model_path='gpt2/models/117M'
        self.sess = sess
    
        self.enc = encoder.get_encoder(model_path)
        hparams = model.default_hparams()
        with open(os.path.join(model_path, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))  

        self.context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        self.output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=self.context,
            batch_size=batch_size,
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(model_path)
        saver.restore(self.sess, ckpt)
            
        
    def generate(self, prompt):
        context_tokens = self.enc.encode(prompt)
        out = self.sess.run(self.output, feed_dict={
                self.context: [context_tokens for _ in range(1)]
            })[:, len(context_tokens):]

        text = self.enc.decode(out[0])
        return text
        
    def generate_story_block(self, prompt):
        block = self.generate(prompt)
        block = cut_trailing_sentence(block)
        block = story_replace(block)
        
        return block
        
    def generate_action_options(self, prompt, action_starts=pos_action_starts):
    
        possible_actions = []
        for phrase in action_starts:
            action = phrase + self.generate(prompt + phrase)
            action = first_sentence(action)
            possible_actions.append(action)
            
        return possible_actions
        
    def generate_action_result(self, prompt, phrase):
        action = phrase + self.generate(prompt + phrase)
        action_result = cut_trailing_sentence(action)
        action_result = story_replace(action_result)
        
        action = first_sentence(action)
        

        return action, action_result

        
