#!/usr/bin/env python3
"""round3_v4.py - round-3 fixes for st185_dash_v4.rd (needle/arc dash).

* Turbo digital (Text Gauge 40): gauge math '=V/1000' (written FIRST - it
  re-splices the record), decimals 0, ranges rescaled to k units, ' k' chip.
* Coolant-pressure block: arc shrunk to 70x70 at (146,352); digital readout
  (Text Gauge 39) moved OUT of the arc to its right (222,360 70x30); 'kPa'
  chip under the digits; label (Text Gauge 26) -> 'COOLANT P' (same spot,
  under the whole block).
* Label/unit convention: 'CHARGE IAT degC' -> 'CHARGE TEMP' + degC chip,
  'FUEL TEMP degC' -> 'FUEL TEMP' + degC chip. % labels keep % (convention).

Keeps the 128-record shape and record order (chips repurpose parked 2x2
records). Backup: _build/backup/st185_dash_v4_20260707_175713_pre_round3.rd
"""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

DL = r"C:\Users\danie\Downloads"
TRANSP = 0x00000000
UNBOUND = 0xFFFFFFFF
UC = 0xFF9A8F80          # dim warm gray matching v4's cream/orange palette


def set_unit(m, name, x, y, w, h, text):
    g = m[name]
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    g.set_fsize_for_h(h)
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [UC] * 6, flag=0)
    g.set_tcolor(UC)
    g.set_hash(UNBOUND)


d = Dash2(DL + r"\st185_dash_v4.rd")
m = d.by_name()

# (c) turbo 'k' - math FIRST (re-splices the record blob)
tg40 = m["Text Gauge 40"]
tg40.set_gauge_math("=V/1000")
tg40.set_decimals(0)
tg40.set_ranges(0, 255, warn=180, crit=190, warn_below=0, crit_below=0)

# (a) coolant block: arc left, readout + kPa to its right, label underneath
m["Arc CoolP"].set_rect_px(146, 352, 70, 70)
tg39 = m["Text Gauge 39"]
tg39.set_rect_px(222, 360, 70, 30)
tg39.set_fsize_for_h(30)
tg26 = m["Text Gauge 26"]
tg26.set_texts("COOLANT P")

# (b) label/unit convention
m["Text Gauge 25"].set_texts("CHARGE TEMP")
m["Text Gauge 29"].set_texts("FUEL TEMP")

# unit chips on parked records (value digits are left-aligned in their box)
set_unit(m, "Text Gauge 130", 105, 384, 24, 18, "\u00b0C")   # charge temp
set_unit(m, "Text Gauge 131", 222, 394, 34, 14, "kPa")       # coolant p
set_unit(m, "Text Gauge 132", 625, 384, 24, 18, "\u00b0C")   # fuel temp
set_unit(m, "Text Gauge 133", 648, 310, 14, 18, "k")         # turbo

assert len(d.gauges) == 128, len(d.gauges)
print("v4:", d.save(DL + r"\st185_dash_v4.rd"))
