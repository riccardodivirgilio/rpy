# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import re

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}
for i in range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))


def replace(match):
    return ESCAPE_DCT[match.group(0)]

def escape(s):
    return '"%s"' % ESCAPE.sub(replace, s)
