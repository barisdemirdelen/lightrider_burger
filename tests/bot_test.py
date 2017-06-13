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


if __name__ == '__main__':
    unittest.main()
