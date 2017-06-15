import unittest

from bot.board import Board


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
