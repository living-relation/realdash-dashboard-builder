#!/usr/bin/env python3
"""build_v3.py - 'MIDNIGHT CIRCUIT' OEM-luxury x synthwave dashboard (concept 2
from _build/research/design_inspiration.md), restyled from the v1 record set.

Boxless violet-black cluster: gradient background, hairline-separated columns,
thin lavender-white numerals, neon cyan accents, magenta criticals. Same
124-record shape as v1/v2 (renderer draws first 122; last 2 pads inert).
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib import Dash, read_str

SRC = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\backup\st185_dash_v1_FINAL.rd"
DST = sys.argv[1]

BG_TOP = 0xFF060411
BG_MID = 0xFF0C0819
BG_BOT = 0xFF131028
CHIP = 0xFF14122A
TEXT = 0xFFF0E8FF
MUTED = 0xFF9070C8
CYAN = 0xFF00F0FF
PURPLE = 0xFFB026FF
YELLOW = 0xFFFCEE0A
MAGENTA = 0xFFFF2A6D
HAIR = 0xFF2A2246
TRACK = 0xFF1A1830
GHOST = 0xFF3A3358
TRANSP = 0x00000000

d = Dash(SRC)
m = d.by_name()


def panel(nm, x, y, w, h, bg):
    g = m[nm]
    g.set_rect_px(x, y, w, h)
    g.set_texts("")
    g.set_bg_states(bg, bg)
    g.set_arr(2, [bg] * 6, flag=0)
    g.set_tcolor(bg)
    return g


def label(nm, x, y, w, h, text, color=MUTED):
    g = m[nm]
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    g.set_fsize_for_h(h)
    g.set_bg_states(TRANSP, TRANSP)
    g.set_arr(2, [color] * 6, flag=0)
    g.set_tcolor(color)
    return g


def value(nm, x, y, w, h, normal=TEXT, warn=YELLOW, crit=MAGENTA):
    g = m[nm]
    g.set_rect_px(x, y, w, h)
    g.set_fsize_for_h(h)
    g.set_bg_states(TRANSP, TRANSP)
    g.set_arr(2, [normal, warn, crit] * 2, flag=0)
    g.set_tcolor(normal)
    return g


def park(nm):
    g = m[nm]
    g.set_rect_px(797, 0, 2, 2)
    g.set_texts("")
    g.set_bg_states(TRANSP, TRANSP)
    g.set_arr(2, [TRANSP] * 6, flag=0)
    g.set_tcolor(TRANSP)
    return g


# ---------- background: 5-band vertical gradient ----------
d.set_canvas_bg(BG_TOP)
bg_a = panel("Text Gauge 110", 0, 120, 800, 120, 0xFF090615)
bg1 = panel("Text Gauge 60", 0, 240, 800, 100, BG_MID)
bg_b = panel("Text Gauge 111", 0, 340, 800, 70, 0xFF100C20)
bg2 = panel("Text Gauge 61", 0, 410, 800, 70, BG_BOT)

# ---------- top status chips: TC / CRUISE / A/C ----------
# chip = CHIP rounded rect (frame panel) + label + bound value
chips = []
CHIPS = [
    ("Text Gauge 96", "Text Gauge 150", "Text Gauge 36", "TC", 40),
    ("Text Gauge 97", "Text Gauge 32", "Text Gauge 45", "CRUISE", 315),
    ("Text Gauge 98", "Text Gauge 33", "Text Gauge 46", "A/C", 590),
]
for fn, ln, vn, lt, x in CHIPS:
    chips.append(panel(fn, x, 10, 170, 32, CHIP))
    chips.append(label(ln, x + 14, 19, 80, 14, lt))
    if vn == "Text Gauge 46":
        chips.append(value(vn, x + 100, 16, 56, 20, normal=CYAN, crit=MAGENTA))
    else:
        chips.append(value(vn, x + 100, 16, 56, 20, normal=CYAN))

# ---------- column hairlines ----------
v1_line = panel("Text Gauge 62", 250, 56, 1, 350, HAIR)
v2_line = panel("Text Gauge 99", 549, 56, 1, 350, HAIR)

# ---------- left column: LAMBDA / THROTTLE / LOAD / TURBO ----------
LEFT = [
    ("Text Gauge 24", "Text Gauge 37", "TARGET \u03bb", "Text Gauge 70", 60, "rule"),
    ("Text Gauge 23", "Text Gauge 34", "THROTTLE %", "Text Gauge 181", 148, "bar"),
    ("Text Gauge 28", "Text Gauge 41", "ENGINE LOAD %", "Text Gauge 182", 236, "bar"),
    ("Text Gauge 27", "Text Gauge 40", "TURBO RPM", "Text Gauge 71", 324, "rule"),
]
left_parts = []
for ln, vn, lt, un, y, kind in LEFT:
    left_parts.append(label(ln, 32, y, 200, 15, lt))
    left_parts.append(value(vn, 32, y + 20, 200, 44))
    if kind == "bar":
        left_parts.append(panel(un, 32, y + 72, 200, 6, TRACK))
    else:
        left_parts.append(panel(un, 32, y + 74, 200, 1.4, HAIR))

# ---------- right column: IAT / COOLANT P / FUEL TEMP / ETHANOL ----------
RIGHT = [
    ("Text Gauge 25", "Text Gauge 38", "CHARGE IAT \u00b0C", "Text Gauge 72", 60),
    ("Text Gauge 26", "Text Gauge 39", "COOLANT P kPa", "Text Gauge 73", 148),
    ("Text Gauge 29", "Text Gauge 42", "FUEL TEMP \u00b0C", "Text Gauge 74", 236),
    ("Text Gauge 30", "Text Gauge 43", "ETHANOL %", "Text Gauge 75", 324),
]
right_parts = []
for ln, vn, lt, un, y in RIGHT:
    right_parts.append(label(ln, 568, y, 200, 15, lt))
    right_parts.append(value(vn, 568, y + 20, 200, 44))
    right_parts.append(panel(un, 568, y + 74, 200, 1.4, HAIR))

# ---------- center hero: BOOST MAP (the drive-mode selector) ----------
hero_label = label("Text Gauge 22", 280, 84, 240, 18, "B O O S T   M A P")
hero_value = value("Text Gauge 35", 300, 108, 200, 108, normal=TEXT)
hero_unit = label("Text Gauge 200", 280, 224, 240, 14, "MAP 0-3 \u00b7 LOW MID HIGH MAX", color=MUTED)
# neon underline glow bars (static decor, stacked alpha look)
glow_outer = panel("Text Gauge 76", 270, 250, 260, 12, TRACK)
glow_inner = panel("Text Gauge 77", 272, 252, 256, 8, 0xFF073A47)

# center lower: TC intervention & trigger errors
c_tc_l = label("Text Gauge 31", 300, 292, 200, 14, "TRIGGER ERR")
c_tc_v = value("Text Gauge 44", 300, 310, 200, 42, normal=CYAN)
c_tc_rule = panel("Text Gauge 78", 300, 358, 200, 1.4, HAIR)
c_ti_l = label("Text Gauge 21", 300, 370, 200, 12, "SYNC HEALTH")
# note: TG21 was a panel; give it label styling via label() above

# ---------- bottom alarm segments ----------
SEGS = [
    ("Text Gauge 3", "FLAT", 20),
    ("Text Gauge 4", "FAN", 148),
    ("Text Gauge 6", "LOFUEL", 276),
    ("Text Gauge 5", "SBFLT", 404),
    ("Text Gauge 7", "COOLANT P", 532),
    ("Text Gauge 8", "OIL P 2", 660),
]
seg_frames = ["Text Gauge 90", "Text Gauge 91", "Text Gauge 92",
              "Text Gauge 93", "Text Gauge 94", "Text Gauge 95"]
seg_parts = []
for i, (gn, txt, x) in enumerate(SEGS):
    seg_parts.append(panel(seg_frames[i], x, 434, 120, 34, CHIP))
    g = m[gn]
    g.set_rect_px(x + 2, 441, 116, 20)
    g.set_fsize_for_h(20)
    g.set_bg_states(CHIP, MAGENTA)      # dynamic bit fill 0->1
    g.set_arr(2, [GHOST] * 3 + [TEXT] * 3, flag=1)
    g.set_tcolor(GHOST)
    seg_parts.append(g)

# ---------- park unused decor ----------
parked = []
for n in (list(range(9, 21)) + list(range(79, 83)) + list(range(100, 103))
          + list(range(112, 123)) + list(range(130, 143)) + list(range(160, 173))
          + [184, 185, 186, 187, 188, 189]):
    parked.append(park("Text Gauge %d" % n))

# ---------- paint order ----------
order = [bg_a, bg1, bg_b, bg2, v1_line, v2_line, glow_outer, glow_inner]
order += chips
order += left_parts + right_parts
order += [hero_label, hero_value, hero_unit, c_tc_l, c_tc_v, c_tc_rule, c_ti_l]
order += seg_parts
order += parked
seen = set()
final = []
for g in order:
    if g.name not in seen:
        seen.add(g.name)
        final.append(g)
final.append(m["Text Gauge 201"])
final.append(m["Text Gauge 202"])
assert len(final) == 124, "expected 124 records, got %d" % len(final)

n, c = d.save(DST, order=final)
print("built %s: %d bytes, %d gauges" % (DST, n, c))
