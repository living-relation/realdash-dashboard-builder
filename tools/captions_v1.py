#!/usr/bin/env python3
"""captions_v1.py - add static caption texts to v1 (lambda + enum legends)."""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib import Dash

SRC = r"C:\Users\danie\Downloads\st185_dash.rd"

d = Dash(SRC)
m = d.by_name()
DIM = 0xFF9FB1C6
DIMMER = 0xFF6E8199
TRANSP = 0x00000000

names = {g.name for g in d.gauges}
if "Text Gauge 200" in names:
    print("captions already present, skipping")
    sys.exit(0)


def make_caption(name, x, y, w, h, text, color):
    g = m["Text Gauge 23"].clone(name)   # unbound static label as template
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    g.set_fsize_for_h(h)
    g.set_bg_states(TRANSP, TRANSP)
    g.set_tc_states(color, color)
    return g


caps = []
# lambda tile (TG12 panel at 586,65 canvasish -> design tile x601? use panel rect)
x, y, w, h = m["Text Gauge 12"].get_rect_px()
caps.append(make_caption("Text Gauge 200", x + 10, y + h - 17, w - 20, 10, "TUNE TARGET", DIMMER))

# cruise legend (panel TG20)
x, y, w, h = m["Text Gauge 20"].get_rect_px()
caps.append(make_caption("Text Gauge 201", x + 10, y + h - 17, w - 20, 10,
                         "0 OFF   1 STBY   2 SET   3 RES   4 OVR", DIMMER))

# A/C legend (panel TG21)
x, y, w, h = m["Text Gauge 21"].get_rect_px()
caps.append(make_caption("Text Gauge 202", x + 10, y + h - 17, w - 20, 10,
                         "0 OFF   1 REQ   2 ON   3 FLT", DIMMER))

d.gauges.extend(caps)
n, c = d.save(SRC)
print("saved %d bytes, %d gauges" % (n, c))
