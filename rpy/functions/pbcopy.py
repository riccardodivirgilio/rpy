from __future__ import absolute_import, print_function, unicode_literals

from rpy.functions.encoding import force_bytes

import subprocess

def pbcopy(text):
    p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    p.stdin.write(force_bytes(text))
    p.stdin.close()
    retcode = p.wait()