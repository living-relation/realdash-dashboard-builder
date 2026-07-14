#!/usr/bin/env python3
"""gen_cf_png.py - bake the Carbon Forge 800x480 background PNG (Plan A).

Layers: 2/2 twill carbon weave, recessed panel wells, brushed-aluminum strip,
boost-bar track well, six 3D pill housings with machined bezels.
Palette per _build/research/dark_dash_inspiration.md.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 800, 480
OUT = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\carbonforge_bg.png"
random.seed(185)

BASE = (0x0B, 0x0C, 0x0E)
TOW_D = (0x10, 0x11, 0x13)     # dark (vertical) tows
TOW_L = (0x1E, 0x21, 0x26)     # light (horizontal) tows
SHEEN = (0x2A, 0x2E, 0x34)     # specular streak
PANEL_T = (0x17, 0x1A, 0x1E)
PANEL_B = (0x0E, 0x10, 0x13)
EDGE_T = (0x31, 0x36, 0x3D)
EDGE_B = (0x05, 0x06, 0x07)
AL = [(0xC7, 0xC8, 0xC9), (0x9E, 0xA1, 0xA6), (0x6B, 0x6E, 0x73), (0xB0, 0xB3, 0xB8)]
GUN = (0x35, 0x3E, 0x43)
GUN_HI = (0x6B, 0x6E, 0x73)
GUN_LO = (0x1A, 0x1D, 0x20)
WELL = (0x08, 0x09, 0x0B)
TRACK = (0x0B, 0x0D, 0x10)


def lerp(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


# ---------- 1. twill weave base ----------
img = Image.new("RGB", (W, H), BASE)
px = img.load()
T = 6          # tow width px
for y in range(H):
    for x in range(W):
        col, row = x // T, y // T
        horiz = ((col - row) % 4) < 2          # 2/2 twill diagonal
        if horiz:
            ph = (y % T) / (T - 1)             # across-tow position
            base = TOW_L
        else:
            ph = (x % T) / (T - 1)
            base = TOW_D
        shade = math.sin(ph * math.pi)         # rounded tow profile
        c = lerp(BASE, base, 0.35 + 0.65 * shade)
        if horiz and abs(ph - 0.5) < 0.18:     # specular band on light tows
            c = lerp(c, SHEEN, 0.55)
        n = random.randint(-2, 2)
        px[x, y] = tuple(max(0, min(255, v + n)) for v in c)
# top-lit sheen: subtle vertical brightness falloff
overlay = Image.new("L", (W, H), 0)
op = overlay.load()
for y in range(H):
    v = max(0, int(18 * (1 - y / 260))) if y < 260 else 0
    for x in range(W):
        op[x, y] = v
img = Image.composite(Image.new("RGB", (W, H), (0x20, 0x24, 0x2C)), img,
                      overlay.point(lambda v: v))

d = ImageDraw.Draw(img)

# ---------- geometry ----------
HEADER = (8, 8, 784, 88)
PANELS = [(x, y, 190, 88) for y in (108, 204, 300) for x in (8, 206, 404, 602)]
PILLS = [(x, 400, 124, 64) for x in (8, 140, 272, 404, 536, 668)]
BAR_TRACK = (330, 24, 452, 56)

# ---------- 2. drop shadows under all wells ----------
sh = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(sh)
for (x, y, w, h) in [HEADER] + PANELS + PILLS:
    sd.rounded_rectangle([x - 1, y + 2, x + w + 1, y + h + 3], radius=10, fill=110)
sh = sh.filter(ImageFilter.GaussianBlur(3))
img = Image.composite(Image.new("RGB", (W, H), (0x04, 0x05, 0x06)), img, sh)
d = ImageDraw.Draw(img)


def panel_well(x, y, w, h, r=8):
    # vertical gradient fill inside rounded rect
    grad = Image.new("RGB", (w, h))
    gp = grad.load()
    for yy in range(h):
        c = lerp(PANEL_T, PANEL_B, yy / (h - 1))
        for xx in range(w):
            gp[xx, yy] = c
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    img.paste(grad, (x, y), mask)
    # edge lights: 1px top inner edge, 1px bottom inner shade
    d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=r,
                        outline=(0x23, 0x27, 0x2D), width=1)
    d.line([x + r, y + 1, x + w - 1 - r, y + 1], fill=EDGE_T, width=1)
    d.line([x + r, y + h - 2, x + w - 1 - r, y + h - 2], fill=EDGE_B, width=1)


# ---------- 3. header + panels ----------
panel_well(*HEADER)
for p in PANELS:
    panel_well(*p)

# boost bar track: recessed well inside header
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
       fill=(0x2A, 0x2F, 0x36), width=1)          # light lip at bottom of recess
for i in (1, 2, 3):                                # quarter notches
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
for yy in range(ah):                                # horizontal grain noise
    for xx in range(ax, ax + aw, 1):
        if random.random() < 0.35:
            n = random.randint(-6, 6)
            r0, g0, b0 = apx[xx, ay + yy]
            apx[xx, ay + yy] = (max(0, min(255, r0 + n)),
                                max(0, min(255, g0 + n)),
                                max(0, min(255, b0 + n)))
d.line([ax, ay, ax + 2, ay + ah - 1], fill=(0x55, 0x58, 0x5C), width=1)
d.line([ax + aw - 3, ay, ax + aw - 1, ay + ah - 1], fill=(0x55, 0x58, 0x5C), width=1)


# ---------- 5. pill housings ----------
def pill_housing(x, y, w, h):
    r = 14
    # bezel body: vertical gunmetal shading
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
    # machined ring: light top arc, dark bottom arc
    d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=r,
                        outline=GUN_LO, width=1)
    d.arc([x, y, x + 2 * r, y + 2 * r], 180, 270, fill=GUN_HI, width=1)
    d.arc([x + w - 1 - 2 * r, y, x + w - 1, y + 2 * r], 270, 360, fill=GUN_HI, width=1)
    d.line([x + r, y, x + w - 1 - r, y], fill=GUN_HI, width=1)
    d.line([x + r, y + h - 1, x + w - 1 - r, y + h - 1], fill=(0x10, 0x12, 0x14), width=1)
    # recessed well (lens seat): inset 5, r=8
    wx, wy, ww, wh = x + 5, y + 5, w - 10, h - 10
    d.rounded_rectangle([wx, wy, wx + ww - 1, wy + wh - 1], radius=8, fill=WELL)
    # depth: 2px dark inner shadow at top, 1px light lip at bottom
    d.line([wx + 8, wy + 1, wx + ww - 9, wy + 1], fill=(0x02, 0x02, 0x03), width=1)
    d.line([wx + 8, wy + 2, wx + ww - 9, wy + 2], fill=(0x04, 0x05, 0x06), width=1)
    d.line([wx + 8, wy + wh - 2, wx + ww - 9, wy + wh - 2], fill=(0x3A, 0x40, 0x46), width=1)


for p in PILLS:
    pill_housing(*p)

img.save(OUT, "PNG")
print("saved %s %dx%d" % (OUT, W, H))

# ---------- sheet variant for the stuck subframe window ----------
# The v5 image record renders UV window (0.875..1, 0..0.125) of its texture
# (measured via calibration probe, 2026-07-07). Sheet 6400x3840 puts our
# 800x480 exactly in that window (x 5600..6400, y 0..480); 8px edge
# extension guards against filtering bleed.
SHEET = OUT.replace("carbonforge_bg.png", "cf_sheet.png")
sheet = Image.new("RGB", (6400, 3840), (0, 0, 0))
sheet.paste(img, (5600, 0))
edge_l = img.crop((0, 0, 1, H)).resize((8, H))
sheet.paste(edge_l, (5592, 0))
edge_b = img.crop((0, H - 1, W, H)).resize((W, 8))
sheet.paste(edge_b, (5600, 480))
sheet.save(SHEET, "PNG")
print("saved %s 6400x3840" % SHEET)
