import pandas as pd

from cumulative.transforms.transform import Transform


class Transition(Transform):
    def transform_row(self, row, src0, src1, percentage=0.5):
        y = row[f"{src0}.y"] * (1 - percentage) + row[f"{src1}.y"] * percentage
        attrs = {"x": row[f"{src0}.x"], "transition.y": y}
        return pd.Series(attrs, copy=True)
