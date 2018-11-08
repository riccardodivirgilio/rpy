# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import os

from rpy.functions.api import fernet, json
from rpy.functions.datastructures import data
from rpy.functions.encoding import force_bytes
from rpy.functions.functional import iterate

def _explode_spec(spec):
    if isinstance(spec, dict):
        return spec
    return {'default': spec}


def _parse_settings(locations, passwords):
    locations = _explode_spec(locations)
    passwords = _explode_spec(passwords)

    return {
        key: data(location=locations[key], password=force_bytes(passwords[key]))
        for key in frozenset(iterate(locations.keys(), passwords.keys()))
    }


class KeyChain(object):

    serializer = json
    cypher = fernet

    def __init__(self, locations, passwords):
        self.settings = _parse_settings(locations, passwords)

    def loads(self, payload, password):
        return self.serializer.loads(
            self.cypher.loads(payload, password=password))

    def dumps(self, payload, password):
        return self.cypher.dumps(
            self.serializer.dumps(payload), password=password)

    def get_location(self, secret_name, *paths):
        return os.path.join(self.settings[secret_name or 'default'].location,
                            *paths)

    def get_password(self, secret_name, *paths):
        return self.settings[secret_name or 'default'].password

    def get_secret(self, key, secret_name=None):
        try:
            with open(self.get_location(secret_name, key), 'rb') as f:
                return self.loads(
                    f.read(), 
                    password=self.get_password(secret_name)
                )
        except FileNotFoundError:
            pass

    def delete_secret(self, key, secret_name=None):
        try:
            os.remove(self.get_location(secret_name, key))
        except FileNotFoundError:
            pass

    def set_secret(self, key, payload, secret_name=None):
        with open(self.get_location(secret_name, key), 'wb') as f:
            f.write(
                self.dumps(
                    payload, 
                    password=self.get_password(secret_name)
                )
            )

        return payload

    def list_secrets(self, secret_name=None):
        try:
            for file in os.scandir(self.get_location(secret_name)):
                if not file.is_dir() and not file.name.startswith('.'):
                    yield file.name
        except FileNotFoundError:
            pass
