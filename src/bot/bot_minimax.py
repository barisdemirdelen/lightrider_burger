import sys

import time

from bot.board import BLOCKED


class BotMinimax(object):
    def __init__(self):
        self.game = None
        self.separated = False
        self.last_path = []
        self.last_only_me = False
        self.depth_times = []
        self.total_nodes = 0
        self.start_time = 0
        self.cached = 0

    def setup(self, game):
        self.game = game

    def give_reward(self, reward):
        pass

    def init_turn(self):
        self.total_nodes = 0
        self.depth_times = []
        self.game.last_order = None
        self.start_time = time.time()
        self.game.rounds_left = 0.5 * self.game.field.height * self.game.field.width - self.game.field.round
        self.game.field.score = None
        self.game.field.legal_player = self.game.my_botid
        self.game.field.adjacents = [None] * 256
        self.game.field.update_zobrist()
        self.game.field._legal_moves = None
        if self.separated:
            self.game.field.block_unreachable(self.game.my_botid)
        self.game.field = self.game.field.find_child_field()

    def do_turn(self):
        self.init_turn()
        score = None
        legal = self.game.field.legal_moves()
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

            # total_nodes = 0
            if not self.separated:
                self.separated = self.game.field.is_players_separated()
            if self.separated:
                rounds_left_0 = self.game.field.total_area(self.game.field.players[0].coord, player_id=0)
                rounds_left_1 = self.game.field.total_area(self.game.field.players[1].coord, player_id=1)
                self.game.rounds_left = min(rounds_left_0, rounds_left_1) + 1

                search_path = []
                if self.last_path is not None and len(self.last_path) > 0:
                    if self.last_only_me:
                        search_path = self.last_path[1:]
                    else:
                        if len(self.last_path) > 1:
                            for j in range(len(self.last_path)):
                                if j % 2 == 0:
                                    search_path.append(self.last_path[j])
                score, best_path, depth = self.iterative_deepening_alpha_beta(only_me=True, search_path=search_path)
            else:
                # blocked_field = self.game.field.block_middle()
                # if self.game.field.round > 2:
                rounds_left_0 = self.game.field.total_area(self.game.field.players[0].coord, player_id=0)
                self.game.rounds_left = rounds_left_0 + 1
                search_path = self.game.field.best_moves[:]
                score, best_path, depth = self.iterative_deepening_alpha_beta(only_me=False, search_path=search_path)
                # depth = depth / 2.0
            best_path = self.game.field.best_moves
            score = self.game.field.score
            depth = self.game.field.search_depth
            self.last_only_me = self.separated
            self.last_path = best_path

            elapsed = time.time() - self.start_time

            if score is not None:
                sys.stderr.write(
                    'Round: %d, Score: %.4f, Depth: %d, Nodes: %d, Time: %d, RoundsLeft: %d, Cached: %d, '
                    'Depth times: %s\n' % (
                        self.game.field.round, score, depth, self.total_nodes,
                        self.game.last_timebank - elapsed * 1000, self.game.rounds_left, self.cached,
                        str(self.depth_times)))
            else:
                sys.stderr.write('Score is None\n')
            if len(best_path) > 0:
                self.game.issue_order(best_path[0])
            else:
                self.game.issue_order(legal[0][1])
            sys.stderr.flush()

        return score

    def iterative_deepening_alpha_beta(self, only_me, search_path):
        i = 1 if only_me else 2
        best_path = []
        if search_path is not None:
            if len(search_path) > 0 and search_path[-1] == 'pass':
                search_path = search_path[:-1]
            if not only_me and len(search_path) > 0 and len(search_path) % 2 == 1:
                search_path = search_path[:-1]
            best_path = search_path
            # if not only_me and len(search_path) %2 == 1:
            #     sys.stderr.write('Wrong length of path\n')
            i += len(search_path)
            # sys.stderr.write(str(len(search_path)) + '\n')
        # i = i if search_path is None or len(search_path) == 0 else len(search_path)
        # average_score = self.evaluate(self.game.field, only_me)
        best_score = None
        best_move = None
        best_depth = i
        available_time = self.game.get_available_time_per_turn()
        while True:
            current_depth_start_time = time.time()
            score, path = self.alpha_beta(self.game.field, i, self.game.my_botid,
                                          -float('inf'),
                                          float('inf'), move_history=[], only_me=only_me, search_path=best_path)
            if path is not None and score is not None:
                best_score = score
                best_depth = i
                if len(path) > 0:
                    best_move = path[0]
                    best_path = path
                if len(path) == 0:
                    sys.stderr.write('Path is empty\n')

            current_time = time.time()
            depth_time = (current_time - current_depth_start_time) * 1000.0
            time_left = (available_time - current_time + self.start_time) * 1000
            self.depth_times.append('%.2f' % depth_time)
            if best_move == 'pass':
                break
            if score is None or score >= 999 or score <= -999:
                break
            if best_path is None or best_path[-1] == 'pass':
                break
            if i > self.game.rounds_left * 2:
                break
            if current_time - self.start_time > available_time:
                break
            i += 1 if only_me else 2
        return best_score, best_path, best_depth

    def alpha_beta(self, field, depth, player_id, alpha, beta, move_history, only_me, search_path):
        self.total_nodes += 1
        if only_me:
            alpha, beta = -beta, -alpha

        if depth <= field.search_depth and field.score is not None:
            self.cached += 1
            return field.score, field.best_moves

        moves = field.legal_moves()
        if depth <= 0 or len(moves) == 0:
            score = -1001
            if len(moves) > 0:
                half_step = False if only_me else player_id != self.game.my_botid
                score = self.evaluate(field, only_me, half_step, player_id)
            alpha_history = move_history + ['pass'] if len(moves) == 0 else move_history
            field.score = score
            field.search_depth = depth
            field.best_moves = alpha_history
            if alpha_history is None:
                sys.stderr.write('Wnt is this None\n')
            return score, alpha_history

        elapsed_time = time.time() - self.start_time
        if float(elapsed_time) > self.game.last_timebank * 0.9 / 1000:
            sys.stderr.write('We are on limit at time\n')
            return None, None
        if elapsed_time > self.game.get_available_time_per_turn():
            # sys.stderr.write('We are on turn time\n')
            return None, None

        priority_move = None
        search_path = search_path[:]
        if len(search_path) > 0:
            priority_move = search_path.pop(0)

        child_fields, directions = field.get_child_fields()
        child_fields, directions = self.sort_moves(child_fields, directions, player_id,
                                                   calculate_distance=False, priority=priority_move, only_me=only_me)

        best_score, alpha_history = self.aspiration_search_moves(child_fields, directions, depth, player_id, alpha,
                                                                 beta, move_history, only_me,
                                                                 search_path)
        if best_score is not None:
            field.score = best_score
            field.search_depth = depth
            field.best_moves = alpha_history
        return best_score, alpha_history

    def aspiration_search_moves(self, child_fields, directions, depth, player_id, alpha, beta, move_history, only_me,
                                search_path):

        alpha_history = move_history
        best_score = 0
        next_depth = depth - 1
        score = -1999
        for i, child_field in enumerate(child_fields):
            if i == 0:
                best_score, node_history = self.alpha_beta(child_field, next_depth,
                                                           player_id if only_me else player_id ^ 1,
                                                           -beta, -alpha,
                                                           move_history,
                                                           only_me, search_path)
                if best_score is None:
                    # sys.stderr.write('We are returning None\n')
                    return None, None
                best_score = best_score if only_me else -best_score

                if best_score > alpha:
                    alpha_history = [directions[i]] + node_history
                    if best_score >= beta:
                        return best_score, alpha_history
                    alpha = best_score
            else:
                if self.game.my_botid == player_id:
                    next_depth = 1 if depth - 5 < 1 else depth - 5
                else:
                    next_depth = 0 if depth - 5 < 0 else depth - 5
                score, node_history = self.alpha_beta(child_field, next_depth,
                                                      player_id if only_me else player_id ^ 1,
                                                      -alpha - 1, -alpha,
                                                      move_history,
                                                      only_me, search_path)
                if score is None:
                    # sys.stderr.write('We are returning None\n')
                    return None, None
                score = score if only_me else -score
                if beta > score > alpha:
                    next_depth = depth - 1
                    score, node_history = self.alpha_beta(child_field, next_depth,
                                                          player_id if only_me else player_id ^ 1,
                                                          -beta, -alpha,
                                                          move_history,
                                                          only_me, search_path)
                    if score is None:
                        # sys.stderr.write('We are returning None\n')
                        return None, None
                    score = score if only_me else -score
                    if score > alpha:
                        alpha = score

            if score > best_score:
                alpha_history = [directions[i]] + node_history
                if score >= beta:
                    return score, alpha_history
                best_score = score

        return best_score, alpha_history

    def sort_moves(self, fields, directions, next_player_id, calculate_distance, priority, only_me):
        children_counts = []
        distances = []
        for field in fields:
            children_counts.append(0)
            if calculate_distance:
                half_step = False if only_me else next_player_id != self.game.my_botid
                score = 0
                if not half_step:
                    score = -self.evaluate(field, only_me, half_step, next_player_id)
                distances.append(score)
            else:
                distances.append(0)

        if priority is None:
            child_list = sorted(zip(children_counts, fields, directions, distances), key=lambda x: (x[3]))
        else:
            child_list = sorted(zip(children_counts, fields, directions, distances),
                                key=lambda x: (0 if x[2] == priority else 1, x[3]))
        _, sorted_fields, sorted_directions, sorted_distances = zip(*child_list)

        return sorted_fields, sorted_directions

    def evaluate(self, field, only_me, half_step, player_id):
        depth = field.round - self.game.field.round
        my_player = field.players[0]
        enemy_player = field.players[1]

        if only_me:
            if self.game.my_botid == 0:
                my_score = field.total_area(my_player.coord, player_id=self.game.my_botid) + depth
                enemy_score = 0
            else:
                my_score = 0
                enemy_score = field.total_area(enemy_player.coord, player_id=self.game.my_botid) + depth
        else:
            p1_extra = 0
            p2_extra = 0
            # if half_step:
            #     # print('Where does animals come from?')
            #     if self.game.my_botid == 0:
            #         p1_extra = 1
            #     else:
            #         p2_extra = 1
            my_score, enemy_score = field.block_middle_score(p1_extra, p2_extra)
            if my_score != 0 or enemy_score != 0:
                if my_score == 0:
                    my_score = -999
                elif enemy_score == 0:
                    enemy_score = -999
        score = my_score - enemy_score
        score = score if player_id == 0 or (only_me and self.game.my_botid == 0) else -score
        return score
