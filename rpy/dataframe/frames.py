# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from rpy.functions.dispatch import Dispatch
from rpy.functions.encoding import force_text


class DataColumn(object):

    def __init__(self, function, name = None, short_description = None):
        self.name = name
        self.function = function
        self.short_description = short_description

    def get_name(self, index):
        return self.name or 'column_%s' % index

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name or 'unnamed')

to_data_column = Dispatch()
to_data_column.register(lambda d: DataColumn(**d), dict)
to_data_column.register(lambda d: d, DataColumn)
to_data_column.register(lambda d: DataColumn(d))

class DataFrame(object):

    def __init__(self, obj_list, columns = (force_text, )):
        self.obj_list = obj_list
        self.columns = {
            c.get_name(i+1): c
            for i, c in enumerate(map(to_data_column, columns))
        }
