from cumulative.transforms.transform import Transform


class Copy(Transform):
    def apply(self, src):
        cols = self.c.columns_with_prefix(src)
        df = self.c.df[cols].copy()
        df.columns = [col.removeprefix(f"{src}.") for col in cols]
        return df
