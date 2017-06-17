import random

import math
import operator
from collections import defaultdict

import itertools


class Node(object):
    def __init__(self, field):
        self.score = 0
        self.visits = 1
        self.state = field
        self.children = []
        self.action = None
        self.possible_next_actions = []
        self.C = 1.5

    def select_new_action(self):
        candidates = self.possible_next_actions[:]
        for child in self.children:
            candidates.remove(child.action)
        return random.choice(candidates)

    def select_child(self):

        if len(self.children) == 1:
            return self.children[0]

        p1_actions, p1_visits = self.get_action_scores(0)
        p1_actions = [(k, v, p1_visits[k]) for k, v in p1_actions.items()]

        p1_sorted_actions = sorted(p1_actions,
                                   key=lambda x: x[1] + self.C * (2.0 * math.log(self.visits) / x[2]) ** 0.5)
        p1_action = p1_sorted_actions[-1]

        p2_actions, p2_visits = self.get_action_scores(1)
        p2_actions = [(k, v, p2_visits[k]) for k, v in p2_actions.items()]

        p2_sorted_actions = sorted(p2_actions,
                                   key=lambda x: x[1] - self.C * (2.0 * math.log(self.visits) / x[2]) ** 0.5)
        p2_action = p2_sorted_actions[0]
        joint_action = (p1_action[0], p2_action[0])

        for child in self.children:
            if child.action == joint_action:
                return child
        new_node = self.create_node(self.state, joint_action)
        self.children.append(new_node)
        return new_node

    def get_action_scores(self, player_id):
        action_scores = defaultdict(list)
        action_visits = defaultdict(list)
        action_mean_scores = {}
        action_sum_visits = {}

        for child in self.children:
            my_action = child.action[player_id]
            action_scores[my_action].append(child.score)
            action_visits[my_action].append(child.visits)
        for action in action_scores.keys():
            action_sum_visit = sum(action_visits[action])
            action_mean_scores[action] = 1.0 * sum(action_scores[action]) / action_sum_visit
            action_sum_visits[action] = action_sum_visit

        return action_mean_scores, action_sum_visits

    def get_pessimistic_action_scores(self, player_id):
        action_scores = defaultdict(list)
        action_visits = defaultdict(list)
        action_pessimistic_scores = {}

        for child in self.children:
            my_action = child.action[player_id]
            action_scores[my_action].append(child.score / child.visits)
            # action_visits[my_action].append(child.visits)
        for action in action_scores.keys():
            if player_id == 0:
                action_pessimistic_scores[action] = 1.0 * min(action_scores[action])
            else:
                action_pessimistic_scores[action] = 1.0 * max(action_scores[action])

        return action_pessimistic_scores

    def update(self, action, u1):
        self.score += u1
        self.visits += 1

    def get_best_action(self, player_id):
        action_scores = self.get_pessimistic_action_scores(player_id)
        best_action = None
        best_score = -float('inf') if player_id == 0 else float('inf')
        for action, score in action_scores.items():
            if player_id == 0:
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
        node = Node(field)

        A = field.legal_moves(0)
        B = field.legal_moves(1)

        joint = list(itertools.product(A, B))
        node.possible_next_actions = joint
        node.action = action

        return node
