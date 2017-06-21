import sys
from collections import defaultdict
from heapq import heappush, heappop, _siftdown

from bot import player

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
        self.distance_cache = {}
        self.area_cache = [{}, {}]
        self.cache_distance = True
        self.cache_area = True
        self.fast_area_cache = [{}, {}]
        self.cache_fast_area = True
        self.players_seperated = False
        self.score = None
        self.search_depth = 0
        self.search_score = 0
        self.hash = None

    def create_board(self, coord1=None):
        self.initialized = True
        self.cell = [[EMPTY for col in range(0, self.width)] for row in range(0, self.height)]
        if coord1 is None:
            self.players[0].row = 7
            self.players[0].col = 3
            self.players[1].row = 7
            self.players[1].col = 12
        else:
            self.players[0].row = coord1[0]
            self.players[0].col = coord1[1]
            self.players[1].row = coord1[0]
            self.players[1].col = self.width - coord1[1] - 1
        self.cell[self.players[0].row][self.players[0].col] = 0
        self.cell[self.players[1].row][self.players[1].col] = 1

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

    def is_legal(self, row, col, player_id=0):
        return (self.in_bounds(row, col)) and (self.cell[row][col] == EMPTY or self.cell[row][col] == 4 + player_id)

    def is_legal_with_players(self, row, col, player_id):
        return (self.in_bounds(row, col)) and (self.cell[row][col] == EMPTY or
                                               self.cell[row][col] == PLAYER1 or
                                               self.cell[row][col] == PLAYER2 or
                                               self.cell[row][col] == 4 + player_id)

    def get_adjacent(self, row, col):
        l1, l2, l3, l4 = None, None, None, None

        if 0 <= row - 1 < 16 and 0 <= col < 16 and self.cell[row - 1][col] == EMPTY:
            l1 = (row - 1, col)
        if 0 <= row < 16 and 0 <= col + 1 < 16 and self.cell[row][col + 1] == EMPTY:
            l2 = (row, col + 1)
        if 0 <= row + 1 < 16 and 0 <= col < 16 and self.cell[row + 1][col] == EMPTY:
            l3 = (row + 1, col)
        if 0 <= row < 16 and 0 <= col - 1 < 16 and self.cell[row][col - 1] == EMPTY:
            l4 = (row, col - 1)

        result = {l1, l2, l3, l4}
        if None in result:
            result.remove(None)
        return result

    def get_adjacent_slow(self, row, col, player_id=0):
        result = []
        # for (o_row, o_col), _ in DIRS:
        # t_row, t_col = o_row + row, o_col + col
        if self.is_legal(row - 1, col, player_id):
            result.append((row - 1, col))
        if self.is_legal(row, col + 1, player_id):
            result.append((row, col + 1))
        if self.is_legal(row + 1, col, player_id):
            result.append((row + 1, col))
        if self.is_legal(row, col - 1, player_id):
            result.append((row, col - 1))
        return result

    def get_adjacent_with_players(self, row, col, player_id):
        result = []
        for (o_row, o_col), _ in DIRS:
            t_row, t_col = o_row + row, o_col + col
            if self.is_legal_with_players(t_row, t_col, player_id):
                result.append((t_row, t_col))
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

    def total_area(self, coord, player_id=0):
        if self.cache_area:
            field_hash = hash(str([coord] + self.cell))
            if field_hash in self.area_cache[player_id]:
                return self.area_cache[player_id][field_hash]

        childs = self.get_adjacent(coord[0], coord[1])
        best_area = 0
        for child in childs:
            area = set()
            queue = set()
            queue.add(child)
            while len(queue) > 0:
                current = queue.pop()
                area.add(current)
                current_adjacent = self.get_adjacent(current[0], current[1])
                for adjacent in current_adjacent:
                    if adjacent not in area and adjacent not in queue:
                        queue.add(adjacent)
            best_area = max(best_area, len(area))
        if self.cache_area:
            self.area_cache[player_id][field_hash] = best_area
        return best_area

    def total_area_fast(self, coord, player_id=0):
        if self.cache_fast_area:
            field_hash = hash(str([coord] + self.cell))
            if field_hash in self.fast_area_cache[player_id]:
                return self.fast_area_cache[player_id][field_hash]
        area = set()
        queue = set()
        queue.add(coord)
        while len(queue) > 0:
            current = queue.pop()
            area.add(current)
            current_adjacent = self.get_adjacent(current[0], current[1])
            for adjacent in current_adjacent:
                if adjacent not in area and adjacent not in queue:
                    queue.add(adjacent)
        if self.cache_fast_area:
            self.fast_area_cache[player_id][field_hash] = area
        return area

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
        # self_hash = hash(str(self.cell))
        # if self_hash in self.distance_cache:
        #     return self.distance_cache[self_hash]
        path = self.a_star_player_to_enemy(0)
        distance = float("inf") if path is None else len(path)
        # self.distance_cache[self_hash] = distance
        return distance

    def get_copy(self):
        field = Board()
        field.width = self.width
        field.height = self.height
        field.cell = [row[:] for row in self.cell]
        field.round = self.round
        field.initialized = self.initialized
        field.distance_cache = self.distance_cache
        field.cache_area = self.cache_area
        field.cache_distance = self.cache_distance
        field.area_cache = self.area_cache
        field.cache_fast_area = self.cache_fast_area
        field.fast_area_cache = self.fast_area_cache
        field.players_seperated = self.players_seperated
        field.score = None
        field.players = [player.Player(), player.Player()]
        field.players[0].row, field.players[0].col, field.players[1].row, field.players[1].col = self.players[0].row, \
                                                                                                 self.players[0].col, \
                                                                                                 self.players[1].row, \
                                                                                                 self.players[1].col
        return field

    def is_players_separated(self):
        if not self.players_seperated:
            self.players_seperated = self.get_player_true_distance() == float("inf")
        return self.players_seperated

    def a_star_player_to_enemy(self, player_id, prevent_passing=None):
        return self.a_star(self.players[player_id].coord, self.players[player_id ^ 1].coord, player_id,
                           prevent_passing)

    def a_star(self, start, goal, player_id=0, prevent_passing=None):
        if prevent_passing is None:
            prevent_passing = defaultdict(set)
        if self.cache_distance:
            field_hash = hash(str([start, goal, player_id, prevent_passing] + self.cell))
            if field_hash in self.distance_cache:
                return self.distance_cache[field_hash]
        closed_set = set()
        open_set = {start}
        open_heap = []
        heappush(open_heap, (0, start))

        came_from = {}
        g_score = defaultdict(lambda: float("inf"))
        f_score = defaultdict(lambda: float("inf"))
        g_score[start] = 0
        f_score[start] = self.get_manhattan_distance(start, goal)

        while len(open_set) > 0:
            current = heappop(open_heap)[1]
            # current = sorted(open_set, key=lambda x: f_score[x])[0]
            if current == goal:
                final_path = self.reconstruct_path(came_from, current)
                if self.cache_distance:
                    self.distance_cache[field_hash] = final_path
                return final_path

            open_set.remove(current)
            closed_set.add(current)

            neighbours = self.get_adjacent_with_players(current[0], current[1], player_id)
            for neighbour in neighbours:
                if neighbour in closed_set or neighbour in prevent_passing[current]:
                    continue

                h = self.get_manhattan_distance(neighbour, goal)
                if neighbour not in open_set:
                    open_set.add(neighbour)
                    heappush(open_heap, (h, neighbour))

                tentative_g_score = g_score[current] + 1
                if tentative_g_score >= g_score[neighbour]:
                    continue

                came_from[neighbour] = current
                g_score[neighbour] = tentative_g_score
                f_score[neighbour] = tentative_g_score + h
        if self.cache_distance:
            self.distance_cache[field_hash] = None
        return None

    @staticmethod
    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)
        return list(reversed(total_path[:-1]))

    def block_middle_slow(self):
        field, prevent_p1 = self.block_middle_for_player(0)
        field, prevent_p2 = field.block_middle_for_player(1)

        for prevent_from in prevent_p1.keys():
            for prevent_to in prevent_p1[prevent_from]:
                field.cell[prevent_from[0]][prevent_from[1]] = 4
                field.cell[prevent_to[0]][prevent_to[1]] = 5

        for prevent_from in prevent_p2.keys():
            for prevent_to in prevent_p2[prevent_from]:
                field.cell[prevent_from[0]][prevent_from[1]] = 5
                field.cell[prevent_to[0]][prevent_to[1]] = 4

        field.cell[field.players[0].row][field.players[0].col] = 0
        field.cell[field.players[1].row][field.players[1].col] = 1

        return field

    def block_middle_for_player(self, player_id):
        field = self.get_copy()
        first = True
        path = None
        prevent = defaultdict(set)
        player = field.players[player_id]
        while first or path is not None:
            first = False
            path = field.a_star_player_to_enemy(player_id, prevent_passing=prevent)
            if path is None:
                break
            path = path[:-1]
            if len(path) == 0:
                # TODO buraya bişey yap
                # sys.stderr.write('block middle path len 0?\n')
                # sys.stderr.flush()
                prevent[player.coord].add(field.players[player_id ^ 1].coord)
            elif len(path) % 2 == 0:
                c1 = path[len(path) // 2 - 1]
                c2 = path[len(path) // 2]
                prevent[c1].add(c2)
                # field.cell[c1[0]][c1[1]] = 4
                # field.cell[c2[0]][c2[1]] = 5
            else:
                c = path[(len(path) - 1) // 2]
                field.cell[c[0]][c[1]] = BLOCKED
        return field, prevent

    def set_cell(self, cell):
        self.cell = cell
        for row in range(len(cell)):
            for col in range(len(cell[row])):
                if self.cell[row][col] == PLAYER1:
                    self.players[PLAYER1].row, self.players[PLAYER1].col = row, col
                elif self.cell[row][col] == PLAYER2:
                    self.players[PLAYER2].row, self.players[PLAYER2].col = row, col
        self.width = len(cell)
        self.height = len(cell[0])
        self.initialized = True

    @staticmethod
    def get_coord_of_direction(coord, move):
        for (o_row, o_col), direction in DIRS:
            if direction == move:
                return o_row + coord[0], o_col + coord[1]
        return None

    def get_child_fields(self, next_player_id):
        child_fields = []
        directions = []
        next_player = self.players[next_player_id]
        moves = self.legal_moves(next_player_id)
        for move in moves:
            child_field = self.get_copy()
            child_field.cell[move[0][0]][move[0][1]] = next_player_id
            child_field.cell[next_player.row][next_player.col] = BLOCKED
            child_field.players[next_player_id].row, child_field.players[next_player_id].col = move[0]
            child_fields.append(child_field)
            directions.append(move[1])

        return child_fields, directions

    def block_middle_score(self, p1_extra=0, p2_extra=0):
        p1_coord = self.players[0].coord
        p2_coord = self.players[1].coord
        dijkstra1, _ = self.dijkstra(p1_coord)
        dijkstra2, _ = self.dijkstra(p2_coord)

        p1_score = -1
        p2_score = -1

        for row in range(self.height):
            for col in range(self.width):
                if dijkstra1[(row, col)] + p1_extra < dijkstra2[(row, col)] + p2_extra:
                    p1_score += 1
                elif dijkstra1[(row, col)] + p1_extra > dijkstra2[(row, col)] + p2_extra:
                    p2_score += 1

        return p1_score, p2_score

    def dijkstra(self, start):
        """Returns a map of nodes to distance from start and a map of nodes to
        the neighbouring node that is closest to start."""
        tdist = defaultdict(lambda: float('inf'))
        tdist[start] = 0
        preceding_node = {}
        unvisited = []
        visited = {start}
        heappush(unvisited, (0, start))

        while len(unvisited) > 0:
            min_node = heappop(unvisited)[1]

            neighbours = self.get_adjacent(*min_node)
            for neighbour in neighbours:
                d = tdist[min_node] + 1
                if neighbour not in visited:
                    if tdist[neighbour] > d:
                        preceding_node[neighbour] = min_node
                        heappush(unvisited, (d, neighbour))
                        tdist[neighbour] = d
                    visited.add(neighbour)

        return tdist, preceding_node

    @staticmethod
    def decrease_key(heap, old_key, new_key, value):
        index = heap.index((old_key, value))
        heap[index] = (new_key, value)
        _siftdown(heap, 0, index)

    def get_search_hash(self):
        if self.hash is None:
            self.hash = hash(str(self.cell))
        return self.hash
