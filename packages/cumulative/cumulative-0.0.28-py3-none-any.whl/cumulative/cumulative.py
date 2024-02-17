import logging

import pandas as pd

from cumulative.animation import Animation
from cumulative.explore import Explore
from cumulative.geometry import Geometry
from cumulative.options import options
from cumulative.plot import Plot
from cumulative.transforms.bin import Bin
from cumulative.transforms.cluster import Cluster
from cumulative.transforms.copy import Copy
from cumulative.transforms.derivate import Derivate
from cumulative.transforms.drop import Drop
from cumulative.transforms.features import Features
from cumulative.transforms.fit import Fit
from cumulative.transforms.integrate import Integrate
from cumulative.transforms.interp import Interp
from cumulative.transforms.scale import Scale
from cumulative.transforms.score import Score
from cumulative.transforms.sequence import Sequence
from cumulative.transforms.sort import Sort
from cumulative.transforms.template import Template
from cumulative.transforms.transition import Transition

log = logging.getLogger(__name__)


class Cumulative:
    def __init__(self, df_raw=None, df=None):

        if df is None:
            df = pd.DataFrame()

        self.df_raw = df_raw
        self.df = df
        self.lineage = []

        #
        self.sequence = Sequence(self)
        self.scale = Scale(self)
        self.derivate = Derivate(self)
        self.integrate = Integrate(self)
        self.fit = Fit(self)
        self.score = Score(self)
        self.copy = Copy(self)
        self.sort = Sort(self)
        self.template = Template(self)
        self.interp = Interp(self)
        self.transition = Transition(self)
        self.cluster = Cluster(self)
        self.bin = Bin(self)
        self.drop = Drop(self)
        self.features = Features(self)

        self.plot = Plot(self)
        self.anim = Animation(self)
        self.explore = Explore(self)
        self.geometry = Geometry(self)

    def explain(self) -> None:
        for idx, transform in list(enumerate(self.lineage))[::-1]:
            name = transform["name"]
            kwargs = ", ".join([f"{k}={v}" for k, v in transform["kwargs"].items()])
            if transform["dst"] is not None:
                dst = f'-> {transform["dst"]}'
            else:
                dst = ""
            log.info(f"[{idx}] {name}({kwargs}) {dst}")

    def register_transform(self, name, cls):
        self.__dict__[name] = cls(self)

    def track(self, name, dst, kwargs):
        self.lineage.append({"name": name, "dst": dst, "kwargs": kwargs})

    def columns_with_prefix(self, prefix, errors="raise"):
        cols = [col for col in self.df.columns if col.startswith(f"{prefix}.") or col == prefix]
        if len(cols) == 0 and errors == "raise":
            raise Exception(f"No matching columns for prefix '{prefix}'")
        return cols

    def frame(self, src=None, idx=None):
        src = options.default_if_null(src, "transforms.source")
        cols = self.columns_with_prefix(src)
        df = self.df[["idx"] + cols]
        if idx:
            df = df[df.idx == idx]
        return df
