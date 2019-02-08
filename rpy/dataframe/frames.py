# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from collections.abc import Mapping, Sequence

from rpy.functions import six
from rpy.functions.decorators import to_tuple
from rpy.functions.dispatch import Dispatch
from rpy.functions.encoding import force_text
from rpy.functions.functional import identity


def format_table(table):

    col_width = tuple(max(len(x) for x in col) for col in zip(*table))

    return '\n'.join(
        "| " + " | ".join("{:{}}".format(x, col_width[i])
                            for i, x in enumerate(line)) + " |"
        for line in table
    )

class DataColumn(object):

    def __init__(self, function, name = None, short_description = None, index = None, formatter = identity):
        self.name = name
        self.function = function
        self.short_description = short_description
        self.index = index
        self.formatter = formatter

    def format(self, value):
        return force_text(self.formatter(value))

    def copy(self, **opts):
        defaults = dict(
            function          = self.function,
            name              = self.name,
            short_description = self.short_description,
            index             = self.index
        )
        defaults.update(opts)
        return self.__class__(**defaults)

    def get_name(self):
        return self.name or 'column_%s' % self.index

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name or 'unnamed')

to_data_column = Dispatch()
to_data_column.register(lambda d, i: DataColumn(index = i, **d), dict)
to_data_column.register(lambda d, i: d.copy(index = i), DataColumn)
to_data_column.register(lambda d, i: DataColumn(d, index = i))

class AtomData(object):

    def __init__(self, obj, column):
        self.obj    = obj
        self.column = column
        self.value  = column.function(obj)

    def formatted(self):
        return self.column.format(self.value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return self.formatted()

    def __str__(self):
        return self.formatted()

class ArrayData(Sequence):

    def __init__(self, array, column):
        self.column = column
        self.array = tuple(
            AtomData(obj, column)
            for obj in array
        )

    def __hash__(self):
        return hash(self.array)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.array == other.array
        return self.array == other

    @to_tuple
    def formatted(self):
        yield self.column.get_name()
        for obj in self:
            yield obj.formatted()

    def __getitem__(self, item):
        return self.array[item]

    def __len__(self):
        return len(self.array)

    def __repr__(self):
        return format_table(tuple(zip(self.formatted())))

class DataFrame(Mapping):

    def __init__(self, array, columns):
        self.columns_list = tuple(
            to_data_column(c, i) for i, c in enumerate(columns)
        )
        self.columns_dict = {
            column.get_name(): column
            for column in self.columns_list
        }
        self.table = tuple(
            ArrayData(array = array, column = column)
            for column in self.columns_list
        )

    @to_tuple
    def formatted(self):
        return zip(*(column.formatted() for column in self.values()))

    def __hash__(self):
        return hash(self.table)

    def __getitem__(self, value):
        if not isinstance(value, (six.integer_types, slice)):
            value = self.columns_dict[value].index
        try:
            return self.table[value]
        except IndexError as e:
            raise KeyError(e)

    def __iter__(self):
        return iter(self.columns_dict.keys())

    def __len__(self):
        return len(self.columns_dict)

    def __repr__(self):
        return format_table(self.formatted())
