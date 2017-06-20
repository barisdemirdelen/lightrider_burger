import unittest

from bot.board import Board


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_board_1(self):
        self.board.set_cell([
            [0, 2, 3, 2, 2],
            [2, 2, 3, 2, 2],
            [2, 2, 3, 3, 2],
            [2, 2, 3, 1, 2],
            [2, 2, 2, 2, 2]
        ])

        self.assertEqual(self.board.get_manhattan_distance((0, 0), (3, 3)), 6)
        self.assertEqual(self.board.get_player_manhattan_distance(), 6)
        self.assertEqual(self.board.get_euclidian_distance_square((0, 0), (3, 3)), 18)
        self.assertEqual(self.board.get_player_euclidian_distance_square(), 18)
        self.assertEqual(self.board.get_player_true_distance(), 8)
        self.assertEqual(self.board.legal_moves(0), [((0, 1), 'right'), ((1, 0), 'down')])
        self.assertEqual(self.board.legal_moves(1), [((3, 4), 'right'), ((4, 3), 'down')])
        self.assertEqual(self.board.total_area((0, 0), 0), 18)
        self.assertEqual(self.board.total_area((3, 3), 0), 18)

        blocked1, blocked2 = self.board.block_middle_score()
        real_blocked = [
            [0, 2, 3, 2, 2],
            [2, 2, 3, 2, 2],
            [2, 2, 3, 3, 2],
            [2, 3, 3, 1, 2],
            [3, 2, 2, 2, 2]
        ]
        self.assertEqual(blocked1, 6)
        self.assertEqual(blocked2, 10)


    def test_board_2(self):
        self.board.set_cell([
            [1, 2, 3, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 3, 2, 2],
            [2, 2, 3, 3, 0],
            [2, 2, 2, 2, 2]
        ])

        self.assertEqual(self.board.get_manhattan_distance((0, 0), (3, 4)), 7)
        self.assertEqual(self.board.get_player_manhattan_distance(), 7)
        self.assertEqual(self.board.get_euclidian_distance_square((0, 0), (3, 4)), 25)
        self.assertEqual(self.board.get_player_euclidian_distance_square(), 25)
        self.assertEqual(self.board.get_player_true_distance(), 7)
        self.assertEqual(self.board.legal_moves(0), [((2, 4), 'up'), ((4, 4), 'down')])
        self.assertEqual(self.board.legal_moves(1), [((0, 1), 'right'), ((1, 0), 'down')])
        self.assertEqual(self.board.total_area((3, 4), 0), 19)
        self.assertEqual(self.board.total_area((0, 0), 1), 19)

        blocked1, blocked2 = self.board.block_middle_score()
        real_blocked = [
            [1, 2, 3, 2, 2],
            [2, 2, 5, 4, 2],
            [2, 2, 3, 2, 2],
            [2, 5, 3, 3, 0],
            [5, 4, 2, 2, 2]
        ]
        self.assertEqual(blocked1, 10)
        self.assertEqual(blocked2, 9)

    def test_board_3(self):
        self.board.set_cell([
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [3, 0, 1, 3, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2]
        ])

        player0 = self.board.players[0].coord
        player1 = self.board.players[1].coord

        self.assertEqual(self.board.get_manhattan_distance(player0, player1), 1)
        self.assertEqual(self.board.get_player_manhattan_distance(), 1)
        self.assertEqual(self.board.get_euclidian_distance_square(player0, player1), 1)
        self.assertEqual(self.board.get_player_euclidian_distance_square(), 1)
        self.assertEqual(self.board.get_player_true_distance(), 1)
        self.assertEqual(self.board.legal_moves(0), [((1, 1), 'up'), ((3, 1), 'down')])
        self.assertEqual(self.board.legal_moves(1), [((1, 2), 'up'), ((3, 2), 'down')])
        self.assertEqual(self.board.total_area(player0, 0), 21)
        self.assertEqual(self.board.total_area(player1, 1), 21)

        blocked1, blocked2 = self.board.block_middle_score()
        real_blocked = [
            [2, 4, 5, 2, 2],
            [2, 4, 5, 2, 2],
            [3, 0, 1, 3, 2],
            [2, 4, 5, 2, 2],
            [2, 4, 5, 2, 2]
        ]
        self.assertEqual(blocked1, 8)
        self.assertEqual(blocked2, 13)
