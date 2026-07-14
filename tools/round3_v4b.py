#!/usr/bin/env python3
"""round3_v4b.py - v4 CRUISE / A-C active-state fix.

Stage-1 finding: v4's CRUISE (Text Gauge 45) and A/C (Text Gauge 46) header
tiles are enum-bound text gauges baked '---' -> they render blank when the
state changes (enum text never arrives in sim/offline). Fix like v1-v3:
repurpose them into lit fill blocks (text cleared, per-level backgrounds).

v4 'Podium Classic' palette: dark chip well when off; CRUISE dim brass at
STBY (warn>=0.5), bright amber at SET/RES/OVR (crit>=1.5); A/C bright amber
at REQ/ON (warn>=0.5), red at FLT (crit>=2.5).
Backup: _build/backup/st185_dash_v4_20260707_2015_pre_cruisefix.rd
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

DL = r"C:\Users\danie\Downloads"
WELL = 0xFF1A1512          # darker than the chip 0xFF262019
DIMBRASS = 0xFF7A6A4C
AMBER = 0xFFF2A33C
RED = 0xFFE8482B
TRANSP = 0x00000000
BIG = 9e9

d = Dash2(DL + r"\st185_dash_v4.rd")
m = d.by_name()


def lit_block(nm, x, y, w, h, warn, crit, bgs):
    g = m[nm]
    g.set_rect_px(x, y, w, h)
    g.set_texts("")
    struct.pack_into("<I", g.b, g.nend + 0x5C, bgs[0])
    g.set_arr(0, bgs * 2, flag=0)
    g.set_arr(2, [TRANSP] * 6, flag=0)
    g.set_tcolor(TRANSP)
    g.set_decimals(0)
    g.set_ranges(0, 4, warn=warn, crit=crit, warn_below=-BIG, crit_below=-BIG)


# keep rects/bindings, swap text->fill block
lit_block("Text Gauge 45", 396, 12, 90, 24, 0.5, 1.5, [WELL, DIMBRASS, AMBER])
lit_block("Text Gauge 46", 656, 12, 90, 24, 0.5, 2.5, [WELL, AMBER, RED])

assert len(d.gauges) == 128, len(d.gauges)
print("v4:", d.save(DL + r"\st185_dash_v4.rd"))
