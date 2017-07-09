import sys

import time

from bot.board import BLOCKED
from bot.bot_seperated_minimax import BotSeparatedMinimax
from bot.parameters import Parameters


class BotMinimax(object):
    def __init__(self):
        self.game = None
        self.depth_times = []
        self.total_nodes = 0
        self.start_time = 0
        self.cached = 0
        self.cut = 0
        self.parameters = Parameters()
        self.p1_next_coord_prediction = None
        self.p1_last_coord = None
        self.first_turn = True
        self.separated_bot = None

    def setup(self, game):
        self.game = game
        self.separated_bot = BotSeparatedMinimax(self.game, self.parameters)

    def give_reward(self, reward):
        pass

    def init_turn(self):
        self.start_time = time.time()
        self.total_nodes = 0
        self.depth_times = []
        self.game.last_order = None
        self.game.rounds_left = 0.5 * self.game.field.height * self.game.field.width - self.game.field.round
        self.game.field.score = None
        self.game.field.legal_player = 0
        self.game.field.update_zobrist()
        self.game.field._legal_moves = None
        self.cached = 0
        self.cut = 0

        if self.first_turn:
            self.game.field.cache_adjacent_initial()
        self.first_turn = False
        if self.game.field.players_separated:
            self.game.field.block_unreachable()
        self.game.field = self.game.field.find_child_field()
        if not self.game.field.players_separated:
            p1_new_coord = self.game.field.players[1].coord
            if self.p1_next_coord_prediction and self.p1_last_coord:
                p1_predicted_coord = self.game.field.get_coord_of_direction(self.p1_last_coord,
                                                                            self.p1_next_coord_prediction)
                if p1_new_coord != p1_predicted_coord:
                    sys.stderr.write('I thought he would go %s but i was wrong\n' % self.p1_next_coord_prediction)

            self.p1_last_coord = p1_new_coord
            self.p1_next_coord_prediction = None

    def do_turn(self):
        self.init_turn()
        score = None
        legal = self.game.field.legal_moves
        if not legal:
            self.game.issue_order_pass()
        elif len(legal) == 1:
            self.game.issue_order(legal[0][1])
        else:
            if self.game.field.players_separated:
                rounds_left_0 = self.game.field.total_area(self.game.field.players[0].coord, player_id=0)
                rounds_left_1 = self.game.field.total_area(self.game.field.players[0].coord, player_id=1)
                self.game.rounds_left = min(rounds_left_0, rounds_left_1) + 1
                score, best_path, depth, total_nodes, cached = self.separated_bot.do_turn(self.depth_times,
                                                                                          self.start_time)
                self.total_nodes = total_nodes
                self.cached = cached
            else:
                rounds_left_0 = self.game.field.total_area(self.game.field.players[0].coord, player_id=0) // 2
                self.game.rounds_left = rounds_left_0 + 1
                search_path = self.game.field.best_moves.copy()
                score, best_path, depth = self.iterative_deepening_alpha_beta(search_path=search_path)

            elapsed = time.time() - self.start_time

            if score is not None:
                sys.stderr.write(
                    'Round: %d, Score: %.4f, Depth: %d, Nodes: %d, Time: %d, RoundsLeft: %d, Cached: %d, Cut: %d '
                    'Depth times: %s\n' % (
                        self.game.field.round, score, depth, self.total_nodes,
                        self.game.last_timebank - elapsed * 1000, self.game.rounds_left, self.cached, self.cut,
                        str(self.depth_times)))
            else:
                sys.stderr.write('Score is None\n')
            if best_path:
                self.game.issue_order(best_path[0])
                if len(best_path) > 1 and best_path[1] != 'pass':
                    self.p1_next_coord_prediction = best_path[1]
            else:
                self.game.issue_order(legal[0][1])
            sys.stderr.flush()

        return score

    def iterative_deepening_alpha_beta(self, search_path):
        i = 2
        if search_path and search_path[-1] == 'pass':
            search_path = search_path[:-1]
        if search_path and len(search_path) % 2 == 1:
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
            score, path = self.alpha_beta(self.game.field, i, 0, -float('inf'), float('inf'), search_path=best_path)

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
            if score is None or score >= 999 or score <= -999:
                break
            if not best_path or best_path[-1] == 'pass':
                break
            if i > self.game.rounds_left * 2:
                break
            if current_time - self.start_time > available_time:
                break
            i += 2
        return best_score, best_path, best_depth

    def alpha_beta(self, field, depth, player_id, alpha, beta, search_path):
        self.total_nodes += 1

        if depth <= field.search_depth and field.score is not None:
            self.cached += 1
            return field.score, field.best_moves

        moves = field.legal_moves
        if depth <= 0 or not moves:
            score = self.evaluate(field)
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
        child_fields, directions = self.sort_moves(child_fields, directions, priority=priority_move)

        best_score, alpha_history = self.aspiration_search_moves(child_fields, directions, depth, player_id, alpha,
                                                                 beta, search_path)
        if best_score is not None:
            field.score = best_score
            field.search_depth = depth
            field.best_moves = alpha_history
            if best_score > 900 or best_score < -900:
                field.search_depth = 999

        return best_score, field.best_moves

    def aspiration_search_moves(self, child_fields, directions, depth, player_id, alpha, beta, search_path):

        alpha_history = []
        next_depth = depth - 1
        for i, child_field in enumerate(child_fields):
            if i == 0:
                best_score, node_history = self.alpha_beta(child_field, next_depth, 1 - player_id, -beta, -alpha,
                                                           search_path)
                if best_score is None:
                    return None, None
                best_score = -best_score
                alpha_history = [directions[i]] + node_history
                if best_score > alpha:
                    if best_score >= beta:
                        return best_score, alpha_history
                    alpha = best_score
            else:
                if child_field.score and -child_field.score + 65 < best_score:
                    self.cut += 1
                    continue
                reduction_factor = self.parameters.reduction_factor
                if player_id == 0:
                    next_depth = 1 if depth - reduction_factor < 1 else depth - reduction_factor
                else:
                    next_depth = 0 if depth - reduction_factor < 0 else depth - reduction_factor
                score, node_history = self.alpha_beta(child_field, next_depth, 1 - player_id,
                                                      -alpha - self.parameters.nw_search_window, -alpha, search_path)
                if score is None:
                    return None, None
                score = -score
                if beta > score > alpha:
                    next_depth = depth - 1
                    score, node_history = self.alpha_beta(child_field, next_depth, 1 - player_id, -beta, -alpha,
                                                          search_path)
                    if score is None:
                        return None, None
                    score = -score

                    if score > alpha:
                        alpha = score

                if score > best_score:
                    alpha_history = [directions[i]] + node_history
                    if score >= beta:
                        return score, alpha_history
                    best_score = score
        return best_score, alpha_history

    def sort_moves(self, fields, directions, priority):
        if not fields:
            return fields, directions
        scores = [0] * len(fields)
        child_counts = [0] * len(fields)
        distances = [0] * len(fields)
        for i, field in enumerate(fields):
            if field.legal_player == 0:
                scores[i] = self.evaluate(field)
            else:
                scores[i] = field.score if field.score else 999
            child_counts[i] = len(field.get_child_fields()[0])
            distances[i] = field.get_player_euclidian_distance_square()

        if priority is None:
            child_list = sorted(zip(fields, directions, scores, child_counts, distances),
                                key=lambda x: (x[2], x[3], x[4]))
        else:
            child_list = sorted(zip(fields, directions, scores, child_counts, distances),
                                key=lambda x: (0 if x[1] == priority else 1, x[2], x[3], x[4]))
        sorted_fields, sorted_directions, _, _, _ = zip(*child_list)

        return sorted_fields, sorted_directions

    def evaluate(self, field, cache=True):
        if field.score:
            self.cached += 1
            return field.score
        player_id = field.legal_player
        score = -999
        depth = 0
        if field.legal_moves:
            my_score, enemy_score = field.block_middle_score()
            if my_score != 0 or enemy_score != 0:
                if my_score == 0:
                    my_score = -999
                elif enemy_score == 0:
                    enemy_score = -999
            score = my_score - enemy_score
            score = score if player_id == 0 else -score
        elif not field.adjacents[field.players[1 - player_id].row * 16 + field.players[1 - player_id].col]:
            score = 0
            depth = 999

        if score < -900 or score > 900:
            depth = 999

        if cache:
            field.score = score
            field.search_depth = depth

        return score

    def quiescence_search(self, field, player_id, depth):
        if depth <= field.search_depth and field.score is not None:
            self.cached += 1
            return field.score

        moves = field.legal_moves
        elapsed_time = time.time() - self.start_time
        total_time_limit = float(elapsed_time) > self.game.last_timebank * 0.9 / 1000
        turn_time_limit = elapsed_time > self.game.get_available_time_per_turn(self.parameters.available_time_factor)
        # total_time_limit = False
        # turn_time_limit = False
        if depth <= 0 or not moves or total_time_limit or turn_time_limit:
            score = self.evaluate(field, player_id)
            return score

        # priority_move = None
        child_fields, directions = field.get_child_fields()
        # child_fields, directions = self.sort_moves(child_fields, directions, priority=priority_move)

        best_score = self.quiescence_search_moves(child_fields, depth, player_id)
        if best_score is not None:
            field.score = best_score
            field.search_depth = 0
            if best_score > 900 or best_score < -900:
                field.search_depth = 999

        return best_score

    def quiescence_search_moves(self, child_fields, depth, player_id):
        best_field = None
        best_score = -float('inf')
        for field in child_fields:
            score = field.score
            if not score:
                score = self.evaluate(field)
            if score > best_score:
                best_field = field
                best_score = score
        return -self.quiescence_search(best_field, 1 - player_id, depth - 1)
