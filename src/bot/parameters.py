class Parameters(object):
    __slots__ = ['quiescence_depth', 'nw_search_window', 'reduction_factor', 'available_time_factor']

    def __init__(self):
        self.quiescence_depth = 10
        self.nw_search_window = 1
        self.reduction_factor = 3
        self.available_time_factor = 1.7
