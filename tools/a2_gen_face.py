#!/usr/bin/env python3
"""a2_gen_face.py - repaint roundface.png for v4 style iteration 2:
modern slim bezel, matte near-black face, 5 baked major ticks + 3 minors
per gap, red warn band over the last major gap's upper part (93.75%..100%
of scale = 150k..160k on the turbo dial). 972x972 RGBA like the donor.

Scale geometry (verified on probe shot): angle(v) = 225 deg - frac*270 deg
(math convention, 0=east, CCW+). Majors at frac 0,.25,.5,.75,1.
"""
import math
from PIL import Image, ImageDraw

SZ = 972
C = SZ / 2.0
R = SZ / 2.0
OUT = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\assets\v4_assets\roundface_v2.png"

img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

BEZEL = (0x24, 0x26, 0x2C, 255)
BEZEL_HI = (0x40, 0x44, 0x4E, 255)
FACE = (0x0B, 0x0B, 0x0D, 255)
MAJOR = (0xE8, 0xE8, 0xEC, 255)
MINOR = (0x62, 0x66, 0x6E, 255)
RED = (0xE8, 0x32, 0x1E, 255)
HUB = (0x15, 0x16, 0x19, 255)
HUB_RING = (0x2E, 0x31, 0x38, 255)


def xy(deg, r):
    a = math.radians(deg)
    return (C + r * math.cos(a), C - r * math.sin(a))


# slim bezel ring + matte face
d.ellipse([C - 478, C - 478, C + 478, C + 478], fill=BEZEL)
d.ellipse([C - 462, C - 462, C + 462, C + 462], fill=FACE)
# subtle top-light on the bezel (thin arc highlight)
d.arc([C - 474, C - 474, C + 474, C + 474], 200, 340, fill=BEZEL_HI, width=5)

# red warn band: frac 0.9375 -> 1.0  (150k..160k / throttle WOT zone)
a_hi = 225 - 0.9375 * 270        # -28.125 deg
a_end = 225 - 1.0 * 270          # -45 deg
# PIL arc: angles measured CW from 3 o'clock; convert: pil = -math_deg
band_r0, band_r1 = 396, 452
for rr in range(band_r0, band_r1):
    d.arc([C - rr, C - rr, C + rr, C + rr], -a_hi, -a_end, fill=RED, width=2)


def tick(deg, r0, r1, w, color):
    p0, p1 = xy(deg, r0), xy(deg, r1)
    d.line([p0, p1], fill=color, width=w)
    d.ellipse([p0[0] - w / 2, p0[1] - w / 2, p0[0] + w / 2, p0[1] + w / 2], fill=color)
    d.ellipse([p1[0] - w / 2, p1[1] - w / 2, p1[0] + w / 2, p1[1] + w / 2], fill=color)


for k in range(5):
    tick(225 - k * 67.5, 380, 452, 15, MAJOR)
for k in range(4):
    for j in range(1, 4):
        tick(225 - k * 67.5 - j * 16.875, 416, 452, 6, MINOR)

# hub seat
d.ellipse([C - 46, C - 46, C + 46, C + 46], fill=HUB)
d.ellipse([C - 46, C - 46, C + 46, C + 46], outline=HUB_RING, width=4)

img.save(OUT, "PNG")
print("saved", OUT)
