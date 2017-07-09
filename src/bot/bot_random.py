import random

from bot.board import DIRS, EMPTY


class BotRandom(object):
    def __init__(self, player_id):
        self.game = None
        self.reward = 0
        self.player_id = player_id
        self.legal = None

    def setup(self, game):
        self.game = game

    def give_reward(self, reward):
        self.reward = reward

    def do_turn(self):
        self.game.last_order_coord = None
        self.reward = 0
        row, col = self.game.field.players[self.player_id].coord
        self.legal = self.game.field.adjacents[row * 16 + col].copy()
        # self.real_legal = []
        # for legal in self.legal:
        #     if self.game.field.cell[legal[0]*16 + legal[1]] == EMPTY:
        #         self.real_legal.append(legal)
        if self.legal:
            self.game.last_order_coord = random.choice(list(self.legal))
        return 0

    def sample_move(self):
        legal = self.game.field.legal_moves
        if len(legal) == 0:
            return 0
        else:
            (_, chosen) = random.choice(legal)
            for i, dir in enumerate(DIRS):
                if chosen == dir[1]:
                    return i
            return 0
