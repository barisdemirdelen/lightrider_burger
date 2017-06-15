from bot.board import BLOCKED
from bot.game import Game


class FakeEngine(object):
    def __init__(self, player1, player2):
        self.game = Game()
        p1_game = Game()
        p2_game = Game()

        initial_message = 'settings player_names player0,player1\n' \
                          'settings timebank 1000\n' \
                          'settings time_per_move 20\n' \
                          'settings field_width 16\n' \
                          'settings field_height 16\n' \
                          'update game round 0\n' \
                          'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                          'action move 1000\n'

        self.game.update(initial_message)
        p1_game.update(initial_message)
        p2_game.update(initial_message)
        player1.setup(p1_game)
        player2.setup(p2_game)

        p1_message = 'settings your_bot player0\n' \
                     'settings your_botid 0\n'
        p2_message = 'settings your_bot player1\n' \
                     'settings your_botid 1\n'

        player1.game.update(p1_message)
        player2.game.update(p2_message)

        self.field = self.game.field
        self.player1 = player1
        self.player2 = player2
        self.players = [self.player1, self.player2]
        self.round = 0

    def reset(self):
        self.game = Game()
        p1_game = Game()
        p2_game = Game()

        initial_message = 'settings player_names player0,player1\n' \
                          'settings timebank 1000\n' \
                          'settings time_per_move 20\n' \
                          'settings field_width 16\n' \
                          'settings field_height 16\n' \
                          'update game round 0\n' \
                          'update game field .,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,0,.,.,.,.,.,.,.,.,1,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.\n' \
                          'action move 1000\n'

        self.game.update(initial_message)
        p1_game.update(initial_message)
        p2_game.update(initial_message)
        self.player1.setup(p1_game)
        self.player2.setup(p2_game)

        p1_message = 'settings your_bot player0\n' \
                     'settings your_botid 0\n'
        p2_message = 'settings your_bot player1\n' \
                     'settings your_botid 1\n'

        self.player1.game.update(p1_message)
        self.player2.game.update(p2_message)

        self.field = self.game.field
        self.player1 = self.player1
        self.player2 = self.player2
        self.players = [self.player1, self.player2]
        self.round = 0

    def step(self, move_override=None):
        if move_override == None:
            move_override = [None, None]
        lost = [False, False]
        move_coords = [None, None]

        for i, player in enumerate(self.players):
            message = 'update game round %d\n' \
                      'action move 1000\n' % self.round
            player.game.update(message)
            player.game.field.cell = [row[:] for row in self.field.cell]
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
            if lost[0] and lost[1]:
                self.player1.give_reward(0)
                self.player2.give_reward(0)
            elif lost[0]:
                self.player1.give_reward(-1)
                self.player2.give_reward(1)
            else:
                self.player1.give_reward(1)
                self.player2.give_reward(-1)
            return True

        for i, player in enumerate(self.field.players):
            self.field.cell[player.row][player.col] = BLOCKED
            player.row, player.col = move_coords[i][0], move_coords[i][1]
            self.field.cell[player.row][player.col] = i

        self.round += 1
        return False

    def run(self):
        finished = self.step()
        while not finished:
            finished = self.step()
