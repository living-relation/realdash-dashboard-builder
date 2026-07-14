#!/usr/bin/env python3
"""b2_badge_gen.py - v8 badge sheet from imported Corsa logo art.

Crops the PASNY MOTORSPORTS band from corsa_CORSA_BG.png, converts it to
white-on-transparent (luminance -> alpha) so the image gauge's per-level
blend colors can tint it, and ships it as frame 1 of a 1x12 sheet PNG
(the donor Image Gauge samples the top 1/12 statically).
Output: _build/b2_badge_sheet.png (880x1200 RGBA).
"""
from PIL import Image

BUILD = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build"
SRC = BUILD + r"\assets\imported\corsa_CORSA_BG.png"
OUT = BUILD + r"\b2_badge_sheet.png"

im = Image.open(SRC).convert("RGBA")
crop = im.crop((30, 8, 470, 58))                    # 440x50 logo band
crop = crop.resize((880, 100), Image.LANCZOS)

# white extraction: alpha = luminance (black bg -> transparent)
px = crop.load()
for y in range(100):
    for x in range(880):
        r, g, b, a = px[x, y]
        lum = int(0.299 * r + 0.587 * g + 0.114 * b)
        alpha = 0 if lum < 28 else min(255, int((lum - 28) * 255 / 180))
        px[x, y] = (255, 255, 255, min(alpha, a))

sheet = Image.new("RGBA", (880, 1200), (0, 0, 0, 0))
sheet.paste(crop, (0, 0))
sheet.save(OUT, "PNG")
print("saved", OUT, sheet.size)
