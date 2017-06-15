#!/usr/bin/python
# Ported from the hackman python2 starter package 

import sys
import time
import traceback

from bot.board import Board
from . import board
from . import player


class Game(object):
    def __init__(self):
        self.initial_timebank = 10000
        self.time_per_move = 200
        self.player_names = []
        self.my_bot = 'not set'
        self.my_botid = -1
        self.other_botid = -1

        self.field = Board()
        self.last_order = None
        self.last_update = 0
        self.last_timebank = 0
        self.rounds_left = 0

    def my_player(self):
        return self.field.players[self.my_botid]

    def other_player(self):
        return self.field.players[self.other_botid]

    def get_available_time_per_turn(self):
        available_time = self.time_per_move + self.last_timebank / self.rounds_left
        return available_time / 1000
        # return 100000000

    def update(self, data):
        """parse input"""
        # start timer
        self.last_update = time.time()
        for line in data.split('\n'):
            line = line.strip()
            if len(line) > 0:
                tokens = line.split()
                key0 = tokens[0]
                if key0 == 'settings':
                    key1 = tokens[1]
                    if key1 == 'timebank':
                        self.timebank = int(tokens[2])
                    if key1 == 'time_per_move':
                        self.time_per_move = int(tokens[2])
                    if key1 == 'player_names':
                        self.player_names = tokens[2].split(',')
                    if key1 == 'your_bot':
                        self.my_bot = tokens[2]
                    if key1 == 'your_botid':
                        self.my_botid = int(tokens[2])
                        self.other_botid = 1 - self.my_botid
                    if key1 == 'field_width':
                        self.field.width = int(tokens[2])
                    if key1 == 'field_height':
                        self.field.height = int(tokens[2])
                elif key0 == 'update':
                    key1 = tokens[1]
                    if key1 == 'game':
                        key2 = tokens[2]
                        if key2 == 'round':
                            self.field.round = int(tokens[3])
                        elif key2 == 'field':
                            if not self.field.initialized:
                                self.field.create_board()
                            self.field.parse(self.field.players, tokens[3])
                elif key0 == 'action' and tokens[1] == 'move':
                    self.last_timebank = int(tokens[2])
                    # Launching bot logic happens after setup finishes
                elif key0 == 'quit':
                    pass

    def time_remaining(self):
        return self.last_timebank - int(1000 * (time.clock() - self.last_update))

    def issue_order(self, order):
        """issue an order, noting that (col, row) is the expected output
        however internally, (row, col) is used."""
        self.last_order = order
        # sys.stdout.write('%s\n' % order)
        # sys.stdout.flush()

    @staticmethod
    def issue_order_pass():
        """ pass the turn """
        sys.stdout.write('pass\n')
        sys.stdout.flush()

    def run(self, bot):
        """parse input, update game state and call the bot classes do_turn method"""
        not_finished = True
        data = ''
        while not_finished:
            try:
                current_line = sys.stdin.readline().rstrip('\r\n')
                data += current_line + '\n'
                if current_line.lower().startswith('action move'):
                    self.update(data)
                    if bot.game is None:
                        bot.setup(self)
                    bot.do_turn()
                    data = ''
                elif current_line.lower().startswith('quit'):
                    not_finished = False
            except EOFError:
                break
            except KeyboardInterrupt:
                raise
            except:
                # don't raise error or return so that bot attempts to stay alive
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()
