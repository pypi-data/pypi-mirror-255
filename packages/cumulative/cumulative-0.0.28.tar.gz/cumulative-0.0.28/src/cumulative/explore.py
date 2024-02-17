class Explore:
    def __init__(self, c):
        self.c = c

    def corr(self, col=None, value_abs=True, display=True, sort=False, limit=None):
        numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
        df = self.c.df.dropna().select_dtypes(include=numerics).corr()
        df = df.dropna(axis=1, how="all")
        df = df.dropna(axis=0, how="all")
        if value_abs:
            df = df.abs()

        if col:
            df = df[[col]]
            df = df[df.index != col]

        if sort:
            df = df.sort_values(col, ascending=False)

        if limit:
            df = df.head(limit)

        if display:
            return df.style.background_gradient(axis=0)
        else:
            return df
