from bot.bot_minimax import BotMinimax
from bot.game import Game


def main():
    bot = BotMinimax()
    game = Game()
    game.run(bot)


if __name__ == '__main__':
    # print('hello')
    main()
