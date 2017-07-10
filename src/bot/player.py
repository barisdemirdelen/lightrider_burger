class Player(object):
    __slots__ = ['row', 'col']

    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col

    @property
    def coord(self):
        return self.row, self.col

    @property
    def copy(self):
        return Player(self.row, self.col)
