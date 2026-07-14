#!/usr/bin/env python3
"""r5_v10.py - build st185_dash_v10.rd "MERIDIAN GT" (round 5).

Design: big CENTER-DIAL classic with modern flat trim. Warm graphite
canvas, one large perfectly-circular turbo dial (aspect compensation
K=1.152 from the start), flat porcelain/copper trim, left column
Throttle hero + bar + lambda/boost/tc-mode/ethanol, right column Engine
Load hero + load trace graph + coolant/charge/fuel, CRUISE & A/C state
lenses, six steady pills (flag=0 static, zero blink everywhere).

Donor: _build/b2_v9_donor.rd (asset donor + RaceHead/Aerospace/Draco).
"""
import math
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4_common import Dash2, H, TRANSP, set_static, park  # noqa: E402
from rd_lib2 import read_str  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

BUILD = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build"
SRC = BUILD + r"\b2_v9_donor.rd"
FACE = BUILD + r"\r5_meridian_face.png"
OUT = r"C:\Users\danie\Downloads\st185_dash_v10.rd"

K = 1.152                       # h_design = K * w_design -> circular render
H_TCI = 0x5A59FBBD

BG = 0xFF13110E
PANEL = 0xFF1B1815
TRACK = 0xFF262119
LENS_DK = 0xFF17140F
NEARBLK = 0xFF0F0D0A
COPPER = 0xFFB87333
COPBRT = 0xFFD98F4E
PORC = 0xFFF4EFE6
LBL = 0xFF8D857A
CHIPC = 0xFF6E675C
AMBER = 0xFFE8A13C
RED = 0xFFE8482B
BIG = 9e9

RACE, AERO, DRACO, DEF = "RaceHead.ttf", "Aerospace.ttf", "Draco.otf", "defaultdashfont"

# ---------------- face art: classic dial, modern flat trim ----------------
SZ = 972
C = SZ / 2.0
img = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
dr = ImageDraw.Draw(img)


def xy(deg, r):
    a = math.radians(deg)
    return (C + r * math.cos(a), C - r * math.sin(a))


def tick(deg, r0, r1, w, color):
    p0, p1 = xy(deg, r0), xy(deg, r1)
    dr.line([p0, p1], fill=color, width=w)


FACE_C = (0x19, 0x16, 0x13, 255)
COP = (0xB8, 0x73, 0x33, 255)
PORC_C = (0xF4, 0xEF, 0xE6, 255)
MIN_C = (0x57, 0x50, 0x3F, 255)
RED_C = (0xE8, 0x48, 0x2B, 255)
HUB_C = (0x14, 0x11, 0x0D, 255)
HAIR = (0x2A, 0x25, 0x1E, 255)

dr.ellipse([C - 466, C - 466, C + 466, C + 466], fill=FACE_C)
dr.ellipse([C - 466, C - 466, C + 466, C + 466], outline=COP, width=4)
dr.ellipse([C - 310, C - 310, C + 310, C + 310], outline=HAIR, width=2)
# red band 93.75%..100% of 0-160k = 150-160k
a_hi, a_end = 225 - 0.9375 * 270, 225 - 270
for rr in range(404, 452):
    dr.arc([C - rr, C - rr, C + rr, C + rr], -a_hi, -a_end, fill=RED_C, width=3)
for k in range(5):
    tick(225 - k * 67.5, 396, 452, 13, PORC_C)
for k in range(4):
    for j in range(1, 4):
        tick(225 - k * 67.5 - j * 16.875, 428, 452, 4, MIN_C)
dr.ellipse([C - 46, C - 46, C + 46, C + 46], fill=HUB_C)
dr.ellipse([C - 46, C - 46, C + 46, C + 46], outline=COP, width=4)
img.save(FACE, "PNG")
print("face saved", FACE)

# ---------------- donor + asset splice ----------------
d = Dash2(SRC)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]
d.set_canvas_bg(BG)


def splice_asset(dash, name, png_path):
    hh = bytes(dash.header)
    i = 0
    while i < len(hh) - 8:
        r = read_str(hh, i)
        if r and r[0] == name:
            size_off = r[1]
            old = struct.unpack_from("<I", hh, size_off)[0]
            blob = b"\x00\x00\x00\x00" + open(png_path, "rb").read()
            dash.header = bytearray(
                hh[:size_off] + struct.pack("<I", len(blob)) + blob
                + hh[size_off + 4 + old:])
            return old, len(blob)
        i += 1
    raise KeyError(name)


print("face spliced:", splice_asset(d, "roundface.png", FACE))


# ---------------- helpers (b2_v9-proven) ----------------
def zero_blink(gg):
    off = gg._range_off()
    struct.pack_into("<3f", gg.b, off + 40, 0.0, 0.0, 0.0)


def static_bg(gg, argb):
    if gg.type == 2:
        struct.pack_into("<I", gg.b, gg.nend + 0x5C, argb)


def label(gg, x, y, w, h, text, color=LBL, font=AERO):
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
    gg.set_font(font)
    gg.set_level_fonts(font)
    gg.set_rect_px(x, y, w, h)
    set_static(gg, False)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [PORC, AMBER, RED] * 2, flag=0)
    gg.set_tcolor(PORC)
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


def word(gg, x, y, w, h, hash_, vmax, warn, crit, words, tcs, font=AERO):
    gg.set_font(font)
    gg.set_level_fonts(font)
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


def pill_housing(gg, x, y, w, h, hash_, lit):
    """PERMANENT round-5 recipe: flag=0 STATIC [off, lit, lit] - hard
    on/off, no value-lerp fade, zero blink."""
    gg.set_font(DEF)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts("", ["", "", ""])
    set_static(gg, True)
    static_bg(gg, LENS_DK)
    gg.set_arr(0, [LENS_DK, lit, lit] * 2, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
    zero_blink(gg)


def pill_word(gg, x, y, w, h, text, hash_, lit_tc):
    gg.set_font(AERO)
    gg.set_level_fonts(AERO)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(text, [text, text, text])
    set_static(gg, True)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [0xFF4A443B, lit_tc, lit_tc] * 2, flag=0)
    gg.set_tcolor(0xFF4A443B)
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
    zero_blink(gg)


# ---------------- header ----------------
label(g(60), 16, 8, 340, 20, "ST185 GT-FOUR", PORC, DRACO)
label(g(61), 16, 33, 340, 10, "MERIDIAN GT - V10", LBL, AERO)
rulebar(g(62), 16, 48, 768, 2, COPPER)

# ---------------- center dial (turbo, K-compensated) ----------------
n_turbo = m["Needle Gauge 1"]
n_turbo.rename("Needle Turbo")
n_turbo.set_gauge_math("=V/1000")           # FIRST write on this record
DW = 270.0
DH = DW * K                                 # 311.0
DCX, DCY = 400.0, 206.0
n_turbo.set_rect_px(DCX - DW / 2, DCY - DH / 2, DW, DH)
n_turbo.set_hash(H["turbo"])
n_turbo.set_decimals(0)
n_turbo.set_ranges(0, 160, warn=140, crit=150, warn_below=-BIG, crit_below=-BIG)
n_turbo.set_autoscale(maxdig=3, segments=5)  # 0/40/80/120/160
n_turbo.set_arr(1, [0xFFFFFFFF] * 6, flag=0)  # face true color
n_turbo.set_arr(2, [PORC] * 6, flag=0)        # scale label color

# in-dial caption + readout (painted after the needle)
label(g(70), 352, 262, 96, 11, "TURBO", LBL, AERO)
tg40 = g(40)
tg40.set_gauge_math("=V/1000")              # FIRST write on this gauge
value(tg40, 340, 276, 120, 36, RACE)
tg40.set_decimals(0)
tg40.set_ranges(0, 255, warn=180, crit=190, warn_below=-BIG, crit_below=-BIG)
label(g(73), 462, 290, 50, 13, "k RPM", CHIPC, DEF)

# under-dial TC CUT
label(g(32), 352, 372, 96, 10, "TC CUT", LBL, AERO)
tg44 = g(44)
tg44.set_hash(H_TCI)
tg44.set_texts("0", ["0", "0", "0"])
value(tg44, 362, 384, 50, 26, RACE)
tg44.set_decimals(0)
tg44.set_ranges(0, 100, warn=1, crit=40, warn_below=-999, crit_below=-999)
label(g(75), 416, 392, 22, 13, "%", CHIPC, DEF)

# ---------------- left column ----------------
label(g(23), 20, 64, 160, 11, "THROTTLE %", LBL, AERO)
value(g(34), 20, 78, 130, 46, RACE)
g(34).set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
rulebar(g(13), 20, 132, 228, 10, TRACK)
bar = m["Bar Gauge 1"]
bar.rename("Bar Throttle")
bar.set_rect_px(20, 132, 228, 10)
bar.set_hash(H["throttle"])
bar.set_decimals(0)
bar.set_ranges(0, 100, warn=85, crit=BIG, warn_below=-BIG, crit_below=-BIG)
bar.replace_level_colors(COPBRT, AMBER, RED)

label(g(24), 20, 158, 160, 11, "TARGET \u03bb", LBL, DEF)
value(g(37), 20, 172, 110, 36, RACE)
g(37).set_ranges(0, 2, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)

label(g(22), 20, 222, 160, 11, "BOOST MAP", LBL, AERO)
value(g(35), 20, 236, 80, 32, RACE)
label(g(150), 20, 282, 160, 11, "TC MODE", LBL, AERO)
value(g(36), 20, 296, 80, 32, RACE)
label(g(30), 20, 342, 160, 11, "ETHANOL %", LBL, AERO)
value(g(43), 20, 356, 90, 30, RACE)
g(43).set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)

# badge
label(g(31), 20, 398, 170, 14, "MERIDIAN", COPBRT, DRACO)
label(g(28), 20, 415, 170, 8, "GRAND TOURING PANEL", 0xFF57503F, AERO)

# ---------------- right column ----------------
label(g(71), 552, 64, 170, 11, "ENGINE LOAD %", LBL, AERO)
value(g(41), 552, 78, 130, 46, RACE)
g(41).set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
rulebar(g(12), 552, 132, 232, 64, LENS_DK)
graph = m["Graph Gauge 1"]
graph.rename("Graph Load")
graph.set_rect_px(552, 132, 232, 64)
graph.set_hash(H["load"])
graph.set_decimals(0)
graph.set_ranges(0, 100, warn=70, crit=90, warn_below=-BIG, crit_below=-BIG)
graph.replace_level_colors(COPBRT, AMBER, RED)

label(g(27), 552, 222, 130, 11, "COOLANT P", LBL, AERO)
value(g(39), 552, 236, 84, 30, RACE)
g(39).set_ranges(0, 300, warn=150, crit=250, warn_below=-BIG, crit_below=-BIG)
label(g(77), 642, 246, 40, 13, "kPa", CHIPC, DEF)

label(g(26), 552, 282, 130, 11, "CHARGE TEMP", LBL, AERO)
value(g(38), 552, 296, 84, 30, RACE)
g(38).set_ranges(-50, 150, warn=60, crit=80, warn_below=-99, crit_below=-99)
label(g(76), 642, 306, 36, 13, "\u00b0C", CHIPC, DEF)

label(g(29), 552, 342, 130, 11, "FUEL TEMP", LBL, AERO)
value(g(42), 552, 356, 84, 30, RACE)
g(42).set_ranges(-50, 150, warn=60, crit=80, warn_below=-99, crit_below=-99)
label(g(78), 642, 366, 36, 13, "\u00b0C", CHIPC, DEF)

# ---------------- CRUISE / A-C ----------------
CR_BG = [LENS_DK, 0xFF3A342C, COPBRT, PORC, 0xFFFF7A1A]
CR_W = ["OFF", "STBY", "SET", "RES", "OVR"]
CR_TC = [LBL, PORC, NEARBLK, NEARBLK, NEARBLK]
AC_BG = [LENS_DK, AMBER, COPBRT, RED]
AC_W = ["OFF", "REQ", "ON", "FLT"]
AC_TC = [LBL, NEARBLK, NEARBLK, PORC]

label(g(160), 16, 428, 64, 11, "CRUISE", LBL, AERO)
rulebar(g(80), 86, 422, 300, 26, COPPER)
rulebar(g(19), 87, 423, 298, 24, LENS_DK)
fill(g(45), 89, 425, 294, 20, H["cruise"], 4, 0.5, 1.5, CR_BG[0:3])
fill(g(163), 89, 425, 294, 20, H["cruise"], 4, 2.5, 3.5,
     [TRANSP, CR_BG[3], CR_BG[4]])
word(g(164), 161, 427, 150, 15, H["cruise"], 4, 0.5, 1.5,
     [CR_W[0], CR_W[1], ""], [CR_TC[0], CR_TC[1], TRANSP])
word(g(165), 161, 427, 150, 15, H["cruise"], 4, 1.5, 2.5,
     ["", CR_W[2], ""], [TRANSP, CR_TC[2], TRANSP])
word(g(166), 161, 427, 150, 15, H["cruise"], 4, 2.5, 3.5,
     ["", CR_W[3], CR_W[4]], [TRANSP, CR_TC[3], CR_TC[4]])

label(g(162), 400, 428, 40, 11, "A/C", LBL, AERO)
rulebar(g(81), 446, 422, 338, 26, COPPER)
rulebar(g(20), 447, 423, 336, 24, LENS_DK)
fill(g(46), 449, 425, 332, 20, H["ac"], 3, 0.5, 1.5, AC_BG[0:3])
fill(g(167), 449, 425, 332, 20, H["ac"], 3, 2.5, 999,
     [TRANSP, AC_BG[3], AC_BG[3]])
word(g(168), 541, 427, 148, 15, H["ac"], 3, 0.5, 1.5,
     [AC_W[0], AC_W[1], ""], [AC_TC[0], AC_TC[1], TRANSP])
word(g(169), 541, 427, 148, 15, H["ac"], 3, 1.5, 2.5,
     ["", AC_W[2], AC_W[3]], [TRANSP, AC_TC[2], AC_TC[3]])

# ---------------- pills (ALL steady, zero blink - round-5 rule) --------
PILLS = [
    (3, 9, "FLAT", RED, PORC),
    (4, 10, "FAN", COPBRT, NEARBLK),
    (6, 11, "LOFUEL", AMBER, NEARBLK),
    (5, 14, "SBFLT", AMBER, NEARBLK),
    (7, 15, "COOL P", RED, PORC),
    (8, 16, "OIL P", RED, PORC),
]
for i, (wrec, hrec, txt, lit, tc) in enumerate(PILLS):
    x = 16 + i * 129
    hsh = g(wrec).get_hash()
    pill_housing(g(hrec), x, 456, 120, 18, hsh, lit)
    pill_word(g(wrec), x, 459, 120, 12, txt, hsh, tc)

# ---------------- park unused ----------------
USED = {60, 61, 62, 70, 40, 73, 32, 44, 75,
        23, 34, 13, 24, 37, 22, 35, 150, 36, 30, 43, 31, 28,
        71, 41, 12, 27, 39, 77, 26, 38, 76, 29, 42, 78,
        160, 80, 19, 45, 163, 164, 165, 166,
        162, 81, 20, 46, 167, 168, 169,
        3, 4, 6, 5, 7, 8, 9, 10, 11, 14, 15, 16}
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
arc.set_rect_px(797, 0, 2, 2)
img_g = m["Image Gauge 1"]
img_g.set_rect_px(797, 0, 2, 2)

pad1, pad2 = parked[-2], parked[-1]
parked = parked[:-2]

# ---------------- paint order (v9-proven shape) ----------------
texts = [g(n) for n in (62, 13, 12, 80, 19, 81, 20,
                        60, 61, 23, 24, 22, 150, 30, 31, 28,
                        71, 27, 26, 29, 160, 162, 32,
                        34, 37, 35, 36, 43, 41, 39, 38, 42, 44, 75,
                        77, 76, 78,
                        45, 163, 164, 165, 166, 46, 167, 168, 169,
                        9, 10, 11, 14, 15, 16, 3, 4, 6, 5, 7, 8)]
late_texts = [g(n) for n in (70, 40, 73)]
order = (parked + texts + [arc, graph, bar, n_turbo]
         + late_texts + [img_g, pad1, pad2])
assert len(order) == len(d.gauges), (len(order), len(d.gauges))
n = d.save(OUT, order=order)
print("saved v10", n, "records", len(order), "img idx", order.index(img_g))
