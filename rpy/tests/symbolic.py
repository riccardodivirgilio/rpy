# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from rotostampa.utils.symbolic import evaluate, sym


class SymbolicTest(unittest.TestCase):

    def test_symbolic(self):

        for expr, context, result in (
            (sym.x + 2,             {'x': 2}, 4),
            (sym.int(sym.x),        {'x': 3.2}, 3),
            (sym.x + sym.z + sym.y, {'x': sym.y, 'y': 4, 'z': 2}, 10),
            (sym.x(2, 3, 4),        {'x': lambda a, b, c: a + b + c}, 9),
            (sym.x.join(['ciao', 'bella']), {'x': ', '}, 'ciao, bella'),
            (sym.x['foo'], {'x': {'foo': 2}}, 2),
            (sym.x[2:3], {'x': [1, 2, 3, 4, 5]}, [3]),
            ):

            self.assertEqual(evaluate(expr), expr)
            self.assertEqual(evaluate(expr, context), result)
