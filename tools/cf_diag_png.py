#!/usr/bin/env python3
"""cf_diag_png.py - diagnostic sheet: 9x6 grid, each cell labeled with its
row-major index, distinct border colors, so one load reveals the exact
sampled UV window."""
from PIL import Image, ImageDraw

W, H = 1800, 1080          # divisible by 9 and 6
img = Image.new("RGB", (W, H), (10, 10, 12))
d = ImageDraw.Draw(img)
tw, th = W // 9, H // 6
cols = [(255, 60, 60), (60, 200, 60), (80, 120, 255), (255, 210, 0),
        (0, 220, 220), (255, 0, 255)]
for r in range(6):
    for c in range(9):
        i = r * 9 + c
        x, y = c * tw, r * th
        d.rectangle([x + 2, y + 2, x + tw - 3, y + th - 3],
                    outline=cols[r], width=6)
        d.text((x + tw // 2 - 20, y + th // 2 - 24), str(i),
               fill=(240, 240, 240), font_size=48)
img.save(r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\cf_diag.png")
print("saved diag")
