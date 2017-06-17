import random
from collections import deque
from copy import deepcopy

import tensorflow as tf
import numpy as np
from tensorflow.python.framework.errors_impl import NotFoundError

from bot.board import DIRS
from bot.bot_nn import BotNN
from bot.bot_nn2 import BotNN2
from bot.bot_random import BotRandom
from bot.fake_engine import FakeEngine


def main():
    sess = tf.Session()
    bot = BotNN(sess)
    enemy = BotRandom()
    engine = FakeEngine(bot, enemy)
    y = 0.995
    e = 0.0
    num_episodes = 1000000
    batch_size = 128
    max_memory_size = 10000

    train = True
    bot.training = True
    enemy.training = True

    init = tf.global_variables_initializer()

    rewards = []
    rounds = []
    # sess.run(init)
    # try:
    #     bot.saver.restore(sess, 'checkpoints/model/nn_model.ckpt')
    # except NotFoundError:
    #     print('Not Found')

    D = deque()
    D2 = deque()
    total_steps = 0
    for episode in range(num_episodes):
        # Reset environment and get first new observation
        engine.reset()
        loss = None
        # The Q-Network
        round = 0
        while True:
            # Choose an action by greedily (with e chance of random action) from the Q-network
            current_state = bot.get_cell_tensor()
            prediction, rlogits, probs = sess.run([bot.prediction, bot.logits, bot.probs],
                                                  feed_dict={bot.inputs: current_state})

            prediction = [np.random.choice(np.arange(4), p=probs[0])]
            original_prediction = prediction[0]

            if np.isnan(probs[0, 0]):
                print('NAAAAN')
            elif probs[0, 0] == 0:
                print('ZEROOOO')
            elif probs[0, 0] == 1:
                print('ONEEEEEE')

            if random.random() < e:
                prediction[0] = bot.sample_move()

            string_move = DIRS[prediction[0]][1]

            # legal_moves = bot.game.field.legal_moves(0)
            # for move in legal_moves:
            #     if move[1] == string_move:
            #         break
            # else:
            #     prediction[0] = bot.sample_move()

            target_action = np.zeros(4)
            action_index = prediction[0]
            target_action[action_index] = 1
            target_action = [target_action]

            string_move = DIRS[action_index][1]

            current_state2 = bot.get_cell_tensor(reverse_players=True)
            prediction2, rlogits2, probs2 = sess.run([bot.prediction, bot.logits, bot.probs],
                                                     feed_dict={bot.inputs: current_state2})

            prediction2 = [np.random.choice(np.arange(4), p=probs2[0])]
            if np.isnan(probs2[0, 0]):
                print('NAAAAN2222')
            elif probs2[0, 0] == 0:
                print('ZEROOOO2222')
            elif probs2[0, 0] == 1:
                print('ONEEEEEE2222')

            string_move2 = DIRS[prediction2[0]][1]

            # legal_moves2 = enemy.game.field.legal_moves(1)
            # for move in legal_moves2:
            #     if move[1] == string_move2:
            #         break
            # else:
            #     prediction2[0] = enemy.sample_move()

            target_action2 = np.zeros(4)
            action_index2 = prediction2[0]
            target_action2[action_index2] = 1
            target_action2 = [target_action2]

            string_move2 = DIRS[action_index2][1]

            # Get new state and reward from environment
            d = engine.step([string_move, string_move2])
            reward = bot.reward
            reward2 = enemy.reward
            next_state = bot.get_cell_tensor()
            next_state2 = bot.get_cell_tensor(reverse_players=True)

            if train:
                D.append((current_state, target_action, reward, next_state, d))
                D.append((current_state2, target_action2, reward2, next_state2, d))
                # D2.append((current_state2, probs2, reward2, next_state2, d))

                if len(D) > max_memory_size:
                    D.popleft()

                if len(D) > batch_size:
                    minibatch = random.sample(D, batch_size)
                    state_batch = [data[0][0] for data in minibatch]
                    action_batch = [data[1][0] for data in minibatch]
                    reward_batch = [data[2] for data in minibatch]
                    nextState_batch = [data[3][0] for data in minibatch]

                    y_batch = reward_batch
                    QValue_batch = sess.run(bot.probs, feed_dict={bot.inputs: nextState_batch})
                    # for i in range(0, batch_size):
                    # terminal = minibatch[i][4]
                    # if terminal:
                    #     y_batch.append(reward_batch[i])
                    # else:
                    # y_batch.append(reward_batch[i] + y * np.max(QValue_batch[i]))
                    # y_batch.append(reward_batch[i] + y * np.max(QValue_batch[i]))

                    _, loss = sess.run([bot.optimizer, bot.loss],
                                       feed_dict={bot.inputs: state_batch, bot.target_actions: action_batch,
                                                  bot.rewards: y_batch})

                    # if len(D2) > max_memory_size:
                    #     D2.popleft()
                    #
                    # if len(D2) > batch_size:
                    #     minibatch = random.sample(D2, batch_size)
                    #     state_batch = [data[0][0] for data in minibatch]
                    #     action_batch = [data[1][0] for data in minibatch]
                    #     reward_batch = [data[2] for data in minibatch]
                    #     nextState_batch = [data[3][0] for data in minibatch]
                    #
                    #     y_batch = []
                    #     QValue_batch = sess.run(enemy.probs, feed_dict={enemy.inputs: nextState_batch})
                    #     for i in range(0, batch_size):
                    #         terminal = minibatch[i][4]
                    #         if terminal:
                    #             y_batch.append(reward_batch[i])
                    #         else:
                    #             y_batch.append(reward_batch[i] + y * np.max(QValue_batch[i]))
                    #
                    #     sess.run([enemy.optimizer],
                    #              feed_dict={enemy.inputs: state_batch, enemy.target_actions: action_batch,
                    #                         enemy.rewards: y_batch})

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
                rounds.append(round)
                rewards.append(bot.reward)
                # Reduce chance of random action as we train the model.
                e *= 0.9995

                break

        print(
            'Episode %d, round: %d, average_round: %.4f, reward: %d, average_reward: %.4f, e:%.4f, max_prob:%.4f, min_prob: %.4f, prediction: %d, loss: %.4f' % (
                episode, rounds[-1], np.mean(rounds), rewards[-1], np.mean(rewards), e, max(probs[0]), min(probs[0]),
                original_prediction, 0 if loss is None else np.mean(loss)))

        bot.saver.save(sess, 'checkpoints/model/nn_model.ckpt')
        # enemy.saver.save(sess, 'checkpoints/model2/nn_model2.ckpt')
        # print("Average reward: %.4f" % (sum(rList) / num_episodes))


# game.run(bot)


if __name__ == '__main__':
    main()
