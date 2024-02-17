import logging

import pandas as pd
from tqdm.auto import tqdm

from cumulative.options import options
from cumulative.utils import validate_frame

log = logging.getLogger(__name__)


def process_row(func, row, **kwargs):
    return func(row, **kwargs)


class Transform:
    def __init__(self, c, name=None):
        self.c = c
        self.name = self.__class__.__name__.lower() if not name else name

    def transform_row(self, row):
        return pd.Series()

    def __call__(self, **kwargs):
        tqdm_params = options.get("tqdm")
        tqdm_params["desc"] = self.name
        tqdm.pandas(**tqdm_params)
        # The destination prefix is not required/expected by row transforms,
        # let's drop it if present.

        kwargs["src"] = options.default_if_null(kwargs.pop("src", None), "transforms.source")
        dst = options.default_if_null(kwargs.pop("dst", None), "transforms.destination")

        df = self.apply(**kwargs)

        self.c.track(self.name, dst, kwargs)

        if df is None:
            # Sort
            return self.c

        if isinstance(df, pd.DataFrame):
            df.columns = [f"{dst}.{col}" if col != "idx" else col for col in df.columns]
        elif isinstance(df, pd.Series):
            df = df.rename(dst).to_frame()
        else:
            raise Exception("Invalid argument type")

        validate_frame(df, f"Transform {self.name}")

        drop_cols = self.c.columns_with_prefix(dst, errors="ignore")
        self.c.df = self.c.df.drop(columns=drop_cols, errors="ignore")
        self.c.df = pd.concat(
            [self.c.df, df],
            axis=1,
        )
        return self.c

    def apply(self, **kwargs):
        return self.c.df.progress_apply(lambda row: self.transform_row(row, **kwargs), axis=1)
