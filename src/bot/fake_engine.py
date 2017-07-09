import random

from bot.game import Game


class FakeEngine(object):
    def __init__(self, player1, player2, field=None):
        if field:
            self.game = Game()
            player1.game = self.game
            player2.game = self.game
            self.game.field = field.copy()
        else:
            self.game = Game()
            player1.game = self.game
            player2.game = self.game
            self.game.field.width = 16
            self.game.field.height = 16
            self.game.field.round = 0

            coord1 = (random.randint(0, 15), random.randint(0, 15))

            self.game.field.create_board(coord1)

        self.game.silent = True
        self.player1 = player1
        self.player2 = player2
        self.players = [self.player1, self.player2]

    def reset(self, field=None):
        self.__init__(*self.players, field)

    def step(self):
        lost = [False, False]
        move_coords = [None, None]
        # self.game.field.cache_adjacent_initial()

        for i, (player, player_coord) in enumerate(zip(self.players, self.game.field.players)):
            player.do_turn()
            move = player.game.last_order_coord
            if move is None or not self.game.field.is_legal(*move):
                lost[i] = True
            move_coords[i] = move

        if move_coords[0] == move_coords[1]:
            lost[0], lost[1] = True, True

        if True in lost:
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

        for i, (player_coord, move_coord) in enumerate(zip(self.game.field.players, move_coords)):
            # field.legal_player = i
            self.game.field.move(move_coord)
            # cell = field.cell
            # cell[player_coord.row * 16 + player_coord.col] = BLOCKED
            # player_coord.row, player_coord.col = move_coord
            # cell[player_coord.row * 16 + player_coord.col] = i
        # field.round += 1
        return False

    def run(self):
        finished = self.step()
        while not finished:
            finished = self.step()
        return True

    def free_turn(self, player_id):
        lost = [False, False]
        # self.field._legal_moves = None
        # self.field.legal_player = player_id
        player = self.players[player_id]
        player.do_turn()
        move_coords = player.game.last_order_coord
        # p_move_coord = self.field.get_coord_of_direction(self.field.players[player_id].coord, p_move)
        # move_coords = p_move_coord

        if move_coords is None:
            lost[player_id] = True

        if move_coords == self.game.field.players[player_id ^ 1].coord:
            lost[0], lost[1] = True, True

        if True in lost:
            # area1 = len(self.field.total_area_fast(self.field.players[0].coord, 0))
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

        if self.game.field.legal_player != player_id:
            print('lol')
        # self.game.field.cache_adjacent_initial()
        self.game.field.move(move_coords)
        # player_coord = self.field.players[player_id]
        # self.field.cell[player_coord.row * self.field.height + player_coord.col] = BLOCKED
        # player_coord.row, player_coord.col = move_coords[0], move_coords[1]
        # self.field.cell[player_coord.row * self.field.height + player_coord.col] = player_id
        return False
