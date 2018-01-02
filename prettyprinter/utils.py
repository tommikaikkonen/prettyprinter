import os
from itertools import islice


def intersperse(x, ys):
    """
    Returns an iterable where ``x`` is inserted between
    each element of ``ys``

    :type ys: Iterable
    """
    it = iter(ys)

    try:
        y = next(it)
    except StopIteration:
        return

    yield y

    for y in it:
        yield x
        yield y


def find(predicate, iterable, default=None):
    filtered = iter((x for x in iterable if predicate(x)))
    return next(filtered, default)


def rfind_idx(predicate, seq):
    length = len(seq)
    for i, el in enumerate(reversed(seq)):
        if predicate(el):
            return length - i - 1
    return -1


def identity(x):
    return x


def get_terminal_width(default=79):
    try:
        _rows, columns = os.popen('stty size', 'r').read().split()
        columns = int(columns)
    except Exception:
        return default
    return columns


def take(n, iterable):
    return islice(iterable, n)


def compose(f, g):
    if f is identity:
        return g
    if g is identity:
        return f

    def composed(x):
        return f(g(x))

    composed.__name__ = 'composed_{}_then_{}'.format(
        g.__name__,
        f.__name__
    )

    return composed
