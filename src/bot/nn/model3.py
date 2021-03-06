import tensorflow as tf
from tensorflow.contrib.layers import l2_regularizer

from bot.nn.ops import conv2d_layer, pool2d, flatten2d, fully_connected


class Model3(object):
    def __init__(self):
        self.weight_regularizer = l2_regularizer(1e-4)
        # self.weight_regularizer = None
        self.parameters = []
        self.reuse = False

    def inference(self, x):
        with tf.variable_scope("nn_model3"):
            conv, W, b = conv2d_layer(x, filter=[5, 5], units=4, padding='SAME', name='conv1_13')
            self.parameters.append(W)
            self.parameters.append(b)
            i = 0
            for i in range(0):
                conv, W, b = conv2d_layer(conv, filter=[3, 3], units=4, padding='SAME', name='conv1_%d3' % (i + 2))
                self.parameters.append(W)
                self.parameters.append(b)

            conv, W, b = conv2d_layer(conv, filter=[1, 1], units=1, padding='SAME', name='conv1_%d3' % (i + 3))
            self.parameters.append(W)
            self.parameters.append(b)
            # conv3_1 = conv2d_layer(pool2, filter=[3, 3], units=64, padding='SAME', name='conv3_1')
            # conv3_2 = conv2d_layer(conv3_1, filter=[3, 3], units=64, padding='SAME', name='conv3_2')
            # pool3 = pool2d(conv3_2, 'pool3')
            #
            # conv4_1 = conv2d_layer(pool3, filter=[3, 3], units=128, padding='SAME', name='conv4_1')
            # conv4_2 = conv2d_layer(conv4_1, filter=[3, 3], units=128, padding='SAME', name='conv4_2')
            # pool4 = pool2d(conv4_2, 'pool4')
            #
            # conv5_1 = conv2d_layer(pool4, filter=[3, 3], units=256, padding='SAME', name='conv5_1')
            # conv5_2 = conv2d_layer(conv5_1, filter=[3, 3], units=256, padding='SAME', name='conv5_2')
            # pool5 = pool2d(conv5_2, 'pool5')

        return conv

    def accuracy(self, logits, labels):
        with tf.name_scope('accuracy'):
            softmax = tf.nn.softmax(logits)
            correct_prediction = tf.equal(tf.argmax(softmax, 1), tf.argmax(labels, 1))
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            tf.summary.scalar("accuracy", accuracy)

        return accuracy

    def loss(self, probs, target_actions, rewards):
        # cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=labels))

        # tf.summary.scalar("cross_entropy_loss", cross_entropy)
        # tf.summary.scalar("regularization_loss", regularizer)
        # tf.summary.scalar("total_loss", loss)

        q_action = tf.reduce_sum(tf.multiply(probs, target_actions), reduction_indices=(1, 2))
        loss = tf.reduce_mean(tf.square(rewards - q_action))

        regularizer = 0
        if self.weight_regularizer is not None:
            for parameter in tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES):
                regularizer += self.weight_regularizer(parameter)
        loss = loss + regularizer

        return loss
