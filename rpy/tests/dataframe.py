# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from rpy.dataframe.frames import DataFrame


class DataframeTest(unittest.TestCase):

    def test_dataframe_slice(self):

        frame = DataFrame([1, 2, 3], columns = (
            lambda i: i,
            lambda i: i+2,
            dict(function = lambda i: i+4, name = 'last'),
        ))
        self.assertEqual(frame[0], (1, 2, 3))
        self.assertEqual(frame[1], (3, 4, 5))
        self.assertEqual(frame['last'], (5, 6, 7))
        self.assertEqual(frame['last'][0], 5)

        frame = DataFrame([1, 2, 3], columns = {
            'foo': lambda i: i+4,
            'bar': lambda i: i+6,
        })

        self.assertEqual(frame['foo'], (5, 6, 7))
        self.assertEqual(frame['bar'], (7, 8, 9))

    def test_dataframe_symbolic(self):

        frame = DataFrame([1, 2, 3], columns = {
            'foo': lambda i: i+4,
            'bar': lambda i: i+6,
        })