from bot.bot_nn import BotNN
from bot.bot_random import BotRandom
from bot.fake_engine import FakeEngine

if __name__ == '__main__':
    p1 = BotNN()
    p2 = BotRandom()
    engine = FakeEngine(p1, p2)
    engine.run()
