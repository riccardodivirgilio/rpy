# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from functools import reduce
from itertools import islice

from rpy.functions import six


def first(iterable, default=None):
    try:
        return next(iter(iterable))
    except StopIteration:
        return default


def last(iterable, default=None):
    try:
        return iterable[-1]
    except IndexError:
        return default


def identity(x):
    return x


def composition(*functions):

    if not functions:
        return identity

    if len(functions) == 1:
        return first(functions)

    return reduce(lambda f, g: lambda *args, **kw: f(g(*args, **kw)),
                  reversed(functions))


def is_iterable(obj, exclude_list=six.string_types):
    if isinstance(obj, exclude_list):
        return False
    return hasattr(obj, '__iter__')


def iterate(*args):
    for arg in args:
        if not is_iterable(arg):
            yield arg
        else:
            for item in arg:
                yield item


def flatten(*args):
    for arg in args:
        if is_iterable(arg):
            for sub in arg:
                for el in flatten(sub):
                    yield el
        else:
            yield arg


def riffle(iterable, separator):
    iterable = iter(iterable)
    try:
        yield next(iterable)
        for el in iterable:
            yield separator
            yield el
    except StopIteration:
        pass


def partition(iterable, n):
    """ Yield successive n-sized chunks from l. """
    iterable = iter(iterable)
    res = tuple(islice(iterable, n))
    while len(res) != 0:
        yield res
        res = tuple(islice(iterable, n))
