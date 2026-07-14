#!/usr/bin/env python3
"""Round 5 Task 3: make v9's two hidden-bezel dials render circular.
Canvas renders at exactly 1920x1000 px => x-scale 2.4, y-scale 2.08333
px/design-unit. Circular rendering needs h_design = K*w_design,
K = 2.4/2.08333 = 1.152. Dials sized to clear the header rulebar (y 52-54):
ring semi-v = 0.9465*h/2 <= 117 -> w=214, h=246.5, centers preserved."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2

K = 1.152
PATH = r"C:\Users\danie\Downloads\st185_dash_v9.rd"
d = Dash2(PATH)
W = 214.0
H = W * K
for g in d.gauges:
    if g.name in ("Needle Load", "Needle Turbo"):
        x, y, w, h = g.get_rect_px()
        cx, cy = x + w / 2, y + h / 2
        g.set_rect_px(cx - W / 2, cy - H / 2, W, H)
        print(g.name, "(%.0f,%.0f %.0fx%.0f) -> (%.1f,%.1f %.1fx%.1f)"
              % (x, y, w, h, cx - W / 2, cy - H / 2, W, H))
n, c = d.save(PATH)
print("saved %d bytes %d records" % (n, c))
