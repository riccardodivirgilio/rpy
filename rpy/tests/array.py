from __future__ import absolute_import, print_function, unicode_literals

from rpy.functions.api import numpy

import unittest

class TestCase(unittest.TestCase):
    def compare_array(self, a1, a2):

        t = a1 == a2
        if hasattr(t, "all"):
            t = t.all()

        return self.assertTrue(t, "%s vs %s" % (a1, a2))

    def test_map(self):

        # identity
        self.compare_array(numpy.map(lambda x: x, numpy.arange(10)), numpy.arange(10))

        # constant array
        self.compare_array(numpy.map(lambda x: 2, numpy.arange(10)), numpy.full(10, 2))

        # double array
        self.compare_array(
            numpy.map(lambda x: [x, 2.0], numpy.arange(10)),
            numpy.core.records.fromarrays((numpy.arange(10), numpy.full(10, 2.0))),
        )

        # double array
        self.compare_array(
            numpy.map(lambda x: {"a": x, "b": 2.0}, numpy.arange(10)),
            numpy.core.records.fromarrays(
                (numpy.arange(10), numpy.full(10, 2.0)), names=("a", "b")
            ),
        )

        # double map
        self.compare_array(
            numpy.map(
                lambda x: x.a + x.b, numpy.map(lambda x: {"a": x, "b": 2.0}, numpy.arange(10))
            ),
            numpy.arange(10) + 2.0,
        )

    def test_filter(self):

        self.compare_array(numpy.filter(lambda x: x < 3, numpy.arange(10)), numpy.arange(3))

        # identity
        self.compare_array(
            numpy.filter(
                lambda x: x.a < 3, numpy.map(lambda x: {"a": x, "b": 2.0}, numpy.arange(10))
            ),
            numpy.map(lambda x: {"a": x, "b": 2.0}, numpy.arange(3)),
        )