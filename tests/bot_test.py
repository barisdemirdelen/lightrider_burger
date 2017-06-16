import unittest

import sys
import io

import time

from bot.bot_minimax import Bot
from bot.bot_nn import BotNN
from bot.game import Game


class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = BotNN()
        self.game = Game()
        initial_message = 'settings your_botid 0\n' \
                          'settings field_width 16\n' \
                          'settings field_height 16\n' \
                          'update game round 0\n' \
                          'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                          'action move 10000'

        self.game.update(initial_message)
        self.bot.setup(self.game)

    def tearDown(self):
        pass

    def test_turning_1(self):
        field_message = 'update game field .,0,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,x,x,1,x,.,x,x,x,x,x,.,x,x,x,x,.,.,x,x,.,.,x,x,x,x,x,.,x,x,x,x,.,.,.,x,x,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,x,x,.,.,.,.,.,x,x,x,x,x,.,.,.,.,.,x,x,.,.,.,.,x,x,x,x,x,.,.,.,.,.,.,x,x,x,x,.,x,x,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.'
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'left')

    def test_mate(self):
        field_message = 'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,0,1,x,.,.,.,.,.,.,.'
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'left')

    def test_mate_2(self):
        initial_message = 'settings your_botid 1\n' \
                          'settings field_width 16\n' \
                          'settings field_height 16\n' \
                          'update game round 13\n' \
                          'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                          'action move 10000'
        field_message = 'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,0,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.'
        self.game.update(initial_message)
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'right')

    def test_total_area_1(self):
        field_message = 'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,' \
                        '.,.,.,.,.,.,x,x,x,.,.,.,.,.,.,.,' \
                        '.,.,.,.,.,.,0,1,x,.,.,.,.,.,.,.'
        self.game.update(field_message)
        area = self.game.field.total_area((15, 7))
        self.assertEqual(area, 0)

    def test_mate_along_wall(self):
        """ https://starapple.riddles.io/competitions/light-riders/matches/8be094a2-e0ff-4322-b064-1345a7546423 """
        initial_message = 'settings your_botid 1\n' \
                          'settings field_width 16\n' \
                          'settings field_height 16\n' \
                          'update game round 11\n' \
                          'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                          'action move 10000'
        field_message = 'update game field .,.,.,.,.,.,x,x,x,0,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,1,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.'
        self.game.update(initial_message)
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'right')

    def test_mate_in_5(self):
        """https://starapple.riddles.io/competitions/light-riders/matches/f5e9f509-1dfa-4f8f-a819-6fd95cfcc331"""
        initial_message = 'settings your_botid 1\n' \
                          'settings field_width 16\n' \
                          'settings field_height 16\n' \
                          'update game round 11\n' \
                          'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                          'action move 10000'
        field_message = 'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,x,x,x,x,x,x,x,.,x,x,x,x,.,.,.,.,x,x,x,x,x,x,.,.,x,.,.,.,.,.,.,.,.,.,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,x,x,.,.,x,x,x,.,.,.,.,.,.,.,.,.,x,x,.,.,x,.,.,.,.,.,.,.,.,.,.,.,0,.,.,1,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.'
        self.game.update(initial_message)
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertNotEqual(self.game.last_order, 'up')

    def test_mate_in_2(self):
        """https://starapple.riddles.io/competitions/light-riders/matches/f5e9f509-1dfa-4f8f-a819-6fd95cfcc331
        round 25"""
        field_message = 'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,.,.,x,x,x,x,x,x,.,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,x,x,0,.,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.'
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertNotEqual(self.game.last_order, 'right')

    def test_mate_in_3(self):
        field_message = 'update game field x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,.,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,1,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,.,x,x,x,x,x,x,x,x,.,.,x,x,x,x,x,0,x,x,x,x,x,x,x,x,.,.,x,x,x,x,x,.,.,.,x,x,x,x,x,x,.,.,x,x,x,x,x,.,.,.,x,x,x,x,x,x,.,.,x,x,x,x,x,x,x,x,x,x,x,x,x,x,.,.,x,x,x,x,x,x,x,x,x,x,x,x,x,x,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,.,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x'
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'down')

    def test_score(self):
        message = 'update game round 32\n' \
                  'update game field .,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,x,.,.,.,.,.,.,.,.,x,.,.,.,.,.,.,x,.,x,x,.,.,.,.,.,x,.,.,.,.,.,.,x,.,x,x,.,.,.,.,.,x,x,x,.,.,.,.,x,.,x,x,.,.,.,.,.,.,.,x,.,.,.,.,x,.,x,x,x,x,.,.,.,.,.,x,.,.,.,.,x,.,x,.,.,x,.,.,.,.,.,x,.,.,.,.,x,.,x,.,.,x,x,x,x,x,.,x,.,.,.,.,.,.,x,x,x,x,x,x,x,x,1,0,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                  'action move 7343\n'
        self.game.update(message)
        score = self.bot.do_turn()
        self.assertLess(score, 0)

    def test_strategical_turning(self):
        message = 'update game field .,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,x,.,.,.,.,x,x,x,x,x,x,x,.,.,x,.,x,.,.,.,.,x,x,x,x,x,x,x,.,.,x,.,x,.,.,.,.,x,x,x,x,x,x,x,x,0,x,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.'
        self.game.update(message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'down')

    def test_turning_2(self):
        message = 'update game round 32\n' \
                  'update game field .,.,.,.,.,x,x,.,.,x,x,.,.,x,x,x,.,.,.,.,x,x,x,x,x,x,x,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,.,x,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,x,.,.,x,x,x,x,x,x,x,x,x,x,x,1,x,x,.,.,x,x,x,.,x,x,x,x,x,x,x,.,x,x,.,.,x,x,x,.,x,x,x,x,x,x,x,.,x,x,.,.,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,x,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,x,.,.,.,x,x,x,x,x,x,x,x,x,x,x,x,x,.,.,.,x,x,x,x,x,x,x,x,x,x,x,x,x,.,x,x,x,x,x,.,.,x,x,x,x,x,x,x,x,.,x,x,x,x,.,.,.,x,x,x,x,x,x,x,x,.,.,.,.,0,.,.,.,x,x,x,x,x,x,x,x\n' \
                  'action move 4437\n'
        self.game.update(message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'left')

    def test_mate_along_wall_2(self):
        message = 'update game round 21\n' \
                  'update game field .,.,.,.,.,.,.,.,.,.,.,.,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,x,.,.,.,.,.,.,.,.,.,x,x,x,x,x,.,x,.,.,.,.,.,.,.,.,.,x,.,.,x,x,.,x,.,.,.,.,.,.,.,.,.,x,.,.,x,x,.,x,.,.,.,.,x,x,x,x,x,x,.,.,x,x,.,x,x,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                  'action move 8381\n'
        self.game.update(message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'down')

    def test_end_game_score(self):
        message = 'update game round 82\n' \
                  'update game field .,.,.,x,x,x,x,.,.,x,x,x,x,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,1,x,.,.,0,x,x,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.\n' \
                  'action move 6427\n'
        self.game.update(message)
        self.bot.do_turn()
        self.assertNotEqual(self.game.last_order, 'left')

    def test_turning_3(self):
        message = 'update game round 15\n' \
                  'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,0,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,x,x,x,.,.,x,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                  'action move 8517\n'
        self.game.update(message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'right')

    def test_strategical_turning_2(self):
        message = 'update game round 11\n' \
                  'update game field .,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,x,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,x,x,x,0,x,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,x,.,.,.,x,.,.,.,.,.,.,x,x,x,x,x,x,.,.,.,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                  'action move 8638\n'
        self.game.update(message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'down')

    def test_strategical_turning_3(self):
        """https://starapple.riddles.io/competitions/light-riders/matches/b2ec40ce-7248-4558-a883-a04a9c017548"""
        message = 'update game round 29\n' \
                  'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,1,x,x,x,x,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,x,x,x,x,x,x,x,.,.,x,x,x,0,.,.,.,x,x,x,x,x,x,x,.,.,x,x,x,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                  'action move 8292\n'
        self.game.update(message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'down')

    def test_strategical_turning_4(self):
        """https://starapple.riddles.io/competitions/light-riders/matches/b2ec40ce-7248-4558-a883-a04a9c017548"""
        message = 'update game round 29\n' \
                  'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,1,x,x,x,x,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,x,x,x,x,x,x,x,.,.,x,x,x,0,.,.,.,x,x,x,x,x,x,x,.,.,x,x,x,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                  'action move 8292\n'
        self.game.update(message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'down')

    def test_time_management(self):
        message = 'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,0,1,x,x,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.'
        self.game.update(message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'down')

    def test_turn1(self):
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'right')

    def input_test(self):
        start_time = time.time()
        initial_message = 'settings player_names player0,player1\n' \
                          'settings your_bot player0\n' \
                          'settings timebank 0\n' \
                          'settings time_per_move 200\n' \
                          'settings your_botid 0\n' \
                          'settings field_width 16\n' \
                          'settings field_height 16\n' \
                          'update game round 0\n' \
                          'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                          'action move 1000\n'
        self.game.update(initial_message)
        self.bot.do_turn()
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.assertLess(elapsed_time, 1)


if __name__ == '__main__':
    unittest.main()
