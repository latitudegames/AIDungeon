import tensorflow as tf
import numpy as np

def angle_defn(pos, i, d_model_size):
  angle_rates = 1 / np.power(10000, (2 * (i//2)) / np.float32(d_model_size))
  return pos * angle_rates

def positional_encoding(position, d_model_size):
  # create the sinusoidal pattern for the positional encoding
  angle_rads = angle_defn(np.arange(position)[:, np.newaxis], np.arange(d_model_size)[np.newaxis, :], d_model_size)
  
  sines = np.sin(angle_rads[:, 0::2])
  cosines = np.cos(angle_rads[:, 1::2])
  
  pos_encoding = tf.cast(np.concatenate([sines, cosines], axis=-1)[np.newaxis, ...], dtype=tf.float32)
  return pos_encoding 



def scaled_dot_product_attention(q, k, v, mask):
  # calculate attention
  matmul_qk = tf.matmul(q, k, transpose_b=True)
  
  dk = tf.cast(tf.shape(k)[-1], tf.float32)
  scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)

  if mask is not None:
    scaled_attention_logits += (mask * -1e9)
    
  attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1) 
  output = tf.matmul(attention_weights, v) 
  return output

class MultiHeadAttention(tf.keras.layers.Layer):
  def __init__(self, d_model_size, num_heads):
    super(MultiHeadAttention, self).__init__()
    self.num_heads = num_heads
    self.d_model_size = d_model_size
    
    self.depth = int(d_model_size / self.num_heads)
    
    self.Wq = tf.keras.layers.Dense(d_model_size)
    self.Wk = tf.keras.layers.Dense(d_model_size)
    self.Wv = tf.keras.layers.Dense(d_model_size)
    
    self.dense = tf.keras.layers.Dense(d_model_size)
        
  def split_into_heads(self, x, batch_size):
    x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
    return tf.transpose(x, perm=[0, 2, 1, 3])
    
  def call(self, v, k, q, mask):
    batch_size = tf.shape(q)[0]
    
    q = self.Wq(q)
    k = self.Wk(k)
    v = self.Wv(v)
    
    q = self.split_into_heads(q, batch_size)
    k = self.split_into_heads(k, batch_size)
    v = self.split_into_heads(v, batch_size)
    
    scaled_attention = tf.transpose(scaled_dot_product_attention(q, k, v, mask), perm=[0, 2, 1, 3])
    original_size_attention = tf.reshape(scaled_attention,  (batch_size, -1, self.d_model_size))
    output = self.dense(original_size_attention) 
        
    return output



def point_wise_feed_forward_network(d_model_size, dff):
  return tf.keras.Sequential([tf.keras.layers.Dense(dff, activation='relu'), 
      tf.keras.layers.Dense(d_model_size)])


class EncoderLayer(tf.keras.layers.Layer):
  def __init__(self, d_model_size, num_heads, dff, rate=0.1):
    super(EncoderLayer, self).__init__()

    self.multi_head_attention = MultiHeadAttention(d_model_size, num_heads)
    self.ffn = point_wise_feed_forward_network(d_model_size, dff)

    self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
    self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
    
    self.dropout1 = tf.keras.layers.Dropout(rate)
    self.dropout2 = tf.keras.layers.Dropout(rate)
    
  def call(self, x, training, mask):
    normed = self.layernorm1(x)
    attn_output  = self.multi_head_attention(normed, normed, normed, mask)
    attn_output = self.dropout1(attn_output, training=training)
    out1 = x + attn_output

    out2 = self.layernorm2(out1)
    ffn_output = self.ffn(out2)
    ffn_output = self.dropout2(ffn_output, training=training)
    out2 = out1 + ffn_output
    
    return out2




class Encoder(tf.keras.layers.Layer):
  def __init__(self, num_layers=48, d_model_size=1280, num_heads=16, dff=8192, input_vocab_size=50000,
               rate=0.1, **kwargs):
    super(Encoder, self).__init__()

    self.d_model_size = d_model_size
    self.num_layers = num_layers
    
    self.pos_encoding = positional_encoding(input_vocab_size, self.d_model_size)

    for i in range(num_layers):
      setattr(self, "layer%i" % i, EncoderLayer(d_model_size, num_heads, dff, rate))
    
    self.layernorm = tf.keras.layers.LayerNormalization(epsilon=1e-6)  
    self.dropout = tf.keras.layers.Dropout(rate)

  def get_config(self):
    base_config = super(Encoder, self).get_config()
    return base_config
  
  def call(self, x, training):

    seq_len = tf.shape(x)[1]
    
    mask = 1 - tf.linalg.band_part(tf.ones((seq_len, seq_len)), -1, 0)
    
    x *= tf.math.sqrt(tf.cast(self.d_model_size, tf.float32))
    x += self.pos_encoding[:, :seq_len, :]

    x = self.dropout(x, training=training)
    
    for i in range(self.num_layers):
      x = getattr(self, "layer%i" % i)(x, training, mask)
    return self.layernorm(x)

