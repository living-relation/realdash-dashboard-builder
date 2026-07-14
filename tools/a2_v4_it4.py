#!/usr/bin/env python3
"""a2_v4_it4.py - final v4 polish over v4p3r.rd (red needle chosen):
tick dots moved OUTSIDE the arc rings (6px), zone-colored lit states:
dim brass off; lit CREAM in normal zone, AMBER in warn zone, RED via crit
level when the value crosses the arc's critical threshold.
Output: st185_dash_v4.rd (Downloads).
"""
import math
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

DL = r"C:\Users\danie\Downloads"
SRC = DL + r"\v4p3r.rd"
DST = DL + r"\st185_dash_v4.rd"

CREAM = 0xFFF2EAD9
AMBER = 0xFFF2A33C
RED = 0xFFE8482B
DIM = 0xFF564B39
BIG = 9e9

d = Dash2(SRC)

ARC_START, ARC_SWEEP = 220.0, 282.0
BLOCKS = [
    # cx, cy, arc_sz, vmin, vmax, warn, crit, ticks
    (56, 384, 64, 0, 120, 50, 60, [0, 30, 60, 90, 120]),
    (181, 387, 70, 0, 300, 150, 250, [0, 60, 120, 180, 240, 300]),
    (572, 384, 64, 0, 100, 55, 70, [0, 25, 50, 75, 100]),
    (697, 384, 64, 0, 100, None, None, [0, 25, 50, 75, 100]),
]

dots = [g for g in d.gauges
        if g.type == 2 and abs(g.get_rect_px()[2] - 5) < 0.35
        and abs(g.get_rect_px()[3] - 5) < 0.35]
assert len(dots) == 21, len(dots)
k = 0
for cx, cy, sz, vmin, vmax, warn, crit, ticks in BLOCKS:
    r = sz / 2.0 + 4.5
    for tv in ticks:
        frac = (tv - vmin) / float(vmax - vmin)
        ang = math.radians(ARC_START - frac * ARC_SWEEP)
        x = cx + r * math.cos(ang)
        y = cy - r * math.sin(ang)
        dg = dots[k]
        dg.set_rect_px(x - 3, y - 3, 6, 6)
        litc = AMBER if (warn is not None and tv >= warn) else CREAM
        struct.pack_into("<I", dg.b, dg.nend + 0x5C, DIM)
        dg.set_arr(0, [DIM, litc, RED] * 2, flag=0)
        dg.set_ranges(vmin, vmax,
                      warn=(tv if tv > vmin else vmin - 1e-3),
                      crit=(crit if crit is not None else BIG),
                      warn_below=-BIG, crit_below=-BIG)
        k += 1
assert k == 21

n, c = d.save(DST)
print("built %s: %d bytes, %d records" % (DST, n, c))
