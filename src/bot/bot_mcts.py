import random
import sys
import time

from bot.bot_random import BotRandom
from bot.fake_engine import FakeEngine
from bot.node import Node
from bot.parameters import Parameters

start_time = 0


class BotMCTS(object):
    def __init__(self):
        self.game = None
        self.current_node = None
        self.bot1 = BotRandom(0)
        self.bot2 = BotRandom(1)
        self.engine = None
        self.parameters = Parameters()
        self.first_turn = True

    def setup(self, game):
        self.game = game

    def give_reward(self, reward):
        pass

    def do_turn(self):
        global start_time

        if self.first_turn:
            self.game.field.cache_adjacent_initial()
            self.engine = FakeEngine(self.bot1, self.bot2, self.game.field)
        self.first_turn = False
        self.game.field.legal_player = 0

        self.game.last_order = None
        score = None
        start_time = time.time()
        self.game.rounds_left = 0.5 * self.game.field.height * self.game.field.width - self.game.field.round
        legal = self.game.field.legal_moves
        if len(legal) == 0:
            self.game.issue_order_pass()
        else:
            if self.current_node is None:
                self.current_node = Node.create_node(self.game.field.copy(), None)
            else:
                for child in self.current_node.children:
                    if self.game.field.players[0].coord == child.state.players[0].coord:
                        for grandchild in child.children:
                            child_field = grandchild.state
                            if self.game.field.players[1].coord == child_field.players[1].coord:
                                self.current_node = grandchild
                                self.game.field = self.current_node.state
                                break
                        break
                else:
                    sys.stderr.write('This wasnt in our plans\n')
                    self.current_node = Node.create_node(self.game.field.copy(), None)
            while True:
                current_time = time.time()
                available_time = self.game.get_available_time_per_turn(self.parameters.available_time_factor)
                if current_time - start_time > available_time:
                    break
                u1 = self.sm_mcts(self.current_node)
                self.current_node.score += u1
                self.current_node.visits += 1
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
        A = field.legal_moves
        if not A:
            return -1 if s.player_id == 0 else 1

        if len(s.children) < len(s.possible_next_actions):
            action = s.select_new_action()
            new_field = field.copy()
            new_field.move(action[0])
            new_s = Node.create_node(new_field, action)
            s.children.append(new_s)
            u1 = self.playout(new_s)
            # u1 = self.value_factor * v + (1 - self.value_factor) * z
            new_s.update(action, u1)
            return u1
        new_s = s.select_child()
        u1 = self.sm_mcts(new_s)
        new_s.update(new_s.action, u1)
        return u1

    def playout(self, s):
        # s.state.cache_adjacent_initial()
        self.engine.reset(field=s.state)
        finished = False
        if s.player_id == 1:
            finished = self.engine.free_turn(s.player_id)

        if not finished:
            self.engine.run()

        return self.bot1.reward
