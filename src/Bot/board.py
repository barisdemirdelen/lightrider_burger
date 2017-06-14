import sys
from collections import defaultdict

from Bot import player

PLAYER1, PLAYER2, EMPTY, BLOCKED = [0, 1, 2, 3]
S_PLAYER1, S_PLAYER2, S_EMPTY, S_BLOCKED, = ['0', '1', '.', 'x']

CHARTABLE = [(PLAYER1, S_PLAYER1), (PLAYER2, S_PLAYER2), (EMPTY, S_EMPTY), (BLOCKED, S_BLOCKED)]

DIRS = [
    ((-1, 0), 'up'),
    ((0, 1), 'right'),
    ((1, 0), 'down'),
    ((0, -1), 'left')
]


class Board(object):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.cell = None
        self.players = [player.Player(), player.Player()]
        self.round = 0
        self.initialized = False

    def create_board(self):
        self.initialized = True
        self.cell = [[EMPTY for col in range(0, self.width)] for row in range(0, self.height)]

    @staticmethod
    def parse_cell_char(players, row, col, char):
        result = -1
        if char == S_PLAYER1:
            players[0].row = row
            players[0].col = col
        elif char == S_PLAYER2:
            players[1].row = row
            players[1].col = col
        for (i, symbol) in CHARTABLE:
            if symbol == char:
                result = i
                break
        return result

    def parse_cell(self, players, row, col, data):
        item = self.parse_cell_char(players, row, col, data)
        return item

    def parse(self, players, data):
        cells = data.split(',')
        col = 0
        row = 0
        for cell in cells:
            if col >= self.width:
                col = 0
                row += 1
            self.cell[row][col] = self.parse_cell(players, row, col, cell)
            col += 1

    def in_bounds(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width

    def is_legal(self, row, col):
        return (self.in_bounds(row, col)) and (self.cell[row][col] == EMPTY)

    def is_legal_with_players(self, row, col):
        return (self.in_bounds(row, col)) and (self.cell[row][col] != BLOCKED)

    def get_adjacent(self, row, col):
        result = []
        # for (o_row, o_col), _ in DIRS:
        # t_row, t_col = o_row + row, o_col + col
        if self.is_legal(row - 1, col):
            result.append((row - 1, col))
        if self.is_legal(row, col + 1):
            result.append((row, col + 1))
        if self.is_legal(row + 1, col):
            result.append((row + 1, col))
        if self.is_legal(row, col - 1):
            result.append((row, col - 1))
        return result

    def get_adjacent_with_players(self, row, col):
        result = []
        # for (o_row, o_col), _ in DIRS:
        # t_row, t_col = o_row + row, o_col + col
        if self.is_legal_with_players(row - 1, col):
            result.append((row - 1, col))
        if self.is_legal_with_players(row, col + 1):
            result.append((row, col + 1))
        if self.is_legal_with_players(row + 1, col):
            result.append((row + 1, col))
        if self.is_legal_with_players(row, col - 1):
            result.append((row, col - 1))
        return result

    def legal_moves(self, my_id):
        my_player = self.players[my_id]
        result = []
        for ((o_row, o_col), order) in DIRS:
            t_row = my_player.row + o_row
            t_col = my_player.col + o_col
            if self.is_legal(t_row, t_col):
                result.append(((t_row, t_col), order))
        return result

    @staticmethod
    def output_cell(cell):
        done = False
        for (i, symbol) in CHARTABLE:
            if i in cell:
                if not done:
                    sys.stderr.write(symbol)
                done = True
                break
        if not done:
            sys.stderr.write('!')

    def output(self):
        for row in self.cell:
            sys.stderr.write('\n')
            for cell in row:
                self.output_cell(cell)
        sys.stderr.write('\n')
        sys.stderr.flush()

    def total_area(self, coord):
        childs = self.get_adjacent(*coord)
        best_area = 0
        for child in childs:
            area = set()
            queue = set()
            queue.add(child)
            while len(queue) > 0:
                current = queue.pop()
                area.add(current)
                current_adjacent = self.get_adjacent(*current)
                for adjacent in current_adjacent:
                    if adjacent not in area and adjacent not in queue:
                        queue.add(adjacent)
            best_area = max(best_area, len(area))
        return best_area

    @staticmethod
    def get_manhattan_distance(c1, c2):
        y0, x0 = c1
        y1, x1 = c2
        return abs(x1 - x0) + abs(y1 - y0)

    @staticmethod
    def get_euclidian_distance_square(c1, c2):
        y0, x0 = c1
        y1, x1 = c2
        return (x1 - x0) ** 2 + (y1 - y0) ** 2

    def get_player_euclidian_distance_square(self):
        return self.get_euclidian_distance_square(self.players[0].coord, self.players[1].coord)

    def get_player_manhattan_distance(self):
        return self.get_manhattan_distance(self.players[0].coord, self.players[1].coord)

    def get_player_true_distance(self):
        path = self.a_star_player_to_enemy(0)
        return float("inf") if path is None else len(path)

    def get_copy(self):
        field = Board()
        field.width = self.width
        field.height = self.height
        field.cell = [row[:] for row in self.cell]
        field.round = self.round
        field.initialized = self.initialized
        field.players = [player.Player(), player.Player()]
        field.players[0].row, field.players[0].col, field.players[1].row, field.players[1].col = self.players[0].row, \
                                                                                                 self.players[0].col, \
                                                                                                 self.players[1].row, \
                                                                                                 self.players[1].col
        return field

    # def is_players_separated(self):
    #     area = set()
    #     queue = set()
    #     queue.add(self.players[0].coord)
    #     while len(queue) > 0:
    #         current = queue.pop()
    #         if current == self.players[1].coord:
    #             return False
    #         area.add(current)
    #         current_adjacent = self.get_adjacent_with_players(*current)
    #         for adjacent in current_adjacent:
    #             if adjacent not in area and adjacent not in queue:
    #                 queue.add(adjacent)
    #     return True

    def is_players_separated(self):
        return self.a_star(self.players[0].coord, self.players[1].coord) is None

    def a_star_player_to_enemy(self, player_id):
        return self.a_star(self.players[player_id].coord, self.players[player_id ^ 1].coord)

    def a_star(self, start, goal):
        closed_set = set()
        open_set = {start}

        came_from = {}
        g_score = defaultdict(lambda: float("inf"))
        f_score = defaultdict(lambda: float("inf"))
        g_score[start] = 0
        f_score[start] = self.get_manhattan_distance(start, goal)

        while len(open_set) > 0:
            current = sorted(list(open_set), key=lambda x: f_score[x])[0]
            if current == goal:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)
            closed_set.add(current)

            neighbours = self.get_adjacent_with_players(*current)
            for neighbour in neighbours:
                if neighbour in closed_set:
                    continue

                open_set.add(neighbour)

                tentative_g_score = g_score[current] + 1
                if tentative_g_score >= g_score[neighbour]:
                    continue

                came_from[neighbour] = current
                g_score[neighbour] = tentative_g_score
                f_score[neighbour] = tentative_g_score + self.get_manhattan_distance(neighbour, goal)
        return None

    @staticmethod
    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)
        return list(reversed(total_path[:-1]))

    def block_middle(self):
        field = self.get_copy()
        first = True
        path = None
        while first or path is not None:
            first = False
            path = field.a_star_player_to_enemy(0)
            if path is None:
                break
            path = path[:-1]
            if len(path) == 0:
                # TODO buraya bişey yap
                break
            if len(path) % 2 == 0:
                c1 = path[len(path) // 2 - 1]
                c2 = path[len(path) // 2]
                field.cell[c1[0]][c1[1]] = BLOCKED
                field.cell[c2[0]][c2[1]] = BLOCKED
            else:
                c = path[(len(path) - 1) // 2]
                field.cell[c[0]][c[1]] = BLOCKED
        return field
