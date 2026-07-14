#!/usr/bin/env python3
"""r4_dump.py <file.rd> - compact one-line-per-record dump via rd_lib2."""
import sys, struct
sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, TYPE_NAMES

d = Dash2(sys.argv[1])
print("records=%d header=%d" % (len(d.gauges), len(d.header)))
for i, g in enumerate(d.gauges):
    x, y, w, h = g.get_rect_px()
    try:
        m = g.get_gauge_math()
    except Exception:
        m = "?"
    try:
        h_ = "%08X" % g.get_hash()
    except Exception:
        h_ = "?"
    bg = ""
    if g.type == 2:
        bg = "%08X" % struct.unpack_from("<I", g.b, g.nend + 0x5C)[0]
    tc = "%08X" % struct.unpack_from("<I", g.b, g.text_end + 4)[0]
    print("%3d t%-2d %-16s (%4.0f,%4.0f %4.0fx%3.0f) txt=%-14r m=%-8r h=%s bg=%s tc=%s" % (
        i, g.type, g.name[:16], x, y, w, h, g.text[:14], m, h_, bg, tc))
