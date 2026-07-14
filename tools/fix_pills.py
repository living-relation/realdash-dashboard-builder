#!/usr/bin/env python3
"""fix_pills.py - Part 1 fixes on the user-approved (app-resaved) dashes.

v1/v2/v3: FAN pill becomes a STEADY status indicator: warning/critical
  thresholds pushed out of reach (warn/crit above=999, below=-999) so the
  gauge can never enter an alarm level -> no blink, no per-level recolor.
  The 0/1 dynamic-color-range fill (min=0 max=1) still lights it steadily.
v2 extra: top sweep strip gets its missing labels (throttle sweep scale)
  and the track is bound to Throttle for a live glow (text kept invisible
  by matching text color to the background interpolation).
v2 FAN lights GREEN (status) instead of alarm RED; v3 FAN lights CYAN
  instead of critical MAGENTA. v1 FAN already lights status blue - kept.
All outputs restored to the proven 124-record shape (2 inert pads).
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib import Dash, read_str

DL = r"C:\Users\danie\Downloads"
TRANSP = 0x00000000


def range_off(g):
    j = g.text_end + 0x78
    for _ in range(3):
        j = read_str(g.b, j)[1]
    return j + 4


def set_ranges(g, vmin, vmax, warn, crit, warn_below, crit_below):
    off = range_off(g)
    assert struct.unpack_from("<I", g.b, off)[0] == 0x10, "range anchor bad %s" % g.name
    struct.pack_into("<f", g.b, off + 4, crit_below)
    struct.pack_into("<f", g.b, off + 8, crit)
    struct.pack_into("<f", g.b, off + 12, warn_below)
    struct.pack_into("<f", g.b, off + 16, warn)
    struct.pack_into("<f", g.b, off + 20, vmin)
    struct.pack_into("<f", g.b, off + 24, vmax)


def set_hash(g, h):
    struct.pack_into("<I", g.b, g._arr_marker() - 12, h)


def make_fan_steady(g):
    # unreachable alarm windows: bit value 0/1 can never leave [-999, 999]
    set_ranges(g, 0, 1, warn=999, crit=999, warn_below=-999, crit_below=-999)


def add_pads(d, m):
    pads = []
    for i, nm in enumerate(("Text Gauge 201", "Text Gauge 202")):
        pad = m["Text Gauge 23"].clone(nm)
        pad.set_rect_px(790 + i * 4, 476, 2, 2)
        pad.set_texts("")
        pad.set_bg_states(TRANSP, TRANSP)
        pad.set_tc_states(TRANSP, TRANSP)
        set_hash(pad, 0xFFFFFFFF)
        pads.append(pad)
    return pads


def strip_label(src, nm, x, y, w, h, text, color):
    g = src.clone(nm)
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    g.set_fsize_for_h(h)
    g.set_bg_states(TRANSP, TRANSP)
    g.set_arr(2, [color] * 6, flag=0)
    g.set_tcolor(color)
    set_hash(g, 0xFFFFFFFF)
    return g


# ---------------- v1 ----------------
d = Dash(DL + r"\st185_dash.rd")
m = d.by_name()
make_fan_steady(m["Text Gauge 4"])
for nm in ("Text Gauge 3", "Text Gauge 4", "Text Gauge 5", "Text Gauge 6",
           "Text Gauge 7", "Text Gauge 8"):
    g = m[nm]
    o = g.arr_offsets()[0]
    cols = struct.unpack_from("<6I", g.b, o)
    print("v1 %-14s %-10r bg n=%08X a=%08X" % (nm, g.text, cols[0], cols[3]))
order = list(d.gauges) + add_pads(d, m)
assert len(order) == 124
print("v1:", d.save(DL + r"\st185_fix1.rd", order=order))

# ---------------- v2 ----------------
PANEL = 0xFF121212
GREEN = 0xFF3DDC5A
DARK = 0xFF0A0A0A
LABEL = 0xFF8C8C8C
WOTCOL = 0xFFFF5A3C
YGLOW = 0xFF6B5900          # dim yellow glow target for the strip at WOT

d = Dash(DL + r"\st185_dash_v2.rd")
m = d.by_name()
fan = m["Text Gauge 4"]
make_fan_steady(fan)
fan.set_arr(0, [PANEL] * 3 + [GREEN] * 3, flag=1)
fan.set_arr(2, [0xFF4A4A4A] * 3 + [DARK] * 3, flag=1)

# top strip: live throttle glow on the track
thr_hash = m["Text Gauge 34"].get_hash()
track = m["Text Gauge 60"]
set_hash(track, thr_hash)
track.set_decimals(0)
set_ranges(track, 0, 100, warn=999, crit=999, warn_below=-999, crit_below=-999)
track.set_arr(0, [PANEL] * 3 + [YGLOW] * 3, flag=1)
# live value text rendered invisible: text color tracks the same gradient
track.set_arr(2, [PANEL] * 3 + [YGLOW] * 3, flag=1)
track.set_tcolor(PANEL)

# segment labels (replace parked records with clones of a known-good label)
lab_src = m["Text Gauge 23"]
repl = {}
for nm, x, w, txt, col in [
    ("Text Gauge 96", 16, 150, "THROTTLE SWEEP", LABEL),
    ("Text Gauge 97", 206, 36, "25", LABEL),
    ("Text Gauge 98", 405, 36, "50", LABEL),
    ("Text Gauge 99", 604, 36, "75", LABEL),
    ("Text Gauge 100", 706, 60, "WOT", WOTCOL),
]:
    repl[nm] = strip_label(lab_src, nm, x, 14, w, 16, txt, col)
order = [repl.get(g.name, g) for g in d.gauges] + add_pads(d, m)
assert len(order) == 124
print("v2:", d.save(DL + r"\st185_fix2.rd", order=order))

# ---------------- v3 ----------------
CHIP = 0xFF14122A
CYAN = 0xFF00F0FF
DARKV = 0xFF0A0818
GHOST = 0xFF3A3358

d = Dash(DL + r"\st185_dash_v3.rd")
m = d.by_name()
fan = m["Text Gauge 4"]
make_fan_steady(fan)
fan.set_arr(0, [CHIP] * 3 + [CYAN] * 3, flag=1)
fan.set_arr(2, [GHOST] * 3 + [DARKV] * 3, flag=1)
order = list(d.gauges) + add_pads(d, m)
assert len(order) == 124
print("v3:", d.save(DL + r"\st185_fix3.rd", order=order))
