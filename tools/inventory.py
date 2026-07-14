#!/usr/bin/env python3
"""inventory.py <file.rd> - one-line-per-gauge inventory using rd_lib2."""
import sys
import struct
from rd_lib2 import Dash2

d = Dash2(sys.argv[1])
print("header=%d bytes, %d gauges" % (len(d.header), len(d.gauges)))
for i, g in enumerate(d.gauges):
    x, y, w, h = g.get_rect_px()
    try:
        hsh = g.get_hash()
        dec = struct.unpack_from("<I", g.b, g._arr_marker() - 8)[0]
    except Exception:
        hsh, dec = None, None
    print("%3d t%-2d %-22s px(%3.0f,%3.0f %3.0fx%3.0f) hash=%s dec=%s text=%r st=%r" % (
        i, g.type, g.name, x, y, w, h,
        ("%08X" % hsh) if hsh is not None else "?", dec,
        g.text[:20],
        None))
