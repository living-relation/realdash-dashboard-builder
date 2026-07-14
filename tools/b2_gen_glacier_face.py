#!/usr/bin/env python3
"""b2_gen_glacier_face.py - v9 GLACIER hidden-bezel roundface.png (972x972).

No bezel ring, fully transparent face: the dial 'floats' on the canvas.
Ice-white majors (5, matching seg=5 scales on both dials), steel minors,
hairline outer arc, crimson tip band (last 6.25% = 150-160k turbo /
94-100% load), dark hub w/ steel ring.
Geometry proven by A2: angle(v) = 225 - frac*270 deg (math conv).
"""
import math
from PIL import Image, ImageDraw

SZ = 972
C = SZ / 2.0
OUT = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\b2_glacier_face.png"

img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

MAJOR = (0xE9, 0xF2, 0xF8, 255)
MINOR = (0x4A, 0x58, 0x66, 255)
HAIR = (0x3A, 0x46, 0x52, 255)
RED = (0xFF, 0x30, 0x40, 255)
HUB = (0x10, 0x16, 0x1D, 255)
HUB_RING = (0x3E, 0x4C, 0x5A, 255)


def xy(deg, r):
    a = math.radians(deg)
    return (C + r * math.cos(a), C - r * math.sin(a))


def tick(deg, r0, r1, w, color):
    p0, p1 = xy(deg, r0), xy(deg, r1)
    d.line([p0, p1], fill=color, width=w)
    d.ellipse([p0[0] - w / 2, p0[1] - w / 2, p0[0] + w / 2, p0[1] + w / 2],
              fill=color)
    d.ellipse([p1[0] - w / 2, p1[1] - w / 2, p1[0] + w / 2, p1[1] + w / 2],
              fill=color)


# hairline outer arc along the 270-deg sweep (structure without a bezel)
# math 225..-45 deg -> PIL CW angles -225..45 => draw from -225 to 45
for rr in (458, 459, 460):
    d.arc([C - rr, C - rr, C + rr, C + rr], -225, 45, fill=HAIR, width=2)

# crimson tip band: frac 0.9375 -> 1.0
a_hi = 225 - 0.9375 * 270
a_end = 225 - 1.0 * 270
for rr in range(400, 452):
    d.arc([C - rr, C - rr, C + rr, C + rr], -a_hi, -a_end, fill=RED, width=2)

# 5 majors + 3 minors per gap
for k in range(5):
    tick(225 - k * 67.5, 384, 452, 14, MAJOR)
for k in range(4):
    for j in range(1, 4):
        tick(225 - k * 67.5 - j * 16.875, 420, 452, 5, MINOR)

# hub
d.ellipse([C - 44, C - 44, C + 44, C + 44], fill=HUB)
d.ellipse([C - 44, C - 44, C + 44, C + 44], outline=HUB_RING, width=4)

img.save(OUT, "PNG")
print("saved", OUT)
