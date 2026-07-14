#!/usr/bin/env python3
"""Least-squares axis-aligned ellipse fit on ring-line pixels.
Usage: r5_fit_ellipse.py <shot.png> <x0> <y0> <x1> <y1>
Ring line = desaturated gray-blue pixels (the dial's outer circle art).
Fits A x^2 + B y^2 + C x + D y = 1 -> center/semi-axes."""
import sys
from PIL import Image

path, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
im = Image.open(path).convert("RGB")
px = im.load()


def isring(c):
    r, g, b = c
    return (55 < r < 160 and 55 < g < 170 and 60 < b < 190
            and abs(r - g) < 40 and abs(g - b) < 55)


pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if isring(px[x, y])]
print("ring pixels:", len(pts))
# normal equations for [A,B,C,D] with rows [x^2, y^2, x, y] = 1
S = [[0.0] * 4 for _ in range(4)]
T = [0.0] * 4
for (x, y) in pts:
    row = (x * x, y * y, x, y)
    for i in range(4):
        T[i] += row[i]
        for j in range(4):
            S[i][j] += row[i] * row[j]
# gaussian elimination
for i in range(4):
    p = max(range(i, 4), key=lambda r: abs(S[r][i]))
    S[i], S[p] = S[p], S[i]
    T[i], T[p] = T[p], T[i]
    d = S[i][i]
    S[i] = [v / d for v in S[i]]
    T[i] /= d
    for r in range(4):
        if r != i and S[r][i]:
            f = S[r][i]
            S[r] = [a - f * b for a, b in zip(S[r], S[i])]
            T[r] -= f * T[i]
A, B, C, D = T
cx = -C / (2 * A)
cy = -D / (2 * B)
k = 1 + A * cx * cx + B * cy * cy
a = (k / A) ** 0.5
b = (k / B) ** 0.5
print("center=(%.1f,%.1f) a=%.1f b=%.1f ratio a/b=%.4f" % (cx, cy, a, b, a / b))
