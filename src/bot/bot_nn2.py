import random

from tensorflow.python.framework.errors_impl import NotFoundError
from tensorflow.python.training.saver import Saver
import numpy as np

from bot.board import DIRS
import tensorflow as tf

from bot.nn.model2 import Model2
from bot.nn.model3 import Model3

start_time = 0


def softmax(x):
    e_x = np.exp(x - np.max(x))
    out = e_x / e_x.sum()
    return out


class BotNN2(object):
    def __init__(self, session=None):
        self.game = None
        self.separated = False
        self.model = Model2()
        self.model_T = Model3()
        self.training = False

        if session is None:
            session = tf.Session()

        self.inputs = tf.placeholder(dtype=tf.float32, shape=[None, 16, 16, 3], name='inputs2')
        self.target_actions = tf.placeholder(dtype=tf.float32, shape=[None, 16, 16], name='target_actions2')
        self.rewards = tf.placeholder(dtype=tf.float32, shape=[None], name='rewards2')

        self.logits = self.model.inference(self.inputs)
        flat = tf.reshape(self.logits, shape=(-1, 256))
        self.probs = tf.reshape(tf.nn.softmax(flat), shape=(-1, 16, 16))
        # self.prediction = tf.argmax(self.probs)
        self.loss = self.model.loss(probs=self.probs, target_actions=self.target_actions, rewards=self.rewards)
        self.algorithm = tf.train.AdamOptimizer(learning_rate=1e-5)
        self.optimizer = self.algorithm.minimize(self.loss)

        self.logits_T = self.model_T.inference(self.inputs)
        flat_T = tf.reshape(self.logits, shape=(-1, 256))
        self.probs_T = tf.reshape(tf.nn.softmax(flat_T), shape=(-1, 16, 16))

        self.assign_T_operation = [t.assign(o) for o, t in zip(self.model.parameters, self.model_T.parameters)]

        self.reward = 0
        self.saver = Saver()
        init = tf.global_variables_initializer()

        self.session = session
        self.session.run(init)
        try:
            self.saver.restore(self.session,
                               '/home/burger/projects/lightrider_burger/checkpoints/model2/nn_model2.ckpt')
        except NotFoundError:
            print('Not Found')

        self.session.run(self.assign_T_operation)

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
            # probs = self.session.run(self.probs, feed_dict={self.inputs: self.get_cell_tensor()})
            # action = np.random.choice(np.arange(4), p=probs[0])
            # string_move = DIRS[action][1]
            # self.game.issue_order(string_move)
            current_state = self.get_cell_tensor(reverse_players=self.game.my_botid)
            rlogits, probs = self.session.run([self.logits, self.probs],
                                              feed_dict={self.inputs: current_state})

            # prediction = np.random.choice(np.arange(256), p=np.ravel(probs[0]))
            # prediction_coords = int(np.floor(prediction / 16)), prediction % 16

            # if np.isnan(probs[0, 0, 0]):
            #     print('NAAAAN')

            string_move = 'pass'
            legal = self.game.field.legal_moves(self.game.my_botid)
            if len(legal) > 0:
                legal_probs = []
                legal_logits = []
                for move in legal:
                    legal_probs.append(probs[0][move[0]])
                    legal_logits.append(rlogits[0, :, :, 0][move[0]])
                    # if prediction_coords == move[0]:
                    #     string_move = move[1]
                    #     break

                original_legal_probs = np.array(legal_probs)
                legal_logits = np.array(legal_logits)
                legal_probs = softmax(legal_logits)
                prediction_id = np.random.choice(np.arange(len(legal_probs)), p=legal_probs)
                prediction_coords = legal[prediction_id][0]
                string_move = legal[prediction_id][1]
            self.game.issue_order(string_move)

        return 0

    def get_cell_tensor(self, reverse_players=False):
        p1 = self.game.field.players[0]
        p2 = self.game.field.players[1]
        cell_tensor = np.array(self.game.field.cell)
        cell_tensor = np.reshape(cell_tensor, (self.game.field.height, self.game.field.width))
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
