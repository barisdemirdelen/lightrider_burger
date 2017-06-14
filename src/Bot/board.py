import sys

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

    def get_player_manhattan_distance(self):
        y0, x0 = self.players[0].row, self.players[0].col
        y1, x1 = self.players[1].row, self.players[1].col
        return abs(x1 - x0) + abs(y1 - y0)

    def get_player_euclidian_distance_square(self):
        y0, x0 = self.players[0].row, self.players[0].col
        y1, x1 = self.players[1].row, self.players[1].col
        return (x1 - x0) ** 2 + (y1 - y0) ** 2

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
