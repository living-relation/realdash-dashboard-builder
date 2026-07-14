#!/usr/bin/env python3
"""v10 iteration 2 (edits st185_dash_v10.rd in place):
- needle.png tinted copper (luminance-preserving multiply) + splice
- k RPM chip moved under the readout (was overlapping the 160 major)
- TURBO caption/readout re-stacked
- MERIDIAN badge nudged up (subtitle collided with CRUISE row)
"""
import struct
import sys
import os
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rd_lib2 import Dash2, read_str

BUILD = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build"
PATH = r"C:\Users\danie\Downloads\st185_dash_v10.rd"
NEEDLE_OUT = BUILD + r"\r5_needle_copper.png"

raw = open(PATH, "rb").read()
n16 = "needle.png".encode("utf-16-le")
i = raw.find(struct.pack("<I", 10) + n16)
assert i > 0
so = i + 4 + len(n16)
size = struct.unpack_from("<I", raw, so)[0]
png = raw[so + 8: so + 4 + size]
open(BUILD + r"\r5_needle_orig.png", "wb").write(png)

im = Image.open(BUILD + r"\r5_needle_orig.png").convert("RGBA")
px = im.load()
CR, CG, CB = 0xD9, 0x8F, 0x4E   # bright copper
for y in range(im.size[1]):
    for x in range(im.size[0]):
        r, g, b, a = px[x, y]
        lum = (r * 299 + g * 587 + b * 114) // 1000
        px[x, y] = (lum * CR // 255, lum * CG // 255, lum * CB // 255, a)
im.save(NEEDLE_OUT, "PNG")
print("needle tinted", im.size)

d = Dash2(PATH)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]


def splice_asset(dash, name, png_path):
    hh = bytes(dash.header)
    j = 0
    while j < len(hh) - 8:
        r = read_str(hh, j)
        if r and r[0] == name:
            size_off = r[1]
            old = struct.unpack_from("<I", hh, size_off)[0]
            blob = b"\x00\x00\x00\x00" + open(png_path, "rb").read()
            dash.header = bytearray(
                hh[:size_off] + struct.pack("<I", len(blob)) + blob
                + hh[size_off + 4 + old:])
            return old, len(blob)
        j += 1
    raise KeyError(name)


print("needle spliced:", splice_asset(d, "needle.png", NEEDLE_OUT))

# dial center stack: TURBO / value / k RPM (all inside bottom gap)
g(70).set_rect_px(352, 256, 96, 11)          # TURBO label
g(40).set_rect_px(340, 270, 120, 36)         # readout
g(73).set_rect_px(365, 310, 70, 13)          # k RPM chip under readout

# badge up, clear of CRUISE row
g(31).set_rect_px(20, 388, 170, 14)
g(28).set_rect_px(20, 405, 170, 8)

n, c = d.save(PATH)
print("saved %d bytes %d records" % (n, c))
