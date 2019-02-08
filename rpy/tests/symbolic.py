# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from rpy.dataframe.symbolic import evaluate, sym


class SymbolicTest(unittest.TestCase):

    def test_symbolic(self):

        for expr, context, result in (
            (sym.x + 2,             {'x': 2}, 4),
            (sym.int(sym.x),        {'x': 3.2}, 3),
            (sym.float(sym.x),      {'x': 3}, 3.),
            (sym.x + sym.z + sym.y, {'x': sym.y - 2, 'y': sym.z * 4, 'z': 2}, 16),
            (sym.x(2, 3, 4),        {'x': lambda a, b, c: a + b + c}, 9),
            (sym.x.join(['ciao', 'bella']), {'x': ', '}, 'ciao, bella'),
            (sym.x['foo'], {'x': {'foo': 2}}, 2),
            (sym.x[2:3], {'x': [1, 2, 3, 4, 5]}, [3]),
            (sym.sum(sym.x), {'x': [1, 2, 3]}, 6),
            ):
            self.assertEqual(evaluate(expr), expr)
            self.assertEqual(evaluate(expr, context), result)
