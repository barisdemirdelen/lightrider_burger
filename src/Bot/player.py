class Player(object):
    def __init__(self):
        self.col = 0
        self.row = 0

    @property
    def coord(self):
        return self.row, self.col
