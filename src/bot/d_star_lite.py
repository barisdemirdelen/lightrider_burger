from collections import defaultdict
from heapq import heappush, heapify, heapreplace, heappop


class DStarLite(object):
    def __init__(self, field, s_start, s_goal):
        self.U = []
        self.k_m = 0
        self.s_start = s_start
        self.s_goal = s_goal
        self.rhs = defaultdict(lambda: float('inf'))
        self.g = defaultdict(lambda: float('inf'))
        self.rhs[s_goal] = 0
        self.g[s_goal] = 0
        self.field = field
        heappush(self.U, (self.calculate_key(s_goal), s_goal))

    def h(self, s1, s2):
        return self.field.get_manhattan_distance(s1, s2)

    def calculate_key(self, s):
        min_g_rhs = min(self.g[s], self.rhs[s])
        key = min(min_g_rhs + self.h(self.s_start, s) + self.k_m, min_g_rhs)
        return key

    def initialize(self):
        pass

    def update_vertex(self, u):
        index = -1
        for i, member in enumerate(self.U):
            if member[1] == u:
                index = i
                break

        if self.g[u] != self.rhs[u] and index >= 0:
            del self.U[index]
            self.U.append((self.calculate_key(u), u))
            heapify(self.U)
        elif self.g[u] != self.rhs[u] and index < 0:
            heappush(self.U, (self.calculate_key(u), u))
        elif self.g[u] == self.rhs[u] and index >= 0:
            del self.U[index]
            heapify(self.U)

    def compute_shortest_path(self):
        while self.U[0][0] < self.calculate_key(self.s_start) or self.rhs[self.s_start] > self.g[self.s_start]:
            u = self.U[0][1]
            k_old = self.U[0][0]
            k_new = self.calculate_key(u)
            if k_old < k_new:
                heapreplace(self.U, (k_new, u))
            elif self.g[u] > self.rhs[u]:
                self.g[u] = self.rhs[u]
                heappop(self.U)
                for s in self.field.get_adjacent(*u):
                    if s != self.s_goal:
                        self.rhs[s] = min(self.rhs[s], self.g[u] + 1)
                    self.update_vertex(s)
            else:
                g_old = self.g[u]
                self.g[u] = float('inf')
                for s in self.field.get_adjacent(*u) + [u]:
                    if self.rhs[s] == g_old + 1:
                        if s != self.s_goal:
                            self.rhs[s] = min(0, 0)  # TODO what
                    self.update_vertex(s)
        print('hello')

    def run(self):
        s_last = self.s_start
        self.initialize()
        self.compute_shortest_path()

