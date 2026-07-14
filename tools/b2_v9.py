#!/usr/bin/env python3
"""b2_v9.py - build st185_dash_v9.rd "GLACIER AVIONICS" (Stage B2, round 4).

Donor: _build/b2_v9_donor.rd = asset_donor_template.rd + the 3 font asset
blocks spliced binarily into the header (NO GUI imports - B2 first).

Design: cold avionics panel. Blue-black canvas, twin HIDDEN-BEZEL floating
dials (heroes: Engine Load left, Turbo k RPM right - never-shipped bezel
treatment + neon-blue needle), Engine Load history graph w/ warning
shading, TC CUT live bar, annunciator-style state lenses and pills.
RaceHead values, Aerospace labels, Draco title.
"""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import Dash2, H, TRANSP, set_static, static_bg, park  # noqa: E402
from rd_lib2 import read_str  # noqa: E402

BUILD = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build"
SRC = BUILD + r"\b2_v9_donor.rd"
FACE = BUILD + r"\b2_glacier_face.png"
NEEDLE = BUILD + r"\assets\v4_assets\needle_blue.png"
OUT = r"C:\Users\danie\Downloads\st185_dash_v9.rd"

BG = 0xFF0C1116
ICE = 0xFFE9F2F8
CYAN = 0xFF48C8F0
STEEL = 0xFF5E6E7E
CHIP = 0xFF54626E
HAIR = 0xFF223039
AMBER = 0xFFFFB300
RED = 0xFFFF3040
PILL_BG = 0xFF121A22
LENS_IN = 0xFF0A0F14
FRAME = 0xFF2C3A46
TRACK = 0xFF10181F
NEARBLACK = 0xFF0A0F14
BIG = 9e9

RACE = "RaceHead.ttf"
AERO = "Aerospace.ttf"
DRACO = "Draco.otf"
DEF = "defaultdashfont"

d = Dash2(SRC)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]

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


print("face:", splice_asset(d, "roundface.png", FACE))
print("needle:", splice_asset(d, "needle.png", NEEDLE))


def zero_blink(gg):
    off = gg._range_off()
    for k in (40, 44, 48):
        struct.pack_into("<f", gg.b, off + k, 0.0)


def crit_blink(gg):
    struct.pack_into("<f", gg.b, gg._range_off() + 48, 1.0)


def label(gg, x, y, w, h, text, color=STEEL, font=AERO):
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
    zero_blink(gg)


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
    zero_blink(gg)


def value(gg, x, y, w, h, font=RACE):
    """Restyle existing bound value gauge (keeps hash/decimals/math/ranges)."""
    gg.set_font(font)
    gg.set_level_fonts(font)
    gg.set_rect_px(x, y, w, h)
    set_static(gg, False)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [ICE, AMBER, RED] * 2, flag=0)
    gg.set_tcolor(ICE)
    zero_blink(gg)


def pill_housing(gg, x, y, w, h, hash_, lit, blink=False):
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
    gg.set_arr(2, [0xFF3C4A56] * 3 + [lit_tc] * 3, flag=1)
    gg.set_tcolor(0xFF3C4A56)
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
label(g(60), 16, 8, 360, 20, "ST185 GT-FOUR", ICE, DRACO)
label(g(61), 16, 34, 360, 10, "GLACIER AVIONICS - V9", STEEL, AERO)
rulebar(g(62), 16, 52, 768, 2, FRAME)

# ---------------- twin hidden-bezel dials ----------------
n_load = m["Needle Gauge 1"]
n_load.rename("Needle Load")
n_load.set_rect_px(40, 58, 230, 230)
n_load.set_hash(H["load"])
n_load.set_decimals(0)
n_load.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG,
                  crit_below=-BIG)
n_load.set_autoscale(maxdig=3, segments=5)      # 0/25/50/75/100
n_load.set_arr(1, [0xFFFFFFFF] * 6, flag=0)     # face true-color
n_load.set_arr(2, [ICE] * 6, flag=0)            # scale label color

n_turbo = n_load.clone("Needle Turbo")
n_turbo.set_gauge_math("=V/1000")               # FIRST write on the clone
n_turbo.set_rect_px(530, 58, 230, 230)
n_turbo.set_hash(H["turbo"])
n_turbo.set_decimals(0)
n_turbo.set_ranges(0, 160, warn=140, crit=150, warn_below=-BIG,
                   crit_below=-BIG)
n_turbo.set_autoscale(maxdig=3, segments=5)     # 0/40/80/120/160
d.gauges.append(n_turbo)

# in-dial captions + readouts (painted after the needles)
label(g(71), 95, 240, 120, 11, "ENGINE LOAD %", STEEL, AERO)
value(g(41), 105, 254, 100, 32, RACE)
label(g(74), 207, 266, 26, 13, "%", CHIP, DEF)
label(g(70), 585, 240, 120, 11, "TURBO", STEEL, AERO)
tg40 = g(40)
tg40.set_gauge_math("=V/1000")                  # FIRST write on this gauge
value(tg40, 595, 254, 100, 32, RACE)
tg40.set_decimals(0)
tg40.set_ranges(0, 255, warn=180, crit=190, warn_below=-BIG, crit_below=-BIG)
label(g(73), 697, 266, 54, 13, "k RPM", CHIP, DEF)

# ---------------- center column ----------------
label(g(24), 316, 64, 168, 12, "TARGET \u03bb", STEEL, DEF)
value(g(37), 316, 80, 168, 44, RACE)
label(g(22), 316, 138, 168, 12, "BOOST MAP", STEEL, AERO)
value(g(35), 316, 154, 168, 40, RACE)
label(g(150), 316, 208, 168, 12, "TC MODE", STEEL, AERO)
value(g(36), 316, 224, 168, 40, RACE)

label(g(32), 316, 274, 168, 12, "TC CUT", STEEL, AERO)
rulebar(g(12), 316, 290, 168, 14, TRACK)
bar = m["Bar Gauge 1"]
bar.rename("Bar TCCut")
bar.set_rect_px(316, 290, 168, 14)
bar.set_hash(H["tci"])
bar.set_decimals(0)
bar.set_ranges(0, 100, warn=1, crit=40, warn_below=-BIG, crit_below=-BIG)
bar.replace_level_colors(CYAN, AMBER, RED)
tg44 = g(44)
tg44.set_texts("0", ["0", "0", "0"])
tg44.set_hash(H["tci"])
value(tg44, 316, 310, 70, 26, RACE)
tg44.set_decimals(0)
tg44.set_ranges(0, 100, warn=1, crit=40, warn_below=-999, crit_below=-999)
label(g(75), 390, 318, 22, 13, "%", CHIP, DEF)

rulebar(g(21), 16, 344, 768, 1, HAIR)

# ---------------- bottom band: graph + cells ----------------
label(g(23), 30, 352, 250, 11, "ENGINE LOAD HISTORY %", STEEL, AERO)
rulebar(g(13), 30, 366, 330, 56, TRACK)
graph = m["Graph Gauge 1"]
graph.rename("Graph Load")
graph.set_rect_px(30, 366, 330, 56)
graph.set_hash(H["load"])
graph.set_decimals(0)
graph.set_ranges(0, 100, warn=80, crit=95, warn_below=-BIG, crit_below=-BIG)
graph.replace_level_colors(CYAN, AMBER, RED)

CELLS = [
    # (labelrec, valrec, label, labelfont, chiprec, chiptext, col, row)
    (25, 34, "THROTTLE %", AERO, None, None, 0, 0),
    (26, 38, "CHARGE TEMP", AERO, 76, "\u00b0C", 1, 0),
    (27, 39, "COOLANT P", AERO, 77, "kPa", 2, 0),
    (29, 42, "FUEL TEMP", AERO, 78, "\u00b0C", 0, 1),
    (30, 43, "ETHANOL %", AERO, None, None, 1, 1),
]
COLX = (376, 512, 648)
ROWY = (352, 392)
for lr, vr, lt, lf, cr, ct, c, r in CELLS:
    x = COLX[c]
    y = ROWY[r]
    label(g(lr), x, y, 128, 10, lt, STEEL, lf)
    if cr is not None:
        value(g(vr), x, y + 12, 82, 24, RACE)
        label(g(cr), x + 68, y + 22, 40, 13, ct, CHIP, DEF)
    else:
        value(g(vr), x, y + 12, 128, 24, RACE)
# temps: BELOW guard so offline/sim negatives are not critical
g(38).set_ranges(-50, 150, warn=60, crit=80, warn_below=-99, crit_below=-99)
g(42).set_ranges(-50, 150, warn=60, crit=80, warn_below=-99, crit_below=-99)
# throttle: no alarm semantics (donor had a stale crit level)
g(34).set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
# badge in the empty 6th slot
label(g(31), 648, 398, 136, 12, "GLACIER", CYAN, DRACO)
label(g(28), 648, 414, 136, 8, "AVIONICS PANEL", 0xFF3C4A56, AERO)

# ---------------- CRUISE / A-C annunciators ----------------
CR_BG = [0xFF141C24, 0xFF3A4854, CYAN, ICE, 0xFFFF7A1A]
CR_W = ["OFF", "STBY", "SET", "RES", "OVR"]
CR_TC = [STEEL, ICE, NEARBLACK, NEARBLACK, NEARBLACK]
AC_BG = [0xFF141C24, AMBER, CYAN, RED]
AC_W = ["OFF", "REQ", "ON", "FLT"]
AC_TC = [STEEL, NEARBLACK, NEARBLACK, ICE]

label(g(160), 16, 434, 68, 11, "CRUISE", STEEL, AERO)
rulebar(g(80), 92, 428, 298, 24, FRAME)
rulebar(g(19), 93, 429, 296, 22, LENS_IN)
fill(g(45), 95, 431, 292, 18, H["cruise"], 4, 0.5, 1.5, CR_BG[0:3])
fill(g(163), 95, 431, 292, 18, H["cruise"], 4, 2.5, 3.5,
     [TRANSP, CR_BG[3], CR_BG[4]])
word(g(164), 167, 433, 148, 14, H["cruise"], 4, 0.5, 1.5,
     [CR_W[0], CR_W[1], ""], [CR_TC[0], CR_TC[1], TRANSP])
word(g(165), 167, 433, 148, 14, H["cruise"], 4, 1.5, 2.5,
     ["", CR_W[2], ""], [TRANSP, CR_TC[2], TRANSP])
word(g(166), 167, 433, 148, 14, H["cruise"], 4, 2.5, 3.5,
     ["", CR_W[3], CR_W[4]], [TRANSP, CR_TC[3], CR_TC[4]])

label(g(162), 412, 434, 42, 11, "A/C", STEEL, AERO)
rulebar(g(81), 458, 428, 326, 24, FRAME)
rulebar(g(20), 459, 429, 324, 22, LENS_IN)
fill(g(46), 461, 431, 320, 18, H["ac"], 3, 0.5, 1.5, AC_BG[0:3])
fill(g(167), 461, 431, 320, 18, H["ac"], 3, 2.5, 999,
     [TRANSP, AC_BG[3], AC_BG[3]])
word(g(168), 551, 433, 140, 14, H["ac"], 3, 0.5, 1.5,
     [AC_W[0], AC_W[1], ""], [AC_TC[0], AC_TC[1], TRANSP])
word(g(169), 551, 433, 140, 14, H["ac"], 3, 1.5, 2.5,
     ["", AC_W[2], AC_W[3]], [TRANSP, AC_TC[2], AC_TC[3]])

# ---------------- pills ----------------
PILLS = [
    (3, 9, "FLAT", RED, ICE, False),
    (4, 10, "FAN", CYAN, NEARBLACK, False),    # steady lit, working recipe
    (6, 11, "LOFUEL", AMBER, NEARBLACK, False),
    (5, 14, "SBFLT", AMBER, NEARBLACK, False),
    (7, 15, "COOL P", RED, ICE, True),         # blink on critical
    (8, 16, "OIL P", RED, ICE, True),          # blink on critical
]
for i, (wrec, hrec, txt, lit, tc, bl) in enumerate(PILLS):
    x = 16 + i * 129
    hsh = g(wrec).get_hash()
    pill_housing(g(hrec), x, 458, 120, 18, hsh, lit, blink=bl)
    pill_word(g(wrec), x, 461, 120, 12, txt, hsh, tc)

# ---------------- park unused ----------------
USED = ({60, 61, 62, 71, 41, 74, 70, 40, 73, 24, 37, 22, 35, 150, 36,
         32, 12, 44, 75, 21, 23, 13, 31, 28, 160, 80, 19, 45, 163, 164,
         165, 166, 162, 81, 20, 46, 167, 168, 169,
         3, 4, 6, 5, 7, 8, 9, 10, 11, 14, 15, 16}
        | {lr for lr, _, _, _, _, _, _, _ in CELLS}
        | {vr for _, vr, _, _, _, _, _, _ in CELLS}
        | {cr for _, _, _, _, cr, _, _, _ in CELLS if cr is not None})
parked = []
for gg in d.gauges:
    if gg.type != 2:
        continue
    n = int(gg.name.split()[-1])
    if n not in USED:
        park(gg)
        zero_blink(gg)
        parked.append(gg)
print("parked", len(parked), "; used", len(USED))

arc = m["Arc Gauge 1"]
arc.set_rect_px(797, 0, 2, 2)                   # park (single arc unused)
img = m["Image Gauge 1"]
img.set_rect_px(797, 0, 2, 2)                   # park (v4-proven)

pad1, pad2 = parked[-2], parked[-1]
parked = parked[:-2]

# ---------------- paint order (v4-proven shape) ----------------
texts = [g(n) for n in (62, 21, 12, 13, 80, 19, 81, 20,
                        60, 61, 24, 22, 150, 32, 23, 31, 28, 160, 162)]
texts += [g(lr) for lr, _, _, _, _, _, _, _ in CELLS]
texts += [g(cr) for _, _, _, _, cr, _, _, _ in CELLS if cr is not None]
texts += [g(n) for n in (37, 35, 36, 44, 75)]
texts += [g(vr) for _, vr, _, _, _, _, _, _ in CELLS]
texts += [g(n) for n in (45, 163, 164, 165, 166, 46, 167, 168, 169)]
texts += [g(n) for n in (9, 10, 11, 14, 15, 16, 3, 4, 6, 5, 7, 8)]
late_texts = [g(n) for n in (71, 41, 74, 70, 40, 73)]
order = (parked + texts + [arc, graph, bar, n_load, n_turbo]
         + late_texts + [img, pad1, pad2])
assert len(order) == len(d.gauges), (len(order), len(d.gauges))
n = d.save(OUT, order=order)
print("saved v9", n, "img idx", order.index(img), "of", len(order))
