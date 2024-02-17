import numpy as np
import pandas as pd

from cumulative.transforms.transform import Transform


class ExceptionInvalidName(Exception):
    pass


def normalized_tunable_sigmoid(x, k=0.5):
    k = min(k, 1 - 1e-5)
    y = (1 - k) * (2 * x + -1) / (k - 2 * k * np.abs(2 * x + -1) + 1) * 0.5 + 0.5
    return y


class Template(Transform):
    def transform_row(self, row, src, name="diagonal", **kwargs):
        if name == "diagonal":
            y = row[f"{src}.x"]
        elif name == "sigmoid":
            y = normalized_tunable_sigmoid(row[f"{src}.x"], k=kwargs.get(name, 0.5))
        else:
            raise ExceptionInvalidName(f"Invalid value for parameter 'name': '{name}'")

        return pd.Series({"x": row[f"{src}.x"], "y": y})
