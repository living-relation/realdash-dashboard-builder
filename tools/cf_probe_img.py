#!/usr/bin/env python3
"""cf_probe_img.py - minimal Plan A probe on probe_base donor.

Build st185_cfprobe.rd: full-screen Image gauge (spliced carbonforge PNG into
_indicators.png_) painted FIRST, followed by ~12 visible text gauges.
If the background + all texts render -> the image-first pipeline is sound
and yesterday's v5 failures come from something else in the big build.
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

DL = r"C:\Users\danie\Downloads"
PNG = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\cf_calib.png"
TRANSP = 0x00000000
UNBOUND = 0xFFFFFFFF
BIG = 9e9

raw = open(DL + r"\probe_base.rd", "rb").read()
png = open(PNG, "rb").read()
name16 = "_indicators.png_".encode("utf-16-le")
ni = raw.find(struct.pack("<I", 16) + name16)
assert ni > 0
size_off = ni + 4 + len(name16)
old_size = struct.unpack_from("<I", raw, size_off)[0]
new_blob = b"\x00\x00\x00\x00" + png
raw = (raw[:size_off] + struct.pack("<I", len(new_blob)) + new_blob +
       raw[size_off + 4 + old_size:])
TMP = DL + r"\_cfp_tmp.rd"
open(TMP, "wb").write(raw)

d = Dash2(TMP)
m = d.by_name()
img = m["Image Gauge 1"]
img.rename("Image Background")
img.set_rect_px(0, 0, 800, 480)
# CONFIRMED-SAFE writes for type 5: rect1, +20 UV, +36 UV2, blend arr,
# hash, ranges. POISON (blank all image types): rect_anchor+72,
# text_end+104/108. (probe3=OK, probe4=+72 killed it)
# Calibration run: leave ALL subframe fields as donor (grid 9x6, index 9,
# uv36 donor); only rect1 + uv20 identity.
struct.pack_into("<4f", img.b, img.rect_anchor + 20, 0.0, 0.0, 1.0, 1.0)
img.set_arr(1, [0xFFFFFFFF] * 6, flag=0)
img.set_hash(UNBOUND)
img.set_ranges(0, 1, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)

# 48 visible text labels: 12 columns x 4 rows (budget test for actives)
texts = [g for g in d.gauges if g.type == 2]
vis = []
grid = [(8 + (i % 6) * 132, 108 + (i // 6) * 40) for i in range(48)]
for i, (x, y) in enumerate(grid):
    g = texts[i]
    g.set_rect_px(x, y, 120, 20)
    g.set_texts("T%d" % (i + 1))
    g.set_fsize_for_h(20)
    struct.pack_into("<I", g.b, g.nend + 0x5C, TRANSP)
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [0xFFF2F4F6] * 6, flag=0)
    g.set_tcolor(0xFFF2F4F6)
    g.set_hash(UNBOUND)
    vis.append(g)
rest = [g for g in texts if g not in vis]
for g in rest:
    g.set_rect_px(797, 0, 2, 2)
    g.set_texts("")
    struct.pack_into("<I", g.b, g.nend + 0x5C, TRANSP)
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [TRANSP] * 6, flag=0)
    g.set_tcolor(TRANSP)
    g.set_hash(UNBOUND)

for nm in ("Arc Gauge 1", "Graph Gauge 1", "Bar Gauge 1", "Needle Gauge 1"):
    g = m[nm]
    g.set_rect_px(797, 0, 2, 2)
    g.set_hash(UNBOUND)

order = ([img] + vis + rest +
         [m["Arc Gauge 1"], m["Graph Gauge 1"], m["Bar Gauge 1"],
          m["Needle Gauge 1"]])
assert len(order) == len(d.gauges)
print(d.save(DL + r"\st185_cfprobe.rd", order=order))
import os
os.remove(TMP)
