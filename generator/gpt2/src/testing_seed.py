import numpy as np
import tensorflow as tf



seed=None

print(np.random.seed(seed))
# 

tf.set_random_seed(seed)
generate = tf.random_uniform(())
with tf.Session() as sess:
  print(generate.eval())
  # 0.96046877