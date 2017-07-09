import random

import math
import operator
from collections import defaultdict

import itertools


class Node(object):
    def __init__(self, field, player_id):
        self.score = 0
        self.visits = 1
        self.state = field
        self.children = []
        self.action = None
        self.possible_next_actions = []
        self.C = 0.5
        self.heuiristic_factor = 0.0
        self._heuristic_value = None
        self.player_id = player_id

    def select_new_action(self):
        candidates = self.possible_next_actions.copy()
        for child in self.children:
            candidates.remove(child.action)
        return random.choice(candidates)

    def get_uct_action(self, actions):
        best_action = None
        best_confidence = -float('inf') if self.player_id == 0 else float('inf')
        if self.player_id == 0:
            for action in actions:
                score = action[1] + self.C * (2.0 * math.log(self.visits) / action[2]) ** 0.5
                if score > best_confidence:
                    best_confidence = score
                    best_action = action
        else:
            for action in actions:
                score = action[1] - self.C * (2.0 * math.log(self.visits) / action[2]) ** 0.5
                if score < best_confidence:
                    best_confidence = score
                    best_action = action
        return best_action

    def select_child(self):

        if len(self.children) == 1:
            return self.children[0]

        p1_actions = self.get_action_scores()
        p1_action = self.get_uct_action(p1_actions)
        for child in self.children:
            if child.action == p1_action[0]:
                return child
        # new_node = self.create_node(self.state, joint_action)
        # self.children.append(new_node)
        return None

    def get_action_scores(self):
        child_len = len(self.children)
        scores = [None] * child_len
        for i, child in enumerate(self.children):
            visits = child.visits
            scores[i] = (child.action, child.score / visits, visits)

        return scores

    def update(self, action, u1):
        self.score += u1
        self.visits += 1

    def get_best_action(self):
        action_scores = self.get_action_scores()
        best_action = None
        best_score = -float('inf') if self.player_id == 0 else float('inf')
        for action, score, _ in action_scores:
            if self.player_id == 0:
                if best_score < score:
                    best_score = score
                    best_action = action
            else:
                if best_score > score:
                    best_score = score
                    best_action = action
        return best_action, best_score

    @staticmethod
    def create_node(field, action):
        node = Node(field, field.legal_player)
        node.possible_next_actions = field.legal_moves
        node.action = action

        return node