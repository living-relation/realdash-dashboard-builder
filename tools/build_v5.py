#!/usr/bin/env python3
"""build_v5.py - 'GLACIER TELEMETRY' light-theme engineering board.

Style: pale glacier-blue canvas, white cards, dark slate numerals, deep-teal
accents, dark-amber/red alarms. Completely different from v1-v4 (first light
theme). New gauge types used:
  - GRAPH gauge: hero live throttle trace (center top)
  - NEEDLE gauge: CHARGE IAT dial (dark chrome anchor on light bg)
  - BAR gauge: engine load fill
  - ARC gauge: ethanol ring on a dark tile
  - IMAGE gauge: warning-triangle indicator lit by trigger errors

Constraints honored (learned this session):
  - image-type records grouped at END, Image Gauge 1 last
  - only needle records may be cloned (bar/graph/image clones HANG the app;
    arc clones silently don't render) - v5 uses each once, no clones
  - autoscale: only write segments (+44) / maxdig (+52); +40 and +56
    writes blank image-type gauges
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\probe_base.rd"
DST = sys.argv[1]

CANVAS = 0xFFE9EDF2
CARD = 0xFFFFFFFF
DARKCARD = 0xFF1E2A33
INK = 0xFF1E2A33
MUTED = 0xFF5D6B78
TEAL = 0xFF0E8C96
WARN = 0xFFC77800
CRIT = 0xFFC62828
GHOST_BG = 0xFFD8DEE5
GHOST_TX = 0xFF8A94A0
TRACK = 0xFFDCE2E9
TRANSP = 0x00000000
BIG = 9e9

H = {
    "throttle": 0xA5AA7D05, "boostmap": 0xE1F72794, "tc": 0x4E28D27A,
    "lambda": 0x9ED3572B, "iat": 0x978E3E78, "coolp": 0xDD266D22,
    "turbo": 0x413F90BA, "load": 0x9007B539, "fuelt": 0x80D7FC73,
    "eth": 0xBDB0E378, "trig": 0x04B07E8E, "cruise": 0x18ECF9C1,
    "ac": 0xE975C645, "flat": 0x6B5F9216, "fan": 0xC44AB478,
    "lofuel": 0xDD06C8FD, "sbflt": 0x7F8E9FE9, "hicool": 0x3A7D877E,
    "looil": 0xAD193AD0, "none": 0xFFFFFFFF,
}

d = Dash2(SRC)
m = d.by_name()


def panel(nm, x, y, w, h, bg):
    g = m[nm]
    g.set_rect_px(x, y, w, h)
    g.set_texts("")
    g.set_bg_states(bg, bg)
    g.set_arr(2, [bg] * 6, flag=0)
    g.set_tcolor(bg)
    g.set_hash(H["none"])
    return g


def label(nm, x, y, w, h, text, color=MUTED):
    g = m[nm]
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    g.set_fsize_for_h(h)
    g.set_bg_states(TRANSP, TRANSP)
    g.set_arr(2, [color] * 6, flag=0)
    g.set_tcolor(color)
    g.set_hash(H["none"])
    return g


def value(nm, x, y, w, h, hkey, dec, vmin, vmax, warn=None, crit=None,
          below=None, normal=INK, wcol=WARN, ccol=CRIT, baked="0"):
    g = m[nm]
    g.set_rect_px(x, y, w, h)
    g.set_texts(baked)
    g.set_fsize_for_h(h)
    g.set_bg_states(TRANSP, TRANSP)
    g.set_arr(2, [normal, wcol, ccol] * 2, flag=0)
    g.set_tcolor(normal)
    g.set_hash(H[hkey])
    g.set_decimals(dec)
    g.set_ranges(vmin, vmax,
                 warn=warn if warn is not None else BIG,
                 crit=crit if crit is not None else BIG,
                 warn_below=below if below is not None else -BIG,
                 crit_below=below if below is not None else -BIG)
    return g


def park(g):
    g.set_rect_px(797, 0, 2, 2)
    if g.type == 2:
        g.set_texts("")
        g.set_bg_states(TRANSP, TRANSP)
        g.set_arr(2, [TRANSP] * 6, flag=0)
        g.set_tcolor(TRANSP)
    g.set_hash(H["none"])
    return g


d.set_canvas_bg(CANVAS)

# ---------- top rail: status chips ----------
chips_bg = [
    panel("Text Gauge 9", 20, 10, 210, 34, CARD),
    panel("Text Gauge 10", 295, 10, 210, 34, CARD),
    panel("Text Gauge 11", 570, 10, 210, 34, CARD),
]
chips_fg = [
    label("Text Gauge 150", 36, 19, 60, 16, "TC", color=TEAL),
    label("Text Gauge 32", 311, 19, 90, 16, "CRUISE", color=TEAL),
    label("Text Gauge 33", 586, 19, 60, 16, "A/C", color=TEAL),
    value("Text Gauge 36", 140, 17, 74, 20, "tc", 0, 0, 4),
    value("Text Gauge 45", 396, 17, 92, 20, "cruise", 0, 0, 4, baked="---"),
    value("Text Gauge 46", 671, 17, 92, 20, "ac", 0, 0, 3,
          warn=3, crit=3, baked="---", wcol=CRIT, ccol=CRIT),
]

# ---------- left: CHARGE IAT needle dial ----------
n_iat = m["Needle Gauge 1"]
n_iat.rename("Needle IAT")
n_iat.set_rect_px(24, 64, 216, 240)
n_iat.set_hash(H["iat"])
n_iat.set_decimals(0)
n_iat.set_ranges(0, 120, warn=50, crit=60, warn_below=-99, crit_below=-99)
n_iat.set_autoscale(maxdig=3, segments=7)     # labels 0,20,...,120

left_fg = [
    value("Text Gauge 38", 76, 288, 112, 28, "iat", 0, 0, 120,
          warn=50, crit=60, below=-99),
    label("Text Gauge 25", 24, 322, 216, 14, "CHARGE IAT \u00b0C"),
]

# left lower card: TURBO RPM
card_turbo = panel("Text Gauge 12", 20, 352, 220, 84, CARD)
left_fg += [
    label("Text Gauge 27", 36, 362, 190, 13, "TURBO RPM"),
    value("Text Gauge 40", 36, 380, 190, 44, "turbo", 0, 0, 200000,
          warn=180000, crit=190000),
]

# ---------- center: throttle trace hero + lambda + boost map ----------
card_graph = panel("Text Gauge 13", 262, 64, 276, 150, CARD)
graph = m["Graph Gauge 1"]
graph.rename("Graph Throttle")
graph.set_rect_px(270, 88, 260, 118)
graph.set_hash(H["throttle"])
graph.set_decimals(0)
graph.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
graph.replace_level_colors(TEAL, WARN, CRIT)
center_fg = [
    label("Text Gauge 23", 270, 70, 180, 13, "THROTTLE % \u00b7 LIVE"),
    value("Text Gauge 34", 468, 68, 62, 18, "throttle", 0, 0, 100,
          normal=TEAL),
]

card_lam = panel("Text Gauge 14", 262, 224, 276, 108, CARD)
center_fg += [
    label("Text Gauge 24", 278, 234, 180, 14, "TARGET \u03bb"),
    value("Text Gauge 37", 278, 252, 244, 66, "lambda", 2, 0.6, 1.3,
          baked="0.60"),
]

card_bm = panel("Text Gauge 15", 262, 342, 276, 94, CARD)
center_fg += [
    label("Text Gauge 22", 278, 352, 140, 13, "BOOST MAP"),
    value("Text Gauge 35", 278, 370, 120, 54, "boostmap", 0, 0, 3,
          normal=TEAL),
    label("Text Gauge 31", 420, 352, 100, 13, "TRIG ERR"),
    value("Text Gauge 44", 420, 370, 100, 54, "trig", 0, 0, 255,
          warn=1, crit=5),
]

# warning triangle lights up with trigger errors
img = m["Image Gauge 1"]
img.rename("Image TrigWarn")
img.set_rect_px(497, 344, 34, 40)
img.set_hash(H["trig"])
img.set_decimals(0)
img.set_ranges(0, 255, warn=1, crit=5, warn_below=-BIG, crit_below=-BIG)
img.set_arr(1, [0x00000000, CRIT, CRIT] * 2, flag=0)   # blend: hidden->red

# ---------- right column cards ----------
card_load = panel("Text Gauge 16", 560, 64, 220, 88, CARD)
bar = m["Bar Gauge 1"]
bar.rename("Bar Load")
bar.set_rect_px(576, 118, 188, 16)
bar.set_hash(H["load"])
bar.set_decimals(0)
bar.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
bar.replace_level_colors(TEAL, WARN, CRIT)
right_fg = [
    label("Text Gauge 28", 576, 74, 140, 13, "ENGINE LOAD %"),
    value("Text Gauge 41", 704, 72, 60, 22, "load", 0, 0, 100),
]
bar_track = panel("Text Gauge 17", 576, 118, 188, 16, TRACK)

card_cool = panel("Text Gauge 18", 560, 162, 220, 84, CARD)
right_fg += [
    label("Text Gauge 26", 576, 172, 190, 13, "COOLANT P kPa"),
    value("Text Gauge 39", 576, 190, 190, 44, "coolp", 0, 0, 1000,
          warn=150, crit=250),
]
card_fuel = panel("Text Gauge 19", 560, 256, 220, 84, CARD)
right_fg += [
    label("Text Gauge 29", 576, 266, 190, 13, "FUEL TEMP \u00b0C"),
    value("Text Gauge 42", 576, 284, 190, 44, "fuelt", 0, -50, 205,
          warn=55, crit=70, below=-99),
]

# ethanol: dark tile + arc ring
card_eth = panel("Text Gauge 20", 560, 350, 220, 86, DARKCARD)
arc = m["Arc Gauge 1"]
arc.rename("Arc Ethanol")
arc.set_rect_px(584, 354, 72, 78)
arc.set_hash(H["eth"])
arc.set_decimals(0)
arc.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
arc.set_autoscale(segments=3, maxdig=3)      # quiet scale: 0/50/100
arc.replace_level_colors(0xFF77E6EE, WARN, CRIT)
right_fg += [
    label("Text Gauge 30", 668, 366, 100, 13, "ETHANOL %", color=0xFF9FB4C2),
    value("Text Gauge 43", 668, 384, 100, 40, "eth", 0, 0, 100,
          normal=0xFF77E6EE),
]

# ---------- bottom alarm pills ----------
PILLS = [
    ("Text Gauge 3", "FLAT", "flat", 20, False),
    ("Text Gauge 4", "FAN", "fan", 148, True),
    ("Text Gauge 6", "LOFUEL", "lofuel", 276, False),
    ("Text Gauge 5", "SBFLT", "sbflt", 404, False),
    ("Text Gauge 7", "COOLANT P", "hicool", 532, False),
    ("Text Gauge 8", "OIL P 2", "looil", 660, False),
]
pills = []
for nm, txt, hk, x, steady in PILLS:
    g = m[nm]
    g.set_rect_px(x, 450, 120, 22)
    g.set_texts(txt)
    g.set_fsize_for_h(22)
    g.set_hash(H[hk])
    g.set_decimals(0)
    if steady:
        g.set_bg_states(GHOST_BG, TEAL)
        g.set_arr(2, [GHOST_TX] * 3 + [CARD] * 3, flag=1)
        g.set_tcolor(GHOST_TX)
        g.set_ranges(0, 1, warn=999, crit=999, warn_below=-999, crit_below=-999)
    else:
        g.set_bg_states(GHOST_BG, CRIT)
        g.set_arr(2, [GHOST_TX] * 3 + [CARD] * 3, flag=1)
        g.set_tcolor(GHOST_TX)
        g.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
    pills.append(g)

# ---------- park everything unused ----------
used = {g.name for g in
        chips_bg + chips_fg + left_fg + center_fg + right_fg + pills +
        [n_iat, graph, bar, bar_track, arc, img, card_turbo, card_graph,
         card_lam, card_bm, card_load, card_cool, card_fuel, card_eth]}
parked = []
for g in d.gauges:
    if g.name not in used:
        parked.append(park(g))

# ---------- paint order: text first, image types grouped last ----------
text_order = [g for g in parked if g.type == 2]
text_order += chips_bg + [card_turbo, card_graph, card_lam, card_bm,
                          card_load, card_cool, card_fuel, card_eth,
                          bar_track]
text_order += chips_fg + left_fg + center_fg + right_fg + pills
img_order = [arc, graph, bar, n_iat, img]
order = text_order + img_order
seen = set()
final = []
for g in order:
    if g.name not in seen:
        seen.add(g.name)
        final.append(g)
assert len(final) == len(d.gauges), "%d vs %d" % (len(final), len(d.gauges))
n, c = d.save(DST, order=final)
print("built %s: %d bytes, %d gauges" % (DST, n, c))
