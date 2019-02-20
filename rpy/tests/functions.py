# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from rpy.functions.functional import composition, delete_duplicates


class TestCase(unittest.TestCase):

    def test_composition(self):
        self.assertEqual(
            composition()(1), 
            1
        )
        self.assertEqual(
            composition(lambda s: s+2)(1), 
            3
        )
        self.assertEqual(
            composition(lambda s: s+2, lambda s: s*3)(1), 
            9
        )

    def test_delete_duplicates(self):

        self.assertEqual(
            delete_duplicates(()),
            ()
        )

        self.assertEqual(
            delete_duplicates((1, 1)),
            (1, )
        )

        self.assertEqual(
            delete_duplicates((1, 2, 3, 2, 3, 4)),
            (1, 2, 3, 4)
        )


        self.assertEqual(
            delete_duplicates(
                (
                    {'price': 20, 'mode': 'tomorrow'}, 
                    {'price': 30, 'mode': 'asap'},
                    {'price': 40, 'mode': 'tomorrow'},
                    {'price': 50, 'mode': 'asap'}, 
                    {'price': 10, 'mode': 'asap'}, 
                ),
                key = lambda data: data['mode']
            ), (
                {'price': 20, 'mode': 'tomorrow'}, 
                {'price': 30, 'mode': 'asap'},
            )
        )