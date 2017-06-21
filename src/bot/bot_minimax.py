import sys

import time

from bot.board import BLOCKED

total_nodes = 0
start_time = 0
cached = 0


class BotMinimax(object):
    def __init__(self):
        self.game = None
        self.separated = False
        self.cache = {}
        self.T = []

    def setup(self, game):
        self.game = game

    def give_reward(self, reward):
        pass

    def do_turn(self):
        global start_time
        global cached
        self.game.last_order = None
        cached = 0
        score = None
        start_time = time.time()
        self.game.rounds_left = 0.5 * self.game.field.height * self.game.field.width - self.game.field.round
        self.game.field.score = None
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
                rounds_left_0 = self.game.field.total_area(self.game.field.players[0].coord, player_id=0)
                rounds_left_1 = self.game.field.total_area(self.game.field.players[1].coord, player_id=0)
                self.game.rounds_left = min(rounds_left_0, rounds_left_1) + 1
                score, best_path, depth = self.iterative_deepening_alpha_beta(only_me=True)
            else:
                # blocked_field = self.game.field.block_middle()
                # if self.game.field.round > 2:
                rounds_left_0 = self.game.field.total_area(self.game.field.players[0].coord, player_id=0)
                self.game.rounds_left = rounds_left_0 + 1
                score, best_path, depth = self.iterative_deepening_alpha_beta(only_me=False)
                depth = depth / 2.0
            elapsed = time.time() - start_time

            if score is not None:
                sys.stderr.write(
                    "Round: %d, Score: %.4f, Depth: %.1f, Nodes: %.4f, Time: %d, RoundsLeft: %d\n" % (
                        self.game.field.round, score, depth, total_nodes / (self.game.field.round + 1),
                        self.game.last_timebank - elapsed * 1000, self.game.rounds_left))
            else:
                sys.stderr.write("Score is None\n")
            sys.stderr.flush()

            self.game.issue_order(best_path)

        return score

    def iterative_deepening_alpha_beta(self, only_me):
        i = 1
        # average_score = self.evaluate(self.game.field, only_me)
        best_score = None
        best_move = None
        best_depth = i
        best_path = []
        while True:
            current_time = time.time()
            available_time = self.game.get_available_time_per_turn()
            if current_time - start_time > available_time:
                break

            score, move, path = self.search_root(self.game.field, i, self.game.my_botid,
                                                 -float('inf'),
                                                 float('inf'), only_me=only_me, priority=best_path)
            if move is not None:
                best_score = score
                best_move = move
                best_depth = i
                best_path = path
            if best_move == 'pass':
                break
            if score == float('inf') or score == -float('inf'):
                break
            if best_path is None or best_path[-1] == 'pass':
                break
            i += 1
        return best_score, best_move, best_depth

    def search_root(self, field, depth, player_id, alpha, beta, only_me, priority):
        priority_move = None
        search_path = priority[:]
        if len(search_path) > 0:
            priority_move = search_path.pop(0)

        child_fields, directions = self.get_child_fields(field, player_id)
        child_fields, directions = self.sort_moves(child_fields, directions, player_id,
                                                   calculate_distance=False, priority=priority_move, only_me=only_me)
        scores = []
        best_score = alpha
        best_path = None
        best_move = None
        i = 0
        for child_field, direction in zip(child_fields, directions):
            score, path = self.alpha_beta(child_field, depth - 1, player_id ^ 1, -beta, -best_score, [direction],
                                          only_me,
                                          search_path)
            if score is None:
                return None, None, None
            score = score if only_me else -score
            scores.append(score)
            if score > best_score:
                best_score = score
                best_move = direction
                best_path = path
            i += 1
        return best_score, best_move, best_path

    def alpha_beta(self, field, depth, player_id, alpha, beta, move_history, only_me, search_path):
        global total_nodes
        global cached
        total_nodes += 1
        if only_me:
            alpha, beta = -beta, -alpha

        moves = field.legal_moves(player_id)
        elapsed_time = time.time() - start_time
        if depth == 0 or len(moves) == 0:
            half_step = False if only_me else player_id != self.game.my_botid
            score = self.evaluate(field, only_me, half_step)
            return score if player_id == 0 or only_me else -score, move_history + ['pass'] if len(
                moves) == 0 else move_history

        if elapsed_time > self.game.get_available_time_per_turn():
            return None, None

        priority_move = None
        search_path = search_path[:]
        if len(search_path) > 0:
            priority_move = search_path.pop(0)

        child_fields, directions = self.get_child_fields(field, player_id)
        child_fields, directions = self.sort_moves(child_fields, directions, player_id,
                                                   calculate_distance=False, priority=priority_move, only_me=only_me)

        alpha_history = move_history
        bv_search = True
        for i, child_field in enumerate(child_fields):
            if bv_search:
                score, node_history = self.alpha_beta(child_field, depth - 1, player_id if only_me else player_id ^ 1,
                                                      -beta, -alpha,
                                                      move_history,
                                                      only_me, search_path)
                if score is None:
                    return None, None
                score = score if only_me else -score
            else:
                score, node_history = self.alpha_beta(child_field, depth - 1, player_id if only_me else player_id ^ 1,
                                                      -alpha - 1, -alpha,
                                                      move_history,
                                                      only_me, search_path)
                if score is None:
                    return None, None
                score = score if only_me else -score
                if score > alpha:
                    score, node_history = self.alpha_beta(child_field, depth - 1,
                                                          player_id if only_me else player_id ^ 1,
                                                          -beta, -alpha,
                                                          move_history,
                                                          only_me, search_path)
                    if score is None:
                        return None, None
                    score = score if only_me else -score

            if score >= beta:
                return score, node_history
            if score > alpha:
                alpha = score
                alpha_history = [directions[i]] + node_history
                bv_search = False
        return alpha, alpha_history

    def sort_moves(self, fields, directions, next_player_id, calculate_distance, priority, only_me):
        children_counts = []
        distances = []
        for field in fields:
            child_fields, _ = self.get_child_fields(field, next_player_id)
            children_counts.append(len(child_fields))
            if calculate_distance:
                half_step = False if only_me else next_player_id == self.game.my_botid
                distance_score = self.evaluate(field, only_me, half_step)
                distances.append(distance_score if next_player_id == 1 else -distance_score)
            else:
                distances.append(0)

        if priority is None:
            child_list = sorted(zip(children_counts, fields, directions, distances), key=lambda x: (x[3], x[0]))
        else:
            child_list = sorted(zip(children_counts, fields, directions, distances),
                                key=lambda x: (0 if x[2] == priority else 1, x[3], x[0]))
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
            child_field.round += 1
            child_fields.append(child_field)
            directions.append(move[1])

        return child_fields, directions

    def evaluate(self, field, only_me, half_step):
        if field.score is not None:
            return field.score
        my_player = field.players[0]
        enemy_player = field.players[1]

        if only_me:
            if self.game.my_botid == 0:
                my_score = field.total_area(my_player.coord, player_id=self.game.my_botid)
                enemy_score = 0
            else:
                my_score = 0
                enemy_score = field.total_area(enemy_player.coord, player_id=self.game.my_botid)
        else:
            p1_extra = 0
            p2_extra = 0
            if half_step:
                if self.game.my_botid == 0:
                    p1_extra=1
                else:
                    p2_extra = 1
            my_score, enemy_score = field.block_middle_score(p1_extra, p2_extra)
            if half_step:
                if self.game.my_botid == 0:
                    enemy_score -= 1
                else:
                    my_score -= 1
            if my_score != 0 or enemy_score != 0:
                if my_score == 0:
                    my_score = -float('inf')
                elif enemy_score == 0:
                    enemy_score = -float('inf')
        score = my_score - enemy_score
        if field.score is not None and field.score != score:
            print('wart')
        field.score = score
        return score
