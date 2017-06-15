from bot.bot import Bot

from bot.game import Game


def main():
    bot = Bot()
    game = Game()
    game.run(bot)


if __name__ == '__main__':
    # print('hello')
    main()
