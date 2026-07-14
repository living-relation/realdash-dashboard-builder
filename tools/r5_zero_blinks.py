#!/usr/bin/env python3
"""Round 5 Task 1 fix: zero EVERY nonzero blink slot on every record of all
nine dashes (permanent rule: FAN/status pills never blink)."""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2

DASHES = [r"C:\Users\danie\Downloads\st185_dash.rd"] + [
    r"C:\Users\danie\Downloads\st185_dash_v%d.rd" % i for i in range(2, 10)]

for path in DASHES:
    d = Dash2(path)
    fixed = []
    for i, g in enumerate(d.gauges):
        try:
            off = g._range_off()
        except Exception:
            continue
        b = struct.unpack_from("<3f", g.b, off + 40)
        if any(abs(x) > 1e-9 for x in b):
            struct.pack_into("<3f", g.b, off + 40, 0.0, 0.0, 0.0)
            fixed.append("[%d]%s" % (i, g.name))
    if fixed:
        n, cnt = d.save(path)
        print(os.path.basename(path), "zeroed:", ", ".join(fixed),
              "-> saved %dB %drec" % (n, cnt))
    else:
        print(os.path.basename(path), "clean")
