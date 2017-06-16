import random


class BotHeuristic(object):
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
            if random.randint(0,100) < 20:
                # enemy_coord = self.game.field.players[self.game.my_botid ^ 1].coord
                # best_move = None
                # best_dist = 200
                # for move in legal:
                #     move_coord = move[0]
                #     dist = (move_coord[0] - enemy_coord[0]) ** 2 + (move_coord[1] - enemy_coord[1]) ** 2
                #     if dist < best_dist:
                #         best_dist = dist
                #         best_move = move[1]

                self.game.issue_order(best_move)
            else:
                (_, chosen) = random.choice(legal)
                self.game.issue_order(chosen)

        return 0
