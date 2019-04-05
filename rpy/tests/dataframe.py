# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
import unittest

from rpy.dataframe.excel import write_to_stream
from rpy.dataframe.frames import DataFrame, DataFrames
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


        frames = DataFrames(
            frame_1 = dict(
                data = (i+1 for i in range(5)), 
                headers = {
                    'baz':  lambda i: i,
                    'foo':  lambda i: sym.baz + 2,
                    'mul':  lambda i: sym.min(sym.baz, sym.foo * 3, 2),
                    'bar':  lambda i: datetime.datetime.now(),
                    'pow':  lambda i: sym.foo ** 2,
                    'sum1': lambda i: sym.sum(sym.dataframe['baz']),
                    'sum2': lambda i: sym.sum(sym.dataframe['pow']),
                    'cond1': lambda i: bool(i % 2),
                    'cond2': lambda i: sym.IF(sym.foo == 2, None, 1),
                },
            ),
            frame_2 = dict(
                data = (i+1 for i in range(3)), 
                headers = {
                    'formula': lambda i: sym.AND(1, 2, 3),
                    'comp1':   lambda i: sym.dataframes['frame_1']['foo'] > 2,
                    'comp2':   lambda i: sym.comp1 == 3,
                    'aggr':    lambda i: sym.min(sym.dataframes['frame_1']['foo'], sym.something),

                }
            )
        )

        with open('/Users/rdv/Desktop/test.xlsx', 'wb') as stream:
            write_to_stream(
                frames.excel_formula(),
                stream = stream
            )

        system_open('/Users/rdv/Desktop/test.xlsx')
