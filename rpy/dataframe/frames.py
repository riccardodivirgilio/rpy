# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from collections.abc import Mapping

from rpy.dataframe.excel import excel_enumerate
from rpy.dataframe.symbolic import Symbol, evaluate
from rpy.functions import six
from rpy.functions.decorators import to_tuple
from rpy.functions.dispatch import Dispatch
from rpy.functions.encoding import force_text
from rpy.functions.functional import identity


class Copyable:

    __slots__ = ()

    def __init__(self, **opts):
        for arg in self.__slots__:
            setattr(self, arg, opts.pop(arg))
        assert len(opts) == 0, opts

    def copy(self, **opts):
        defaults = dict(
            (attr, getattr(self, attr))
            for attr in self.__slots__
        )
        defaults.update(opts)
        return self.__class__(**defaults)


def format_table(table):

    col_width = tuple(max(len(x) for x in col) for col in zip(*table))

    return '\n'.join(
        "| " + " | ".join("{:{}}".format(x, col_width[i])
                            for i, x in enumerate(line)) + " |"
        for line in table
    )

class DataHeader(Copyable):

    __slots__ = ('name', 'function', 'short_description', 'index', 'formatter', 'excel_index')

    def __init__(self, function, name = None, short_description = None, index = None, excel_index = None, formatter = identity):
        self.name = name
        self.function = function
        self.short_description = short_description
        self.index = index
        self.excel_index = excel_index
        self.formatter = formatter

    def format(self, value):
        return force_text(self.formatter(value))

    def formatted(self):
        return self.short_description or self.value().title()

    def excel_formula(self):
        return self.formatted()

    def value(self):
        return self.name or 'column_%s' % self.index

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name or 'unnamed')

to_data_header = Dispatch()
to_data_header.register(lambda d, **opts: DataHeader(**opts, **d), dict)
to_data_header.register(lambda d, **opts: d.copy(**opts), DataHeader)
to_data_header.register(lambda d, **opts: DataHeader(d, **opts))

class AtomData(object):

    def __init__(self, data, dataframe, column, index):
        self.obj       = data
        self.dataframe = dataframe
        self.column    = column
        self.index     = index
        self._computed = self.column.header.function(self.obj)

    def formatted(self):
        return self.column.header.format(self.value())

    def value(self):
        return evaluate(self._computed, missing_function = self.resolve_symbolic_value)

    def excel_formula(self):
        return evaluate(self._computed, missing_function = self.resolve_symbolic_excel_formula)

    def resolve_symbolic_excel_formula(self, symbol):
        
        if symbol.__symbolname__ in self.dataframe:
            return ExcelDataFrameSymbol(
                dataframe = self.dataframe, 
                col = symbol.__symbolname__,
                row = self.index + self.dataframe.header_lines() + 1,
                workbook_name = None,
            )

        if symbol.__symbolname__ == 'dataframes':
            return ExcelDataFramesSymbol(self.dataframe.dataframes)

        if symbol.__symbolname__ == 'dataframe':
            return ExcelDataFrameSymbol(
                dataframe = self.dataframe, 
                workbook_name = None,
            )

        if symbol.__symbolname__ == 'column':
            return ExcelDataFrameSymbol(
                dataframe = self.dataframe, 
                workbook_name = None,
                col = symbol.__symbolname__,
            )

        raise KeyError


    def resolve_symbolic_value(self, symbol):

        try:
            return self.dataframe[symbol.__symbolname__][self.index]
        except KeyError:
            pass

        if symbol.__symbolname__ == 'dataframe':
            return self.dataframe

        if symbol.__symbolname__ == 'column':
            return self.column

        raise KeyError('Symbol %s not found. Choices are: dataframe, column, %s' % (symbol, ', '.join(self.dataframe.keys())))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._computed == other._computed
        return self._computed == other

    def __hash__(self):
        return hash(self._computed)

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self._computed
        )

    def __str__(self):
        return self.formatted()

class ColumnData(object):

    def __init__(self, data, header, dataframe):
        self.dataframe = dataframe
        self.header    = header
        self.column    = tuple(
            AtomData(atom, column = self, index = index, dataframe = dataframe)
            for index, atom in enumerate(data)
        )

    def __hash__(self):
        return hash(self.column)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.column == other.column
        return self.column == other

    @to_tuple
    def formatted(self):
        yield self.header.formatted()
        for obj in self.column:
            yield obj.formatted()

    @to_tuple
    def value(self):
        yield self.header.value()
        for obj in self.column:
            yield obj.value()

    @to_tuple
    def excel_formula(self):
        yield self.header.excel_formula()
        for obj in self.column:
            yield obj.excel_formula()

    def __getitem__(self, item):
        return self.column[item].value()

    def __iter__(self):
        for obj in self.column:
            yield obj.value()

    def __len__(self):
        return len(self.column)

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.header.value()
        )

    def __str__(self):
        return format_table(tuple(zip(self.formatted())))

class DataFrame(Mapping):

    def __init__(self, data, headers, dataframes = None):

        if isinstance(headers, dict):
            self.headers_list = tuple(
                to_data_header(headers[name], name = name, index = index, excel_index = excel_index)
                for index, excel_index, name in excel_enumerate(headers.keys())
            )
        else:
            self.headers_list = tuple(
                to_data_header(c, index = index, excel_index = excel_index) 
                for index, excel_index, c in excel_enumerate(headers)
            )
        self.headers_dict = {
            header.value(): header
            for header in self.headers_list
        }
        self.table = tuple(
            ColumnData(
                data = data, 
                header = header,
                dataframe = self,
            )
            for header in self.headers_list
        )
        self.dataframes = dataframes

    def header_lines(self):
        return 1

    @to_tuple
    def formatted(self):
        return zip(*(column.formatted() for column in self.values()))

    @to_tuple
    def value(self):
        return zip(*(column.value() for column in self.values()))

    @to_tuple
    def excel_formula(self):
        return zip(*(column.excel_formula() for column in self.values()))

    def __hash__(self):
        return hash(self.table)

    def __getitem__(self, value):
        if not isinstance(value, (six.integer_types, slice)):
            value = self.headers_dict[value].index
        try:
            return self.table[value]
        except IndexError as e:
            raise KeyError(e)

    def __iter__(self):
        return iter(self.headers_dict.keys())

    def __len__(self):
        return len(self.headers_dict)

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            ', '.join(self.keys())
        )

    def __str__(self):
        return format_table(self.formatted())

to_data_frame = Dispatch()
to_data_frame.register(lambda d, **opts: DataFrame(**opts, **d), dict)
to_data_frame.register(lambda d, **opts: DataFrame(*d, **opts))

class DataFrames(Mapping):

    def __init__(self, **kwargs):
        self.kwargs = {
            key: to_data_frame(value, dataframes = self)
            for key, value in kwargs.items()
        }

    def __getitem__(self, k):
        return self.kwargs.__getitem__(k)

    def __iter__(self):
        return iter(self.kwargs)

    def __len__(self):
        return len(self.kwargs)

    def value(self):
        return {k: v.value() for k, v in self.items()}

    def excel_formula(self):
        return {k: v.excel_formula() for k, v in self.items()}

class ExcelDataFrameSymbol(Copyable, Symbol):

    __slots__ = ('dataframe', 'workbook_name', 'row', 'col')

    def __init__(self, dataframe = None, workbook_name = None, row = None, col = None):
        self.dataframe = dataframe
        self.workbook_name = workbook_name
        self.row = row
        self.col = col

        if not col and not row:
            self.__symbolname__ = '%s:%s' % (
                self.dataframe.headers_list[0].excel_index, 
                self.dataframe.headers_list[1].excel_index
            )
        elif col and not row:
            self.__symbolname__ = '%s:%s' % (
                self.dataframe[col].header.excel_index, 
                self.dataframe[col].header.excel_index
            )
        elif row and not col:
            self.__symbolname__ = '%s:%s' % (
                row, 
                row
            )
        else:
            self.__symbolname__ = '%s%s'  % (
                self.dataframe[col].header.excel_index, 
                row
            )

        if self.workbook_name:
            self.__symbolname__ = "'%s'!%s" % (self.workbook_name, self.__symbolname__)

    def __getitem__(self, value):
        if not self.row and not self.col:
            return self.copy(col = value)
        elif not self.row and self.col:
            return self.copy(row = value)
        elif self.row and not self.col:
            return self.copy(col = value)
        else:
            raise KeyError('Workbook already has col and row reference')

class ExcelDataFramesSymbol(Symbol):

    def __init__(self, dataframes):
        self.dataframes = dataframes
        self.__symbolname__ = ''

    def __getitem__(self, value):
        return ExcelDataFrameSymbol(self.dataframes[value], workbook_name = value)
