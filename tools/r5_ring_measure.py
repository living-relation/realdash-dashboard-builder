#!/usr/bin/env python3
"""Definitive dial-ring ellipse measure.
Usage: r5_ring_measure.py <shot.png> <x0> <y0> <x1> <y1>
Filters ring-line-colored pixels (desaturated gray-blue), computes:
  per-row spans -> a = max_span/2 at row cy_row
  per-col spans -> b = max_span/2 at col cx_col
Reports a, b, ratio. Region must contain the whole ring w/ margin."""
import sys
from PIL import Image

path, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
im = Image.open(path).convert("RGB")
px = im.load()


def isring(c):
    r, g, b = c
    return (55 < r < 160 and 55 < g < 170 and 60 < b < 190
            and abs(r - g) < 40 and abs(g - b) < 55)


mask = {}
for y in range(y0, y1):
    for x in range(x0, x1):
        if isring(px[x, y]):
            mask.setdefault(y, []).append(x)
# horizontal: rows sorted by span; take widest, require both edges inside region
rows = sorted(((xs[-1] - xs[0], y, xs[0], xs[-1]) for y, xs in mask.items()),
              reverse=True)
span, cy, lx, rx = rows[0]
assert lx > x0 + 2 and rx < x1 - 3, "ring clipped horizontally, widen region"
cx = (lx + rx) / 2
# vertical: span of ring pixels in a 3-px column around cx
colys = [y for y, xs in mask.items() if any(abs(x - cx) <= 1.5 for x in xs)]
top, bot = min(colys), max(colys)
assert top > y0 + 2 and bot < y1 - 3, "ring clipped vertically, widen region"
a = span / 2
b = (bot - top) / 2
print("center=(%.1f,%.1f) a=%.1f (x %d..%d) b=%.1f (y %d..%d) ratio=%.4f"
      % (cx, (top + bot) / 2, a, lx, rx, b, top, bot, a / b))
