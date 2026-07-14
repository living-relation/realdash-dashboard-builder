#!/usr/bin/env python3
"""r4_v7.py - build st185_dash_v7.rd "APEX NIGHT" from the GUI-phase donor.

Donor: _build/backup/b1_v7_guiphase.rd (v1 layout + 3 embedded fonts +
GUI-added Image Gauge 1 = 12-frame LED shift strip, subframes 1x12,
bound to ST185: Throttle 0-100).

Design: open black timing-board. No tile boxes. Racing-red rules,
RaceHead hero digits (Turbo / Throttle), Aerospace labels, Draco badge,
LED strip across the header. 12 channels, 6 pills, no Trigger Err.
"""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import Dash2, H, TRANSP, set_static, static_bg, park  # noqa: E402

SRC = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\backup\b1_v7_guiphase.rd"
OUT = r"C:\Users\danie\Downloads\st185_dash_v7.rd"

BG = 0xFF0B0B0D
BAND = 0xFF101014
RULE = 0xFF26262E
RED = 0xFFE8272E
WHITE = 0xFFF2F2F4
DIM = 0xFF73737E
CHIP = 0xFF8A8A94
AMBER = 0xFFFFB300
CRIT = 0xFFFF2E38
NEARBLACK = 0xFF101013

RACE = "RaceHead.ttf"
AERO = "Aerospace.ttf"
DRACO = "Draco.otf"

d = Dash2(SRC)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]
img = m["Image Gauge 1"]

d.set_canvas_bg(BG)


def zero_blink(gg):
    off = gg._range_off()
    for k in (40, 44, 48):
        struct.pack_into("<f", gg.b, off + k, 0.0)


def label(gg, x, y, w, h, text, color=DIM, font=AERO):
    gg.set_font(font)
    gg.set_level_fonts(font)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(text, [text, text, text])
    set_static(gg, True)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [color] * 6, flag=0)
    gg.set_tcolor(color)
    gg.set_hash(0xFFFFFFFF)


def rulebar(gg, x, y, w, h, color):
    gg.set_font("defaultdashfont")
    gg.set_rect_px(x, y, w, h)
    gg.set_texts("", ["", "", ""])
    set_static(gg, True)
    static_bg(gg, color)
    gg.set_arr(0, [color] * 6, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(0xFFFFFFFF)


def value(gg, x, y, w, h, font=RACE):
    """Restyle an existing bound value gauge: keep hash/decimals/math/ranges."""
    gg.set_font(font)
    gg.set_level_fonts(font)
    gg.set_rect_px(x, y, w, h)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [WHITE, AMBER, CRIT] * 2, flag=0)
    gg.set_tcolor(WHITE)
    zero_blink(gg)


def pill(gg, x, y, w, h, text, lit, lit_tc):
    gg.set_font(AERO)
    gg.set_level_fonts(AERO)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(text, [text, text, text])
    set_static(gg, True)
    static_bg(gg, 0xFF141419)
    gg.set_arr(0, [0xFF141419] * 3 + [lit] * 3, flag=1)
    gg.set_arr(2, [0xFF4A4A54] * 3 + [lit_tc] * 3, flag=1)
    gg.set_tcolor(0xFF4A4A54)
    gg.set_decimals(0)
    gg.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
    zero_blink(gg)


def fill(gg, x, y, w, h, hash_, vmax, warn, crit, bgs):
    gg.set_font(AERO)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts("", ["", "", ""])
    set_static(gg, True)
    static_bg(gg, bgs[0])
    gg.set_arr(0, list(bgs) * 2, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(0, vmax, warn=warn, crit=crit, warn_below=-999,
                  crit_below=-999)
    zero_blink(gg)


def word(gg, x, y, w, h, hash_, vmax, warn, crit, words, tcs):
    gg.set_font(AERO)
    gg.set_level_fonts(AERO)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(words[0], list(words))
    set_static(gg, True)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, list(tcs) * 2, flag=0)
    gg.set_tcolor(tcs[0])
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(0, vmax, warn=warn, crit=crit, warn_below=-999,
                  crit_below=-999)
    zero_blink(gg)


# ---------------- header ----------------
rulebar(g(60), 0, 0, 800, 66, BAND)
rulebar(g(61), 0, 66, 800, 2, RED)
img.set_rect_px(120, 2, 560, 62)                    # LED rail art (frame 1)
img.set_arr(1, [0xFFFFFFFF] * 6, flag=0)            # neutral blend: no level tint

# 9 progressive LED lenses under the rail outlines (art cells measured in px
# of the 1476x170 frame: x starts/ends below, y 48..120)
LED_CELLS = [(60, 131), (220, 291), (381, 452), (542, 613), (702, 773),
             (863, 934), (1024, 1095), (1185, 1255), (1345, 1416)]
LED_COLORS = [0xFF2E7BFF] * 3 + [0xFF23D51F] * 4 + [0xFFC324E0, 0xFFFF1E1E]
LED_RECS = (9, 10, 11, 12, 13, 14, 15, 16, 17)
# Measured on-screen: the frame maps 1:1 onto the rect (stretch fill).
SX, SY = 560.0 / 1476.0, 62.0 / 170.0
X0 = 120.0


def led(gg, x, y, w, h, thr, lit):
    gg.set_font("defaultdashfont")
    gg.set_rect_px(x, y, w, h)
    gg.set_texts("", ["", "", ""])
    set_static(gg, True)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP, lit, lit] * 2, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(H["throttle"])
    gg.set_decimals(0)
    gg.set_ranges(0, 100, warn=thr, crit=thr + 6, warn_below=-999,
                  crit_below=-999)
    zero_blink(gg)


for k, (cx1, cx2) in enumerate(LED_CELLS):
    x = X0 + cx1 * SX + 2
    w = (cx2 - cx1) * SX - 4
    y = 2 + 48 * SY + 2
    h = (120 - 48) * SY - 4
    led(g(LED_RECS[k]), x, y, w, h, (k + 1) * 10, LED_COLORS[k])
label(g(71), 8, 10, 104, 20, "ST185", WHITE, DRACO)
label(g(72), 8, 36, 104, 12, "GT-FOUR", RED, DRACO)
label(g(76), 694, 14, 100, 14, "SHIFT", DIM, AERO)
label(g(77), 694, 34, 100, 11, "THR %", 0xFF4A4A54, AERO)

# ---------------- heroes ----------------
label(g(27), 30, 78, 160, 18, "TURBO", DIM, AERO)
value(g(40), 30, 100, 220, 92, RACE)                # =V/1000 kept
label(g(186), 256, 148, 72, 20, "k RPM", CHIP, "defaultdashfont")
rulebar(g(74), 30, 200, 298, 3, RED)

label(g(23), 610, 78, 160, 18, "THROTTLE", DIM, AERO)
value(g(34), 550, 100, 220, 92, RACE)
label(g(200), 516, 148, 30, 20, "%", CHIP, "defaultdashfont")
rulebar(g(75), 472, 200, 298, 3, RED)

rulebar(g(160), 22, 100, 4, 92, RED)
rulebar(g(161), 774, 100, 4, 92, RED)

# center badge
label(g(73), 338, 92, 124, 30, "APEX", RED, DRACO)
label(g(78), 338, 128, 124, 13, "CELICA ST185", DIM, AERO)
label(g(79), 338, 148, 124, 11, "ROUND 4 - V7", 0xFF4A4A54, AERO)

# ---------------- grid (2 rows x 4 cols) ----------------
rulebar(g(138), 30, 236, 740, 1, RULE)
COLX = (30, 220, 410, 600)
ROWY = (246, 324)
GRID = [
    # (labelrec, valrec, label text, label font, chiprec, chip text)
    (22, 35, "BOOST MAP", AERO, None, None),
    (150, 36, "TC MODE", AERO, None, None),
    (24, 37, "TARGET \u03bb", "defaultdashfont", None, None),
    (25, 38, "CHARGE TEMP", AERO, 184, "\u00b0C"),
    (26, 39, "COOLANT P", AERO, 185, "kPa"),
    (29, 42, "FUEL TEMP", AERO, 188, "\u00b0C"),
    (30, 43, "ETHANOL %", AERO, None, None),
    (28, 41, "ENGINE LOAD %", AERO, None, None),
]
for i, (lr, vr, lt, lf, cr, ct) in enumerate(GRID):
    x = COLX[i % 4]
    y = ROWY[i // 4]
    label(g(lr), x, y, 170, 13, lt, DIM, lf)
    value(g(vr), x, y + 17, 112, 42, RACE)
    if cr is not None:
        label(g(cr), x + 118, y + 33, 50, 17, ct, CHIP, "defaultdashfont")
rulebar(g(139), 30, 390, 740, 1, RULE)
# thin column separators
for rec, sx in ((162, 209), (163, 399), (164, 589)):
    rulebar(g(rec), sx, 246, 1, 136, RULE)

# λ needs default font if RaceHead lacks '.'? keep RaceHead, verify in sim.

# ---------------- state lenses ----------------
CR_BG = [0xFF17171C, 0xFF3A3A44, RED, 0xFFFF7A1A, WHITE]
CR_W = ["OFF", "STBY", "SET", "RES", "OVR"]
CR_TC = [DIM, WHITE, WHITE, NEARBLACK, NEARBLACK]
AC_BG = [0xFF17171C, AMBER, WHITE, CRIT]
AC_W = ["OFF", "REQ", "ON", "FLT"]
AC_TC = [DIM, NEARBLACK, NEARBLACK, WHITE]

label(g(32), 30, 406, 70, 14, "CRUISE", DIM, AERO)
rulebar(g(80), 104, 398, 286, 40, 0xFF2A2A31)
rulebar(g(19), 107, 401, 280, 34, 0xFF121216)
fill(g(45), 110, 404, 274, 28, H["cruise"], 4, 0.5, 1.5, CR_BG[0:3])
fill(g(100), 110, 404, 274, 28, H["cruise"], 4, 2.5, 3.5,
     [TRANSP, CR_BG[3], CR_BG[4]])
word(g(120), 180, 408, 134, 20, H["cruise"], 4, 0.5, 1.5,
     [CR_W[0], CR_W[1], ""], [CR_TC[0], CR_TC[1], TRANSP])
word(g(140), 180, 408, 134, 20, H["cruise"], 4, 1.5, 2.5,
     ["", CR_W[2], ""], [TRANSP, CR_TC[2], TRANSP])
word(g(181), 180, 408, 134, 20, H["cruise"], 4, 2.5, 3.5,
     ["", CR_W[3], CR_W[4]], [TRANSP, CR_TC[3], CR_TC[4]])

label(g(33), 410, 406, 54, 14, "A/C", DIM, AERO)
rulebar(g(170), 474, 398, 296, 40, 0xFF2A2A31)
rulebar(g(187), 477, 401, 290, 34, 0xFF121216)
fill(g(46), 480, 404, 284, 28, H["ac"], 3, 0.5, 1.5, AC_BG[0:3])
fill(g(31), 480, 404, 284, 28, H["ac"], 3, 2.5, 999,
     [TRANSP, AC_BG[3], AC_BG[3]])
word(g(44), 556, 408, 134, 20, H["ac"], 3, 0.5, 1.5,
     [AC_W[0], AC_W[1], ""], [AC_TC[0], AC_TC[1], TRANSP])
word(g(182), 556, 408, 134, 20, H["ac"], 3, 1.5, 2.5,
     ["", AC_W[2], AC_W[3]], [TRANSP, AC_TC[2], AC_TC[3]])

# ---------------- pills ----------------
PILLS = [
    (3, "FLAT", CRIT, WHITE),
    (4, "FAN", WHITE, NEARBLACK),      # steady lit (working recipe)
    (6, "LOFUEL", AMBER, NEARBLACK),
    (5, "SBFLT", AMBER, NEARBLACK),
    (7, "COOL P", CRIT, WHITE),
    (8, "OIL P", CRIT, WHITE),
]
for i, (rec, txt, lit, tc) in enumerate(PILLS):
    pill(g(rec), 30 + i * 124, 450, 114, 20, txt, lit, tc)

# ---------------- park all unused decorative records ----------------
USED = {60, 61, 71, 72, 76, 77, 27, 40, 186, 74, 23, 34, 200, 75, 160, 161,
        73, 78, 79, 138, 139, 162, 163, 164, 184, 185, 188, 32, 80, 19, 45,
        100, 120, 140, 181, 33, 170, 187, 46, 31, 44, 182, 3, 4, 6, 5, 7, 8,
        22, 150, 24, 25, 26, 29, 30, 28, 35, 36, 37, 38, 39, 42, 43, 41,
        9, 10, 11, 12, 13, 14, 15, 16, 17}
parked = []
for gg in d.gauges:
    if gg.name == "Image Gauge 1":
        continue
    n = int(gg.name.split()[-1])
    if n not in USED:
        park(gg)
        parked.append(gg)
print("parked", len(parked), "records")

# ---------------- paint order ----------------
front = [g(60), g(61)]                                   # header band + rule
mid_names = [n for n in (71, 72, 76, 77, 27, 186, 74, 23, 200, 75, 160, 161,
                         73, 78, 79, 138, 139, 162, 163, 164,
                         22, 150, 24, 25, 26, 29, 30, 28, 184, 185, 188,
                         32, 33)]
mids = [g(n) for n in mid_names]
vals = [g(n) for n in (40, 34, 35, 36, 37, 38, 39, 42, 43, 41)]
lens = [g(n) for n in (80, 19, 45, 100, 120, 140, 181,
                       170, 187, 46, 31, 44, 182)]
pills_ = [g(n) for n in (3, 4, 6, 5, 7, 8)]
leds = [g(n) for n in LED_RECS]
actives = front + leds + mids + vals + lens + pills_ + [img]
order = actives + parked
assert len(order) == len(d.gauges), (len(order), len(d.gauges))
n = d.save(OUT, order=order)
print("saved v7", n, "image idx", order.index(img))
