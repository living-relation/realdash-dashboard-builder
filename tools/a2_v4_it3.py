#!/usr/bin/env python3
"""a2_v4_it3.py - v4 style iteration 3 (over v4p2.rd):
- needle.png recolored to neon (red or blue variant), white-hot core kept
- scale labels cream on both dials (arr2 was tinting labels)
- tick dots: bigger (7px), radius = ring-8, re-laid
Usage: python a2_v4_it3.py red|blue [out.rd]
"""
import math
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2
from PIL import Image

DL = r"C:\Users\danie\Downloads"
ASSETS = (r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan"
          r"\_build\assets\v4_assets")
variant = sys.argv[1] if len(sys.argv) > 1 else "red"
SRC = DL + r"\v4p2.rd"
DST = sys.argv[2] if len(sys.argv) > 2 else DL + (r"\v4p3%s.rd" % variant[0])

NEON = (255, 42, 42) if variant == "red" else (0, 200, 255)
CREAM = 0xFFF2EAD9
TICK_OFF = 0xFF8A7B60      # mid brass: visible on the dark track
TICK_ON = 0xFF1D1812       # dark notch on the lit fill
BIG = 9e9

# ---------- recolor needle sprite ----------
src_img = Image.open(ASSETS + r"\needle.png").convert("RGBA")
px = src_img.load()
w, h = src_img.size
for yy in range(h):
    for xx in range(w):
        r, g, b, a = px[xx, yy]
        if a == 0:
            continue
        lum = (r + g + b) / 765.0
        # tint: keep a white-hot core on the brightest pixels
        if lum > 0.92:
            mix = 0.45
        else:
            mix = 1.0
        nr = int(r * (1 - mix) + NEON[0] * lum * mix)
        ng = int(g * (1 - mix) + NEON[1] * lum * mix)
        nb = int(b * (1 - mix) + NEON[2] * lum * mix)
        px[xx, yy] = (min(nr, 255), min(ng, 255), min(nb, 255), a)
npath = ASSETS + r"\needle_%s.png" % variant
src_img.save(npath, "PNG")
png = open(npath, "rb").read()

raw = open(SRC, "rb").read()
name16 = "needle.png".encode("utf-16-le")
ni = raw.find(struct.pack("<I", 10) + name16)
assert 0 < ni < 400000, "needle asset name not found"
size_off = ni + 4 + len(name16)
old_size = struct.unpack_from("<I", raw, size_off)[0]
new_blob = b"\x00\x00\x00\x00" + png
raw = (raw[:size_off] + struct.pack("<I", len(new_blob)) + new_blob +
       raw[size_off + 4 + old_size:])
TMP = DL + r"\_a2_tmp3.rd"
open(TMP, "wb").write(raw)
print("needle spliced: old=%d new=%d" % (old_size, len(new_blob)))

d = Dash2(TMP)
m = d.by_name()

# ---------- cream labels both dials ----------
m["Needle Throttle"].set_arr(2, [CREAM] * 6, flag=0)
m["Needle Turbo"].set_arr(2, [CREAM] * 6, flag=0)

# ---------- re-lay tick dots ----------
ARC_START, ARC_SWEEP = 220.0, 282.0
BLOCKS = [
    # (cx, cy, arc_sz, vmin, vmax, ticks)
    (56, 384, 64, 0, 120, [0, 30, 60, 90, 120]),
    (181, 387, 70, 0, 300, [0, 60, 120, 180, 240, 300]),
    (572, 384, 64, 0, 100, [0, 25, 50, 75, 100]),
    (697, 384, 64, 0, 100, [0, 25, 50, 75, 100]),
]
# dots are the bound 5x5 records around each center; find by size+bg
dots = [g for g in d.gauges
        if g.type == 2 and abs(g.get_rect_px()[2] - 5) < 0.35
        and abs(g.get_rect_px()[3] - 5) < 0.35]
print("found %d dot records" % len(dots))
assert len(dots) == 21, len(dots)
k = 0
for cx, cy, sz, vmin, vmax, ticks in BLOCKS:
    r = sz / 2.0 - 5.5        # centered under the arc ring -> notch look
    for tv in ticks:
        frac = (tv - vmin) / float(vmax - vmin)
        ang = math.radians(ARC_START - frac * ARC_SWEEP)
        x = cx + r * math.cos(ang)
        y = cy - r * math.sin(ang)
        dg = dots[k]
        dg.set_rect_px(x - 2.5, y - 2.5, 5, 5)
        struct.pack_into("<I", dg.b, dg.nend + 0x5C, TICK_OFF)
        dg.set_arr(0, [TICK_OFF, TICK_ON, TICK_ON] * 2, flag=0)
        k += 1
assert k == 21

n, c = d.save(DST)
print("built %s: %d bytes, %d records" % (DST, n, c))
import os
os.remove(TMP)
