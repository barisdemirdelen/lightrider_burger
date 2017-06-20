import unittest

from bot.board import Board
from bot.bot_minimax import BotMinimax
from bot.game import Game


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.bot = BotMinimax()
        self.game.silent = True
        initial_message = 'settings your_botid 0\n' \
                          'settings field_width 16\n' \
                          'settings field_height 16\n' \
                          'update game round 0\n' \
                          'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                          'action move 10000'

        self.game.update(initial_message)
        self.bot.setup(self.game)
        self.field = self.game.field

    def test_sort_moves_1(self):
        child_fields, directions = self.bot.get_child_fields(self.field, 0)
        child_fields, directions = self.bot.sort_moves(child_fields, directions, 0,
                                                       calculate_distance=True, priority=None, only_me=False)
        self.assertEqual(directions[0], 'right')

    def test_sort_moves_2(self):
        child_fields, directions = self.bot.get_child_fields(self.field, 0)
        child_fields, directions = self.bot.get_child_fields(child_fields[0], 1)
        child_fields, directions = self.bot.sort_moves(child_fields, directions, 1,
                                                       calculate_distance=True, priority=None, only_me=False)
        self.assertEqual(directions[0], 'left')

    def test_sort_moves_3(self):
        child_fields, directions = self.bot.get_child_fields(self.field, 0)
        child_fields, directions = self.bot.sort_moves(child_fields, directions, 0,
                                                       calculate_distance=True, priority='right', only_me=False)
        self.assertEqual(directions[0], 'right')

    def test_sort_moves_4(self):
        child_fields, directions = self.bot.get_child_fields(self.field, 0)
        child_fields, directions = self.bot.get_child_fields(child_fields[0], 1)
        child_fields, directions = self.bot.sort_moves(child_fields, directions, 1,
                                                       calculate_distance=True, priority='left', only_me=False)
        self.assertEqual(directions[0], 'left')
