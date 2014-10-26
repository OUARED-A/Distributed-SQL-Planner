from utils import flat


class Alias(object):

    def __init__(self, wrapper=lambda x: x):
        self._wrapper = wrapper
        self._aliases = {}

    def __call__(self, key):
        return self[key]

    def __iter__(self):
        return iter(self._aliases)

    def __getitem__(self, key):
        if key not in self:
            return self._wrapper([key])
        else:
            return self._wrapper(flat([self[x] for x in self._aliases[key]]))

    def __setitem__(self, key, val):
        if key in self._aliases:
            assert self[key] == val
        else:
            self._aliases[key] = val
