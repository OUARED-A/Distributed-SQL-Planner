from collections import defaultdict
from itertools import combinations


class eqclass():

    def __init__(self):
        self._classes = defaultdict(set)

    def add(self, a, b):
        eq = self._classes[a] | self._classes[b] | {a, b}
        for el in eq:
            self._classes[el] = eq
        return self

    def merge(self, other):
        if not isinstance(other, eqclass):
            raise TypeError('cannot merge eqclass with `%s`' % type(other))
        for eq in other:
            for a, b in combinations(eq, 2):
                self.add(a, b)
        return self

    def __iter__(self):
        return iter(filter(None, set(map(tuple, self._classes.values()))))

    def __getitem__(self, key):
        return self._classes[key]

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return str(self)
