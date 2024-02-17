from cumulative.transforms.transform import Transform


class Score(Transform):
    def apply(self, src, reverse=False, argsort=False):

        s = self.c.df[src].copy()
        s -= s.min()
        s /= s.max()

        if reverse:
            s = 1 - s

        if argsort:
            s = s.argsort() / len(s)
            s -= s.min()
            s /= s.max()

        return s
