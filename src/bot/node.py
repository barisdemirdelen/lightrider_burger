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
        self.heuiristic_factor = 0.2
        self._heuristic_value = None
        self.player_id = player_id

    def select_new_action(self):
        candidates = self.possible_next_actions[:]
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

        p1_actions, p1_visits = self.get_action_scores()
        p1_actions = [(k, v, p1_visits[k]) for k, v in p1_actions.items()]

        p1_action = self.get_uct_action(p1_actions)
        for child in self.children:
            if child.action == p1_action[0]:
                return child
        # new_node = self.create_node(self.state, joint_action)
        # self.children.append(new_node)
        return None

    def get_action_scores(self):
        action_scores = {}
        action_visits = {}
        # action_mean_scores = {}
        # action_sum_visits = {}

        for child in self.children:
            my_action = child.action
            current_score = 1.0 * child.score
            value = child.heuristic_value
            score = (1 - self.heuiristic_factor) * current_score + self.heuiristic_factor * value * child.visits
            action_scores[my_action] = score / child.visits
            action_visits[my_action] = child.visits
        # for action in action_scores.keys():
        #     action_sum_visit = sum(action_visits[action])
        #     action_mean_scores[action] = 1.0 * sum(action_scores[action]) / action_sum_visit
        #     action_sum_visits[action] = action_sum_visit

        return action_scores, action_visits

    # def get_pessimistic_action_scores(self, player_id):
    #     action_scores = defaultdict(list)
    #     # action_visits = defaultdict(list)
    #     action_pessimistic_scores = {}
    #
    #     for child in self.children:
    #         my_action = child.action[player_id]
    #         current_score = 1.0 * child.score / child.visits
    #         value = child.heuristic_value
    #         score = (1 - self.heuiristic_factor) * current_score + self.heuiristic_factor * value
    #         action_scores[my_action].append(score)
    #         # action_visits[my_action].append(child.visits)
    #     for action in action_scores.keys():
    #         if player_id == 0:
    #             action_pessimistic_scores[action] = 1.0 * min(action_scores[action])
    #         else:
    #             action_pessimistic_scores[action] = 1.0 * max(action_scores[action])
    #
    #     return action_pessimistic_scores

    def update(self, action, u1):
        self.score += u1
        self.visits += 1

    def get_best_action(self):
        action_scores, _ = self.get_action_scores()
        best_action = None
        best_score = -float('inf') if self.player_id == 0 else float('inf')
        for action, score in action_scores.items():
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
    def create_node(field, action, player_id):
        node = Node(field, player_id)
        node.possible_next_actions = field.legal_moves(player_id)
        node.action = action

        return node

    def middle_block_area_heuristic(self):
        field = self.state
        p1_coord = field.players[0].coord
        p2_coord = field.players[1].coord

        my_score, enemy_score = field.block_middle_score()
        score = my_score / (128 - field.round) - enemy_score / (128 - field.round)
        return score

    def fast_area_heuristic(self):
        field = self.state
        p1_coord = field.players[0].coord
        p2_coord = field.players[1].coord

        blocked_field = field.block_middle()
        my_score = blocked_field.total_area(p1_coord, 0)
        enemy_score = blocked_field.total_area(p2_coord, 1)
        score = my_score / (128 - field.round) - enemy_score / (128 - field.round)
        return score

    @property
    def heuristic_value(self):
        if self._heuristic_value is None:
            self._heuristic_value = 0.0
            if self.heuiristic_factor > 0:
                self._heuristic_value = self.middle_block_area_heuristic()
        return self._heuristic_value
