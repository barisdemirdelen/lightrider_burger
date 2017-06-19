import random
from collections import deque
from copy import deepcopy, copy

import tensorflow as tf
import numpy as np
from tensorflow.python.framework.errors_impl import NotFoundError

from bot.board import DIRS
from bot.bot_nn2 import BotNN2
from bot.bot_random import BotRandom
from bot.fake_engine import FakeEngine


def softmax(x):
    e_x = np.exp(x - np.max(x))
    out = e_x / e_x.sum()
    return out


def main():
    sess = tf.Session()
    bot = BotNN2(sess)
    enemy = BotRandom()
    engine = FakeEngine(bot, enemy)
    y = 0.1
    e = 0.1
    num_episodes = 1000000
    batch_size = 32
    max_memory_size = 100000

    train = True
    bot.training = True
    enemy.training = True

    init = tf.global_variables_initializer()

    rewards = deque()
    rounds = deque()
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
            rlogits, probs = sess.run([bot.logits, bot.probs],
                                      feed_dict={bot.inputs: current_state})

            # prediction = np.random.choice(np.arange(256), p=np.ravel(probs[0]))
            # prediction_coords = int(np.floor(prediction / 16)), prediction % 16

            if np.isnan(probs[0, 0, 0]):
                print('NAAAAN')

            string_move = 'pass'
            legal = bot.game.field.legal_moves(0)
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
            else:
                prediction = np.random.choice(np.arange(256), p=np.ravel(probs[0]))
                prediction_coords = int(np.floor(prediction / 16)), prediction % 16

            original_prediction = copy(string_move)

            if random.random() < e:
                sample = bot.sample_move()
                string_move = DIRS[sample][1]

            target_action = np.zeros((16, 16))
            # action_index = prediction[0]
            target_action[prediction_coords] = 1
            target_action = [target_action]

            # string_move = DIRS[action_index][1]

            current_state2 = bot.get_cell_tensor(reverse_players=True)
            rlogits2, probs2 = sess.run([bot.logits_T, bot.probs_T],
                                        feed_dict={bot.inputs: current_state2})

            prediction2 = np.random.choice(np.arange(256), p=np.ravel(probs2[0]))
            prediction_coords2 = int(np.floor(prediction2 / 16)), prediction2 % 16

            if np.isnan(probs2[0, 0, 0]):
                print('NAAAAN2222')

            string_move2 = 'pass'
            legal2 = enemy.game.field.legal_moves(1)
            if len(legal2) > 0:
                legal_probs2 = []
                legal_logits2 = []
                for move2 in legal2:
                    legal_probs2.append(probs2[0][move2[0]])
                    legal_logits2.append(rlogits2[0, :, :, 0][move2[0]])
                    # if prediction_coords == move[0]:
                    #     string_move = move[1]
                    #     break
                legal_probs2 = np.array(legal_probs2)
                legal_logits2 = np.array(legal_logits2)
                legal_probs2 = softmax(legal_logits2)
                # legal_probs2 = legal_probs2 / np.sum(legal_probs2)
                prediction_id2 = np.random.choice(np.arange(len(legal_probs2)), p=legal_probs2)
                prediction_coords2 = legal2[prediction_id2][0]
                string_move2 = legal2[prediction_id2][1]
            else:
                prediction2 = np.random.choice(np.arange(256), p=np.ravel(probs2[0]))
                prediction_coords2 = int(np.floor(prediction2 / 16)), prediction2 % 16

            if random.random() < e:
                sample2 = enemy.sample_move()
                string_move2 = DIRS[sample2][1]

            target_action2 = np.zeros((16, 16))
            # action_index = prediction[0]
            target_action2[prediction_coords2] = 1
            target_action2 = [target_action2]

            # Get new state and reward from environment
            d = engine.step([string_move, string_move2])
            reward = bot.reward
            reward2 = enemy.reward
            next_state = bot.get_cell_tensor()
            next_state2 = bot.get_cell_tensor(reverse_players=True)

            if train:
                if d:
                    D.append((current_state, target_action, reward, next_state, d))
                # D.append((current_state2, target_action2, reward2, next_state2, d))
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
                    # QValue_batch = sess.run(bot.probs, feed_dict={bot.inputs: nextState_batch})
                    # prediction_q = np.random.choice(np.arange(256), p=np.ravel(QValue_batch[0]))
                    # prediction_q_coords = int(np.floor(prediction / 16)), prediction % 16
                    # target_action_q = np.zeros((16, 16))
                    # target_action_q[prediction_coords] = 1
                    # target_action_q = [target_action_q]


                    QValue_T_batch = sess.run(bot.probs_T, feed_dict={bot.inputs: nextState_batch})
                    # for i in range(0, batch_size):
                    #     # terminal = minibatch[i][4]
                    #     # if terminal:
                    #         y_batch.append(reward_batch[i])
                        # else:
                        #     y_batch.append(reward_batch[i] + y * np.max(QValue_T_batch[i]))

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

                # Reduce chance of random action as we train the model.
                # e *= 0.9995
                # if episode % 10 == 0:
                #     e += 0.37121
                #     if e > 1.0:
                #         e -= 1.0

                if episode % 10 == 0:
                    try:
                        bot.saver.save(sess,
                                       '/home/burger/projects/lightrider_burger/checkpoints/model2/nn_model2.ckpt')
                    except Exception:
                        print('Couldnt save')
                        # enemy.saver.save(sess, 'checkpoints/model2/nn_model2.ckpt')
                        # print("Average reward: %.4f" % (sum(rList) / num_episodes))

                if episode % 500 == 0:
                    print('NEW VALUEEES')
                    sess.run(bot.assign_T_operation)
                    rounds = []
                    rewards = []

                rounds.append(round)
                rewards.append(bot.reward)
                if len(rounds) > 500:
                    rounds.popleft()
                if len(rewards) > 500:
                    rewards.popleft()

                break

        print(
            'Episode %d, round: %d, average_round: %.4f, reward: %d, average_reward: %.4f, e:%.4f, max_prob:%.4f, min_prob: %.4f, total_prob: %.4f prediction: %s, loss: %.4f' % (
                episode, rounds[-1], np.mean(rounds), rewards[-1], np.mean(rewards), e, np.max(original_legal_probs),
                np.min(original_legal_probs), np.sum(original_legal_probs),
                original_prediction, 0 if loss is None else np.mean(loss)))

    try:
        bot.saver.save(sess, '/home/burger/projects/lightrider_burger/checkpoints/model2/nn_model2.ckpt')
    except Exception:
        print('Couldnt save')
        # enemy.saver.save(sess, 'checkpoints/model2/nn_model2.ckpt')
        # print("Average reward: %.4f" % (sum(rList) / num_episodes))


# game.run(bot)


if __name__ == '__main__':
    main()
