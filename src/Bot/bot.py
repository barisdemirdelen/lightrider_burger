import copy
import random

import sys

from Bot.board import BLOCKED

total_nodes = 0


class Bot(object):
    def __init__(self):
        self.game = None
        self.last_score = 0

    def setup(self, game):
        self.game = game

    def do_turn(self):
        legal = self.game.field.legal_moves(self.game.my_botid)
        if len(legal) == 0:
            self.game.issue_order_pass()
        elif len(legal) == 1:
            self.game.issue_order(legal[0][1])
        else:
            # best_score = 0
            # best_move = None
            # for move in legal:
            #     score = self.total_area(move[0])
            #     if score >= best_score:
            #         best_score = score
            #         best_move = move
            global total_nodes
            # total_nodes = 0
            if self.game.field.get_player_manhattan_distance() > 5 or self.last_score > 0:
                score, best_path, _ = self.alpha_beta(self.game.field, 4, self.game.my_botid,
                                                      -float("inf"), float("inf"), [], only_me=True)
            else:
                score, best_path, _ = self.alpha_beta(self.game.field, 4, self.game.my_botid,
                                                      -float("inf"), float("inf"), [], only_me=False)
            self.last_score = score

            sys.stderr.write(str(total_nodes) + '\n')
            sys.stderr.flush()

            if len(best_path) > 0:
                self.game.issue_order(best_path[0])
            else:

                # legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
                # if len(legal) == 0:
                #     self.game.issue_order_pass()
                # else:
                (_, chosen) = random.choice(legal)
                self.game.issue_order(chosen)

    def alpha_beta(self, field, depth, player_id, alpha, beta, move_history, only_me):
        global total_nodes
        total_nodes += 1
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

        child_fields, directions = self.get_child_fields(field, player_id)
        child_fields, directions = self.sort_moves(child_fields, directions, player_id if only_me else player_id ^ 1)

        if player_id == 0:
            best_value = -float("inf")
            best_history = move_history
            best_distance = float("inf")
            for i, child_field in enumerate(child_fields):
                v, node_history, distance = self.alpha_beta(child_field, depth - 1,
                                                            player_id if only_me else player_id ^ 1, alpha, beta,
                                                            move_history, only_me)
                if v > best_value:  # or (v == best_value and distance < best_distance):
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
                v, node_history, distance = self.alpha_beta(child_field, depth - 1,
                                                            player_id if only_me else player_id ^ 1, alpha, beta,
                                                            move_history, only_me)
                if v < best_value:  # or (v == best_value and distance < best_distance):
                    best_value = v
                    best_history = [directions[i]] + node_history
                    best_distance = distance
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
        return best_value, best_history, best_distance

    def sort_moves(self, fields, directions, next_player_id):
        children_counts = []
        for field in fields:
            child_fields, _ = self.get_child_fields(field, next_player_id)
            children_counts.append(len(child_fields))

        child_list = sorted(zip(children_counts, fields, directions),
                            key=lambda x: x[0])

        sorted_fields, sorted_directions = [], []
        for child in child_list:
            sorted_fields.append(child[1])
            sorted_directions.append(child[2])
        return sorted_fields, sorted_directions

    def get_child_fields(self, field, next_player_id):
        child_fields = []
        directions = []
        next_player = field.players[next_player_id]
        moves = field.legal_moves(next_player_id)
        for move in moves:
            child_field = copy.deepcopy(field)
            child_field.cell[move[0][0]][move[0][1]] = [next_player_id]
            child_field.cell[next_player.row][next_player.col] = [BLOCKED]
            child_field.players[next_player_id].row, child_field.players[next_player_id].col = move[0]
            child_fields.append(child_field)
            directions.append(move[1])

        return child_fields, directions
