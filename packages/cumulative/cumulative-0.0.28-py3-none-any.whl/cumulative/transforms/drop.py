from cumulative.transforms.transform import Transform


class Drop(Transform):
    def apply(self, src):
        cols = self.c.columns_with_prefix(src)
        self.c.df = self.c.df.drop(columns=cols)
