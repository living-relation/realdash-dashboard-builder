#!/usr/bin/env python3
"""Measure a dial's rendered tick-ring ellipse in a screenshot.
Usage: r5_measure_ellipse.py <shot.png> <x0> <y0> <x1> <y1> [thresh]
Crops the box, finds bright pixels, reports width/height/ratio of the
extremes and the ellipse center. Ticks are the outermost bright pixels, so
xmin/xmax give 2a; ymin at the top tick gives b via cy from the side ticks."""
import sys
from PIL import Image

path, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
th = int(sys.argv[6]) if len(sys.argv) > 6 else 190
im = Image.open(path).convert("RGB").crop((x0, y0, x1, y1))
W, H = im.size
px = im.load()
pts = [(x, y) for y in range(H) for x in range(W)
       if px[x, y][0] > th and px[x, y][1] > th and px[x, y][2] > th]
if not pts:
    sys.exit("no bright pixels")
xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
side_l = [p[1] for p in pts if p[0] <= xmin + 3]
side_r = [p[1] for p in pts if p[0] >= xmax - 3]
top_x = [p[0] for p in pts if p[1] <= ymin + 3]
cy = (sum(side_l) / len(side_l) + sum(side_r) / len(side_r)) / 2
cx = sum(top_x) / len(top_x)
a = (xmax - xmin) / 2
b = cy - ymin
print("crop %dx%d bright=%d  xspan=%d yspan=%d" % (W, H, len(pts), xmax - xmin, ymax - ymin))
print("center=(%.1f,%.1f)+crop  a=%.1f b=%.1f  ratio a/b=%.4f" % (cx, cy, a, b, a / b if b else 0))
