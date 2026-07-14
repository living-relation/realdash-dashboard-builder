#!/usr/bin/env python3
"""cf_calib_png.py - calibration sheet 7200x2880 (9x6 tiles of 800x480).
Tile 8 (row0,col8: x 6400..7200, y 0..480) carries a measurable pattern:
- 8px red frame exactly on the tile boundary
- green vertical lines every 100px (tile-local), labeled 0..8
- cyan horizontal lines every 100px, labeled 0..4
Everything else flat black.
"""
from PIL import Image, ImageDraw

W, H = 7200, 2880
TX, TY, TW, TH = 6400, 0, 800, 480
img = Image.new("RGB", (W, H), (0, 0, 0))
d = ImageDraw.Draw(img)
d.rectangle([TX, TY, TX + TW - 1, TY + TH - 1], outline=(255, 40, 40), width=8)
for i in range(1, 8):
    x = TX + i * 100
    d.line([x, TY, x, TY + TH - 1], fill=(40, 220, 40), width=3)
    d.text((x + 6, TY + 200), str(i), fill=(230, 230, 230), font_size=40)
for j in range(1, 5):
    y = TY + j * 100
    d.line([TX, y, TX + TW - 1, y], fill=(40, 200, 220), width=3)
    d.text((TX + 360, y + 6), chr(64 + j), fill=(230, 230, 230), font_size=40)
img.save(r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\cf_calib.png")
print("saved calib")
