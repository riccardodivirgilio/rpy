# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from rpy.functions.dispatch import Dispatch
from rpy.functions.functional import iterate, partial, reduce

builtin = (
    ('__add__', 'add', None),
    ('__sub__', 'sub', None),
    ('__mul__', 'mul', None),
    ('__floordiv__', 'floordiv', None),
    ('__mod__', 'mod', None),
    ('__divmod__', 'divmod', None),
    ('__pow__', 'pow', None),
    ('__lshift__', 'lshift', None),
    ('__rshift__', 'rshift', None),
    ('__and__', 'and', None),
    ('__xor__', 'xor', None),
    ('__or__', 'or', None),
    ('__div__', 'div', None),
    ('__truediv__', 'truediv', None),
    ('__radd__', 'radd', None),
    ('__rsub__', 'rsub', None),
    ('__rmul__', 'rmul', None),
    ('__rdiv__', 'rdiv', None),
    ('__rtruediv__', 'rtruediv', None),
    ('__rfloordiv__', 'rfloordiv', None),
    ('__rmod__', 'rmod', None),
    ('__rdivmod__', 'rdivmod', None),
    ('__rpow__', 'rpow', None),
    ('__rlshift__', 'rlshift', None),
    ('__rrshift__', 'rrshift', None),
    ('__rand__', 'rand', None),
    ('__rxor__', 'rxor', None),
    ('__ror__', 'ror', None),
    ('__neg__', 'neg', None),
    ('__pos__', 'pos', None),
    ('__abs__', 'abs', None),
    ('__invert__', 'invert', None),
    ('__complex__', 'complex', None),
    ('__int__', 'int', None),
    ('__long__', 'long', None),
    ('__float__', 'float', None),
    ('__oct__', 'oct', None),
    ('__hex__', 'hex', None),
    ('__index__', 'index', None),
    ('__coerce__', 'coerce', None),
    ('__getattr__', 'getattr', getattr),
    ('__getitem__', 'getitem', None),
)

def call(attr, obj, *args, **opts):
    return getattr(obj, attr)(*args, **opts)

def create_function_call(attr, func):
    m = partial(call, attr)

    if func:
        return func

    def func(*args):
        if len(args) <= 1:
            return m(*args)
        return reduce(m, args)
    return func

DEFAULT_CONTEXT = {
    name: create_function_call(attr, func)
    for attr, name, func in builtin
}

def proxy(attr, self, *args, **kwargs):
    return Symbol(attr)(self, *args, **kwargs)

class ExpressionMeta(object):

    def __bool__(self):
        return True

    def __call__(self, *args, **opts):
        return Function(self, *args, **opts)

for attr, name, func in builtin:
    setattr(ExpressionMeta, attr, partial(proxy, name))

class Symbol(ExpressionMeta):

    __slots__ = '__symbolname__'

    def __init__(self, name):
        self.__symbolname__ = name

    def __hash__(self):
        return hash((Symbol.__name__, self.__symbolname__))

    def __len__(self):
        return 0  #consistent with Length(x)

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.__symbolname__ == other.__symbolname__

    def __repr__(self):
        return self.__symbolname__

    def __str__(self):
        return self.__symbolname__

class Function(ExpressionMeta):

    __slots__ = '__symbol__', '__functionargs__', '__functionkwargs__'

    def __init__(self, head, *args, **kwargs):
        self.__symbol__         = head
        self.__functionargs__   = args
        self.__functionkwargs__ = kwargs

    def __hash__(self):
        return hash((self.__symbol__, self.__functionargs__, self.__functionkwargs__))

    def __eq__(self, other):
        return isinstance(
            other,
            Function) and self.__symbol__ == other.__symbol__ and self.__functionargs__ == other.__functionargs__ and self.__functionkwargs__ == other.__functionkwargs__

    def __len__(self):
        return len(self.__functionargs__) + len(self.__functionkwargs__)

    def __repr__(self):
        return '%s(%s)' % (repr(self.__symbol__), ', '.join(
            iterate(
                (repr(x) for x in self.__functionargs__),
                ('%s = %s' % (repr(k), repr(v)) for k, v in self.__functionkwargs__.items()),
            )
        ))

class SymbolFactory(object):

    def __getattr__(self, attr):
        return Symbol(attr)

evaluate_with_context = Dispatch()

@evaluate_with_context.dispatch(Symbol)
def evaluate_symbol(symbol, context):
    try:
        result = context[symbol.__symbolname__]
    except KeyError:
        return symbol

    return evaluate_with_context(result, context)

@evaluate_with_context.dispatch(Function)
def evaluate_function(func, *args, **opts):
    return evaluate_with_context(func.__symbol__,         *args, **opts)(
          *evaluate_with_context(func.__functionargs__,   *args, **opts),
         **evaluate_with_context(func.__functionkwargs__, *args, **opts),
    )

@evaluate_with_context.dispatch(tuple, list)
def evaluate_generic(objs, *args, **opts):
    return objs.__class__(evaluate_with_context(obj, *args, **opts) for obj in objs)

@evaluate_with_context.dispatch(dict)
def evaluate_generic(mapping, *args, **opts):
    return mapping.__class__(
        (evaluate_with_context(key, *args, **opts), evaluate_with_context(value, *args, **opts))
        for key, value in mapping.items()
    )

@evaluate_with_context.dispatch()
def evaluate_generic(obj, *args, **opts):
    return obj

def evaluate(symbol, context = {}, default_context = DEFAULT_CONTEXT):
    context.update(default_context)
    return evaluate_with_context(symbol, context)

sym = SymbolFactory()
