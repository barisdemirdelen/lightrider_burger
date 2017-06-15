import random


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
