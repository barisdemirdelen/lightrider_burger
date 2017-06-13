import copy


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
            best_score = 0
            best_move = None
            for move in legal:
                score = self.total_area(move[0])
                if score >= best_score:
                    best_score = score
                    best_move = move

            self.game.issue_order(best_move[1])
            # legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
            # if len(legal) == 0:
            #     self.game.issue_order_pass()
            # else:
            #     (_, chosen) = random.choice(legal)
            #     self.game.issue_order(chosen)

    def minimax(self, field, depth, player_id):
        child_fields = []
        field.get_adjacent()
        if depth == 0 or len(child_fields) == 0:
            pass
        # copy_field = copy.deepcopy(self.game.field)

    def total_area(self, coord):
        area = set()
        queue = set()
        queue.add(coord)
        while len(queue) > 0:
            current = queue.pop()
            area.add(current)
            current_adjacent = self.game.field.get_adjacent(*current)
            for adjacent in current_adjacent:
                if adjacent not in area and adjacent not in queue:
                    queue.add(adjacent)
        return len(area)
