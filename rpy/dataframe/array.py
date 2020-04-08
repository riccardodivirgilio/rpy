from __future__ import absolute_import, print_function, unicode_literals

from rpy.dataframe.symbolic import evaluate, sym, Symbolic
from rpy.functions.dispatch import Dispatch
from rpy.functions import six
import numpy as np
import types

to_array = Dispatch()

@to_array.dispatch(Symbolic)
def render_value(formula, length, context):
    return evaluate(formula, context=context)

@to_array.dispatch((six.integer_types, float, six.string_types))
def render_value(value, length, context):
    return np.full(length, value)

@to_array.dispatch(dict)
def render_value(d, length, context):

    # same implementation of np.core.records.fromarrays

    columns = tuple((k, to_array(v, length, context)) for k, v in d.items())

    a = np.recarray((length,), list((k, v.dtype) for k, v in columns))

    for k, v in columns:
        a[k] = v

    return a

@to_array.dispatch((list, tuple, types.GeneratorType))
def render_value(value, length, context):
    return to_array({"f%i" % i: v for i, v in enumerate(value)}, length, context)

def array_map(func, array):
    return to_array(func(sym.array), length=len(array), context = {'array': array})

def array_map_indexed(func, array):
    return to_array(func(sym.array, sym.index), length=len(array), context = {'array': array, 'index': np.arange(len(array))})

def array_filter(func, array):
    return array[array_map(func, array)]