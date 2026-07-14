#!/usr/bin/env python3
"""exp_clone4.py - can bar/graph/image records be cloned? Keep original
order, insert clones immediately after their parents."""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\probe_base.rd"
d = Dash2(SRC)
m = d.by_name()

m["Bar Gauge 1"].set_rect_px(40, 300, 160, 24)
bar2 = m["Bar Gauge 1"].clone("Bar Gauge 2")
bar2.set_rect_px(40, 340, 160, 24)
bar2.set_hash(0xA5AA7D05)
bar2.set_ranges(0, 100, warn=9e9, crit=9e9, warn_below=-9e9, crit_below=-9e9)

m["Graph Gauge 1"].set_rect_px(240, 300, 160, 100)
gr2 = m["Graph Gauge 1"].clone("Graph Gauge 2")
gr2.set_rect_px(440, 300, 160, 100)
gr2.set_hash(0x9007B539)

m["Image Gauge 1"].set_rect_px(640, 300, 50, 60)
im2 = m["Image Gauge 1"].clone("Image Gauge 2")
im2.set_rect_px(700, 300, 50, 60)

order = []
for g in d.gauges:
    order.append(g)
    if g.name == "Bar Gauge 1":
        order.append(bar2)
    elif g.name == "Graph Gauge 1":
        order.append(gr2)
    elif g.name == "Image Gauge 1":
        order.append(im2)
print(d.save(r"C:\Users\danie\Downloads\st185_expf.rd", order=order))
