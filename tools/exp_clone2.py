#!/usr/bin/env python3
"""exp_clone2.py - clone naming variants:
C: byte-exact duplicate arc (same name) at new position
D: renamed 'Arc Gauge 2' (same name length pattern)
E: renamed 'Arc Gauge 3' placed right AFTER the original in order
"""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, G2

SRC = r"C:\Users\danie\Downloads\probe_base.rd"

d = Dash2(SRC)
m = d.by_name()
orig = m["Arc Gauge 1"]
orig.set_rect_px(20, 300, 120, 140)

c = G2(bytes(orig.b))          # same name, moved
c.set_rect_px(160, 300, 120, 140)

e = orig.clone("Arc Gauge 2")
e.set_rect_px(300, 300, 120, 140)

f = orig.clone("Arc Gauge 3")
f.set_rect_px(440, 300, 120, 140)

# order: insert f right after the original; c and e at end
order = []
for g in d.gauges:
    order.append(g)
    if g.name == "Arc Gauge 1":
        order.append(f)
order += [c, e]
print(d.save(r"C:\Users\danie\Downloads\st185_expc.rd", order=order))
