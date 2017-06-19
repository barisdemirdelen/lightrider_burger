import random


class BotHeuristic(object):
    def __init__(self):
        self.game = None
        self.reward = 0
        self.last_move = None

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
        elif len(legal) == 1:
            self.game.issue_order(legal[0][1])
        else:

            if not self.last_move_heuristic(legal):
                (_, chosen) = random.choice(legal)
                self.game.issue_order(chosen)

        self.last_move = self.game.last_order
        return 0

    def last_move_heuristic(self, legal):
        if self.last_move is not None and random.random() < 0.0:
            for move in legal:
                if self.last_move == move[1]:
                    self.game.issue_order(self.last_move)
                    return True
        return False

    def least_distance_heuristic(self, legal):
        if random.random() < 0.5:
            enemy_coord = self.game.field.players[self.game.my_botid ^ 1].coord
            best_move = None
            best_dist = float('inf')
            for move in legal:
                move_coord = move[0]
                dist = (move_coord[0] - enemy_coord[0]) ** 2 + (move_coord[1] - enemy_coord[1]) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best_move = move[1]

            self.game.issue_order(best_move)
            return True
        return False

    def least_true_distance_heuristic(self, legal):
        if random.random() < 0.1:
            enemy_coord = self.game.field.players[self.game.my_botid ^ 1].coord
            best_move = None
            best_dist = float('inf')
            for move in legal:
                move_coord = move[0]
                dist = self.game.field.a_star(move_coord, enemy_coord, self.game.my_botid)
                if dist is not None:
                    dist = len(dist)
                    if dist < best_dist:
                        best_dist = dist
                        best_move = move[1]

            self.game.issue_order(best_move)
            return True
        return False

    def total_area_heuristic(self, legal):
        if random.random() < 0.1:
            best_area = -float('inf')
            best_moves = []
            area_list = set()
            for move in legal:
                if move[0] not in area_list:
                    area_list = self.game.field.total_area_fast(move[0], self.game.my_botid)
                area = len(area_list)
                if area > best_area:
                    best_area = area
                    best_moves = [move[1]]
                elif area == best_area:
                    best_moves.append(move[1])

            self.game.issue_order(random.choice(best_moves))
            return True
        return False

    def middle_block_area_heuristic(self, legal):
        if random.random() < 0.01:
            p1_coord = self.game.field.players[0].coord
            p2_coord = self.game.field.players[1].coord
            children, directions = self.game.field.get_child_fields(self.game.my_botid)
            best_score = -float('inf') if self.game.my_botid == 0 else float('inf')
            best_move = None
            for field, direction in zip(children, directions):

                blocked_field = field.block_middle()
                my_score = blocked_field.total_area(field.get_coord_of_direction(p1_coord, direction), 0)
                enemy_score = blocked_field.total_area(field.get_coord_of_direction(p2_coord, direction), 1)
                score = my_score - enemy_score
                if self.game.my_botid == 0:
                    if best_score < score:
                        best_score = score
                        best_move = direction
                else:
                    if best_score > score:
                        best_score = score
                        best_move = direction
                self.game.issue_order(best_move)
                return True
        return False
