# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from rpy.functions import six


def force_text(s, encoding='utf-8', errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if issubclass(type(s), six.text_type):
        return s
    if not issubclass(type(s), six.string_types):
        if six.PY3:
            if isinstance(s, bytes):
                s = six.text_type(s, encoding, errors)
            else:
                s = six.text_type(s)
        elif hasattr(s, '__unicode__'):
            s = six.text_type(s)
        else:
            s = six.text_type(bytes(s), encoding, errors)
    else:
        # Note: We use .decode() here, instead of six.text_type(s, encoding,
        # errors), so that if s is a SafeBytes, it ends up being a
        # SafeText at the end.
        s = s.decode(encoding, errors)
    return s


def force_bytes(s, encoding='utf-8', errors='strict'):
    """
    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)

    if isinstance(s, six.buffer_types):
        return bytes(s)

    if not isinstance(s, six.string_types):
        try:
            if six.PY3:
                return six.text_type(s).encode(encoding)
            else:
                return bytes(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return b' '.join(
                    force_bytes(arg, encoding, errors=errors) for arg in s)
            return six.text_type(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)


def safe_force_text(obj):
    try:
        return force_text(obj, errors='ignore')
    except Exception as e:
        return '<unprintable obj: %s>' % e
