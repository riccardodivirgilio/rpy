# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from rpy.password.keychain import KeyChain

import tempfile

class TestCase(unittest.TestCase):

    def test_keychain(self):

        f1 = tempfile.mkdtemp()
        
        kc = KeyChain(f1, b'RCxUTuGNXXxmSeYtPxArbIaW3UtSj5cvYxUHgbxXcus=')
        kc.set_secret("foo", {"x": 2})

        self.assertEqual(kc.get_secret("foo"), {"x":2})
