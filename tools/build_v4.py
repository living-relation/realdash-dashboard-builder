#!/usr/bin/env python3
"""build_v4.py - 'PODIUM CLASSIC' analog-cluster dashboard (v2 layout).

Warm-black vintage motorsport cluster:
  - two chrome NEEDLE gauges (Throttle left, Turbo RPM right), clean faces
    (autoscale numerals off), digital readouts underneath
  - one ARC gauge on the center-bottom Coolant Pressure column
  - one real BAR gauge (Engine Load) in the center stack
  - one GRAPH gauge (live throttle history sparkline) under trigger errors
  - cream numerals, brass labels, red-orange alarms, steady FAN pill

Learned constraints honored:
  - image-type records (needle/arc/graph/bar/image) stay grouped at the END
    of the record list; Image Gauge 1 (asset-map trailer) is always last
  - arc records cannot be cloned (clones never render) - exactly one arc
  - needle clones DO render
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\probe_base.rd"
DST = sys.argv[1]

CANVAS = 0xFF171310
CHIP = 0xFF262019
CREAM = 0xFFF2EAD9
BRASS = 0xFFC7A25A
DIMBRASS = 0xFF7A6A4C
RED = 0xFFE8482B
AMBER = 0xFFF2A33C
HAIR = 0xFF3A3226
PILL_TXT = 0xFF6B5F4D
ARC_FILL = 0xFFE8D9B8
GRAPH_C = 0xFFC7A25A
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


def label(nm, x, y, w, h, text, color=BRASS):
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
          below=None, normal=CREAM, wcol=AMBER, ccol=RED, baked="0"):
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

# ---------- top chips ----------
chips_bg = [
    panel("Text Gauge 9", 40, 8, 200, 32, CHIP),
    panel("Text Gauge 10", 300, 8, 200, 32, CHIP),
    panel("Text Gauge 11", 560, 8, 200, 32, CHIP),
]
chips_fg = [
    label("Text Gauge 150", 56, 16, 60, 15, "TC"),
    label("Text Gauge 32", 316, 16, 90, 15, "CRUISE"),
    label("Text Gauge 33", 576, 16, 60, 15, "A/C"),
    value("Text Gauge 36", 150, 14, 70, 20, "tc", 0, 0, 4),
    value("Text Gauge 45", 396, 14, 84, 20, "cruise", 0, 0, 4, baked="---"),
    value("Text Gauge 46", 656, 14, 84, 20, "ac", 0, 0, 3,
          warn=3, crit=3, baked="---", wcol=RED, ccol=RED),
]

# ---------- needles (clean faces) ----------
n_thr = m["Needle Gauge 1"]
n_thr.rename("Needle Throttle")
n_thr.set_rect_px(34, 48, 230, 254)
n_thr.set_hash(H["throttle"])
n_thr.set_decimals(0)
n_thr.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
# NOTE: use_auto=False makes needle gauges vanish entirely; keep autoscale on
n_thr.set_autoscale(maxdig=3, segments=11)   # labels 0,10..100

n_tur = n_thr.clone("Needle Turbo")
n_tur.set_rect_px(536, 48, 230, 254)
n_tur.set_hash(H["turbo"])
# maxdig (autoscale +52) is a label TRUNCATION width: maxdig=1 rendered
# 10..18 as "1" (user-reported bug). maxdig=2 keeps double-digit labels;
# scale reads x10000 RPM: 0,2,4,6,8,10,12,14,16,18,20
# Label truncation is leading-chars (maxdig=1 caused the '1,1,1' bug), so
# mixed-magnitude scales need FULL labels: maxdig=6, majors every 50k
n_tur.set_ranges(0, 200000, warn=180000, crit=190000,
                 warn_below=-BIG, crit_below=-BIG)
n_tur.set_autoscale(maxdig=6, segments=5)
d.gauges.append(n_tur)

needle_fg = [
    value("Text Gauge 34", 89, 306, 120, 30, "throttle", 0, 0, 100),
    value("Text Gauge 40", 591, 306, 120, 24, "turbo", 0, 0, 200000,
          warn=180000, crit=190000),
    label("Text Gauge 23", 34, 340, 230, 14, "THROTTLE %"),
    label("Text Gauge 27", 536, 340, 230, 14, "TURBO RPM"),
]

# ---------- center stack ----------
c_parts = [
    label("Text Gauge 24", 300, 58, 200, 13, "TARGET \u03bb"),
    value("Text Gauge 37", 300, 74, 200, 54, "lambda", 2, 0.6, 1.3, baked="0.60"),
    panel("Text Gauge 60", 330, 138, 140, 2, HAIR),
    label("Text Gauge 22", 300, 148, 200, 13, "BOOST MAP"),
    value("Text Gauge 35", 300, 164, 200, 46, "boostmap", 0, 0, 3, normal=AMBER),
    label("Text Gauge 28", 300, 220, 200, 12, "ENGINE LOAD %"),
    value("Text Gauge 41", 300, 252, 200, 22, "load", 0, 0, 100),
    label("Text Gauge 31", 300, 284, 200, 12, "TRIGGER ERR"),
    value("Text Gauge 44", 300, 298, 200, 22, "trig", 0, 0, 255, warn=1, crit=5),
    label("Text Gauge 61", 300, 328, 200, 11, "THROTTLE TRACE", color=DIMBRASS),
]

bar = m["Bar Gauge 1"]
bar.rename("Bar Load")
bar.set_rect_px(300, 234, 200, 14)
bar.set_hash(H["load"])
bar.set_decimals(0)
bar.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
bar.replace_level_colors(BRASS, AMBER, RED)
bar_track = panel("Text Gauge 62", 300, 234, 200, 14, 0xFF201B15)

graph = m["Graph Gauge 1"]
graph.rename("Graph Throttle")
graph.set_rect_px(300, 342, 200, 92)
graph.set_hash(H["throttle"])
graph.set_decimals(0)
graph.set_ranges(0, 100, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)
graph.replace_level_colors(GRAPH_C, AMBER, RED)
graph_bg = panel("Text Gauge 13", 300, 342, 200, 92, 0xFF1D1812)

# ---------- bottom side columns ----------
arc = m["Arc Gauge 1"]
arc.rename("Arc CoolP")
arc.set_rect_px(158, 348, 90, 100)
arc.set_hash(H["coolp"])
arc.set_decimals(0)
arc.set_ranges(0, 300, warn=150, crit=250, warn_below=-BIG, crit_below=-BIG)
# CRITICAL: writing use_auto (+56) or +40 on an image-type record blanks it
# AND every image record painted after it. Leave arc autoscale untouched;
# only shrink segment count for a cleaner ring scale.
arc.set_autoscale(segments=6, maxdig=3)
arc.replace_level_colors(ARC_FILL, AMBER, RED)

COLS = [
    ("Text Gauge 25", "Text Gauge 38", "CHARGE IAT \u00b0C", "iat", 20,
     (0, 120, 50, 60, -99)),
    ("Text Gauge 26", "Text Gauge 39", "COOLANT P kPa", "coolp", 155,
     (0, 300, 150, 250, None)),
    ("Text Gauge 29", "Text Gauge 42", "FUEL TEMP \u00b0C", "fuelt", 540,
     (0, 100, 55, 70, -99)),
    ("Text Gauge 30", "Text Gauge 43", "ETHANOL %", "eth", 665,
     (0, 100, None, None, None)),
]
col_parts = []
for ln, vn, lt, hk, x, (vmin, vmax, warn, crit, below) in COLS:
    if hk == "coolp":
        col_parts.append(value(vn, x + 3, 378, 96, 26, hk, 0, vmin, vmax,
                               warn=warn, crit=crit, below=below))
        col_parts.append(label(ln, x - 9, 430, 120, 11, lt, color=DIMBRASS))
    else:
        col_parts.append(value(vn, x, 366, 115, 40, hk, 0, vmin, vmax,
                               warn=warn, crit=crit, below=below))
        col_parts.append(label(ln, x, 418, 115, 11, lt, color=DIMBRASS))

# ---------- alarm pills ----------
PILLS = [
    ("Text Gauge 3", "FLAT", "flat", 14, False),
    ("Text Gauge 4", "FAN", "fan", 144, True),
    ("Text Gauge 6", "LOFUEL", "lofuel", 274, False),
    ("Text Gauge 5", "SBFLT", "sbflt", 404, False),
    ("Text Gauge 7", "COOLANT P", "hicool", 534, False),
    ("Text Gauge 8", "OIL P 2", "looil", 664, False),
]
pills = []
for nm, txt, hk, x, steady in PILLS:
    g = m[nm]
    g.set_rect_px(x, 452, 118, 22)
    g.set_texts(txt)
    g.set_fsize_for_h(22)
    g.set_hash(H[hk])
    g.set_decimals(0)
    if steady:
        g.set_bg_states(CHIP, BRASS)
        g.set_arr(2, [PILL_TXT] * 3 + [0xFF171310] * 3, flag=1)
        g.set_tcolor(PILL_TXT)
        g.set_ranges(0, 1, warn=999, crit=999, warn_below=-999, crit_below=-999)
    else:
        g.set_bg_states(CHIP, RED)
        g.set_arr(2, [PILL_TXT] * 3 + [CREAM] * 3, flag=1)
        g.set_tcolor(PILL_TXT)
        g.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
    pills.append(g)

hair = panel("Text Gauge 12", 14, 446, 772, 1.4, HAIR)

# ---------- park everything unused ----------
used = {g.name for g in
        chips_bg + chips_fg + needle_fg + c_parts + col_parts + pills +
        [n_thr, n_tur, bar, bar_track, graph, graph_bg, arc, hair]}
parked = []
for g in d.gauges:
    if g.name not in used:
        parked.append(park(g))

# ---------- paint order: text records first, image records grouped last ----
text_order = [g for g in parked if g.type == 2]
text_order += chips_bg + [bar_track, graph_bg, hair]
text_order += chips_fg + c_parts + needle_fg + col_parts + pills
img_order = [arc, graph, bar, n_thr, n_tur]
img_order += [g for g in parked if g.type == 5]      # Image Gauge 1 last
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
