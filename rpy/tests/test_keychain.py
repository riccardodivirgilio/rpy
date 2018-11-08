# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from rpy.password.keychain import KeyChain
from rpy.functions.api import json, fernet

import tempfile
import shutil

class TestCase(unittest.TestCase):

    def credentials(self):
        return tempfile.mkdtemp(), fernet.Fernet.generate_key()

    def test_single_single(self):

        f1, p1 = self.credentials()
        
        kc = KeyChain(f1, p1)
        kc.set_secret("foo", {"x": 2})

        self.assertEqual(kc.get_secret("foo"), {"x":2})

        shutil.rmtree(f1)

    def test_keychain_double(self):

        f1, p1 = self.credentials()
        f2, p2 = self.credentials()
        f3, p3 = self.credentials()
        
        kc = KeyChain(
            {'default': f1, 'sensitive': f2, 'developer': f3},
            {'default': p1, 'sensitive': p2, 'developer': p3},
        )

        
        for secret_name in ('default', 'sensitive', 'developer', None): 

            for value in ({"x": 2}, 4):
                kc.set_secret("name", value, secret_name = secret_name)
                self.assertEqual(
                    kc.get_secret("name", secret_name = secret_name), 
                    value
                )

            self.assertEqual(
                tuple(kc.list_secrets(secret_name = secret_name)),
                ('name', )
            )

        shutil.rmtree(f1)
        shutil.rmtree(f2)
        shutil.rmtree(f3)
