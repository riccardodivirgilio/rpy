import numpy as np
from rpy.dataframe.symbolic import Symbolic, evaluate, sym
from rpy.functions.functional import iterate, partial, reduce
import types
from rpy.functions.dispatch import Dispatch

to_array = Dispatch()

@to_array.dispatch(Symbolic)
def render_value(formula, array):
    return evaluate(formula, context = {'array': array})

@to_array.dispatch((int, float))
def render_value(value, array):
    return np.full(len(array), value)


@to_array.dispatch(dict)
def render_value(d, array):
    columns = {
        k: to_array(v, array)
        for k, v in d.items()
    }
    return np.core.records.fromarrays(
        tuple(
            columns.values()
        ),
        names = tuple(columns.keys())
    )


@to_array.dispatch((list, tuple, types.GeneratorType))
def render_value(value, array):
    return np.core.records.fromarrays(
        tuple(
            to_array(v, array)
            for v in value
        )
    )

def array_map(func, array):
    return to_array(func(sym.array), array = array)

def array_filter(func, array):
    return array[array_map(func, array)]


