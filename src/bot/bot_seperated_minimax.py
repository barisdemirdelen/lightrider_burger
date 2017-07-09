import sys

import time

from bot.board import BLOCKED
from bot.parameters import Parameters


class BotSeparatedMinimax(object):
    def __init__(self, game, parameters):
        self.game = game
        self.parameters = parameters
        self.depth_times = None
        self.start_time = None
        self.total_nodes = 0
        self.cached = 0

    def do_turn(self, depth_times, start_time):
        self.depth_times = depth_times
        self.start_time = start_time
        self.total_nodes = 0
        self.cached = 0
        search_path = self.game.field.separated_best_moves.copy()
        score, best_path, depth = self.separated_iterative_deepening_alpha_beta(search_path=search_path)
        return score, best_path, depth, self.total_nodes, self.cached

    def separated_iterative_deepening_alpha_beta(self, search_path):
        i = 1
        if search_path and search_path[-1] == 'pass':
            search_path = search_path[:-1]
        best_path = search_path.copy()
        i = max(i, len(search_path))
        # self.parameters.quiescence_depth = i

        best_score = None
        best_move = None
        best_depth = i
        available_time = self.game.get_available_time_per_turn(self.parameters.available_time_factor)
        while True:
            current_depth_start_time = time.time()
            score, path = self.separated_alpha_beta(self.game.field, i, 0, search_path=best_path)

            if path and score is not None:
                best_score = score
                best_depth = i
                best_move = path[0]
                best_path = path

            current_time = time.time()
            depth_time = (current_time - current_depth_start_time) * 1000.0
            self.depth_times.append('%.2f' % depth_time)
            if best_move == 'pass':
                break
            if score is None or score == i:
                break
            if not best_path or best_path[-1] == 'pass':
                break
            if i > self.game.rounds_left:
                break
            if current_time - self.start_time > available_time:
                break
            i += 1
        return best_score, best_path, best_depth

    def separated_alpha_beta(self, field, depth, alpha, search_path):
        self.total_nodes += 1

        if depth <= field.separated_search_depth and field.separated_score is not None:
            self.cached += 1
            return field.separated_score, field.separated_best_moves

        moves = field.legal_moves
        if depth <= 0 or not moves:
            score = self.separated_evaluate(field)
            alpha_history = ['pass'] if not moves else []
            if alpha_history is None:
                sys.stderr.write('Why is this None\n')
            return score, alpha_history

        elapsed_time = time.time() - self.start_time
        if float(elapsed_time) > self.game.last_timebank * 0.7 / 1000:
            sys.stderr.write('We are on limit at time\n')
            return None, None
        if elapsed_time > self.game.get_available_time_per_turn(self.parameters.available_time_factor):
            return None, None

        priority_move = None
        search_path = search_path.copy()
        if search_path:
            priority_move = search_path.pop(0)

        child_fields, directions = field.get_child_fields()
        child_fields, directions = self.separated_sort_moves(child_fields, directions, priority=priority_move)

        best_score, alpha_history = self.separated_aspiration_search_moves(child_fields, directions, depth, alpha,
                                                                           search_path)
        if best_score is not None:
            field.separated_score = best_score
            field.separated_search_depth = depth
            field.separated_best_moves = alpha_history
            if best_score == depth:
                field.separated_search_depth = 999

        return best_score, field.separated_best_moves

    def separated_aspiration_search_moves(self, child_fields, directions, depth, alpha, search_path):

        alpha_history = []
        next_depth = depth - 1
        for i, child_field in enumerate(child_fields):
            if i == 0:
                best_score, node_history = self.separated_alpha_beta(child_field, next_depth, alpha - 1, search_path)
                if best_score is None:
                    return None, None
                best_score += 1
                alpha_history = [directions[i]] + node_history
                if best_score > alpha:
                    alpha = best_score
            else:
                # reduction_factor = self.parameters.reduction_factor
                # next_depth = 1 if depth - reduction_factor < 1 else depth - reduction_factor
                # score, node_history = self.separated_alpha_beta(child_field, next_depth, alpha - 1, search_path)
                # if score is None:
                #     return None, None
                # score += 1
                # if score > alpha:
                next_depth = depth - 1
                score, node_history = self.separated_alpha_beta(child_field, next_depth, alpha - 1, search_path)
                if score is None:
                    return None, None
                score += 1
                if score > alpha:
                    alpha = score

                if score > best_score:
                    alpha_history = [directions[i]] + node_history
                    best_score = score
        return best_score, alpha_history

    def separated_sort_moves(self, fields, directions, priority):
        if not fields:
            return fields, directions
        areas = [0] * len(fields)
        child_counts = [0] * len(fields)
        for i, field in enumerate(fields):
            areas[i] = -field.separated_score if field.separated_score else 0
            child_counts[i] = len(field.get_child_fields()[0])

        if priority is None:
            child_list = sorted(zip(fields, directions, areas, child_counts), key=lambda x: (x[2], x[3]))
        else:
            child_list = sorted(zip(fields, directions, areas, child_counts),
                                key=lambda x: (0 if x[1] == priority else 1, x[2], x[3]))
        sorted_fields, sorted_directions, _, _ = zip(*child_list)

        return sorted_fields, sorted_directions

    def separated_evaluate(self, field):
        if field.score:
            self.cached += 1
            return field.separated_score

        score = 0
        depth = 0
        if field.legal_moves:
            score, _ = field.separated_block_middle_score()

        if score == 0:
            depth = 999

        field.separated_score = score
        field.separated_search_depth = depth

        return score
