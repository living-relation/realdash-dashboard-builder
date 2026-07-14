#!/usr/bin/env python3
"""r4_v2.py - round-4 fixes for st185_dash_v2.rd.

- throttle sweep rebuilt as 16 UNIFORM segments (identical lit/unlit
  geometry): each segment is ONE record, dark cell when below threshold,
  colored when at/above it. No more 3-big-unlit vs 13-lit mismatch.
- Turbo notation: label 'Turbo', chip 'k RPM'
- FAN pill: reachable alarms so the dynamic fill lights
- TRIG ERRORS small tile kept as-is
"""
import struct
from r4_common import Dash2, H, TRANSP, park

SRC = r"C:\Users\danie\Downloads\st185_dash_v2.rd"

d = Dash2(SRC)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]

DARKCELL = 0xFF1C1C1C
YEL = 0xFFFFD400
ORG = 0xFFFF7A00
RED = 0xFFFF3226

# ---------- 1. uniform 16-segment sweep ----------
# track: TG61 outer (2,2 796x40), TG60 inner (4,4 792x36) kept as-is.
# 16 segments, x from 8, width 45, gap 4 (pitch 49), y8 h28.
# gaps after seg 4/8/12 align with the 25/50/75 labels.
seg_recs = [110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
            120, 121, 122, 160, 161, 162]
for k, n in enumerate(seg_recs):
    gg = g(n)
    thresh = max(0.6, k * 6.25)
    lit = YEL if k < 10 else (ORG if k < 13 else RED)
    gg.set_rect_px(8 + 49 * k, 8, 45, 28)
    gg.set_texts("", ["", "", ""])
    struct.pack_into("<I", gg.b, gg.nend + 0x5C, DARKCELL)
    gg.set_arr(0, [DARKCELL, lit, lit] * 2, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(H["throttle"])
    gg.set_decimals(0)
    gg.set_ranges(0, 100, warn=thresh, crit=999,
                  warn_below=-999, crit_below=-999)
park(g(163))   # old WOT block no longer needed

# ---------- 2. Turbo notation ----------
g(27).set_texts("Turbo", ["Turbo"] * 3)
g(136).set_rect_px(94, 396, 84, 20)
g(136).set_texts("k RPM", ["k RPM"] * 3)

# ---------- 3. FAN pill fix ----------
g(4).set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)

n = d.save(SRC)
print("saved v2", n)
