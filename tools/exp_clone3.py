#!/usr/bin/env python3
"""exp_clone3.py - differential: restyled clone vs plain clone, both right
after the original, total records kept at 128 (drop Text Gauge 200)."""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\probe_base.rd"

d = Dash2(SRC)
m = d.by_name()
orig = m["Arc Gauge 1"]
orig.set_rect_px(20, 300, 120, 140)

styled = orig.clone("Arc CoolP")
styled.set_rect_px(160, 300, 120, 140)
styled.set_hash(0xDD266D22)
styled.set_decimals(0)
styled.set_ranges(0, 300, warn=150, crit=250, warn_below=-9e9, crit_below=-9e9)
styled.set_autoscale(use_auto=False)
styled.replace_level_colors(0xFFE8D9B8, 0xFFF2A33C, 0xFFE8482B)

plain = orig.clone("Arc Gauge 4")
plain.set_rect_px(300, 300, 120, 140)

order = []
for g in d.gauges:
    if g.name == "Text Gauge 200":
        continue
    order.append(g)
    if g.name == "Arc Gauge 1":
        order += [styled, plain]
print(d.save(r"C:\Users\danie\Downloads\st185_expd.rd", order=order))
