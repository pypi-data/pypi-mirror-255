import numpy as np
import pandas as pd

from cumulative.transforms.transform import Transform


class Derivate(Transform):
    def transform_row(self, row, src):

        s = pd.Series(np.gradient(row[f"{src}.y"]), index=row[f"{src}.x"], copy=True)

        attrs = {
            "x_min": s.index.min(),
            "x_max": s.index.max(),
            "y_min": s.min(),
            "y_max": s.max(),
        }

        s -= s.min()
        s /= s.max()
        s = s.values

        attrs["x"] = row[f"{src}.x"]
        attrs["y"] = s

        return pd.Series(attrs)
