#!/usr/bin/env python3
"""cf_strip.py <prefix> <frac_top> <frac_bot> <out.png> [nframes]
Stack a horizontal band from each burst frame into one composite image."""
import glob
import os
import sys
from PIL import Image

SHOTS = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\shots"
prefix, ft, fb, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
files = sorted(glob.glob(os.path.join(SHOTS, prefix + "_f*.png")))
if len(sys.argv) > 5:
    files = files[:int(sys.argv[5])]
bands = []
for f in files:
    im = Image.open(f)
    w, h = im.size
    band = im.crop((0, int(h * ft), w, int(h * fb)))
    band = band.resize((w // 2, band.height // 2))
    bands.append(band)
W = bands[0].width
Hh = sum(b.height for b in bands)
comp = Image.new("RGB", (W, Hh))
y = 0
for b in bands:
    comp.paste(b, (0, y))
    y += b.height
comp.save(os.path.join(SHOTS, out))
print("saved", out, comp.size, len(bands), "bands")
