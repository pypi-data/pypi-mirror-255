import numpy as np
import pandas as pd

from cumulative.transforms.transform import Transform


class Interp(Transform):
    def transform_row(self, row, src, n_samples=1000, complete=False):

        attrs = {}

        if complete:
            attrs["x"] = np.unique(np.concatenate([row[f"{src}.x"], np.linspace(0, 1, num=n_samples)]))
            attrs["y"] = np.interp(attrs["x"], row[f"{src}.x"], row[f"{src}.y"])
        else:
            attrs["x"] = np.linspace(0, 1, num=n_samples)
            attrs["y"] = np.interp(attrs["x"], row[f"{src}.x"], row[f"{src}.y"])

        return pd.Series(attrs)
