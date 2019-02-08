# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import unittest

from rpy.dataframe.excel import write_to_stream
from rpy.dataframe.frames import DataFrame
from rpy.dataframe.symbolic import sym
from rpy.functions.process import system_open


class DataframeTest(unittest.TestCase):

    def test_dataframe_slice(self):

        frame = DataFrame(
            [1, 2, 3], 
            headers = (
                lambda i: i,
                lambda i: i+2,
                dict(function = lambda i: i+4, name = 'last'),
            )
        )
        self.assertEqual(frame[0], (1, 2, 3))
        self.assertEqual(frame[1], (3, 4, 5))
        self.assertEqual(frame['last'], (5, 6, 7))
        self.assertEqual(frame['last'][0], 5)

        self.assertIsInstance(frame[0][1], int)

        frame = DataFrame(
            [1, 2, 3], 
            headers = {
                'foo': lambda i: i+4,
                'bar': lambda i: i+6,
            }
        )

        self.assertEqual(frame['foo'], (5, 6, 7))
        self.assertEqual(frame['bar'], (7, 8, 9))

    def test_dataframe_symbolic(self):

        frame = DataFrame(
            [1, 2, 3], 
            headers = {
                'baz': lambda i: i,
                'foo': lambda i: sym.baz + 2,
                'bar': lambda i: sym.foo + datetime.datetime.now(),
                'arr': lambda i: [1, 2, 3],
                #'pow': lambda i: sym.bar ** 2,
                #'baz': lambda i: sym.sum(sym.dataframe['bar']),
                #'bax': lambda i: sym.sum(sym.dataframe['foo']),
            }, 
        )

        with open('/Users/rdv/Desktop/test.xlsx', 'wb') as stream:
            write_to_stream(
                frame.excel_formula(),
                stream = stream
            )

        system_open('/Users/rdv/Desktop/test.xlsx')
