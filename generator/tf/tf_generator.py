import json
import os
import numpy as np
import tensorflow as tf

from src.model import *
from tensorflow.contrib import predictor
from src.sample import *
from src.encoder import *
import pdb

pos_action_starts = ["You attack", "You tell", "You use", "You go"]


class TFGenerator():

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

def save_model():
    length=75
    temperature=0.9
    top_k=40
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    
    with tf.Session() as sess:
        seed = None
        batch_size=None
        model_path='models/774M'

        hparams = default_hparams()
        with open(os.path.join(model_path, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))  

        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
        )
        print("***********************",type(output))
        
        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(model_path)
        saver.restore(sess, ckpt)

        tf.saved_model.simple_save(sess, "./saved_model", inputs={"context": context}, outputs={"output": output})

def load_model():
    fraction = 0.6
    config = config = generate_gpu_config(fraction)
    path_to_graph = "./saved"

    # tf.saved_model.loader.load(
    #   session,
    #  [tf.saved_model.tag_constants.SERVING],
    # path_to_graph)

    # output = session.graph.get_tensor_by_name('output:0')
    # context = session.graph.get_tensor_by_name('context:0')
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
    
      
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    


        
