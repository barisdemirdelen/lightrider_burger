import tensorflow as tf
from tensorflow.contrib.layers import l2_regularizer

from bot.nn.ops import conv2d_layer, flatten2d, fully_connected


class ValueModel(object):
    def __init__(self):
        self.weight_regularizer = l2_regularizer(1e-4)
        # self.weight_regularizer = None
        self.parameters = []
        self.reuse = False

    def inference(self, x):
        with tf.variable_scope("value_model"):
            conv, W, b = conv2d_layer(x, filter=[5, 5], units=8, padding='SAME', name='conv1_1')
            self.parameters.append(W)
            self.parameters.append(b)

            i = 0
            for i in range(8):
                conv, W, b = conv2d_layer(conv, filter=[3, 3], units=16, padding='SAME', name='conv1_%d' % (i + 2))
                self.parameters.append(W)
                self.parameters.append(b)
            conv, W, b = conv2d_layer(conv, filter=[1, 1], units=1, padding='SAME', name='conv1_%d' % (i + 3))
            self.parameters.append(W)
            self.parameters.append(b)

            flatten = flatten2d(conv, name='flatten')
            logits = fully_connected(flatten, units=1, activation=False, name='logits')

        return logits

    def accuracy(self, logits, labels):
        with tf.name_scope('accuracy'):
            softmax = tf.nn.softmax(logits)
            correct_prediction = tf.equal(tf.argmax(softmax, 1), tf.argmax(labels, 1))
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            tf.summary.scalar("accuracy", accuracy)

        return accuracy

    def loss(self, logits, labels):
        cross_entropy = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=logits, labels=labels))
        regularizer = 0
        if self.weight_regularizer is not None:
            for parameter in tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES):
                regularizer += self.weight_regularizer(parameter)
        loss = cross_entropy + regularizer

        return loss
