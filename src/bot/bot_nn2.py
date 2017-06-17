import random

from tensorflow.python.framework.errors_impl import NotFoundError
from tensorflow.python.training.saver import Saver
import numpy as np

from bot.board import DIRS
from bot.nn.model import Model
import tensorflow as tf

start_time = 0


class BotNN(object):
    def __init__(self, session=None):
        self.game = None
        self.separated = False
        self.model = Model()
        self.training = False

        self.inputs = tf.placeholder(dtype=tf.float32, shape=[None, 16, 16, 3], name='inputs2')
        self.target_actions = tf.placeholder(dtype=tf.float32, shape=[None, 4], name='target_actions2')
        self.rewards = tf.placeholder(dtype=tf.float32, shape=[None], name='rewards2')

        self.logits = self.model.inference(self.inputs)
        self.probs = tf.nn.softmax(self.logits)
        self.prediction = tf.argmax(self.probs, axis=1)
        self.loss = self.model.loss(probs=self.probs, target_actions=self.target_actions, rewards=self.rewards)
        self.algorithm = tf.train.AdamOptimizer(learning_rate=1e-4)
        self.optimizer = self.algorithm.minimize(self.loss)
        self.reward = 0
        self.saver = Saver()
        init = tf.global_variables_initializer()
        if session is None:
            session = tf.Session()
        self.session = session
        self.session.run(init)
        try:
            self.saver.restore(self.session, '/home/burger/projects/lightrider_burger/checkpoints/model2/nn_model2.ckpt')
        except NotFoundError:
            print('Not Found')

    def setup(self, game):
        self.game = game

    def give_reward(self, reward):
        self.reward = reward

    def sample_move(self):
        legal = self.game.field.legal_moves(self.game.my_botid)
        if len(legal) == 0:
            return 0
        else:
            (_, chosen) = random.choice(legal)
            for i, dir in enumerate(DIRS):
                if chosen == dir[1]:
                    return i
            return 0

    def do_turn(self):
        self.game.last_order = None
        self.reward = 0

        if not self.training:
            probs = self.session.run(self.probs, feed_dict={self.inputs: self.get_cell_tensor()})
            action = np.random.choice(np.arange(4), p=probs[0])
            string_move = DIRS[action][1]
            self.game.issue_order(string_move)

        return 0

    def get_cell_tensor(self, reverse_players=False):
        p1 = self.game.field.players[0]
        p2 = self.game.field.players[1]
        cell_tensor = np.array(self.game.field.cell)
        cell_tensor = cell_tensor[np.newaxis, :, :, np.newaxis]
        empty_tensor = np.zeros((1, cell_tensor.shape[1], cell_tensor.shape[2], 2))
        cell_tensor = np.concatenate((cell_tensor, empty_tensor), axis=3)
        cell_tensor[cell_tensor < 3] = 0
        cell_tensor[cell_tensor == 3] = 1
        cell_tensor[0, p1.row, p1.col, 1] = 1
        cell_tensor[0, p2.row, p2.col, 2] = 1

        if reverse_players:
            cell_tensor[0, p1.row, p1.col, 1] = 0
            cell_tensor[0, p1.row, p1.col, 2] = 1
            cell_tensor[0, p2.row, p2.col, 1] = 1
            cell_tensor[0, p2.row, p2.col, 2] = 0

        return cell_tensor
