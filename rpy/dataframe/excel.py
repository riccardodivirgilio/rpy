# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
from decimal import Decimal
from itertools import count, islice, product, repeat

from rpy.dataframe.symbolic import Symbolic, evaluate
from rpy.functions import six
from rpy.functions.decorators import to_tuple
from rpy.functions.dispatch import Dispatch
from rpy.functions.encoding import force_text
from rpy.functions.escape import escape

XLSX_MYMETYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

class Formula(object):

    def __init__(self, formula, cell_format = None, extimated_size = None, needs_parenthesis = True):
        self.formula     = formula
        self.cell_format = cell_format
        self.extimated_size = extimated_size
        self.needs_parenthesis = needs_parenthesis

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.formula)

    def __str__(self):
        if self.needs_parenthesis:
            return '(%s)' % self.formula
        return self.formula

def _column_name_generator(alphabeth = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    for i in count(1):
        yield from map(''.join, product(*repeat(alphabeth, i)))

@to_tuple
def get_excel_names(r):
    return islice(_column_name_generator(), r)

def excel_enumerate(iterable):
    return zip(count(), _column_name_generator(), iterable)

class CallableText(object):

    operators = {
        'add': ' + ',
        'sub': ' - ',
        'mul': ' * ',
        'pow': '^',
        'truediv': ' / ',
        'floordiv': ' / ',
    }

    functions = {
        'floordiv': 'FLOOR(%s, 1)'
    }

    def __init__(self, symbol):
        self.name = force_text(symbol)

    def __call__(self, *args):

        args = self.normalize_args(args)

        try:
            inner = self.operators[self.name].join(args)
            templ = self.functions.get(self.name, None) or '(%s)'
        except KeyError:
            inner = ', '.join(args)
            templ = self.functions.get(self.name, None) or (self.name.upper() + '(%s)')

        return templ % inner

    def normalize_args(self, args):
        for arg in args:
            if isinstance(arg, CallableText):
                yield force_text(arg)
            else:
                arg = to_formula(arg)
                if isinstance(arg, Formula):
                    yield force_text(arg)
                elif arg:
                    yield escape(arg)

    def __str__(self):
        return self.name

to_formula = Dispatch()

@to_formula.dispatch(Symbolic)
def handle(value):
    f = evaluate(
        value, 
        missing_function = CallableText, 
        context = {}, 
        default_context = {}
    )
    return Formula(f)


@to_formula.dispatch(Formula)
def handle(value):
    return value

@to_formula.dispatch(bool)
def handle(value):
    return Formula(value and 'TRUE' or 'FALSE', extimated_size = value and 4 or 5, needs_parenthesis = False)

@to_formula.dispatch(datetime.timedelta)
def handle(value):
    return Formula('TIME(0, 0, 0) + (%s / 86400) - TIME(0, 0, 0)' % value.total_seconds())

@to_formula.dispatch(datetime.datetime)
def handle(value):
    return Formula(
        'DATE(%s, %s, %s) + (%s * 3600 + %s * 60 + %s) / 86400' % (
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second + value.microsecond / 1000000,
        ),
        cell_format = ('datetime_format', 'dd-mmm-yy hh:mm:ss'),
        extimated_size = 18
    )

@to_formula.dispatch(datetime.date)
def handle(value):
    return Formula(
        'DATE(%s, %s, %s)' % (value.year, value.month, value.day),
        cell_format = ('date_format', 15),
        extimated_size = 9, 
        needs_parenthesis = False
    )

@to_formula.dispatch(datetime.time)
def handle(value):
    return Formula(
        'TIME(%s, %s, %s) + (%s / 86400)' % (
            value.hour,
            value.minute,
            value.second,
            value.microsecond / 1000000,
        ),
        cell_format = ('time_format', 21),
        extimated_size = 8,
        needs_parenthesis = False
    )

@to_formula.dispatch(int)
def handle(value):
    return Formula(
        '%s' % value,
        needs_parenthesis = False,
        cell_format = ('int_format', 3) # #,##0
    )

@to_formula.dispatch((float, Decimal))
def handle(value):
    return Formula(
        '%s' % value,
        needs_parenthesis = False,
        cell_format = ('dec_format', 4) # #,##0.00
    )

@to_formula.dispatch((tuple, list, set, frozenset))
def handle(value):
    return ",".join([force_text(v) for v in value])

@to_formula.dispatch(type(None))
def handle(value):
    return ""

@to_formula.dispatch()
def handle(value):
    return force_text(value)

class XLSXWriter(object):

    def __init__(self, f, name = 'Workbook', freeze_rows = 1, auto_sizing = True):

        from xlsxwriter import Workbook

        self.stream = f
        self.worksheet = None
        self.workbook = Workbook(self.stream)
        self.formats = {}
        self.worksheet = None
        if name:
            self.new_worksheet(name = name)
        self.freeze_rows = freeze_rows
        self.auto_sizing = auto_sizing

    def new_worksheet(self, name = None):

        self.close_worksheet()

        self.line = 0
        self.worksheet = self.workbook.add_worksheet(name = name)
        self.max = {}

    def get_format(self, name, value):
        try:
            return self.formats[name]
        except KeyError:
            if isinstance(value, six.integer_types):
                fmt = self.workbook.add_format()
                fmt.set_num_format(value)
            elif isinstance(value, six.string_types):
                fmt = self.workbook.add_format({'num_format': value})
            else:
                fmt = self.workbook.add_format(value)

            self.formats[name] = fmt
            return self.formats[name]

    def update_max_size(self, x, l):
        self.max[x] = max(l, self.max.get(x, 0))

    def close_worksheet(self):

        if self.worksheet:
            if self.freeze_rows:

                for i in range(self.freeze_rows):
                    self.worksheet.set_row(i, None, self.get_format(
                        'freezed_rows',
                        {'bold': True, 'bg_color': 'black', 'font_color': 'white'}
                    ))

            if self.auto_sizing:
                for y, l in self.max.items():
                    self.worksheet.set_column(y, y, l)

        self.worksheet = None

    def write(self, value, y, x):
        formula = to_formula(value)

        #this can be string, or formula

        if isinstance(formula, Formula):
            if formula.extimated_size:
                self.update_max_size(x, formula.extimated_size)
            return self.worksheet.write_formula(
                y, x, formula.formula, 
                cell_format = formula.cell_format and self.get_format(*formula.cell_format) or None
            )
        elif formula:
            self.update_max_size(x, len(formula))
            return self.worksheet.write(y, x, formula)

    def writerow(self, row):
        for y, value in enumerate(row):
            self.write(value, self.line, y)
        self.line += 1

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def close(self):
        self.close_worksheet()
        self.workbook.close()

def write_to_stream(lines, stream = None, **opts):
    s = stream or six.BytesIO()
    if not isinstance(lines, dict):
        lines = {'Data': lines}
    with XLSXWriter(s, name = None, **opts) as writer:
        for book, data in lines.items():
            writer.new_worksheet(book)
            for line in data:
                writer.writerow(line)
    if hasattr(s, 'seek'):
        s.seek(0)
    return s
