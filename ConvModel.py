from DQNModel import DQNModel
import numpy as np
import tensorflow as tf

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x,W):
  return tf.nn.conv2d(x,W,strides=[1,1,1,1], padding='SAME')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')

class ConvModel(DQNModel):
  def __init__(
      self, env, initial_learning_rate=0.1,
      learning_rate_decay_factor=0.96, num_steps_per_decay=1000,
      gamma=0.99, tau=0.01, soft_updates=False):
    super(ConvModel, self).__init__(env)

  def build_net(self, x):
    """Builds a two layer neural network. Returns a dictionary
    containing weight variables and outputs.
    """

    W_conv1 = weight_variable([5,5,3,32])
    b_conv1 = bias_variable([32])

    x_image = tf.image.resize_images(x, 28, 28,
        method=0, align_corners=False)

    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    W_conv2 = weight_variable([5,5,32,64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    W_fc2 = weight_variable([1024, self.num_actions])
    b_fc2 = bias_variable([self.num_actions])

    outputs = tf.matmul(h_fc1, W_fc2) + b_fc2

    net_dict = {
        'shared_vars':{
          'W_conv1':W_conv1,
          'b_conv1':b_conv1,
          'W_conv2':W_conv2,
          'b_conv2':b_conv2,
          'W_fc1':W_fc1,
          'b_fc1':b_fc1,
          'W_fc2':W_fc2,
          'b_fc2':b_fc2,
        },
        'outputs':outputs,
    }

    return net_dict

  def reshape_input(self, observation):
    return np.reshape(observation, [-1, self.input_shape[0],
      self.input_shape[1], self.input_shape[2]])

  def infer_online_q(self, observation):
    observation = self.reshape_input(observation)
    q = self.sess.run(self.online_model['outputs'], feed_dict={
      self.inputs:observation})
    return q

  def infer_target_q(self, observation):
    observation = self.reshape_input(observation)
    q = self.sess.run(self.target_model['outputs'], feed_dict={
      self.inputs:observation})
    return q