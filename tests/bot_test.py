import unittest

import sys
import io

from Bot.bot import Bot
from Bot.game import Game


class TestBot(unittest.TestCase):
    def setUp(self):
        self.bot = Bot()
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

    def test_turn_to_larger_area(self):
        field_message = 'update game field .,0,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,x,x,1,x,.,x,x,x,x,x,.,x,x,x,x,.,.,x,x,.,.,x,x,x,x,x,.,x,x,x,x,.,.,.,x,x,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,x,x,.,.,.,.,.,x,x,x,x,x,.,.,.,.,.,x,x,.,.,.,.,x,x,x,x,x,.,.,.,.,.,.,x,x,x,x,.,x,x,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.'
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'left')

    def test_mate(self):
        field_message = 'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,x,x,x,x,x,x,x,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,x,x,x,.,.,.,.,.,.,.,.,.,.,.,.,.,0,1,x,.,.,.,.,.,.,.'
        self.game.update(field_message)
        self.bot.do_turn()
        self.assertEqual(self.game.last_order, 'left')

    def test_mate2(self):
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
        self.assertEqual(area, 1)

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


if __name__ == '__main__':
    unittest.main()
