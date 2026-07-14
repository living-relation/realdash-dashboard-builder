#!/usr/bin/env python3
"""a2_gen_cf2.py - Carbon Forge background v2 for v5 (Stage A2).

Changes vs gen_cf_png.py:
 - REAL carbon weave: ShareTextures 45-degree twill (CC0), darkened to sit
   in the Carbon Forge palette (target tow lum ~ 0x15-0x2A).
 - Pill housings: recessed well now r=2 (near-square) so the square lit
   lens gauge fits EXACTLY (fixes lit-corner overlap wonk).
Outputs: carbonforge_bg2.png (800x480) + cf_sheet2.png (6400x3840 with the
art in the stuck-UV window x5600..6400, y0..480, 8px bleed pads).
"""
import math
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

W, H = 800, 480
BUILD = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build"
CARBON = BUILD + r"\assets\carbon\carbon_sharetextures_2k.jpg"
OUT = BUILD + r"\carbonforge_bg2.png"
random.seed(185)

PANEL_T = (0x17, 0x1A, 0x1E)
PANEL_B = (0x0E, 0x10, 0x13)
EDGE_T = (0x31, 0x36, 0x3D)
EDGE_B = (0x05, 0x06, 0x07)
AL = [(0xC7, 0xC8, 0xC9), (0x9E, 0xA1, 0xA6), (0x6B, 0x6E, 0x73), (0xB0, 0xB3, 0xB8)]
GUN_HI = (0x6B, 0x6E, 0x73)
GUN_LO = (0x1A, 0x1D, 0x20)
WELL = (0x08, 0x09, 0x0B)
TRACK = (0x0B, 0x0D, 0x10)


def lerp(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


# ---------- 1. real twill base ----------
import sys
TILE = int(sys.argv[1]) if len(sys.argv) > 1 else 512
tex = Image.open(CARBON).convert("RGB")
tex = tex.resize((TILE, TILE), Image.LANCZOS)
base = Image.new("RGB", (W, H))
for ty in range(0, H, TILE):
    for tx in range(0, W, TILE):
        base.paste(tex, (tx, ty))
# darken: ShareTextures silvery strands (mean lum 86) -> palette-dark
base = ImageEnhance.Brightness(base).enhance(0.30)
base = ImageEnhance.Contrast(base).enhance(1.05)
img = base
d = ImageDraw.Draw(img)

# ---------- geometry (unchanged from round 3) ----------
HEADER = (8, 8, 784, 88)
PANELS = [(x, y, 190, 88) for y in (108, 204, 300) for x in (8, 206, 404, 602)]
PILLS = [(x, 400, 124, 64) for x in (8, 140, 272, 404, 536, 668)]
BAR_TRACK = (330, 24, 452, 56)

# ---------- 2. drop shadows ----------
sh = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(sh)
for (x, y, w, h) in [HEADER] + PANELS + PILLS:
    sd.rounded_rectangle([x - 1, y + 2, x + w + 1, y + h + 3], radius=10, fill=110)
sh = sh.filter(ImageFilter.GaussianBlur(3))
img = Image.composite(Image.new("RGB", (W, H), (0x04, 0x05, 0x06)), img, sh)
d = ImageDraw.Draw(img)


def panel_well(x, y, w, h, r=8):
    grad = Image.new("RGB", (w, h))
    gp = grad.load()
    for yy in range(h):
        c = lerp(PANEL_T, PANEL_B, yy / (h - 1))
        for xx in range(w):
            gp[xx, yy] = c
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    img.paste(grad, (x, y), mask)
    d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=r,
                        outline=(0x23, 0x27, 0x2D), width=1)
    d.line([x + r, y + 1, x + w - 1 - r, y + 1], fill=EDGE_T, width=1)
    d.line([x + r, y + h - 2, x + w - 1 - r, y + h - 2], fill=EDGE_B, width=1)


# ---------- 3. header + panels + bar track ----------
panel_well(*HEADER)
for p in PANELS:
    panel_well(*p)
bx, by, bw, bh = BAR_TRACK
grad = Image.new("RGB", (bw, bh))
gp = grad.load()
for yy in range(bh):
    c = lerp((0x07, 0x08, 0x0A), TRACK, yy / (bh - 1))
    for xx in range(bw):
        gp[xx, yy] = c
mask = Image.new("L", (bw, bh), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=6, fill=255)
img.paste(grad, (bx, by), mask)
d.rounded_rectangle([bx, by, bx + bw - 1, by + bh - 1], radius=6,
                    outline=(0x03, 0x04, 0x05), width=1)
d.line([bx + 6, by + bh - 2, bx + bw - 7, by + bh - 2],
       fill=(0x2A, 0x2F, 0x36), width=1)
for i in (1, 2, 3):
    nx = bx + int(bw * i / 4)
    d.line([nx, by + 4, nx, by + bh - 5], fill=(0x1C, 0x20, 0x26), width=1)

# ---------- 4. brushed aluminum strip ----------
ax, ay, aw, ah = 8, 96, 784, 4
stops = [AL[0], AL[1], AL[2], AL[3]]
for yy in range(ah):
    t = yy / (ah - 1) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    c = lerp(stops[i], stops[i + 1], t - i)
    d.line([ax, ay + yy, ax + aw - 1, ay + yy], fill=c, width=1)
apx = img.load()
for yy in range(ah):
    for xx in range(ax, ax + aw, 1):
        if random.random() < 0.35:
            n = random.randint(-6, 6)
            r0, g0, b0 = apx[xx, ay + yy]
            apx[xx, ay + yy] = (max(0, min(255, r0 + n)),
                                max(0, min(255, g0 + n)),
                                max(0, min(255, b0 + n)))
d.line([ax, ay, ax + 2, ay + ah - 1], fill=(0x55, 0x58, 0x5C), width=1)
d.line([ax + aw - 3, ay, ax + aw - 1, ay + ah - 1], fill=(0x55, 0x58, 0x5C), width=1)


# ---------- 5. pill housings: SQUARE lens seat (r=2) ----------
def pill_housing(x, y, w, h):
    r = 14
    grad = Image.new("RGB", (w, h))
    gp = grad.load()
    top, bot = (0x40, 0x4A, 0x51), (0x28, 0x2F, 0x34)
    for yy in range(h):
        c = lerp(top, bot, yy / (h - 1))
        for xx in range(w):
            gp[xx, yy] = c
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    img.paste(grad, (x, y), mask)
    d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=r,
                        outline=GUN_LO, width=1)
    d.arc([x, y, x + 2 * r, y + 2 * r], 180, 270, fill=GUN_HI, width=1)
    d.arc([x + w - 1 - 2 * r, y, x + w - 1, y + 2 * r], 270, 360, fill=GUN_HI, width=1)
    d.line([x + r, y, x + w - 1 - r, y], fill=GUN_HI, width=1)
    d.line([x + r, y + h - 1, x + w - 1 - r, y + h - 1], fill=(0x10, 0x12, 0x14), width=1)
    # near-square recessed well: lens gauge (x+10,y+10,104x44) fits EXACTLY
    wx, wy, ww, wh = x + 8, y + 8, w - 16, h - 16
    d.rounded_rectangle([wx, wy, wx + ww - 1, wy + wh - 1], radius=2, fill=WELL)
    d.line([wx + 2, wy + 1, wx + ww - 3, wy + 1], fill=(0x02, 0x02, 0x03), width=1)
    d.line([wx + 2, wy + wh - 2, wx + ww - 3, wy + wh - 2], fill=(0x3A, 0x40, 0x46), width=1)


for p in PILLS:
    pill_housing(*p)

img.save(OUT, "PNG")
print("saved %s %dx%d" % (OUT, W, H))

SHEET = BUILD + r"\cf_sheet2.png"
sheet = Image.new("RGB", (6400, 3840), (0, 0, 0))
sheet.paste(img, (5600, 0))
edge_l = img.crop((0, 0, 1, H)).resize((8, H))
sheet.paste(edge_l, (5592, 0))
edge_b = img.crop((0, H - 1, W, H)).resize((W, 8))
sheet.paste(edge_b, (5600, 480))
sheet.save(SHEET, "PNG")
print("saved %s 6400x3840" % SHEET)
