#!/usr/bin/env python3
"""exp_clone.py - isolate render-stop cause.
A: probe file, NO reorder, NO clones - just move the 5 new gauges to a row.
B: same + 2 arc clones appended at the very end.
"""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\probe_base.rd"

# ---- A ----
d = Dash2(SRC)
m = d.by_name()
m["Arc Gauge 1"].set_rect_px(20, 300, 120, 140)
m["Graph Gauge 1"].set_rect_px(160, 300, 160, 140)
m["Bar Gauge 1"].set_rect_px(340, 300, 160, 40)
m["Needle Gauge 1"].set_rect_px(520, 280, 160, 180)
m["Image Gauge 1"].set_rect_px(700, 300, 60, 70)
print("A:", d.save(r"C:\Users\danie\Downloads\st185_expa.rd"))

# ---- B ----
d = Dash2(SRC)
m = d.by_name()
m["Arc Gauge 1"].set_rect_px(20, 300, 120, 140)
c1 = m["Arc Gauge 1"].clone("Arc Clone A")
c1.set_rect_px(160, 300, 120, 140)
c2 = m["Arc Gauge 1"].clone("Arc Clone B")
c2.set_rect_px(300, 300, 120, 140)
d.gauges.append(c1)
d.gauges.append(c2)
print("B:", d.save(r"C:\Users\danie\Downloads\st185_expb.rd"))
