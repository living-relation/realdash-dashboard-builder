#!/usr/bin/env python3
"""polish_v1.py - final accuracy/polish pass on st185_dash.rd (v1).

Applies per-channel decimals, warn/crit thresholds, offline text, and label
units strictly per link_g4x_realdash.xml. Field map: see rd_lib.py; the range
block sits at stateStringsEnd+4: [u32 16, f critBelow, f critAbove,
f warnBelow, f warnAbove, f min, f max, f current].
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib import Dash, read_str

SRC = r"C:\Users\danie\Downloads\st185_dash.rd"
DST = sys.argv[1] if len(sys.argv) > 1 else SRC

AMBER = 0xFFFFC233
RED = 0xFFFF4D57
TEXT = 0xFFF3F8FF

d = Dash(SRC)
m = d.by_name()


def range_off(g):
    j = g.text_end + 0x78
    for _ in range(3):
        j = read_str(g.b, j)[1]
    return j + 4


def set_ranges(g, vmin, vmax, warn=None, crit=None):
    off = range_off(g)
    assert struct.unpack_from("<I", g.b, off)[0] == 0x10, "range anchor bad %s" % g.name
    if crit is not None:
        struct.pack_into("<f", g.b, off + 8, crit)
    if warn is not None:
        struct.pack_into("<f", g.b, off + 16, warn)
    struct.pack_into("<f", g.b, off + 20, vmin)
    struct.pack_into("<f", g.b, off + 24, vmax)


# name: (decimals, baked_text, min, max, warn, crit, active_text_color)
# warn/crit = None keeps existing; active color = None keeps existing arrays
VALUES = {
    "Text Gauge 35": (0, "0", 0, 3, 99, 99, None),          # Boost Map idx
    "Text Gauge 36": (0, "0", 0, 4, 99, 99, None),          # TC Setting idx
    "Text Gauge 34": (0, "0", 0, 100, 101, 101, None),      # Throttle %
    "Text Gauge 37": (2, "0.60", 0.6, 1.3, 9.9, 9.9, None), # Target Lambda
    "Text Gauge 38": (0, "0", -50, 205, 60, 60, RED),       # Charge IAT C
    "Text Gauge 39": (0, "0", 0, 1000, 150, 150, AMBER),    # Coolant P kPa
    "Text Gauge 40": (0, "0", 0, 200000, 190000, 190000, RED),  # Turbo RPM
    "Text Gauge 41": (0, "0", 0, 100, 101, 101, None),      # Engine Load %
    "Text Gauge 42": (0, "0", -50, 205, 70, 70, RED),       # Fuel Temp C
    "Text Gauge 43": (0, "0", 0, 100, 101, 101, None),      # Ethanol %
    "Text Gauge 44": (0, "0", 0, 255, 1, 5, AMBER),         # Trigger Errors
    "Text Gauge 45": (0, "---", 0, 4, 99, 99, None),        # Cruise enum
    "Text Gauge 46": (0, "---", 0, 3, 3, 3, RED),           # AC enum (FLT=3)
}

for nm, (dec, baked, vmin, vmax, warn, crit, active) in VALUES.items():
    g = m[nm]
    g.set_texts(baked)
    g.set_decimals(dec)
    set_ranges(g, vmin, vmax, warn, crit)
    if active is not None:
        g.set_tc_states(TEXT, active)

# label units: correct per XML (temps in C, pressure kPa, turbo RPM)
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

n_bytes, n_g = d.save(DST)
print("saved %s: %d bytes, %d gauges" % (DST, n_bytes, n_g))
