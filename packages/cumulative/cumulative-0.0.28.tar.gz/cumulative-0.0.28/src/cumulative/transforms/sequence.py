import logging
import warnings

import pandas as pd
from tqdm.auto import tqdm

from cumulative.options import options
from cumulative.transforms.transform import Transform
from cumulative.utils import warn

log = logging.getLogger(__name__)


class SequenceWarning(UserWarning):
    pass


class Sequence(Transform):
    def apply(  # noqa
        self,
        src=None,
        group="group",
        x="x",
        y="y",
        cumsum=False,
        min_len=2,
        min_nunique=2,
        agg=None,
        filter_nochange=True,
        limit=None,
        select=None,
    ):

        self.group_col = group
        self.x = x
        self.y = y

        def build_sequence(df):
            s = pd.Series(df[self.y].values, index=df[self.x].values).rename(df.name).astype(float)

            # ensure that, in case of same index, we aggregate the values.
            # pd.Series([0, 2, 2, 4, 5], index=[0,1,2,2,4]) -> pd.Series([0, 2, 6, 5], index=[0,1,2,4])
            s = s.groupby(s.index).sum()

            if cumsum:
                s = s.cumsum()

            attrs_dict = df.groupby(lambda x: True).agg(agg).iloc[0].to_dict() if agg else {}

            if filter_nochange:
                # Drop values that didn't change from prior value, retaining only points with variations.
                s = s[s != s.shift(1)]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)

                return pd.Series({
                    "x": s.index.values,
                    "y": s.values,
                    "len": s.values.shape[0],
                    "min": s.min(),
                    "max": s.max(),
                    "sum": s.sum(),
                    "attributes": attrs_dict,
                })

        tqdm_params = options.get("tqdm")
        tqdm_params["desc"] = "sequence"
        tqdm.pandas(**tqdm_params)

        if not isinstance(self.c.df_raw, pd.DataFrame):
            raise RuntimeError("df_raw is not a valid Pandas DataFrame")

        df = self.c.df_raw.sort_values(by=[self.x, self.y]).groupby(self.group_col).progress_apply(build_sequence)
        df = df.reset_index(names="name").reset_index(names="idx")

        if min_len:
            m = df["x"].apply(len) < min_len
            if m.sum() > 0:
                warn(f"Ignoring {m.sum()} rows (filter: min_len={min_len})", category=SequenceWarning, stacklevel=1)
                df = df[~m]

        if min_nunique:
            m = df["y"].apply(lambda a: pd.Series(a).nunique()) < min_nunique
            if m.sum() > 0:
                warn(
                    f"Ignoring {m.sum()} rows (filter: min_nunique={min_nunique})",
                    category=SequenceWarning,
                    stacklevel=1,
                )

                df = df[~m]

        if agg:
            prefix = f"{options.get('transforms.sequence.attributes')}."
            df = pd.concat([df, pd.json_normalize(df["attributes"]).add_prefix(prefix)], axis=1)

        df = df.drop(columns=["attributes"])

        if select is not None:
            df = select(df)

        if limit is not None:
            df = df.head(limit)

        df = df.reset_index(drop=True)

        return df
