import random

from bot.board import BLOCKED
from bot.game import Game


class FakeEngine(object):
    def __init__(self, player1, player2, field=None):
        self.game = Game()
        p1_game = Game()
        p2_game = Game()

        self.game.silent = True
        p1_game.silent = True
        p2_game.silent = True

        # initial_message = 'settings player_names player0,player1\n' \
        #                   'settings timebank 1000\n' \
        #                   'settings time_per_move 20\n' \
        #                   'settings field_width 16\n' \
        #                   'settings field_height 16\n' \
        #                   'update game round 0\n' \
        #                   'action move 1000\n'
        if field:
            self.game.field = field
        else:
            self.game.field.width = 16
            self.game.field.height = 16
            self.game.field.round = 0

            coord1 = (random.randint(0, 15), random.randint(0, 15))

            self.game.field.create_board(coord1)

        p1_game.field = self.game.field.get_copy()
        p2_game.field = self.game.field.get_copy()

        # self.game.update(initial_message)
        # p1_game.update(initial_message)
        # p2_game.update(initial_message)
        player1.setup(p1_game)
        player2.setup(p2_game)

        # p1_message = 'settings your_bot player0\n' \
        #              'settings your_botid 0\n'
        # p2_message = 'settings your_bot player1\n' \
        #              'settings your_botid 1\n'

        player1.game.my_botid = 0
        player2.game.my_botid = 1

        player1.game.field.cell = self.game.field.cell
        player2.game.field.cell = self.game.field.cell
        player1.game.field.players = self.game.field.players
        player2.game.field.players = self.game.field.players

        # player1.game.update(p1_message)
        # player2.game.update(p2_message)

        self.field = self.game.field
        self.player1 = player1
        self.player2 = player2
        self.players = [self.player1, self.player2]

    def reset(self, field=None):
        self.__init__(*self.players, field)

    def step(self, move_override=None):
        if move_override is None:
            move_override = [None, None]
        lost = [False, False]
        move_coords = [None, None]
        # self.player1.game.field.cell = self.game.field.cell
        # self.player2.game.field.cell = self.game.field.cell
        # self.player1.game.field.players = self.game.field.players
        # self.player2.game.field.players = self.game.field.players

        for i, player in enumerate(self.players):
            player.game.round = self.field.round
            player.game.field.cell = self.game.field.cell
            player.game.my_botid = i
            player.game.field.players = self.game.field.players
            # player.game.field.cell = [row[:] for row in self.field.cell]
            player.do_turn()
            p_move = player.game.last_order
            if move_override[i] is not None:
                p_move = move_override[i]
            p_move_coord = self.field.get_coord_of_direction(self.field.players[i].coord, p_move)
            move_coords[i] = p_move_coord

            if p_move_coord is None or not self.field.is_legal(p_move_coord[0], p_move_coord[1], 0):
                lost[i] = True

        if move_coords[0] == move_coords[1]:
            lost[0] = True
            lost[1] = True

        if True in lost:
            # area1 = len(self.field.total_area_fast(self.field.players[0].coord, 0))
            # area2 = len(self.field.total_area_fast(self.field.players[1].coord, 1))
            # score = area1/(128 - self.field.round) - area2/(128 - self.field.round)
            if lost[0] and lost[1]:
                self.player2.give_reward(0)
                self.player1.give_reward(0)
            elif lost[0]:
                self.player2.give_reward(1)
                self.player1.give_reward(-1)
            else:
                self.player2.give_reward(-1)
                self.player1.give_reward(1)
            return True

        for i, player_coord in enumerate(self.field.players):
            self.field.cell[player_coord.row * self.field.height + player_coord.col] = BLOCKED
            player_coord.row, player_coord.col = move_coords[i][0], move_coords[i][1]
            self.field.cell[player_coord.row * self.field.height + player_coord.col] = i
            # for player in self.players:
            # player.game.field.cell[player_coord.row][player_coord.col] = BLOCKED
            # player.game.field.players[i].row, player.game.field.players[i].col = move_coords[i][0], move_coords[i][
            #     1]
            # player.game.field.cell[player_coord.row][player_coord.col] = i
        self.field.round += 1
        return False

    def run(self):
        finished = self.step()
        while not finished:
            finished = self.step()
            # if self.field.is_players_separated():
            #     p1_coord = self.field.players[0].coord
            #     p2_coord = self.field.players[1].coord
            #
            #     my_score = len(self.field.total_area_fast(p1_coord, 0))
            #     enemy_score = len(self.field.total_area_fast(p2_coord, 1))
            #     score = 0
            #     if my_score > enemy_score:
            #         score = 1
            #     elif my_score < enemy_score:
            #         score = -1
            #     self.player2.give_reward(score)
            #     self.player1.give_reward(score)
            #     return True
        return True

    def free_turn(self, player_id):
        lost = [False, False]
        move_coords = None

        player = self.players[player_id]
        player.game.round = self.field.round
        player.game.field.cell = self.game.field.cell
        player.game.my_botid = player_id
        player.game.field.players = self.game.field.players
        # player.game.field.cell = [row[:] for row in self.field.cell]
        player.do_turn()
        p_move = player.game.last_order
        p_move_coord = self.field.get_coord_of_direction(self.field.players[player_id].coord, p_move)
        move_coords = p_move_coord

        if p_move_coord is None or not self.field.is_legal(*p_move_coord, player_id):
            lost[player_id] = True

        if move_coords == self.field.players[player_id ^ 1].coord:
            lost[0] = True
            lost[1] = True

        if True in lost:
            # area1 = len(self.field.total_area_fast(self.field.players[0].coord, 0))
            # area2 = len(self.field.total_area_fast(self.field.players[1].coord, 1))
            # score = area1/(128 - self.field.round) - area2/(128 - self.field.round)
            if lost[0] and lost[1]:
                self.player2.give_reward(0)
                self.player1.give_reward(0)
            elif lost[0]:
                self.player2.give_reward(1)
                self.player1.give_reward(-1)
            else:
                self.player2.give_reward(-1)
                self.player1.give_reward(1)
            return True

        player_coord = self.field.players[player_id]
        self.field.cell[player_coord.row * self.field.height + player_coord.col] = BLOCKED
        player_coord.row, player_coord.col = move_coords[0], move_coords[1]
        self.field.cell[player_coord.row * self.field.height + player_coord.col] = player_id
        return False
