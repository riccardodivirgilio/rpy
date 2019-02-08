# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from rpy.dataframe.frames import DataFrame


class DataframeTest(unittest.TestCase):

    def test_dataframe(self):

        print()

        frame = DataFrame([1, 2, 3], columns = (
            lambda i: i,
            lambda i: i+2,
            lambda i: i+4,
            ))

        print(frame[0][0])
