# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import hashlib
import hmac
import os

from rpy.cli.utils import SimpleCommand
from rpy.functions.api import base64, fernet
from rpy.functions.encoding import force_bytes, force_text
from rpy.password.keychain import KeyChain
from rpy.functions.pbcopy import pbcopy as _pbcopy

def validate(s, env, name):
    if not s:
        try:
            return os.environ[env]
        except KeyError:
            raise argparse.ArgumentTypeError(
                '%s is not defined, please use --%s or set an %s in your env' %
                (name, name, env))
    return s

class Command(SimpleCommand):

    dependencies = (('cryptography', None), )

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*', type=str)
        parser.add_argument('--password', dest='default_password', default=None)
        parser.add_argument('--location', dest='default_location', default='~/.passwords/')
        parser.add_argument('--hashkey',  dest='default_hashkey', default=None)

        parser.add_argument('--delete',  dest='delete', default=False, action = 'store_true')
        parser.add_argument('--renew',   dest='renew',  default=False, action = 'store_true')

    def default_secret(self, name, password):
        return "!%s" % force_text(
            base64.dumps(hmac.new(
                key = force_bytes(password),
                msg = force_bytes(name), 
                digestmod=hashlib.sha1
                ).digest())
            )

    def new_secret(self, name):
        return "!%s=" % force_text(fernet.Fernet.generate_key()[0:27])

    def pbcopy(self, text):
        self.print('Copied to clipboard:', text)
        return _pbcopy(text)

    def handle(self, name = None, new_password = None, default_password = None, default_location = None, default_hashkey = None, delete = False, renew = False, pbcopy = False, **opts):

        location = validate(default_location or '~/.passwords/', 'PASS_DEFAULT_LOCATION', name='location')
        password = validate(default_password, 'PASS_DEFAULT_PASSWORD', name='password')
        hashkey  = validate(default_hashkey or default_password, 'PASS_DEFAULT_HASHKEY', name='default_hashkey')

        kc = KeyChain(os.path.expanduser(location), password)

        if name and new_password:
            old = kc.get_secret(name)
            if old and not old == new_password:
                self.print('Previous secret for %s:' % name, old)
            self.pbcopy(kc.set_secret(name, new_password))
        elif name:
            if delete:
                old = kc.get_secret(name)
                if old:
                    self.print('Previous secret for %s:' % name, old)
                kc.delete_secret(name)
                self.pbcopy(self.default_secret(name, password))
            elif renew:
                self.pbcopy(kc.set_secret(name, self.new_secret(name)))
            else:
                self.pbcopy(kc.get_secret(name) or self.default_secret(name, password))
        else:
            for name in kc.list_secrets():
                self.print(name)