#!/usr/bin/env python3
"""Measure bounding boxes of specific colors in a screenshot region."""
import sys
from PIL import Image

path = sys.argv[1]
target = sys.argv[2]  # hex RRGGBB
tol = int(sys.argv[3]) if len(sys.argv) > 3 else 20
x0, y0, x1, y1 = (int(v) for v in sys.argv[4:8]) if len(sys.argv) > 7 else (0, 0, 10**6, 10**6)

tr = int(target[0:2], 16)
tg = int(target[2:4], 16)
tb = int(target[4:6], 16)

im = Image.open(path).convert("RGB")
W, H = im.size
px = im.load()
minx, miny, maxx, maxy, count = 10**6, 10**6, -1, -1, 0
for y in range(max(0, y0), min(H, y1)):
    for x in range(max(0, x0), min(W, x1)):
        r, g, b = px[x, y]
        if abs(r - tr) <= tol and abs(g - tg) <= tol and abs(b - tb) <= tol:
            count += 1
            minx = min(minx, x)
            miny = min(miny, y)
            maxx = max(maxx, x)
            maxy = max(maxy, y)
if count:
    print("color %s: bbox x %d..%d (w %d), y %d..%d (h %d), %d px" % (
        target, minx, maxx, maxx - minx + 1, miny, maxy, maxy - miny + 1, count))
else:
    print("color %s not found" % target)
