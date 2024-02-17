import numpy as np
import pandas as pd

from cumulative.transforms.transform import Transform


class Bin(Transform):
    def transform_row(self, row, src, n_bins=10):

        y_bins = np.linspace(0, 1, num=n_bins)
        y_hat = y_bins[np.searchsorted(y_bins, row[f"{src}.y"])]
        return pd.Series({"x": row[f"{src}.x"], "y": y_hat}, copy=True)
