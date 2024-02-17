import numpy as np

from cumulative.options import options


def intersects(x, y, x_min=None, x_max=None, y_min=None, y_max=None):
    # Returns true if any point in the curve x,y matches the constraints
    match = np.full(x.shape[0], True)
    if x_min:
        match = np.logical_and(match, x >= x_min)
    if x_max:
        match = np.logical_and(match, x <= x_max)
    if y_min:
        match = np.logical_and(match, y >= y_min)
    if y_max:
        match = np.logical_and(match, y <= y_max)
    return np.any(match)


class Geometry:
    def __init__(self, c):
        self.c = c

    def intersects(self, src=None, x_min=None, x_max=None, y_min=None, y_max=None):
        src = options.default_if_null(src, "transforms.source")
        matches = self.c.df.apply(
            lambda row: intersects(row[f"{src}.x"], row[f"{src}.y"], x_min, x_max, y_min, y_max), axis=1
        )
        return self.c.df[matches][["idx"]]
