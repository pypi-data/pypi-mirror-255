import logging

import pandas as pd

from cumulative.transforms.transform import Transform
from cumulative.utils import warn

log = logging.getLogger(__name__)


class ScaleWarning(UserWarning):
    pass


class ExceptionScaler(Exception):
    pass


class Scale(Transform):
    """
    MinMax normalizer on x,y axes to the unit interval [0,1].
    If the sequence contains less than two distinct values, all values are set to 1.
    """

    def transform_row(self, row, src, default_value=0):

        idx = row["idx"]
        s = pd.Series(row[f"{src}.y"], index=row[f"{src}.x"], copy=True)

        attrs = {
            "x_min": s.index.min(),
            "x_max": s.index.max(),
            "y_min": s.min(),
            "y_max": s.max(),
        }

        if s.shape[0] == 0:
            raise ExceptionScaler(f"idx={idx}: Length is zero")

        if s.shape[0] == 1:
            warn(
                f"idx={idx}: Length equal to 1, defaulting `y` to {default_value}", category=ScaleWarning, stacklevel=1
            )
            s[:] = default_value
        elif s.nunique() < 2:
            warn(
                f"idx={idx}: Less than 2 distinct `y` values, defaulting `y` to {default_value}",
                category=ScaleWarning,
                stacklevel=1,
            )
            s[:] = default_value
        else:
            s -= s.min()
            s /= s.max()

        if s.shape[0] == 1:
            warn(f"idx={idx}: Length equal to 1, defaulting `x` to zero", category=ScaleWarning, stacklevel=1)
            s.index = [0]
        else:
            if s.index.nunique() < 2:
                warn(
                    f"idx={idx}: Less than 2 distinct `x` values, defaulting to [0,1,...]/N",
                    category=ScaleWarning,
                    stacklevel=1,
                )
                s = s.reset_index(drop=True)
            s.index -= s.index.min()
            s.index /= s.index.max()

        attrs = {
            **attrs,
            **{
                "x": s.index.values,
                "y": s.values,
            },
        }

        return pd.Series(attrs)
