import random
import sys
import time

from bot.board import BLOCKED
from bot.bot_heuristic import BotHeuristic
from bot.fake_engine import FakeEngine
from bot.node import Node

start_time = 0


class BotMCTS(object):
    def __init__(self):
        self.game = None
        self.current_node = None
        self.bot1 = BotHeuristic()
        self.bot2 = BotHeuristic()
        self.engine = FakeEngine(self.bot1, self.bot2)

    def setup(self, game):
        self.game = game

    def give_reward(self, reward):
        pass

    def do_turn(self):
        global start_time
        global cached
        self.game.last_order = None
        cached = 0
        score = None
        start_time = time.time()
        self.game.rounds_left = 0.5 * self.game.field.height * self.game.field.width - self.game.field.round
        legal = self.game.field.legal_moves(self.game.my_botid)
        if len(legal) == 0:
            self.game.issue_order_pass()
        # elif len(legal) == 1:
        #     self.game.issue_order(legal[0][1])
        else:
            if self.current_node is None:
                self.current_node = Node.create_node(self.game.field.get_copy(), None, self.game.my_botid)
            else:
                for child in self.current_node.children:
                    if self.game.field.players[self.game.my_botid].coord == child.state.players[
                        self.game.my_botid].coord:
                        for grandchild in child.children:
                            child_field = grandchild.state
                            if self.game.field.players[self.game.my_botid ^ 1].coord == child_field.players[
                                        self.game.my_botid ^ 1].coord:
                                self.current_node = grandchild
                                break
                        break
                else:
                    sys.stderr.write('This wasnt in our plans\n')
                    self.current_node = Node.create_node(self.game.field.get_copy(), None, self.game.my_botid)
            while True:
                current_time = time.time()
                available_time = self.game.get_available_time_per_turn()
                if current_time - start_time > available_time:
                    break
                u1 = self.sm_mcts(self.current_node)
                self.current_node.score += u1
                self.current_node.visits += 1
            # self.current_node.select_child()
            best_action, score = self.current_node.get_best_action()
            if best_action is not None:
                self.game.issue_order(best_action[1])
            else:
                (_, chosen) = random.choice(legal)
                self.game.issue_order(chosen)

            elapsed = time.time() - start_time
            sys.stderr.write(
                'Round: %d, Score: %.4f, Simulations: %d, Time: %d, RoundsLeft: %d\n' % (
                    self.game.field.round, score, self.current_node.visits,
                    self.game.last_timebank - elapsed * 1000, self.game.rounds_left))
            sys.stderr.flush()
        return score

    def sm_mcts(self, s):
        field = s.state
        A = field.legal_moves(s.player_id)
        if len(A) == 0:
            if s.player_id == 0:
                return -1
            else:
                return 1

        if len(s.children) < len(s.possible_next_actions):
            action = s.select_new_action()
            new_field = self.make_move(field, action, s.player_id)
            new_s = Node.create_node(new_field, action, s.player_id ^ 1)
            s.children.append(new_s)
            u1 = self.playout(new_s)
            # u1 = self.value_factor * v + (1 - self.value_factor) * z
            new_s.update(action, u1)
            return u1
        new_s = s.select_child()
        u1 = self.sm_mcts(new_s)
        new_s.update(new_s.action, u1)
        return u1

    def make_move(self, field, action, player_id):
        new_field = field.get_copy()
        new_field.cell[action[0][0] * new_field.height + action[0][1]] = 0
        # new_field.cell[action[1][0][0]][action[1][0][1]] = 1
        new_field.cell[new_field.players[player_id].row * new_field.height + new_field.players[player_id].col] = BLOCKED
        # new_field.cell[new_field.players[1].row][new_field.players[1].col] = BLOCKED
        new_field.players[player_id].row, new_field.players[player_id].col = action[0]
        # new_field.players[1].row, new_field.players[1].col = action[1][0]
        new_field.round += 1
        return new_field

    def playout(self, s):
        field = s.state
        self.engine.reset(field.get_copy())
        # self.engine.field = field.get_copy()
        # self.bot1.game.field = field.get_copy()
        # self.bot2.game.field = field.get_copy()

        # d_star = DStarLite(field, (0,0), (5,5))
        # d_star.run()
        finished = False
        if s.player_id == self.game.my_botid:
            finished = self.engine.free_turn(s.player_id ^ 1)

        if not finished:
            self.engine.run()

        return self.bot1.reward
