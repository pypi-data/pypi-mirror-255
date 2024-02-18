import awkward as ak


class Cut:
    def __init__(self, c) -> None:
        self.__cut = c

    @property
    def cut(self):
        return self.__cut

    def __and__(self, c):
        assert isinstance(c, Cut)
        return Cut(lambda x: self.cut(x) & c.cut(x))

    def __or__(self, c):
        assert isinstance(c, Cut)
        return Cut(lambda x: self.cut(x) | c.cut(x))

    def __invert__(self):
        return Cut(lambda x: ~self.cut(x))

    def apply(self, array):
        sel = self.cut(array)
        res_array = array if sel is True else array[sel]
        return res_array

    def get_entries(self, array):
        arr = self.apply(array)
        return len(arr)

    def efficiency(self, array):
        total = len(array)
        return self.get_entries(array) / total
