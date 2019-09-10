import json
import os
import numpy as np
import tensorflow as tf

import gpt2.src.model as model
from tensorflow.contrib import predictor
import gpt2.src.sample as sample
import gpt2.src.encoder as encoder
from utils import *
import pdb

pos_action_starts = ["You attack", "You tell", "You use", "You go"]


class StoryGenerator():

    def __init__(self, sess, length=75, temperature=0.9, top_k=40):
    
        seed = None
        batch_size=1
        model_path='gpt2/models/117M'
        self.sess = sess
    
        self.enc = encoder.get_encoder(model_path)
        hparams = model.default_hparams()
        with open(os.path.join(model_path, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))

        pdb.set_trace()

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


def save_model():
    length=75
    temperature=0.9
    top_k=40
    
    with tf.Session() as sess:
        seed = None
        batch_size=None
        model_path='gpt2/models/117M'

        hparams = model.default_hparams()
        with open(os.path.join(model_path, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))  

        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
        )
        print("***********************",type(output))
        
        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(model_path)
        saver.restore(sess, ckpt)

        tf.saved_model.simple_save(sess, "./saved2", inputs={"context": context}, outputs={"output": output})

def load_model():
    # Set your memory fraction equal to a value less than 1, 0.6 is a good starting point.
    # If no fraction is defined, the tensorflow algorithm may run into gpu out of memory problems.
    fraction = 0.6
    path_to_graph = "./saved"

    model_path = 'gpt2/models/117M'
    enc = encoder.get_encoder(model_path)

    predict_fn = predictor.from_saved_model(path_to_graph, config=config)
    context_tokens = [enc.encode("hello")]
    predictions = predict_fn({"context": context_tokens})
    output = enc.decode(predictions["output"][0])
    print(output)

    return (output, session)

if __name__ == '__main__':
   save_model()
    
      
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    


        
