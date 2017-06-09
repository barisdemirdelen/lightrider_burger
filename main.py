from Bot.game import Game
from Bot.bot import Bot


def main():
    bot = Bot()
    game = Game()
    game.run(bot)


if __name__ == '__main__':
    print('hello')
    main()
