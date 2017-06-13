import copy
import random

from Bot.board import BLOCKED


class Bot(object):
    def __init__(self):
        self.game = None

    def setup(self, game):
        self.game = game

    def do_turn(self):
        legal = self.game.field.legal_moves(self.game.my_botid)
        if len(legal) == 0:
            self.game.issue_order_pass()
        else:
            # best_score = 0
            # best_move = None
            # for move in legal:
            #     score = self.total_area(move[0])
            #     if score >= best_score:
            #         best_score = score
            #         best_move = move
            score, best_path, _ = self.alpha_beta(self.game.field, 10, self.game.my_botid ^ 1,
                                                  -float("inf"), float("inf"), [])
            if len(best_path) > 1:
                self.game.issue_order(best_path[1])
            else:
                # legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
                # if len(legal) == 0:
                #     self.game.issue_order_pass()
                # else:
                (_, chosen) = random.choice(legal)
                self.game.issue_order(chosen)

    def alpha_beta(self, field, depth, player_id, alpha, beta, move_history):
        moves = field.legal_moves(player_id)
        if depth == 0 or len(moves) == 0:
            my_player = field.players[0]
            enemy_player = field.players[1]
            my_score = field.total_area((my_player.row, my_player.col))
            enemy_score = field.total_area((enemy_player.row, enemy_player.col))
            distance = ((my_player.row - enemy_player.row) ** 2 + (
                my_player.col - enemy_player.col) ** 2) ** 0.5
            score = my_score - enemy_score
            return score, move_history + ['pass'] if len(moves) == 0 else move_history, distance

        child_fields = []
        directions = []
        current_player = field.players[player_id]
        for move in moves:
            child_field = copy.deepcopy(field)
            child_field.cell[move[0][0]][move[0][1]] = [player_id]
            child_field.cell[current_player.row][current_player.col] = [BLOCKED]
            child_field.players[player_id].row, child_field.players[player_id].col = move[0]
            child_fields.append(child_field)
            directions.append(move[1])

        if player_id == 0:
            best_value = -float("inf")
            best_history = move_history
            best_distance = float("inf")
            for i, child_field in enumerate(child_fields):
                v, node_history, distance = self.alpha_beta(child_field, depth - 1, player_id ^ 1, alpha, beta,
                                                            move_history)
                if v > best_value or (v == best_value and distance < best_distance):
                    best_value = v
                    best_history = [directions[i]] + node_history
                    best_distance = distance
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
        else:
            best_value = float("inf")
            best_history = move_history
            best_distance = float("inf")
            for i, child_field in enumerate(child_fields):
                v, node_history, distance = self.alpha_beta(child_field, depth - 1, player_id ^ 1, alpha, beta,
                                                            move_history)
                if v < best_value or (v == best_value and distance < best_distance):
                    best_value = v
                    best_history = [directions[i]] + node_history
                    best_distance = distance
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
        return best_value, best_history, best_distance
