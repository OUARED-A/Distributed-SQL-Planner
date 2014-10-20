from itertools import combinations


class eqclass(object):

    def __init__(self, classes=()):
        self._classes = []
        self.merge(classes)

    def extend(self, cls):
        for a, b in combinations(cls, 2):
            self.add(a, b)
        return self

    def add(self, a, b):
        classes = filter(None, [self[a], self[b]])
        if not classes:
            self._classes.append({a, b})
        elif len(classes) == 1:
            classes[0] |= {a, b}
        elif classes[0] != classes[1]:
            self._classes.remove(classes[1])
            classes[0] |= classes[1] | {a, b}
        return self

    def merge(self, classes):
        for eq in classes:
            for a, b in combinations(eq, 2):
                self.add(a, b)

    def __iter__(self):
        return iter(self._classes)

    def __getitem__(self, key):
        for cls in self:
            if key in cls:
                return cls
        return set()

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return str(self)
