#!/usr/bin/env python3
"""build_v2.py - 'STAGE 185' motorsport/race-display dashboard (concept 1 from
_build/research/design_inspiration.md), built by restyling the v1 record set.

True-black race TFT look: #000000 canvas, #121212 boxes with #2E2E2E outlines,
white numerals, rally-yellow hero, amber/red warn/crit, giant size contrast.
Same 124-record shape as v1 (renderer draws first 122; last 2 inert pads).
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib import Dash, read_str

SRC = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\backup\st185_dash_v1_FINAL.rd"
DST = sys.argv[1]

BLACK = 0xFF000000
PANEL = 0xFF121212
OUTLINE = 0xFF2E2E2E
WHITE = 0xFFFFFFFF
LABEL = 0xFF8C8C8C
YELLOW = 0xFFFFD400
AMBER = 0xFFFF9500
RED = 0xFFFF2A00
GREEN = 0xFF3DDC5A
PILL_TXT_OFF = 0xFF4A4A4A
REDZONE = 0xFF200400
TRACK = 0xFF0A0A0A
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


def label(nm, x, y, w, h, text, color=LABEL):
    g = m[nm]
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    g.set_fsize_for_h(h)
    g.set_bg_states(TRANSP, TRANSP)
    g.set_arr(2, [color] * 6, flag=0)
    g.set_tcolor(color)
    return g


def value(nm, x, y, w, h, normal=WHITE, warn=AMBER, crit=RED):
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


# ---------- canvas ----------
d.set_canvas_bg(BLACK)

# ---------- top decorative sweep (race-bar look, static track) ----------
sweep_outline = panel("Text Gauge 61", 2, 2, 796, 40, OUTLINE)
sweep_track = panel("Text Gauge 60", 4, 4, 792, 36, PANEL)
sweep_red = panel("Text Gauge 163", 660, 4, 132, 36, REDZONE)
tick1 = panel("Text Gauge 160", 200, 4, 2, 36, BLACK)
tick2 = panel("Text Gauge 161", 399, 4, 2, 36, BLACK)
tick3 = panel("Text Gauge 162", 598, 4, 2, 36, BLACK)
hairline = panel("Text Gauge 62", 0, 46, 800, 2, OUTLINE)

# ---------- hero THROTTLE ----------
b_thr = panel("Text Gauge 70", 6, 50, 388, 184, OUTLINE)
p_thr = panel("Text Gauge 9", 8, 52, 384, 180, PANEL)
l_thr = label("Text Gauge 23", 24, 62, 220, 22, "THROTTLE %")
v_thr = value("Text Gauge 34", 24, 92, 352, 118, normal=YELLOW)
t_thr = panel("Text Gauge 181", 24, 216, 352, 8, TRACK)

# ---------- hero LAMBDA ----------
b_lam = panel("Text Gauge 71", 398, 50, 196, 184, OUTLINE)
p_lam = panel("Text Gauge 10", 400, 52, 192, 180, PANEL)
l_lam = label("Text Gauge 24", 416, 62, 160, 22, "TARGET \u03bb")
v_lam = value("Text Gauge 37", 408, 104, 176, 84)
cap = label("Text Gauge 200", 416, 204, 160, 14, "TUNE TARGET", color=0xFF5A5A5A)

# ---------- status column: TC / CRUISE / A/C ----------
b_tc = panel("Text Gauge 72", 598, 50, 196, 58, OUTLINE)
p_tc = panel("Text Gauge 11", 600, 52, 192, 54, PANEL)
l_tc = label("Text Gauge 150", 612, 68, 60, 20, "TC")
v_tc = value("Text Gauge 36", 700, 62, 80, 36, normal=GREEN)

b_cr = panel("Text Gauge 73", 598, 112, 196, 58, OUTLINE)
p_cr = panel("Text Gauge 12", 600, 114, 192, 54, PANEL)
l_cr = label("Text Gauge 32", 612, 130, 90, 20, "CRUISE")
v_cr = value("Text Gauge 45", 688, 124, 92, 36, normal=GREEN)

b_ac = panel("Text Gauge 74", 598, 174, 196, 58, OUTLINE)
p_ac = panel("Text Gauge 13", 600, 176, 192, 54, PANEL)
l_ac = label("Text Gauge 33", 612, 192, 60, 20, "A/C")
v_ac = value("Text Gauge 46", 688, 186, 92, 36, normal=GREEN, crit=RED)

# ---------- mid row: BOOST MAP / ENGINE LOAD / CHARGE IAT / COOLANT P ----------
MID = [
    ("Text Gauge 75", "Text Gauge 14", "Text Gauge 22", "Text Gauge 35", "BOOST MAP", 8),
    ("Text Gauge 76", "Text Gauge 15", "Text Gauge 28", "Text Gauge 41", "ENGINE LOAD %", 205),
    ("Text Gauge 77", "Text Gauge 16", "Text Gauge 25", "Text Gauge 38", "CHARGE IAT \u00b0C", 402),
    ("Text Gauge 78", "Text Gauge 17", "Text Gauge 26", "Text Gauge 39", "COOLANT P kPa", 599),
]
mid_parts = []
mid_tracks = ["Text Gauge 182", "Text Gauge 184", "Text Gauge 185", "Text Gauge 186"]
for i, (bn, pn, ln, vn, lt, x) in enumerate(MID):
    mid_parts.append(panel(bn, x - 2, 238, 196, 110, OUTLINE))
    mid_parts.append(panel(pn, x, 240, 192, 106, PANEL))
    mid_parts.append(label(ln, x + 12, 250, 168, 18, lt))
    mid_parts.append(value(vn, x + 12, 274, 168, 56))
    mid_parts.append(panel(mid_tracks[i], x + 12, 334, 168, 6, TRACK))

# ---------- lower row: TURBO / FUEL TEMP / ETHANOL / TRIG ERR ----------
LOW = [
    ("Text Gauge 79", "Text Gauge 18", "Text Gauge 27", "Text Gauge 40", "TURBO RPM", 8),
    ("Text Gauge 80", "Text Gauge 19", "Text Gauge 29", "Text Gauge 42", "FUEL TEMP \u00b0C", 205),
    ("Text Gauge 81", "Text Gauge 20", "Text Gauge 30", "Text Gauge 43", "ETHANOL %", 402),
    ("Text Gauge 82", "Text Gauge 21", "Text Gauge 31", "Text Gauge 44", "TRIG ERRORS", 599),
]
low_parts = []
for bn, pn, ln, vn, lt, x in LOW:
    low_parts.append(panel(bn, x - 2, 352, 196, 76, OUTLINE))
    low_parts.append(panel(pn, x, 354, 192, 72, PANEL))
    low_parts.append(label(ln, x + 12, 361, 168, 16, lt))
    if vn == "Text Gauge 44":   # trigger errors: green when 0 (healthy)
        low_parts.append(value(vn, x + 12, 381, 168, 40, normal=GREEN))
    else:
        low_parts.append(value(vn, x + 12, 381, 168, 40))

# ---------- alarm pills ----------
PILLS = [
    ("Text Gauge 3", "Text Gauge 90", "FLAT", 10),
    ("Text Gauge 4", "Text Gauge 91", "FAN", 141),
    ("Text Gauge 6", "Text Gauge 92", "LOFUEL", 272),
    ("Text Gauge 5", "Text Gauge 93", "SBFLT", 403),
    ("Text Gauge 7", "Text Gauge 94", "COOLANT P", 534),
    ("Text Gauge 8", "Text Gauge 95", "OIL P 2", 665),
]
pill_parts = []
for gn, on, txt, x in PILLS:
    # text height == rect height, so the bound chip is short and sits inside
    # a slightly taller outline frame
    # rendered text em == rect height, so keep the bound chip 20px tall
    # (COOLANT P at em20 ~= 120px, fits 125px chip) inside a taller frame
    pill_parts.append(panel(on, x - 2, 440, 129, 34, OUTLINE))
    g = m[gn]
    g.set_rect_px(x, 447, 125, 20)
    g.set_fsize_for_h(20)
    g.set_bg_states(PANEL, RED)          # dynamic 0->1 fill
    g.set_arr(2, [PILL_TXT_OFF] * 3 + [WHITE] * 3, flag=1)
    g.set_tcolor(PILL_TXT_OFF)
    pill_parts.append(g)

# ---------- park unused decor ----------
parked = []
for n in list(range(96, 103)) + list(range(110, 123)) + list(range(130, 143)) \
        + list(range(164, 173)) + [187, 188, 189]:
    parked.append(park("Text Gauge %d" % n))

# ---------- paint order ----------
order = []
order += [sweep_outline.b and sweep_outline]  # keep list of G
order = [sweep_outline, sweep_track, sweep_red, tick1, tick2, tick3, hairline,
         b_thr, p_thr, b_lam, p_lam, b_tc, p_tc, b_cr, p_cr, b_ac, p_ac]
order += [g for g in mid_parts if g.name.startswith("Text Gauge 7") or g.name in ("Text Gauge 14", "Text Gauge 15", "Text Gauge 16", "Text Gauge 17")]
order += [g for g in low_parts if g.name.startswith("Text Gauge 8") and g.name not in ()]
# simpler: rebuild explicit order
order = [sweep_outline, sweep_track, sweep_red, tick1, tick2, tick3, hairline,
         b_thr, p_thr, b_lam, p_lam, b_tc, p_tc, b_cr, p_cr, b_ac, p_ac]
order += mid_parts
order += low_parts
order += pill_parts
order += [t_thr,
          l_thr, v_thr, l_lam, v_lam, cap,
          l_tc, v_tc, l_cr, v_cr, l_ac, v_ac]
order += parked
# dedupe keeping first occurrence (mid/low parts include labels+values already)
seen = set()
final = []
for g in order:
    if g.name not in seen:
        seen.add(g.name)
        final.append(g)
# pads last (unrendered slots 123/124)
final.append(m["Text Gauge 201"])
final.append(m["Text Gauge 202"])
assert len(final) == 124, "expected 124 records, got %d" % len(final)

n, c = d.save(DST, order=final)
print("built %s: %d bytes, %d gauges" % (DST, n, c))
