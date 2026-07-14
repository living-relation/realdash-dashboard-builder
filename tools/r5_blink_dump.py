#!/usr/bin/env python3
"""Dump EVERY record with any nonzero blink slot on all nine dashes,
with rect + hash + text, to locate what could strobe near the FAN pill."""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2

DASHES = [r"C:\Users\danie\Downloads\st185_dash.rd"] + [
    r"C:\Users\danie\Downloads\st185_dash_v%d.rd" % i for i in range(2, 10)]

for path in DASHES:
    d = Dash2(path)
    hits = []
    for i, g in enumerate(d.gauges):
        try:
            off = g._range_off()
            b = struct.unpack_from("<3f", g.b, off + 40)
        except Exception:
            continue
        if any(abs(x) > 1e-9 for x in b):
            x, y, w, h = g.get_rect_px()
            rng = struct.unpack_from("<7f", g.b, off + 4)
            hits.append("  [%d] t%d %-16s h=%08X r=(%d,%d %dx%d) txt=%r rng(cB,cA,wB,wA,mn,mx)=%s blink=%s"
                        % (i, g.type, g.name[:16], g.get_hash(), x, y, w, h,
                           (g.text or "")[:12],
                           tuple(round(v, 1) for v in rng[:6]),
                           tuple(round(v, 2) for v in b)))
    print(os.path.basename(path), "nonzero-blink records: %d" % len(hits))
    for ln in hits:
        print(ln)
