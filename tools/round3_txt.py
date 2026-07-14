#!/usr/bin/env python3
"""round3_txt.py - round-3 fixes for the three text-tile dashes (v1/v2/v3).

Per dash:
  * Turbo readout: gauge math '=V/1000' injected binarily (byte pattern proven
    identical to the GUI edit via probe_gm.rd diff), ranges rescaled to k units
    (min 0 / max 255 / warn 180 / crit 190), plus a small 'k' unit chip.
  * Label/unit convention: units move out of labels into small dim unit chips
    next to the value (CHARGE TEMP + degC, COOLANT P + kPa, FUEL TEMP + degC).
  * CRUISE / A/C: value gauge background lights per level. Cruise: STBY(1) =
    dim, SET/RES/OVR(>=2) = bright. A/C: REQ/ON(>=1) = lit, FLT(3) = red.
  * v2: top throttle strip becomes a real 13-segment LED bar (each segment
    is a bound text gauge whose bg flips lit at its own threshold, aligned to
    the 25/50/75 tick positions) and the red end-block lights at >=85% (WOT).
  * v3: BOOST MAP tile gets LOW/MID/HIGH/MAX band-lit chips (lit only while
    the map index is inside that band) and a 4-segment cumulative position
    bar under them.

All outputs keep the proven 124-record shape. Writes in place (backups exist
in _build/backup/*round3pre*).
"""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

DL = r"C:\Users\danie\Downloads"
TRANSP = 0x00000000
UNBOUND = 0xFFFFFFFF


def set_unit(d, m, name, x, y, w, h, text, color):
    """Repurpose a record into a static dim unit chip."""
    g = m[name]
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    g.set_fsize_for_h(h)
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [color] * 6, flag=0)
    g.set_tcolor(color)
    g.set_hash(UNBOUND)
    return g


def park(d, m, name):
    g = m[name]
    g.set_rect_px(797, 0, 2, 2)
    g.set_texts("")
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [TRANSP] * 6, flag=0)
    g.set_tcolor(TRANSP)
    g.set_hash(UNBOUND)
    return g


def seg_chip(d, m, name, x, y, w, h, hsh, vmin, vmax, warn, crit,
             col_norm, col_warn, col_crit):
    """Bound chip with invisible text; bg lights per level."""
    g = m[name]
    g.set_rect_px(x, y, w, h)
    g.set_texts("")
    g.set_fsize_for_h(h)
    g.set_hash(hsh)
    g.set_decimals(0)
    g.set_ranges(vmin, vmax, warn=warn, crit=crit,
                 warn_below=-999, crit_below=-999)
    g.set_arr(0, [col_norm, col_warn, col_crit] * 2, flag=0)
    g.set_arr(2, [TRANSP] * 6, flag=0)   # live number stays invisible
    g.set_tcolor(TRANSP)
    return g


def light_enum(g, warn_bg, crit_bg, warn, crit, vmax,
               txt_norm, txt_lit):
    """Bound enum/value gauge: transparent bg normally, lit per level."""
    g.set_ranges(0, vmax, warn=warn, crit=crit, warn_below=-999,
                 crit_below=-999)
    g.set_arr(0, [TRANSP, warn_bg, crit_bg] * 2, flag=0)
    g.set_arr(2, [txt_norm, txt_lit, txt_lit] * 2, flag=0)


def fix_turbo(g):
    g.set_gauge_math("=V/1000")
    g.set_decimals(0)
    g.set_ranges(0, 255, warn=180, crit=190, warn_below=0, crit_below=0)


# ================= v1 =================
d = Dash2(DL + r"\st185_dash.rd")
m = d.by_name()

fix_turbo(m["Text Gauge 40"])
uc = 0xFF7A8CA0
m["Text Gauge 25"].set_texts("CHARGE TEMP")
m["Text Gauge 26"].set_texts("COOLANT P")
m["Text Gauge 29"].set_texts("FUEL TEMP")
# unit chips: repurpose the 8 decorative value-underline bars (4 chips,
# 4 parked so all tiles stay consistent)
set_unit(d, m, "Text Gauge 184", 170, 216, 36, 20, "\u00b0C", uc)   # charge
set_unit(d, m, "Text Gauge 185", 352, 216, 44, 20, "kPa", uc)       # coolant
set_unit(d, m, "Text Gauge 186", 484, 216, 22, 20, "k", uc)         # turbo
set_unit(d, m, "Text Gauge 188", 170, 320, 36, 20, "\u00b0C", uc)   # fuel
for n in ("Text Gauge 181", "Text Gauge 182", "Text Gauge 187",
          "Text Gauge 189"):
    park(d, m, n)
# cruise: STBY dim steel, SET+ bright blue; A/C: lit blue, FLT red
light_enum(m["Text Gauge 45"], 0xFF23507A, 0xFF2E9BFF, warn=0.5,
           crit=1.5, vmax=4, txt_norm=0xFFF3F8FF, txt_lit=0xFFFFFFFF)
light_enum(m["Text Gauge 46"], 0xFF2E9BFF, 0xFFFF3226, warn=0.5,
           crit=2.5, vmax=3, txt_norm=0xFFF3F8FF, txt_lit=0xFFFFFFFF)
assert len(d.gauges) == 124
print("v1:", d.save(DL + r"\st185_dash.rd"))

# ================= v2 =================
PANEL = 0xFF121212
YELLOW = 0xFFFFD400
ORANGE = 0xFFFF7A00
SEGOFF = 0xFF1C1C1C
REDZONE = 0xFF200400
RED = 0xFFFF3226
GREEN = 0xFF3DDC5A
BLACK = 0xFF000000

d = Dash2(DL + r"\st185_dash_v2.rd")
m = d.by_name()
thr_hash = m["Text Gauge 34"].get_hash()

fix_turbo(m["Text Gauge 40"])
uc = 0xFF8C8C8C
m["Text Gauge 25"].set_texts("CHARGE TEMP")
m["Text Gauge 26"].set_texts("COOLANT P")
m["Text Gauge 29"].set_texts("FUEL TEMP")
set_unit(d, m, "Text Gauge 133", 516, 302, 40, 24, "\u00b0C", uc)   # charge
set_unit(d, m, "Text Gauge 134", 737, 302, 48, 24, "kPa", uc)       # coolant
set_unit(d, m, "Text Gauge 135", 290, 398, 36, 20, "\u00b0C", uc)   # fuel
set_unit(d, m, "Text Gauge 136", 92, 398, 20, 20, "k", uc)          # turbo

# --- top strip: 13 LED segments + red WOT block ---
# revert the old invisible whole-track glow to a static panel
track = m["Text Gauge 60"]
track.set_hash(UNBOUND)
track.set_arr(0, [PANEL] * 6, flag=0)
track.set_arr(2, [PANEL] * 6, flag=0)
track.set_tcolor(PANEL)

# strip scale: x=4..796 maps 0..100%, so ticks 200/399/598 = 25/50/75%
SEG_NAMES = ["Text Gauge %d" % n for n in range(110, 123)]  # 13 parked recs
segs = []
for i, nm in enumerate(SEG_NAMES):
    x = 8 + i * 50
    thr = (x - 4 + 23.0) / 792.0 * 100.0     # light at segment center
    lit = YELLOW if i < 10 else ORANGE
    segs.append(seg_chip(d, m, nm, x, 8, 46, 28, thr_hash,
                         0, 100, warn=thr, crit=999,
                         col_norm=SEGOFF, col_warn=lit, col_crit=lit))
# red end-block doubles as the WOT lamp (lights >= 85%)
wot = m["Text Gauge 163"]
wot.set_texts("")
wot.set_hash(thr_hash)
wot.set_decimals(0)
wot.set_ranges(0, 100, warn=85, crit=999, warn_below=-999, crit_below=-999)
wot.set_arr(0, [REDZONE, RED, RED] * 2, flag=0)
wot.set_arr(2, [TRANSP] * 6, flag=0)
wot.set_tcolor(TRANSP)

light_enum(m["Text Gauge 45"], 0xFF1E6B32, GREEN, warn=0.5,
           crit=1.5, vmax=4, txt_norm=0xFFF3F8FF, txt_lit=BLACK)
light_enum(m["Text Gauge 46"], GREEN, RED, warn=0.5,
           crit=2.5, vmax=3, txt_norm=0xFFF3F8FF, txt_lit=BLACK)

# paint order: segments right after the track (under ticks/labels)
segset = set(SEG_NAMES)
order = []
for g in d.gauges:
    if g.name in segset:
        continue
    order.append(g)
    if g.name == "Text Gauge 60":
        order.extend(segs)
assert len(order) == 124, len(order)
print("v2:", d.save(DL + r"\st185_dash_v2.rd", order=order))

# ================= v3 =================
CHIPBG = 0xFF14122A
CYAN = 0xFF00F0FF
VIOLET = 0xFF8878FF
GHOST = 0xFF3A3358
DARKTX = 0xFF0A0818
REDV = 0xFFFF4D57

d = Dash2(DL + r"\st185_dash_v3.rd")
m = d.by_name()
map_hash = m["Text Gauge 35"].get_hash()

fix_turbo(m["Text Gauge 40"])
uc = 0xFF8878B8
m["Text Gauge 25"].set_texts("CHARGE TEMP")
m["Text Gauge 26"].set_texts("COOLANT P")
m["Text Gauge 29"].set_texts("FUEL TEMP")
set_unit(d, m, "Text Gauge 100", 646, 100, 40, 22, "\u00b0C", uc)   # charge
set_unit(d, m, "Text Gauge 101", 676, 188, 48, 22, "kPa", uc)       # coolant
set_unit(d, m, "Text Gauge 102", 646, 276, 40, 22, "\u00b0C", uc)   # fuel
set_unit(d, m, "Text Gauge 112", 110, 364, 22, 22, "k", uc)         # turbo

# --- BOOST MAP tile: band-lit LOW/MID/HIGH/MAX chips + position bar ---
park(d, m, "Text Gauge 200")   # old static caption line
park(d, m, "Text Gauge 77")    # old inner track bar

CHIP_LBL = ["LOW", "MID", "HIGH", "MAX"]
chip_bgs, chip_txts, segs3 = [], [], []
for k in range(4):
    x = 278 + k * 62
    # band chip: warning inside [k-0.5, k+0.5) = lit; critical past it = off
    chip_bgs.append(seg_chip(d, m, "Text Gauge %d" % (9 + k), x, 218, 56, 24,
                             map_hash, 0, 3, warn=k - 0.5, crit=k + 0.5,
                             col_norm=CHIPBG, col_warn=VIOLET,
                             col_crit=CHIPBG))
    t = set_unit(d, m, "Text Gauge %d" % (13 + k), x, 223, 56, 14,
                 CHIP_LBL[k], GHOST)
    chip_txts.append(t)
    # cumulative position segment (lit while map >= k-0.5)
    segs3.append(seg_chip(d, m, "Text Gauge %d" % (79 + k),
                          272 + k * 65, 250, 61, 10, map_hash,
                          0, 3, warn=k - 0.5, crit=999,
                          col_norm=CHIPBG, col_warn=CYAN, col_crit=CYAN))

light_enum(m["Text Gauge 45"], 0xFF106878, CYAN, warn=0.5,
           crit=1.5, vmax=4, txt_norm=0xFFF3F8FF, txt_lit=DARKTX)
light_enum(m["Text Gauge 46"], CYAN, REDV, warn=0.5,
           crit=2.5, vmax=3, txt_norm=0xFFF3F8FF, txt_lit=DARKTX)

# order: chip bgs + position segments after the track outline 76;
# legends after the map value (on top of the lit chips)
moved = set(g.name for g in chip_bgs + chip_txts + segs3)
order = []
for g in d.gauges:
    if g.name in moved:
        continue
    order.append(g)
    if g.name == "Text Gauge 76":
        order.extend(chip_bgs)
        order.extend(segs3)
    if g.name == "Text Gauge 44":
        order.extend(chip_txts)
assert len(order) == 124, len(order)
print("v3:", d.save(DL + r"\st185_dash_v3.rd", order=order))
