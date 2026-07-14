#!/usr/bin/env python3
"""Aspect probe: copy v9 to a throwaway, set the two dials to different
test widths (center preserved), for empirical a(w) measurement."""
import shutil
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\st185_dash_v9.rd"
OUT = r"C:\Users\danie\Downloads\r5_probe_aspect.rd"
shutil.copy(SRC, OUT)
d = Dash2(OUT)
tests = {"Needle Load": 135.0, "Needle Turbo": 160.0}
for g in d.gauges:
    if g.name in tests:
        x, y, w, h = g.get_rect_px()
        nw = tests[g.name]
        g.set_rect_px(x + (w - nw) / 2, y, nw, h)
        print(g.name, "w %.0f -> %.0f (center kept)" % (w, nw))
d.save(OUT)
print("saved", OUT)
