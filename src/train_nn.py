import random
from collections import deque

import tensorflow as tf
import numpy as np
from tensorflow.python.framework.errors_impl import NotFoundError

from bot.board import DIRS
from bot.bot_nn import BotNN
from bot.bot_random import BotRandom
from bot.fake_engine import FakeEngine
from bot.game import Game


def main():
    sess = tf.Session()
    bot = BotNN(sess)
    enemy = BotRandom()
    engine = FakeEngine(bot, enemy)
    y = 0.9
    e = 0.1
    num_episodes = 10000
    batch_size = 16
    max_memory_size = 10000

    bot.training = True

    init = tf.global_variables_initializer()

    rewards = []
    sess.run(init)
    try:
        bot.saver.restore(sess, 'checkpoints/model/nn_model.ckpt')
    except NotFoundError:
        print('Not Found')

    D = deque()
    total_steps = 0
    for episode in range(num_episodes):
        # Reset environment and get first new observation
        engine.reset()

        # The Q-Network
        round = 0
        while True:
            # Choose an action by greedily (with e chance of random action) from the Q-network
            current_state = bot.get_cell_tensor()
            prediction, logits = sess.run([bot.prediction, bot.logits], feed_dict={bot.inputs: current_state})

            if np.random.rand(1) < e:
                prediction[0] = bot.sample_move()

            string_move = DIRS[prediction[0]][1]

            current_state2 = bot.get_cell_tensor(reverse_players=True)
            prediction2, logits2 = sess.run([bot.prediction, bot.logits], feed_dict={bot.inputs: current_state2})

            if np.random.rand(1) < e:
                prediction2[0] = bot.sample_move()

            string_move2 = DIRS[prediction2[0]][1]

            # Get new state and reward from environment
            d = engine.step([string_move, string_move2])
            reward = bot.reward
            reward2 = enemy.reward
            next_state = bot.get_cell_tensor()
            next_state2 = bot.get_cell_tensor(reverse_players=True)

            D.append((current_state, logits, reward, next_state, d))
            D.append((current_state2, logits2, reward2, next_state2, d))

            if len(D) > max_memory_size:
                D.popleft()

            if len(D) > batch_size:
                minibatch = random.sample(D, batch_size)
                state_batch = [data[0][0] for data in minibatch]
                action_batch = [data[1][0] for data in minibatch]
                reward_batch = [data[2] for data in minibatch]
                nextState_batch = [data[3][0] for data in minibatch]

                y_batch = []
                QValue_batch = sess.run(bot.logits, feed_dict={bot.inputs: state_batch})
                for i in range(0, batch_size):
                    terminal = minibatch[i][4]
                    if terminal:
                        y_batch.append(reward_batch[i])
                    else:
                        y_batch.append(reward_batch[i] + y * np.max(QValue_batch[i]))

                sess.run([bot.optimizer], feed_dict={bot.inputs: state_batch, bot.target_actions: action_batch,
                                                     bot.rewards: y_batch})

                # save network every 100000 iteration
                # if total_steps % 100 == 0:
                #     bot.saver.save(sess, 'checkpoints/model/nn_model.ckpt')

            round += 1
            total_steps += 1

            # # Obtain the Q' values by feeding the new state through our network
            # Q1 = sess.run(bot.logits, feed_dict={bot.inputs: get_cell_tensor(bot)})
            # # Obtain maxQ' and set our target value for chosen action.
            # maxQ1 = np.max(Q1)
            # targetQ = allQ
            # targetQ[0, a[0]] = reward + y * maxQ1 - targetQ[0, a[0]]
            # # Train our network using target and predicted Q values
            # sess.run([bot.optimizer], feed_dict={bot.inputs: get_cell_tensor(bot), bot.next_q: targetQ})
            if d:
                rewards.append(round)
                # Reduce chance of random action as we train the model.
                # e = 1. / ((i / 50) + 10)

                break

        print('Episode %d, round: %d, average_round: %.4f' % (episode, rewards[-1], np.mean(rewards)))

        bot.saver.save(sess, 'checkpoints/model/nn_model.ckpt')
        # print("Average reward: %.4f" % (sum(rList) / num_episodes))


# game.run(bot)


if __name__ == '__main__':
    main()
