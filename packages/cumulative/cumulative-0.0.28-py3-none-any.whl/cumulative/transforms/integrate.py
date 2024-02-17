import numpy as np
import pandas as pd

from cumulative.transforms.transform import Transform


class Integrate(Transform):
    def transform_row(self, row, src, scale=False, fillna=False):

        s = pd.Series(np.cumsum(row[f"{src}.y"]), index=row[f"{src}.x"], copy=True)

        attrs = {}

        if scale:
            s -= s.min()
            s /= s.max()
            if fillna:
                s = s.fillna(0)

        attrs["x"] = row[f"{src}.x"]
        attrs["y"] = s.values

        return pd.Series(attrs)
