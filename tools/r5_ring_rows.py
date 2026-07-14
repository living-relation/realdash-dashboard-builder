#!/usr/bin/env python3
"""Robust dial-ring measurement from horizontal row scans.
Usage: r5_ring_rows.py <shot.png> <x0> <x1> <y0> <y1> <expected_cx> [tol]
For each row, take leftmost/rightmost ring-line pixels; keep rows whose
midpoint is within tol of expected_cx (rejects text pollution). Fit
half-span(y) = a*sqrt(1-((y-cy)/b)^2) by least squares over (cy, a, b)."""
import sys
from PIL import Image

path = sys.argv[1]
x0, x1, y0, y1, ecx = map(int, sys.argv[2:7])
tol = int(sys.argv[7]) if len(sys.argv) > 7 else 15
im = Image.open(path).convert("RGB")
px = im.load()


def isring(c):
    r, g, b = c
    return (55 < r < 160 and 55 < g < 170 and 60 < b < 190
            and abs(r - g) < 40 and abs(g - b) < 55)


rows = []
for y in range(y0, y1):
    xs = [x for x in range(x0, x1) if isring(px[x, y])]
    if len(xs) < 2:
        continue
    mid = (xs[0] + xs[-1]) / 2
    if abs(mid - ecx) <= tol and xs[-1] - xs[0] > 30:
        rows.append((y, (xs[-1] - xs[0]) / 2))

best = None
ys = [r[0] for r in rows]
for cy10 in range(min(ys) * 10, max(ys) * 10):
    cy = cy10 / 10.0
    # given cy, linear LSQ for a^2 and (a/b)^2: h^2 = a^2 - (a/b)^2 (y-cy)^2
    su = sv = suu = suv = 0.0
    n = len(rows)
    for (y, h) in rows:
        u = (y - cy) ** 2
        v = h * h
        su += u; sv += v; suu += u * u; suv += u * v
    den = n * suu - su * su
    if not den:
        continue
    m = (n * suv - su * sv) / den          # slope = -(a/b)^2
    c0 = (sv - m * su) / n                 # intercept = a^2
    if m >= 0 or c0 <= 0:
        continue
    err = 0.0
    for (y, h) in rows:
        pred = c0 + m * (y - cy) ** 2
        err += (pred - h * h) ** 2
    if best is None or err < best[0]:
        a2 = c0
        b2 = -c0 / m
        best = (err, cy, a2 ** 0.5, b2 ** 0.5)
err, cy, a, b = best
print("rows used: %d (y %d..%d)" % (len(rows), min(ys), max(ys)))
print("cy=%.1f a=%.2f b=%.2f ratio a/b=%.4f" % (cy, a, b, a / b))
