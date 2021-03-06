import random
import sys
from collections import defaultdict, deque
from heapq import heappush, heappop

from bot.player import Player

PLAYER1, PLAYER2, EMPTY, BLOCKED = [0, 1, 2, 3]
S_PLAYER1, S_PLAYER2, S_EMPTY, S_BLOCKED, = ['0', '1', '.', 'x']

CHARTABLE = [(PLAYER1, S_PLAYER1), (PLAYER2, S_PLAYER2), (EMPTY, S_EMPTY), (BLOCKED, S_BLOCKED)]

DIRS = [
    ((-1, 0), 'up'),
    ((0, 1), 'right'),
    ((1, 0), 'down'),
    ((0, -1), 'left')
]

board_size = 16


class Board(object):
    __slots__ = ['width', 'height', 'cell', 'players', 'round', 'initialized', '_players_separated', 'score',
                 'search_depth', 'best_moves', 'separated_score', 'separated_search_depth', 'separated_best_moves',
                 'hash', 'children', '_legal_moves', 'legal_player', 'adjacents']
    hashtable = None

    def __init__(self):
        self.width = 0
        self.height = 0
        self.cell = None
        self.players = [Player(), Player()]
        self.round = 0
        self.initialized = False
        self._players_separated = False
        self.score = None
        self.search_depth = 0
        self.best_moves = []
        self.separated_score = None
        self.separated_search_depth = 0
        self.separated_best_moves = []
        self.hash = None
        self.children = None
        self._legal_moves = None
        self.legal_player = None
        self.adjacents = None

    def create_board(self, coord1=None, height=None):
        if height:
            self.width = height
            self.height = height
        self.cell = [EMPTY for _ in range(0, self.height * self.width)]
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
        self.cell[self.players[0].row * self.height + self.players[0].col] = 0
        self.cell[self.players[1].row * self.height + self.players[1].col] = 1
        self.init_zobrist()
        self.initialized = True

    def copy(self):
        field = Board.__new__(Board)
        field.width = self.width
        field.height = self.height
        field.round = self.round
        field.initialized = self.initialized
        field._players_separated = self._players_separated
        field.hash = self.hash
        field.legal_player = self.legal_player
        field.adjacents = self.adjacents.copy()
        field.cell = self.cell.copy()
        field.players = [player.copy for player in self.players]
        field.search_depth = 0
        field.separated_search_depth = 0
        field.best_moves = []
        field.separated_best_moves = []
        field.children = None
        field._legal_moves = None
        field.score = None
        field.separated_score = None
        return field

    def move(self, new_coord):
        player = self.players[self.legal_player]
        old_position = player.row * board_size + player.col
        new_poisition = new_coord[0] * board_size + new_coord[1]

        adjacents = self.adjacents[new_poisition]
        for adjacent in adjacents:
            adjacent_posisition = adjacent[0] * 16 + adjacent[1]
            cached_adjacent = self.adjacents[adjacent_posisition].copy()
            cached_adjacent.remove(new_coord)
            self.adjacents[adjacent_posisition] = cached_adjacent
        self.adjacents[old_position] = set()

        self.cell[old_position] = BLOCKED
        self.cell[new_poisition] = self.legal_player
        self.hash ^= Board.hashtable[old_position][self.legal_player]
        self.hash ^= Board.hashtable[old_position][BLOCKED]
        self.hash ^= Board.hashtable[new_poisition][EMPTY]
        self.hash ^= Board.hashtable[new_poisition][self.legal_player]

        if self.legal_player == self.next_legal_player:
            self.round += 1
        else:
            self.round += 0.5

        player.row, player.col = new_coord
        self.legal_player = self.next_legal_player

    def block_middle_score(self):
        p1_coord = self.players[0].coord
        p2_coord = self.players[1].coord
        p1_score, p2_score = self.double_headed_dijkstra(p1_coord, p2_coord)

        return p1_score - 1, p2_score - 1

    def block_middle_score_old(self):
        p1_coord = self.players[0].coord
        p2_coord = self.players[1].coord
        dijkstra1 = self.dijkstra(p1_coord)
        dijkstra2 = self.dijkstra(p2_coord)

        p1_score = -1
        p2_score = -1

        for d1, d2 in zip(dijkstra1, dijkstra2):
            if d1 < d2:
                p1_score += 1
            elif d1 > d2:
                p2_score += 1

        # dijkstra_dead1 = self.dijkstra_without_deadends(p1_coord)
        # dijkstra_dead2 = self.dijkstra_without_deadends(p2_coord)
        #
        # p1_dead_score = -1
        # p2_dead_score = -1
        #
        # for d1, d2 in zip(dijkstra_dead1, dijkstra_dead2):
        #     if d1 < d2:
        #         p1_dead_score += 1
        #     elif d1 > d2:
        #         p2_dead_score += 1
        #
        # p1_score += 0.1 * p1_dead_score
        # p2_score += 0.1 * p2_dead_score

        return p1_score, p2_score

    def separated_block_middle_score(self):
        p1_coord = self.players[0].coord
        dijkstra1 = self.dijkstra(p1_coord)

        p1_score = -1

        for d1 in dijkstra1:
            if d1 < 900:
                p1_score += 1

        return p1_score, 0

    def dijkstra(self, start):
        """Returns a map of nodes to distance from start and a map of nodes to
        the neighbouring node that is closest to start."""
        tdist = [999] * 256
        tdist[start[0] * 16 + start[1]] = 0
        unvisited = deque()
        visited = {start}
        unvisited.append((0, start))
        # heappush(unvisited, (0, start))

        while unvisited:
            dist_min_node, min_node = unvisited.popleft()

            d = dist_min_node + 1
            neighbours = self.adjacents[min_node[0] * 16 + min_node[1]]
            for neighbour in neighbours:
                if neighbour not in visited:
                    # if tdist[neighbour] > d:
                    # unvisited.push(d, neighbour)
                    unvisited.append((d, neighbour))
                    # heappush(unvisited, (d, neighbour))
                    tdist[neighbour[0] * 16 + neighbour[1]] = d
                    visited.add(neighbour)
        return tdist

    def double_headed_dijkstra(self, start1, start2):
        """Returns a map of nodes to distance from start and a map of nodes to
        the neighbouring node that is closest to start."""
        tdist = [999] * 256
        tdist[start1[0] * 16 + start1[1]] = 0
        tdist[start2[0] * 16 + start2[1]] = 0
        unvisited = deque()
        # visited1 = {start1}
        # visited2 = {start2}
        visited = [1, 1]
        unvisited.append((0, start1, 0))
        unvisited.append((0, start2, 1))
        # heappush(unvisited, (0, start))

        while unvisited:
            dist_min_node, min_node, player_id = unvisited.popleft()

            d = dist_min_node + 1
            neighbours = self.adjacents[min_node[0] * 16 + min_node[1]]
            for neighbour in neighbours:
                if tdist[neighbour[0] * 16 + neighbour[1]] > d:
                    # if neighbour not in visited[player_id] and (
                    #                 neighbour not in visited[1 - player_id] or tdist[
                    #                     neighbour[0] * 16 + neighbour[1]] == d):
                    # if tdist[neighbour] > d:
                    # unvisited.push(d, neighbour)
                    unvisited.append((d, neighbour, player_id))
                    # heappush(unvisited, (d, neighbour))
                    tdist[neighbour[0] * 16 + neighbour[1]] = d
                    visited[player_id] += 1
        return visited

    def find_child_field(self):
        if self.children:
            for child in self.children:
                if child.hash == self.hash:
                    return child
                if child.children:
                    for grandchild in child.children:
                        if grandchild.hash == self.hash:
                            return grandchild
        sys.stderr.write('Couldnt find this child.\n')
        self.reset_caches()
        return self

    @property
    def legal_moves(self):
        if self._legal_moves is None:
            my_player = self.players[self.legal_player]
            result = []
            for ((o_row, o_col), order) in DIRS:
                t_row = my_player.row + o_row
                t_col = my_player.col + o_col
                if self.is_legal(t_row, t_col):
                    result.append(((t_row, t_col), order))
            self._legal_moves = result
        return self._legal_moves

    def get_child_fields(self):
        moves = self.legal_moves
        if not moves:
            return [], []
        if self.children is None:
            self.children = []
            for move in moves:
                child_field = self.copy()
                child_field.move(move[0])

                self.children.append(child_field)
        _, directions = zip(*moves)
        return self.children, directions

    def reset_caches(self):
        self.children = None
        self.score = None
        self.best_moves = []
        self.search_depth = 0
        self.cache_adjacent_initial()

    @staticmethod
    def get_all_adjacent(row, col):
        l1, l2, l3, l4 = None, None, None, None
        if 0 <= row - 1 < 16 and 0 <= col < 16:
            l1 = (row - 1, col)
        if 0 <= row < 16 and 0 <= col + 1 < 16:
            l2 = (row, col + 1)
        if 0 <= row + 1 < 16 and 0 <= col < 16:
            l3 = (row + 1, col)
        if 0 <= row < 16 and 0 <= col - 1 < 16:
            l4 = (row, col - 1)

        result = {l1, l2, l3, l4}
        if None in result:
            result.remove(None)
        return result

    @property
    def cell2d(self):
        cell2d = []
        for row in range(self.height):
            current_row = []
            for col in range(self.width):
                current_row.append(self.cell[row * self.height + col])

            cell2d.append(current_row)
        return cell2d

    def cache_adjacent_initial(self):
        self.adjacents = []
        for row in range(16):
            for col in range(16):
                row_16 = row * 16
                if self.cell[row_16 + col] == BLOCKED:
                    self.adjacents.append(set())
                else:
                    l1, l2, l3, l4 = None, None, None, None
                    if 0 <= row - 1 < 16 and 0 <= col < 16 and self.cell[row_16 - 16 + col] == EMPTY:
                        l1 = (row - 1, col)
                    if 0 <= row < 16 and 0 <= col + 1 < 16 and self.cell[row * 16 + col + 1] == EMPTY:
                        l2 = (row, col + 1)
                    if 0 <= row + 1 < 16 and 0 <= col < 16 and self.cell[row_16 + 16 + col] == EMPTY:
                        l3 = (row + 1, col)
                    if 0 <= row < 16 and 0 <= col - 1 < 16 and self.cell[row * 16 + col - 1] == EMPTY:
                        l4 = (row, col - 1)

                    result = {l1, l2, l3, l4}
                    if None in result:
                        result.remove(None)
                    self.adjacents.append(result)

    # ------------------------------------------------------------------------------------------------------------------

    def block_unreachable(self):
        p1_coord = self.players[0].coord
        dijkstra1 = self.dijkstra(p1_coord)

        for i in range(256):
            if dijkstra1[i] == 999:
                self.cell[i] = BLOCKED
        self.update_zobrist()

    def set_cell(self, cell):
        self.create_board(coord1=(0, 0), height=len(cell))
        for row in range(len(cell)):
            for col in range(len(cell[row])):
                self.cell[row * len(cell) + col] = cell[row][col]
                if self.cell[row * len(cell) + col] == PLAYER1:
                    self.players[PLAYER1].row, self.players[PLAYER1].col = row, col
                elif self.cell[row * len(cell) + col] == PLAYER2:
                    self.players[PLAYER2].row, self.players[PLAYER2].col = row, col
        self.width = len(cell)
        self.height = len(cell[0])
        self.initialized = True

    def get_adjacent_with_players(self, row, col, player_id):
        result = []
        for (o_row, o_col), _ in DIRS:
            t_row, t_col = o_row + row, o_col + col
            if self.is_legal_with_players(t_row, t_col, player_id):
                result.append((t_row, t_col))
        return result

    def a_star_player_to_enemy(self, player_id, prevent_passing=None):
        return self.a_star(self.players[player_id].coord, self.players[player_id ^ 1].coord, player_id,
                           prevent_passing)

    def a_star(self, start, goal, player_id=0, prevent_passing=None):
        if prevent_passing is None:
            prevent_passing = defaultdict(set)
        # if self.cache_distance:
        #     field_hash = hash(str([start, goal, player_id, prevent_passing] + self.cell))
        #     if field_hash in self.distance_cache:
        #         return self.distance_cache[field_hash]
        closed_set = set()
        open_set = {start}
        open_heap = []
        heappush(open_heap, (0, start))

        came_from = {}
        g_score = defaultdict(lambda: float("inf"))
        f_score = defaultdict(lambda: float("inf"))
        g_score[start] = 0
        f_score[start] = self.get_manhattan_distance(start, goal)

        while open_set:
            current = heappop(open_heap)[1]
            # current = sorted(open_set, key=lambda x: f_score[x])[0]
            if current == goal:
                final_path = self.reconstruct_path(came_from, current)
                # if self.cache_distance:
                #     self.distance_cache[field_hash] = final_path
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
        # if self.cache_distance:
        #     self.distance_cache[field_hash] = None
        return None

    @staticmethod
    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)
        return list(reversed(total_path[:-1]))

    def dijkstra_without_deadends(self, start):
        """Returns a map of nodes to distance from start and a map of nodes to
        the neighbouring node that is closest to start."""
        tdist = [999] * 256
        tdist[start[0] * 16 + start[1]] = 0
        unvisited = deque()
        visited = {start}
        unvisited.append((0, start))
        # heappush(unvisited, (0, start))

        while unvisited:
            dist_min_node, min_node = unvisited.popleft()

            d = dist_min_node + 1
            neighbours = self.adjacents[min_node[0] * 16 + min_node[1]]
            if len(neighbours) == 2:
                if self.get_euclidian_distance_square(*neighbours) == 4:
                    continue
            for neighbour in neighbours:
                if neighbour not in visited:
                    # if tdist[neighbour] > d:
                    # unvisited.push(d, neighbour)
                    unvisited.append((d, neighbour))
                    # heappush(unvisited, (d, neighbour))
                    tdist[neighbour[0] * 16 + neighbour[1]] = d
                    visited.add(neighbour)
        return tdist

    def init_zobrist(self):
        # fill a table of random numbers/bitstrings
        Board.hashtable = []
        for i in range(256):  # loop over the board, represented as a linear array
            current_hashes = []
            for j in range(4):  # loop over the pieces
                current_hashes.append(random.randint(0, 2 ** 31))
            Board.hashtable.append(current_hashes)
        self.update_zobrist()

    def update_zobrist(self):
        h = 0
        for i in range(256):  # loop over the board positions
            # if self.cell[i] != EMPTY:
            j = self.cell[i]
            h ^= Board.hashtable[i][j]
        self.hash = h

    @property
    def next_legal_player(self):
        return self.legal_player if self._players_separated else self.legal_player ^ 1

    def __hash__(self):
        return self.hash

    def in_bounds(self, row, col):
        return 0 <= row < 16 and 0 <= col < 16

    def is_legal(self, row, col):
        return 0 <= row < 16 and 0 <= col < 16 and self.cell[row * 16 + col] == EMPTY

    def is_legal_with_players(self, row, col, player_id):
        return (self.in_bounds(row, col)) and (self.cell[row * self.height + col] == EMPTY or
                                               self.cell[row * self.height + col] == PLAYER1 or
                                               self.cell[row * self.height + col] == PLAYER2 or
                                               self.cell[row * self.height + col] == 4 + player_id)

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
        p1_coord = self.players[0].coord
        p2_coord = self.players[1].coord
        dijkstra1 = self.dijkstra(p1_coord)
        distance = 998
        for adjacent in self.adjacents[p2_coord[0] * 16 + p2_coord[1]]:
            distance = min(distance, dijkstra1[adjacent[0] * 16 + adjacent[1]])
        distance += 1

        return distance

    @property
    def players_separated(self):
        # return False
        if not self._players_separated:
            self._players_separated = self.get_player_true_distance() > 900
            if self._players_separated:
                sys.stderr.write('Players separated\n')
                self.block_unreachable()
                self.reset_caches()
        return self._players_separated

    @staticmethod
    def get_coord_of_direction(coord, move):
        for (o_row, o_col), direction in DIRS:
            if direction == move:
                return o_row + coord[0], o_col + coord[1]
        return None

    @staticmethod
    def parse_cell_char(players, row, col, char, mybotid):
        result = -1
        if char == S_PLAYER1:
            if mybotid == 0:
                players[0].row = row
                players[0].col = col
                return 0
            else:
                players[1].row = row
                players[1].col = col
                return 1
        elif char == S_PLAYER2:
            if mybotid == 0:
                players[1].row = row
                players[1].col = col
                return 1
            else:
                players[0].row = row
                players[0].col = col
                return 0
        for (i, symbol) in CHARTABLE:
            if symbol == char:
                result = i
                break
        return result

    def parse_cell(self, players, row, col, data, mybotid):
        item = self.parse_cell_char(players, row, col, data, mybotid)
        return item

    def parse(self, players, data, mybotid):
        cells = data.split(',')
        col = 0
        row = 0
        for cell in cells:
            if col >= self.width:
                col = 0
                row += 1
            self.cell[row * 16 + col] = self.parse_cell(players, row, col, cell, mybotid)
            col += 1

    def total_area(self, coord, player_id=0):
        # if self.cache_area:
        #     field_hash = hash(str([coord] + self.cell))
        #     if field_hash in self.area_cache[player_id]:
        #         return self.area_cache[player_id][field_hash]

        childs = self.adjacents[coord[0] * 16 + coord[1]]
        best_area = 0
        for child in childs:
            area = set()
            queue = set()
            queue.add(child)
            while queue:
                current = queue.pop()
                area.add(current)
                current_adjacent = self.adjacents[current[0] * 16 + current[1]]
                for adjacent in current_adjacent:
                    if adjacent not in area and adjacent not in queue:
                        queue.add(adjacent)
            best_area = max(best_area, len(area))
        # if self.cache_area:
        #     self.area_cache[player_id][field_hash] = best_area
        return best_area

    def total_area_fast(self, coord, player_id=0):
        # field_hash = None
        # if self.cache_fast_area:
        #     field_hash = hash(str([coord] + self.cell))
        #     if field_hash in self.fast_area_cache[player_id]:
        #         return self.fast_area_cache[player_id][field_hash]
        area = set()
        queue = set()
        queue.add(coord)
        while queue:
            current = queue.pop()
            area.add(current)
            current_adjacent = self.adjacents[current[0] * 16 + current[1]]
            for adjacent in current_adjacent:
                if adjacent not in area and adjacent not in queue:
                    queue.add(adjacent)
        # if self.cache_fast_area:
        #     self.fast_area_cache[player_id][field_hash] = area
        return area
