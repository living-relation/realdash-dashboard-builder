#!/usr/bin/env python3
"""b2_v8.py - build st185_dash_v8.rd "PASNY ADU" (Stage B2, round 4).

Donor: _build/backup/b1_v7_guiphase.rd (v1 layout + 3 embedded fonts +
GUI-added Image Gauge 1 w/ 1x12 subframes; its sheet asset is spliced here
with the imported PASNY logo badge, white-on-transparent).

Design: ECU-Master-ADU-style telemetry panel. Pure black, continuous thin
grid lines, rising-staircase THROTTLE sweep (heroes: Throttle + Engine
Load giant numeral), ADU yellow accent strip, Aerospace grid values,
RaceHead hero, Draco title. Badge = imported art, per-level image-blend
recolor bound to TC Intervention (white -> amber on cut -> red heavy).
"""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import Dash2, H, TRANSP, set_static, static_bg, park  # noqa: E402
from rd_lib2 import read_str  # noqa: E402

BUILD = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build"
SRC = BUILD + r"\backup\b1_v7_guiphase.rd"
BADGE = BUILD + r"\b2_badge_sheet.png"
OUT = r"C:\Users\danie\Downloads\st185_dash_v8.rd"

BG = 0xFF0A0A0C
LINE = 0xFF3A3A40
WHITE = 0xFFF4F4F6
DIM = 0xFF8A8A92
CHIP = 0xFF6E6E76
YELLOW = 0xFFFFC800
RED = 0xFFFF2020
AMBER = 0xFFFFB300
UNLIT = 0xFF1B1B1F
NEARBLACK = 0xFF0E0E10
PILL_BG = 0xFF141417

RACE = "RaceHead.ttf"
AERO = "Aerospace.ttf"
DRACO = "Draco.otf"
DEF = "defaultdashfont"

d = Dash2(SRC)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]
img = m["Image Gauge 1"]

d.set_canvas_bg(BG)


def splice_asset(dash, name, png_path):
    h = bytes(dash.header)
    i = 0
    while i < len(h) - 8:
        r = read_str(h, i)
        if r and r[0] == name:
            size_off = r[1]
            old = struct.unpack_from("<I", h, size_off)[0]
            blob = b"\x00\x00\x00\x00" + open(png_path, "rb").read()
            dash.header = bytearray(
                h[:size_off] + struct.pack("<I", len(blob)) + blob
                + h[size_off + 4 + old:])
            return old, len(blob)
        i += 1
    raise KeyError(name)


old, new = splice_asset(d, "led_strip_sheet_1x12.png", BADGE)
print("badge spliced over LED sheet: %d -> %d bytes" % (old, new))


def zero_blink(gg):
    off = gg._range_off()
    for k in (40, 44, 48):
        struct.pack_into("<f", gg.b, off + k, 0.0)


def crit_blink(gg):
    struct.pack_into("<f", gg.b, gg._range_off() + 48, 1.0)


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
    gg.set_font(DEF)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts("", ["", "", ""])
    set_static(gg, True)
    static_bg(gg, color)
    gg.set_arr(0, [color] * 6, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(0xFFFFFFFF)


def value(gg, x, y, w, h, font=AERO):
    """Restyle existing bound value gauge (keeps hash/decimals/math/ranges)."""
    gg.set_font(font)
    gg.set_level_fonts(font)
    gg.set_rect_px(x, y, w, h)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [WHITE, AMBER, RED] * 2, flag=0)
    gg.set_tcolor(WHITE)
    zero_blink(gg)


def stair(gg, x, y, w, h, thr, lit):
    """Rising-staircase throttle segment: dark cell -> lit at threshold."""
    gg.set_font(DEF)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts("", ["", "", ""])
    set_static(gg, True)
    static_bg(gg, UNLIT)
    gg.set_arr(0, [UNLIT, lit, lit] * 2, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(H["throttle"])
    gg.set_decimals(0)
    gg.set_ranges(0, 100, warn=thr, crit=thr + 3, warn_below=-999,
                  crit_below=-999)
    zero_blink(gg)


def pill_housing(gg, x, y, w, h, hash_, lit, blink=False):
    """Pill background fill only (text lives in a separate small record)."""
    gg.set_font(DEF)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts("", ["", "", ""])
    set_static(gg, True)
    static_bg(gg, PILL_BG)
    gg.set_arr(0, [PILL_BG] * 3 + [lit] * 3, flag=1)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
    zero_blink(gg)
    if blink:
        crit_blink(gg)


def pill_word(gg, x, y, w, h, text, hash_, lit_tc):
    gg.set_font(AERO)
    gg.set_level_fonts(AERO)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(text, [text, text, text])
    set_static(gg, True)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [0xFF4A4A52] * 3 + [lit_tc] * 3, flag=1)
    gg.set_tcolor(0xFF4A4A52)
    gg.set_hash(hash_)
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
# badge image: PASNY logo (880x100 frame), TC-Intervention state recolor
img.set_rect_px(16, 10, 317, 36)
img.set_arr(1, [0xFFFFFFFF, AMBER, RED] * 2, flag=0)
img.set_hash(H["tci"])
struct.pack_into("<I", img.b, img._arr_marker() - 8, 0)   # decimals
img.set_ranges(0, 100, warn=1, crit=40, warn_below=-999, crit_below=-999)
zero_blink(img)

label(g(60), 420, 14, 364, 15, "ST185 GT-FOUR", WHITE, DRACO)
label(g(61), 420, 38, 364, 11, "ADU TELEMETRY - V8", CHIP, AERO)
rulebar(g(33), 16, 62, 768, 2, LINE)   # TG62 does not exist in this donor

# ---------------- staircase throttle sweep (hero 1) ----------------
label(g(23), 16, 78, 140, 13, "THROTTLE", DIM, AERO)
value(g(34), 16, 96, 110, 58, AERO)
label(g(24), 128, 128, 30, 20, "%", CHIP, DEF)

STAIR_RECS = [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102,
              110, 111, 112, 113, 114, 115, 116]
def stair_h(k):
    return 24 + 56.0 * k / 19.0


for k in range(20):
    h_k = stair_h(k)
    x = 170 + k * 30
    lit = RED if k >= 17 else WHITE
    stair(g(STAIR_RECS[k]), x, 172 - h_k, 26, h_k, (k + 1) * 5 - 3, lit)
SCALES = [(117, 4, "25"), (118, 9, "50"), (119, 14, "75"), (120, 19, "100")]
for rec, k, txt in SCALES:
    label(g(rec), 170 + k * 30 - 8, 172 - stair_h(k) - 15, 42, 12, txt,
          DIM, AERO)

# ADU yellow accent strip
rulebar(g(121), 16, 178, 768, 6, YELLOW)

# ---------------- grid lines ----------------
rulebar(g(130), 16, 192, 768, 1, LINE)      # top
rulebar(g(131), 16, 396, 768, 1, LINE)      # bottom
rulebar(g(132), 296, 260, 488, 1, LINE)     # row line 1 (right of hero)
rulebar(g(133), 296, 328, 488, 1, LINE)     # row line 2
rulebar(g(134), 16, 192, 1, 205, LINE)      # verticals
rulebar(g(135), 296, 192, 1, 205, LINE)
rulebar(g(136), 459, 192, 1, 205, LINE)
rulebar(g(137), 622, 192, 1, 205, LINE)
rulebar(g(138), 783, 192, 1, 205, LINE)

# ---------------- hero cell: ENGINE LOAD ----------------
label(g(28), 26, 200, 260, 14, "ENGINE LOAD %", DIM, AERO)
value(g(41), 26, 226, 260, 116, RACE)

# ---------------- ADU cells (3x3 right of hero) ----------------
# rebind TG44 to TC Intervention; it carried v1 A/C state words -> clear
tg44 = g(44)
tg44.set_texts("0", ["0", "0", "0"])
set_static(tg44, False)
tg44.set_hash(H["tci"])
tg44.set_decimals(0)
tg44.set_ranges(0, 100, warn=1, crit=40, warn_below=-999, crit_below=-999)

COLX = (296, 459, 622)
ROWY = (192, 260, 328)
CELLS = [
    # (col, row, labelrec, valrec, label, labelfont, chiprec, chiptext)
    (0, 0, 27, 40, "TURBO", AERO, 139, "k RPM"),
    (1, 0, 22, 35, "BOOST MAP", AERO, None, None),
    (2, 0, 25, 37, "TARGET \u03bb", DEF, None, None),
    (0, 1, 26, 38, "CHARGE TEMP", AERO, 140, "\u00b0C"),
    (1, 1, 29, 39, "COOLANT P", AERO, 141, "kPa"),
    (2, 1, 30, 42, "FUEL TEMP", AERO, 142, "\u00b0C"),
    (0, 2, 31, 43, "ETHANOL %", AERO, None, None),
    (1, 2, 150, 36, "TC MODE", AERO, None, None),
    (2, 2, 32, 44, "TC CUT", AERO, 160, "%"),
]
for c, r, lr, vr, lt, lf, cr, ct in CELLS:
    x = COLX[c]
    y = ROWY[r]
    label(g(lr), x + 10, y + 8, 145, 11, lt, DIM, lf)
    if cr is not None:
        value(g(vr), x + 6, y + 24, 100, 38, AERO)
        label(g(cr), x + 108, y + 42, 50, 16, ct, CHIP, DEF)
    else:
        value(g(vr), x + 6, y + 24, 151, 38, AERO)

# offline/sim negative temps must not read critical (BELOW -> -99);
# RaceHead for temps: Aerospace's minus glyph is a broken square block
g(38).set_ranges(-50, 150, warn=60, crit=80, warn_below=-99, crit_below=-99)
g(42).set_ranges(-50, 150, warn=60, crit=80, warn_below=-99, crit_below=-99)
for rec in (38, 42):
    g(rec).set_font(RACE)
    g(rec).set_level_fonts(RACE)

# ---------------- CRUISE / A-C state cells ----------------
CR_BG = [0xFF17171A, 0xFF3A3A40, YELLOW, WHITE, 0xFFFF7A1A]
CR_W = ["OFF", "STBY", "SET", "RES", "OVR"]
CR_TC = [DIM, WHITE, NEARBLACK, NEARBLACK, NEARBLACK]
AC_BG = [0xFF17171A, YELLOW, WHITE, RED]
AC_W = ["OFF", "REQ", "ON", "FLT"]
AC_TC = [DIM, NEARBLACK, NEARBLACK, WHITE]

label(g(161), 16, 414, 66, 13, "CRUISE", DIM, AERO)
rulebar(g(80), 88, 404, 302, 34, LINE)
rulebar(g(19), 89, 405, 300, 32, NEARBLACK)
fill(g(45), 91, 407, 296, 28, H["cruise"], 4, 0.5, 1.5, CR_BG[0:3])
fill(g(163), 91, 407, 296, 28, H["cruise"], 4, 2.5, 3.5,
     [TRANSP, CR_BG[3], CR_BG[4]])
word(g(164), 169, 411, 140, 20, H["cruise"], 4, 0.5, 1.5,
     [CR_W[0], CR_W[1], ""], [CR_TC[0], CR_TC[1], TRANSP])
word(g(165), 169, 411, 140, 20, H["cruise"], 4, 1.5, 2.5,
     ["", CR_W[2], ""], [TRANSP, CR_TC[2], TRANSP])
word(g(166), 169, 411, 140, 20, H["cruise"], 4, 2.5, 3.5,
     ["", CR_W[3], CR_W[4]], [TRANSP, CR_TC[3], CR_TC[4]])

label(g(162), 412, 414, 40, 13, "A/C", DIM, AERO)
rulebar(g(81), 458, 404, 326, 34, LINE)
rulebar(g(20), 459, 405, 324, 32, NEARBLACK)
fill(g(46), 461, 407, 320, 28, H["ac"], 3, 0.5, 1.5, AC_BG[0:3])
fill(g(167), 461, 407, 320, 28, H["ac"], 3, 2.5, 999,
     [TRANSP, AC_BG[3], AC_BG[3]])
word(g(168), 551, 411, 140, 20, H["ac"], 3, 0.5, 1.5,
     [AC_W[0], AC_W[1], ""], [AC_TC[0], AC_TC[1], TRANSP])
word(g(169), 551, 411, 140, 20, H["ac"], 3, 1.5, 2.5,
     ["", AC_W[2], AC_W[3]], [TRANSP, AC_TC[2], AC_TC[3]])

# ---------------- pills (housing fill + separate word record) ----------------
PILLS = [
    (3, 70, "FLAT", RED, WHITE, False),
    (4, 71, "FAN", YELLOW, NEARBLACK, False),   # steady lit, working recipe
    (6, 72, "LOFUEL", AMBER, NEARBLACK, False),
    (5, 73, "SBFLT", AMBER, NEARBLACK, False),
    (7, 74, "COOL P", RED, WHITE, True),        # blink on critical
    (8, 75, "OIL P", RED, WHITE, True),         # blink on critical
]
# word goes on TG3-8 (v1 pill records render centered text);
# housing fill on TG70-75 (repurposed panel records)
for i, (rec, wrec, txt, lit, tc, bl) in enumerate(PILLS):
    x = 16 + i * 129
    hsh = g(rec).get_hash()
    pill_housing(g(wrec), x, 444, 120, 26, hsh, lit, blink=bl)
    pill_word(g(rec), x, 450, 120, 13, txt, hsh, tc)

# ---------------- park unused ----------------
USED = ({60, 61, 33, 23, 34, 24, 121, 130, 131, 132, 133, 134, 135, 136,
         137, 138, 28, 41, 44, 161, 80, 19, 45, 163, 164, 165, 166,
         162, 81, 20, 46, 167, 168, 169, 3, 4, 6, 5, 7, 8,
         70, 71, 72, 73, 74, 75}
        | set(STAIR_RECS) | {r for r, _, _ in SCALES}
        | {lr for _, _, lr, _, _, _, _, _ in CELLS}
        | {vr for _, _, _, vr, _, _, _, _ in CELLS}
        | {cr for _, _, _, _, _, _, cr, _ in CELLS if cr is not None})
parked = []
for gg in d.gauges:
    if gg.name == "Image Gauge 1":
        continue
    n = int(gg.name.split()[-1])
    if n not in USED:
        park(gg)
        parked.append(gg)
print("parked", len(parked), "records; used", len(USED))

# ---------------- paint order ----------------
lines = [g(n) for n in (33, 121, 130, 131, 132, 133, 134, 135, 136, 137,
                        138)]
labels = [g(n) for n in (60, 61, 23, 24, 28, 161, 162, 117, 118,
                         119, 120)]
labels += [g(lr) for _, _, lr, _, _, _, _, _ in CELLS]
labels += [g(cr) for _, _, _, _, _, _, cr, _ in CELLS if cr is not None]
stairs = [g(n) for n in STAIR_RECS]
vals = [g(n) for n in (34, 41, 40, 35, 37, 38, 39, 42, 43, 36, 44)]
lens = [g(n) for n in (80, 19, 45, 163, 164, 165, 166,
                       81, 20, 46, 167, 168, 169)]
pills_ = [g(n) for n in (70, 71, 72, 73, 74, 75, 3, 4, 6, 5, 7, 8)]
actives = lines + labels + stairs + vals + lens + pills_ + [img]
order = actives + parked
assert len(order) == len(d.gauges), (len(order), len(d.gauges))
n = d.save(OUT, order=order)
print("saved v8", n, "actives", len(actives), "image idx", order.index(img))
