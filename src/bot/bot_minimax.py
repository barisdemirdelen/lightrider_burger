import sys

import time

from bot.board import BLOCKED

total_nodes = 0
start_time = 0
cached = 0


class Bot(object):
    def __init__(self):
        self.game = None
        self.separated = False
        self.cache = {}

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
                rounds_left_1 = self.game.field.total_area(self.game.field.players[1].coord, player_id=1)
                self.game.rounds_left = min(rounds_left_0, rounds_left_1) // 2 + 1
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

            if len(best_path) > 0:
                self.game.issue_order(best_path[0])
            else:

                # legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
                # if len(legal) == 0:
                #     self.game.issue_order_pass()
                # # else:
                # (_, chosen) = random.choice(legal)
                self.game.issue_order(legal[-1][1])
        return score

    def iterative_deepening_alpha_beta(self, only_me):
        i = 0
        best_score = None
        best_path = []
        best_depth = i
        while True:
            current_time = time.time()
            available_time = self.game.get_available_time_per_turn()
            if current_time - start_time > available_time:
                break
            score, path, _, _ = self.alpha_beta(self.game.field, i, self.game.my_botid,
                                                -float("inf"), float("inf"), [], only_me=only_me, search_path=best_path)
            if score is not None:
                best_score = score
                best_path = path
                best_depth = i
            if len(best_path) < i:
                break
            i += 1
        return best_score, best_path, best_depth

    def alpha_beta(self, field, depth, player_id, alpha, beta, move_history, only_me, search_path):
        global total_nodes
        global cached
        total_nodes += 1
        pruned = False
        # field_hash = hash(str(field))
        # if field_hash in self.cache:
        #     cached+=1
        #     return self.cache[field_hash]

        moves = field.legal_moves(player_id)
        elapsed_time = time.time() - start_time
        if depth == 0 or len(moves) == 0:
            my_player = field.players[0]
            enemy_player = field.players[1]

            distance = 0
            if only_me:
                if self.game.my_botid == 0:
                    my_score = field.total_area(my_player.coord, player_id=self.game.my_botid)
                    enemy_score = 0
                else:
                    my_score = 0
                    enemy_score = field.total_area(enemy_player.coord, player_id=self.game.my_botid)
            else:
                blocked_field = field.block_middle()
                my_score = blocked_field.total_area(my_player.coord, 0)
                enemy_score = blocked_field.total_area(enemy_player.coord, 1)
                distance = field.get_player_true_distance()
            score = my_score - enemy_score
            # self.cache[field_hash] = (
            #     score, move_history + ['pass'] if len(moves) == 0 else move_history, distance, False)
            # return self.cache[field_hash]
            return score, move_history + ['pass'] if len(moves) == 0 else move_history, distance, False

        if elapsed_time > self.game.get_available_time_per_turn():
            return None, None, None, None

        priority_move = None
        search_path = search_path[:]
        if len(search_path) > 0:
            priority_move = search_path.pop(0)

        child_fields, directions = self.get_child_fields(field, player_id)
        child_fields, directions = self.sort_moves(child_fields, directions, player_id if only_me else player_id ^ 1,
                                                   calculate_distance=False, priority=priority_move)

        if player_id == 0:
            best_value = -float("inf")
            best_history = move_history
            best_distance = float("inf")
            for i, child_field in enumerate(child_fields):
                v, node_history, distance, child_pruned = self.alpha_beta(child_field, depth - 1,
                                                                          player_id if only_me else player_id ^ 1,
                                                                          alpha, beta,
                                                                          move_history, only_me, search_path)
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
                                                                          move_history, only_me, search_path)
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
        # self.cache[field_hash] = (best_value, best_history, best_distance, pruned)
        # return self.cache[field_hash]
        return best_value, best_history, best_distance, pruned

    def sort_moves(self, fields, directions, next_player_id, calculate_distance, priority):
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
        if priority is None:
            child_list = sorted(zip(children_counts, fields, directions, distances), key=lambda x: (x[0], x[3]))
        else:
            child_list = sorted(zip(children_counts, fields, directions, distances),
                                key=lambda x: (0 if x[2] == priority else 1, x[0], x[3]))
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
