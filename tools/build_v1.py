#!/usr/bin/env python3
"""build_v1.py - reproducible v1 build from the known-good 11:07 PM snapshot.

Input: _build/diff_before2.rd (phase-D visuals + lambda dec=2 GUI edit; loads OK)
Applies binarily:
  1. pill binding fixes (hashes learned from GUI-save diffs)
  2. XML-accurate decimals / ranges / warn-crit thresholds
  3. label unit corrections
  4. value text color normalization + TUNE TARGET caption
Output: given path (must be a fresh filename for cache busting).
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib import Dash, read_str

SRC = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\diff_before2.rd"
DST = sys.argv[1]

AMBER = 0xFFFFC233
RED = 0xFFFF4D57
TEXT = 0xFFF3F8FF
DIMMER = 0xFF6E8199
TRANSP = 0x00000000

# channel-name hashes (learned from GUI bind + save + diff)
H_FLAT_SHIFT = 0x6B5F9216
H_RADIATOR_FAN = 0xC44AB478
H_LOW_FUEL = 0xDD06C8FD
H_SB_FAULT = 0x7F8E9FE9
H_HI_COOL = 0x3A7D877E
H_LOW_OIL2 = 0xAD193AD0

d = Dash(SRC)
m = d.by_name()


def range_off(g):
    j = g.text_end + 0x78
    for _ in range(3):
        j = read_str(g.b, j)[1]
    return j + 4


def set_ranges(g, vmin, vmax, warn=None, crit=None, warn_below=None, crit_below=None):
    off = range_off(g)
    assert struct.unpack_from("<I", g.b, off)[0] == 0x10, "range anchor bad %s" % g.name
    if crit_below is not None:
        struct.pack_into("<f", g.b, off + 4, crit_below)
    if crit is not None:
        struct.pack_into("<f", g.b, off + 8, crit)
    if warn_below is not None:
        struct.pack_into("<f", g.b, off + 12, warn_below)
    if warn is not None:
        struct.pack_into("<f", g.b, off + 16, warn)
    struct.pack_into("<f", g.b, off + 20, vmin)
    struct.pack_into("<f", g.b, off + 24, vmax)


def set_hash(g, h):
    struct.pack_into("<I", g.b, g._arr_marker() - 12, h)


# ---------- 1. pill binding fixes ----------
PILLS = {
    "Text Gauge 3": H_FLAT_SHIFT,     # FLAT
    "Text Gauge 4": H_RADIATOR_FAN,   # FAN
    "Text Gauge 6": H_LOW_FUEL,       # LOFUEL
    "Text Gauge 5": H_SB_FAULT,       # SBFLT
    "Text Gauge 7": H_HI_COOL,        # COOLANT P
    "Text Gauge 8": H_LOW_OIL2,       # OIL P 2
}
for nm, h in PILLS.items():
    g = m[nm]
    set_hash(g, h)
    set_ranges(g, 0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)

# ---------- 2+3. values: decimals, baked text, ranges, thresholds ----------
# Color array semantics (decoded via editor COLORS panel): 6 slots =
# [normal_c1, warning_c1, critical_c1, normal_c2, warning_c2, critical_c2];
# flag = "use dynamic color range" (value-gradient c1->c2). We want static
# per-level colors, so flag=0 and [normal, warn_color, crit_color] x2.
VALUES = {
    # name: (dec, baked, min, max, warn, crit, warn_below, warn_col, crit_col)
    "Text Gauge 35": (0, "0", 0, 3, 99, 99, None, TEXT, TEXT),
    "Text Gauge 36": (0, "0", 0, 4, 99, 99, None, TEXT, TEXT),
    "Text Gauge 34": (0, "0", 0, 100, 101, 101, None, TEXT, TEXT),
    "Text Gauge 37": (2, "0.60", 0.6, 1.3, 9.9, 9.9, None, TEXT, TEXT),
    "Text Gauge 38": (0, "0", -50, 205, 50, 60, -99, AMBER, RED),
    "Text Gauge 39": (0, "0", 0, 1000, 150, 250, None, AMBER, RED),
    "Text Gauge 40": (0, "0", 0, 200000, 180000, 190000, None, AMBER, RED),
    "Text Gauge 41": (0, "0", 0, 100, 101, 101, None, TEXT, TEXT),
    "Text Gauge 42": (0, "0", -50, 205, 55, 70, -99, AMBER, RED),
    "Text Gauge 43": (0, "0", 0, 100, 101, 101, None, TEXT, TEXT),
    "Text Gauge 44": (0, "0", 0, 255, 1, 5, None, AMBER, RED),
    "Text Gauge 45": (0, "---", 0, 4, 99, 99, None, TEXT, TEXT),
    "Text Gauge 46": (0, "---", 0, 3, 3, 3, None, RED, RED),
}
for nm, (dec, baked, vmin, vmax, warn, crit, below, wcol, ccol) in VALUES.items():
    g = m[nm]
    g.set_texts(baked)
    g.set_decimals(dec)
    set_ranges(g, vmin, vmax, warn, crit,
               warn_below=below if below is not None else None,
               crit_below=below if below is not None else None)
    g.set_arr(2, [TEXT, wcol, ccol, TEXT, wcol, ccol], flag=0)
    g.set_tcolor(TEXT)

# ---------- labels: unit corrections ----------
LABELS = {
    "Text Gauge 22": "BOOST MAP",
    "Text Gauge 150": "TC",
    "Text Gauge 23": "THROTTLE %",
    "Text Gauge 24": "TARGET \u03bb",
    "Text Gauge 25": "CHARGE IAT \u00b0C",
    "Text Gauge 26": "COOLANT P kPa",
    "Text Gauge 27": "TURBO RPM",
    "Text Gauge 28": "ENGINE LOAD %",
    "Text Gauge 29": "FUEL TEMP \u00b0C",
    "Text Gauge 30": "ETHANOL %",
    "Text Gauge 31": "TRIGGER ERR",
    "Text Gauge 32": "CRUISE",
    "Text Gauge 33": "A/C",
}
for nm, txt in LABELS.items():
    g = m[nm]
    if g.text != txt:
        g.set_texts(txt)

# ---------- 4. TUNE TARGET caption on the lambda tile ----------
cap = m["Text Gauge 23"].clone("Text Gauge 200")
cap.set_rect_px(596, 142, 154, 10)
cap.set_texts("TUNE TARGET")
cap.set_fsize_for_h(10)
cap.set_bg_states(TRANSP, TRANSP)
cap.set_tc_states(DIMMER, DIMMER)
d.gauges.append(cap)

# ---------- 5. structural padding ----------
# RealDash 1.92 only renders the first 122 records, but the 124-record shape
# is the one verified to load repeatedly. Records 123/124 are inert spares
# parked offscreen-ish (transparent, 1px) purely to preserve that shape.
for i, nm in enumerate(("Text Gauge 201", "Text Gauge 202")):
    pad = m["Text Gauge 23"].clone(nm)
    pad.set_rect_px(790 + i * 4, 476, 2, 2)
    pad.set_texts("")
    pad.set_bg_states(TRANSP, TRANSP)
    pad.set_tc_states(TRANSP, TRANSP)
    d.gauges.append(pad)

n, c = d.save(DST)
print("built %s: %d bytes, %d gauges" % (DST, n, c))
