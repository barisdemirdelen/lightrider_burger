import copy
import random

import sys

import time

from Bot.board import BLOCKED

total_nodes = 0
start_time = 0


class Bot(object):
    def __init__(self):
        self.game = None
        self.separated = False

    def setup(self, game):
        self.game = game

    def do_turn(self):
        global start_time
        score = None
        start_time = time.time()
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
            if not self.separated:
                self.separated = self.game.field.is_players_separated()
            if self.separated:
                score, best_path, depth = self.iterative_deepening_alpha_beta(only_me=True)
            else:
                score, best_path, depth = self.iterative_deepening_alpha_beta(only_me=False)
                depth = depth / 2
            elapsed = time.time() - start_time

            sys.stderr.write(
                "Round: %d, Score: %.4f, Depth: %d, Nodes: %.4f, Time: %d,\n" % (
                    self.game.field.round, score, depth, total_nodes / (self.game.field.round + 1),
                    self.game.last_timebank - elapsed * 1000))
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
        return score

    def iterative_deepening_alpha_beta(self, only_me):
        i = 2
        best_score = None
        best_path = None
        best_depth = i
        while True:
            current_time = time.time()
            available_time = self.game.get_available_time_per_turn()
            if current_time - start_time > available_time:
                break
            score, path, _, _ = self.alpha_beta(self.game.field, i, self.game.my_botid,
                                                -float("inf"), float("inf"), [], only_me=only_me)
            if score is not None:
                best_score = score
                best_path = path
                best_depth = i
            if len(best_path) < i:
                break
            i += 2
        return best_score, best_path, best_depth

    def alpha_beta(self, field, depth, player_id, alpha, beta, move_history, only_me):
        global total_nodes
        total_nodes += 1
        pruned = False
        moves = field.legal_moves(player_id)
        elapsed_time = time.time() - start_time
        if elapsed_time > self.game.get_available_time_per_turn():
            return None, None, None, None
        if depth == 0 or len(moves) == 0:
            my_player = field.players[0]
            enemy_player = field.players[1]
            my_score = field.total_area((my_player.row, my_player.col))
            enemy_score = field.total_area((enemy_player.row, enemy_player.col))
            if only_me:
                if self.game.my_botid == 0:
                    enemy_score = 0
                else:
                    my_score = 0
            distance = ((my_player.row - enemy_player.row) ** 2 + (
                my_player.col - enemy_player.col) ** 2) ** 0.5
            score = my_score - enemy_score
            return score, move_history + ['pass'] if len(moves) == 0 else move_history, distance, False

        child_fields, directions = self.get_child_fields(field, player_id)
        child_fields, directions = self.sort_moves(child_fields, directions, player_id if only_me else player_id ^ 1,
                                                   calculate_distance=not only_me)

        if player_id == 0:
            best_value = -float("inf")
            best_history = move_history
            best_distance = float("inf")
            for i, child_field in enumerate(child_fields):
                v, node_history, distance, child_pruned = self.alpha_beta(child_field, depth - 1,
                                                                          player_id if only_me else player_id ^ 1,
                                                                          alpha, beta,
                                                                          move_history, only_me)
                if v is None:
                    return None, None, None, None
                if not child_pruned:
                    if v > best_value or self.is_better_equal(v, node_history, distance, best_value, best_history,
                                                              best_distance):
                        best_value = v
                        best_history = [directions[i]] + node_history
                        best_distance = distance
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    pruned = True
                    break
        else:
            best_value = float("inf")
            best_history = move_history
            best_distance = float("inf")
            for i, child_field in enumerate(child_fields):
                v, node_history, distance, child_pruned = self.alpha_beta(child_field, depth - 1,
                                                                          player_id if only_me else player_id ^ 1,
                                                                          alpha, beta,
                                                                          move_history, only_me)
                if v is None:
                    return None, None, None, None
                if not child_pruned:
                    if v < best_value or self.is_better_equal(v, node_history, distance, best_value, best_history,
                                                              best_distance):
                        best_value = v
                        best_history = [directions[i]] + node_history
                        best_distance = distance
                beta = min(beta, best_value)
                if beta <= alpha:
                    pruned = True
                    break
        return best_value, best_history, best_distance, pruned

    def sort_moves(self, fields, directions, next_player_id, calculate_distance):
        children_counts = []
        distances = []
        for field in fields:
            child_fields, _ = self.get_child_fields(field, next_player_id)
            children_counts.append(len(child_fields))
            if calculate_distance:
                true_distance = field.get_player_true_distance()
                # distances.append(field.get_player_euclidian_distance_square())
                distances.append(true_distance)
            else:
                distances.append(0)

        # reverse = False if next_player_id > 0 else True
        child_list = sorted(zip(children_counts, fields, directions, distances), key=lambda x: (x[0], x[3]))
        _, sorted_fields, sorted_directions, sorted_distances = zip(*child_list)

        return sorted_fields, sorted_directions

    @staticmethod
    def get_child_fields(field, next_player_id):
        child_fields = []
        directions = []
        next_player = field.players[next_player_id]
        moves = field.legal_moves(next_player_id)
        for move in moves:
            child_field = field.get_copy()
            child_field.cell[move[0][0]][move[0][1]] = next_player_id
            child_field.cell[next_player.row][next_player.col] = BLOCKED
            child_field.players[next_player_id].row, child_field.players[next_player_id].col = move[0]
            child_fields.append(child_field)
            directions.append(move[1])

        return child_fields, directions

    @staticmethod
    def is_better_equal(v, node_history, distance, best_value, best_history, best_distance):
        return v == best_value and (
            len(node_history) > len(best_history) or (
                len(node_history) == len(best_history) and distance < best_distance))
        # return v == best_value and distance < best_distance
