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
        self.cache_nodes = True
        self.cache = {}
        self.histories = {}
        self.depths = {}
        self.last_path = []
        self.last_only_me = False
        self.T = []
        self.depth_times = []

    def setup(self, game):
        self.game = game

    def give_reward(self, reward):
        pass

    def do_turn(self):
        global start_time
        self.depth_times = []
        self.game.last_order = None
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
                search_path = []
                if self.last_path is not None and len(self.last_path) > 1:
                    search_path = self.last_path[2:]
                score, best_path, depth = self.iterative_deepening_alpha_beta(only_me=False, search_path=search_path)
                # depth = depth / 2.0
            self.last_only_me = self.separated
            self.last_path = best_path

            elapsed = time.time() - start_time

            if score is not None:
                sys.stderr.write(
                    "Round: %d, Score: %.4f, Depth: %.1f, Nodes: %.4f, Time: %d, RoundsLeft: %d, Cached: %d, Depth times: %s\n" % (
                        self.game.field.round, score, depth, total_nodes / (self.game.field.round + 1),
                        self.game.last_timebank - elapsed * 1000, self.game.rounds_left, cached, str(self.depth_times)))
            else:
                sys.stderr.write("Score is None\n")
            sys.stderr.flush()
            if len(best_path) > 0:
                self.game.issue_order(best_path[0])
            else:
                self.game.issue_order(legal[0][1])

        return score

    def iterative_deepening_alpha_beta(self, only_me, search_path):
        i = 1
        global cached
        cached = 0
        # average_score = self.evaluate(self.game.field, only_me)
        best_score = None
        best_move = None
        best_depth = i
        best_path = []
        available_time = self.game.get_available_time_per_turn()
        while True:
            current_depth_start_time = time.time()
            score, path = self.alpha_beta(self.game.field, i, self.game.my_botid,
                                          -float('inf'),
                                          float('inf'), move_history=[], only_me=only_me, search_path=best_path)
            if path is not None:
                best_score = score
                best_move = path[0]
                best_depth = i
                best_path = path
            if best_move == 'pass':
                break
            if score is None or score >= 999 or score <= -999:
                break
            if best_path is None or best_path[-1] == 'pass':
                break
            if i > self.game.rounds_left * 2:
                break
            current_time = time.time()
            if current_time - start_time > available_time:
                break
            depth_time = (current_time - current_depth_start_time) * 1000.0
            time_left = (available_time - current_time + start_time) * 1000
            self.depth_times.append('%.2f' % depth_time)
            if depth_time * 0.9> time_left:
                break
            i += 1
            self.depth_times.append('%.2f' % ((time.time() - current_depth_start_time) * 1000.0))
        return best_score, best_path, best_depth

    def alpha_beta(self, field, depth, player_id, alpha, beta, move_history, only_me, search_path):
        global total_nodes
        total_nodes += 1
        if only_me:
            alpha, beta = -beta, -alpha

        moves = field.legal_moves(player_id)
        elapsed_time = time.time() - start_time
        if depth <= 0 or len(moves) == 0:
            half_step = False if only_me else player_id != self.game.my_botid
            score = self.evaluate(field, only_me, half_step)
            return score if player_id == 0 or (only_me and self.game.my_botid == 0) else -score, move_history + [
                'pass'] if len(
                moves) == 0 else move_history

        if elapsed_time > self.game.last_timebank * 0.9 / 1000:
            sys.stderr.write('We are on limit at time\n')
            return None, None

        priority_move = None
        search_path = search_path[:]
        if len(search_path) > 0:
            priority_move = search_path.pop(0)

        child_fields, directions = self.get_child_fields(field, player_id)
        child_fields, directions = self.sort_moves(child_fields, directions, player_id,
                                                   calculate_distance=True, priority=priority_move, only_me=only_me)

        best_score, alpha_history = self.aspiration_search_moves(child_fields, directions, depth, player_id, alpha,
                                                                 beta, move_history, only_me,
                                                                 search_path)
        return best_score, alpha_history

    def aspiration_search_moves(self, child_fields, directions, depth, player_id, alpha, beta, move_history, only_me,
                                search_path):
        global cached
        alpha_history = move_history
        best_score = 0
        next_depth = depth - 1
        score = -1999
        for i, child_field in enumerate(child_fields):
            if i == 0:
                get_score_from_cache = False
                if self.cache_nodes:
                    child_hash = child_field.get_search_hash()
                    if child_hash in self.cache:
                        if next_depth <= self.depths[child_hash]:
                            get_score_from_cache = True
                    if get_score_from_cache:
                        best_score = self.cache[child_hash]
                        node_history = self.histories[child_hash]
                        cached += 1
                if not get_score_from_cache:
                    best_score, node_history = self.alpha_beta(child_field, next_depth,
                                                               player_id if only_me else player_id ^ 1,
                                                               -beta, -alpha,
                                                               move_history,
                                                               only_me, search_path)
                    if best_score is None:
                        return None, None
                    best_score = best_score if only_me else -best_score
                    if self.cache_nodes:
                        self.cache[child_hash] = best_score
                        self.histories[child_hash] = node_history
                        self.depths[child_hash] = next_depth

                if best_score > alpha:
                    alpha_history = [directions[i]] + node_history
                    if best_score >= beta:
                        return best_score, alpha_history
                    alpha = best_score
            else:
                get_score_from_cache = False
                if self.cache_nodes:
                    child_hash = child_field.get_search_hash()
                    if child_hash in self.cache:
                        if depth - 1 <= self.depths[child_hash]:
                            get_score_from_cache = True
                    if get_score_from_cache:
                        score = self.cache[child_hash]
                        node_history = self.histories[child_hash]
                        cached += 1
                if not get_score_from_cache:
                    next_depth = depth - 4
                    score, node_history = self.alpha_beta(child_field, next_depth,
                                                          player_id if only_me else player_id ^ 1,
                                                          -alpha - 1, -alpha,
                                                          move_history,
                                                          only_me, search_path)
                    if score is None:
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
                            return None, None
                        score = score if only_me else -score
                        if score > alpha:
                            alpha = score
                    if self.cache_nodes:
                        self.cache[child_hash] = score
                        self.histories[child_hash] = node_history
                        self.depths[child_hash] = next_depth

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
            child_fields, _ = self.get_child_fields(field, next_player_id)
            children_counts.append(len(child_fields))
            if calculate_distance and priority == False:
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

    def evaluate(self, field, only_me, half_step):
        if field.score is not None:
            return field.score

        field.depth = field.round - self.game.field.round
        my_player = field.players[0]
        enemy_player = field.players[1]

        if only_me:
            if self.game.my_botid == 0:
                my_score = field.total_area(my_player.coord, player_id=self.game.my_botid) + field.depth
                enemy_score = 0
            else:
                my_score = 0
                enemy_score = field.total_area(enemy_player.coord, player_id=self.game.my_botid) + field.depth
        else:
            p1_extra = 0
            p2_extra = 0
            if half_step:
                if self.game.my_botid == 0:
                    p1_extra = 1
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
                    my_score = -999
                elif enemy_score == 0:
                    enemy_score = -999
        score = my_score - enemy_score
        if field.score is not None and field.score != score:
            print('wart')
        field.score = score
        return score

    @staticmethod
    def get_child_fields(field, next_player_id):
        child_fields = []
        directions = []
        next_player = field.players[next_player_id]
        moves = field.legal_moves(next_player_id)
        for move in moves:
            child_field = field.get_copy()
            child_field.cell[move[0][0] * 16 + move[0][1]] = next_player_id
            child_field.cell[next_player.row * 16 + next_player.col] = BLOCKED
            child_field.players[next_player_id].row, child_field.players[next_player_id].col = move[0]
            child_field.round += 1
            child_fields.append(child_field)
            directions.append(move[1])

        return child_fields, directions


        # def zw_search(self, field, depth, player_id, beta, move_history, only_me, search_path):
        #     global total_nodes
        #     total_nodes += 1
        #     if only_me:
        #         beta = -beta
        #
        #     moves = field.legal_moves(player_id)
        #     elapsed_time = time.time() - start_time
        #     if depth == 0 or len(moves) == 0:
        #         half_step = False if only_me else player_id != self.game.my_botid
        #         score = self.evaluate(field, only_me, half_step)
        #         return score if player_id == 0 or only_me else -score, move_history + ['pass'] if len(
        #             moves) == 0 else move_history
        #
        #     if elapsed_time > self.game.get_available_time_per_turn():
        #         return None, None
        #
        #     priority_move = None
        #     search_path = search_path[:]
        #     if len(search_path) > 0:
        #         priority_move = search_path.pop(0)
        #     child_fields, directions = self.get_child_fields(field, player_id)
        #     child_fields, directions = self.sort_moves(child_fields, directions, player_id,
        #                                                calculate_distance=False, priority=priority_move, only_me=only_me)
        #
        #     i = 0
        #     node_history = []
        #     for i, child_field in enumerate(child_fields):
        #         score, node_history = self.zw_search(child_field, depth - 1, player_id if only_me else player_id ^ 1,
        #                                              1 - beta,
        #                                              move_history,
        #                                              only_me, search_path)
        #         if score is None:
        #             return None, None
        #         score = score if only_me else -score
        #
        #         if score >= beta:
        #             return beta, node_history
        #     return beta - 1, [directions[i]] + node_history
