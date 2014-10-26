from contextlib import contextmanager
from functools import wraps
import cPickle


@contextmanager
def ignored(*exceptions):
    """Execute the code in the with statement ignoring the exceptions"""
    try:
        yield
    except exceptions:
        pass


def memo(func):
    """Memoization decorator for a function taking a single argument"""
    cache = {}

    def _func(*args, **kwargs):
        key = cPickle.dumps(args, 1) + cPickle.dumps(kwargs, 1)
        if key in cache:
            return cache[key]
        ret = cache[key] = func(*args, **kwargs)
        return ret
    return _func


def calldecorator(call, default=None):
    """Generate a decorator that wraps a function in the call function"""
    def decorator(func):
        @wraps(func)
        def _func(*args, **kwargs):
            return call(*filter(None, (func(*args, **kwargs),)))
        return _func
    return decorator


def flat(lst):
    return sum((flat(x) if hasattr(x, '__iter__') else [x] for x in lst), [])

listify = calldecorator(list)
setify = calldecorator(set)
