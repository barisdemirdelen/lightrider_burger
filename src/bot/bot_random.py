import random

from bot.board import DIRS


class BotRandom(object):
    def __init__(self):
        self.game = None
        self.reward = 0

    def setup(self, game):
        self.game = game

    def give_reward(self, reward):
        self.reward = reward

    def do_turn(self):
        self.game.last_order = None
        self.reward = 0
        legal = self.game.field.legal_moves(self.game.my_botid)
        if len(legal) == 0:
            self.game.issue_order_pass()
        else:
            (_, chosen) = random.choice(legal)
            self.game.issue_order(chosen)

        return 0

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
