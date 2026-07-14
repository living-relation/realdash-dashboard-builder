#!/usr/bin/env python3
"""exp_style.py - style all 5 image-type records IN PLACE (no reorder, no
clones, no count change): bind, ranges, autoscale, colors. GO/NO-GO test."""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\probe_base.rd"
d = Dash2(SRC)
m = d.by_name()

CREAM, AMBER, RED = 0xFFE8D9B8, 0xFFF2A33C, 0xFFE8482B
BIG = 9e9

a = m["Arc Gauge 1"]
a.set_rect_px(40, 300, 120, 140)
a.set_hash(0x978E3E78)          # Charge IAT
a.set_decimals(0)
a.set_ranges(0, 120, warn=50, crit=60, warn_below=-99, crit_below=-99)
a.set_autoscale(use_auto=False)
a.replace_level_colors(CREAM, AMBER, RED)

g = m["Graph Gauge 1"]
g.set_rect_px(180, 300, 180, 140)
g.set_hash(0xA5AA7D05)          # Throttle
g.set_decimals(0)
g.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
g.replace_level_colors(0xFF3DAFDC, AMBER, RED)

b = m["Bar Gauge 1"]
b.set_rect_px(380, 300, 180, 30)
b.set_hash(0x9007B539)          # Engine Load
b.set_decimals(0)
b.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
b.replace_level_colors(0xFFC7A25A, AMBER, RED)

n = m["Needle Gauge 1"]
n.set_rect_px(580, 280, 170, 190)
n.set_hash(0x413F90BA)          # Turbo RPM
n.set_decimals(0)
n.set_ranges(0, 200, warn=180, crit=190, warn_below=-BIG, crit_below=-BIG)
n.set_autoscale(maxdig=3, segments=11, midseg=5)

i = m["Image Gauge 1"]
i.set_rect_px(700, 180, 50, 60)
i.set_hash(0xC44AB478)          # Radiator Fan bit
i.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)

print(d.save(r"C:\Users\danie\Downloads\st185_expe.rd"))
