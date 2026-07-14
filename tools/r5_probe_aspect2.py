#!/usr/bin/env python3
"""Aspect probe 2: apply candidate compensation h = w * 1.708 at two sizes,
centers preserved, to verify circular render + vertical linearity."""
import shutil
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\st185_dash_v9.rd"
OUT = r"C:\Users\danie\Downloads\r5_probe_aspect.rd"
shutil.copy(SRC, OUT)
d = Dash2(OUT)
K = 1.7082
tests = {"Needle Load": 140.0, "Needle Turbo": 170.0}
for g in d.gauges:
    if g.name in tests:
        x, y, w, h = g.get_rect_px()
        nw = tests[g.name]
        nh = nw * K
        cx, cy = x + w / 2, y + h / 2
        g.set_rect_px(cx - nw / 2, cy - nh / 2, nw, nh)
        print(g.name, "-> w=%.0f h=%.1f center=(%.0f,%.0f)" % (nw, nh, cx, cy))
d.save(OUT)
print("saved", OUT)
