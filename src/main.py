import tensorflow as tf
from bot.bot_nn import BotNN

from bot.game import Game


def main():
    with tf.Session() as sess:
        bot = BotNN(sess, False)
        game = Game()
        game.run(bot)


if __name__ == '__main__':
    # print('hello')
    main()
