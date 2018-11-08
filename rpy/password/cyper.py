# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from Crypto import Random
from Crypto.Cipher import AES

BLOCK_SIZE = 32

def dumps(message, password):
    # passphrase MUST be 16, 24 or 32 bytes long, how can I do that ?
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(password, AES.MODE_CFB, IV)
    return aes.encrypt(message)

def loads(message, password):
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(password, AES.MODE_CFB, IV)
    return aes.decrypt(message)