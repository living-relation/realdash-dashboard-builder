#!/usr/bin/env python3
"""a2_probe1.py - Stage A2 probe on a throwaway copy of v4 (v4p.rd).

Tests in ONE load:
 1. Needle Turbo: gauge math '=V/1000' + ranges 0-160 (w140/c150),
    segments=5, maxdig=3 -> expect de-zeroed labels 0/40/80/120/160.
 2. Arc CoolP: maxdig=0 -> hope: scale numbers hidden (labels truncate
    to 0 chars). maxdig is a proven-safe write (+52).
 3. Caption text painted AFTER the needles ("TURBO k RPM" inside dial
    bottom) - does a text record render after image-type records?
 4. Needle tint via arr1 (image blend): Throttle needle neon blue,
    Turbo needle neon red - does it tint needle sprite / face / both?
"""
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2

DL = r"C:\Users\danie\Downloads"
SRC = DL + r"\st185_dash_v4.rd"
DST = DL + r"\v4p.rd"

NEON_RED = 0xFFFF2A2A
NEON_BLUE = 0xFF00C8FF
CREAM = 0xFFF2EAD9
TRANSP = 0x00000000

d = Dash2(SRC)
m = d.by_name()

# --- 1. turbo needle rescale (math FIRST - re-splices record) ---
nt = m["Needle Turbo"]
nt.set_gauge_math("=V/1000")
nt.set_ranges(0, 160, warn=140, crit=150, warn_below=-9e9, crit_below=-9e9)
nt.set_autoscale(segments=5, maxdig=3)

# --- 2. arc numbers off? ---
m["Arc CoolP"].set_autoscale(maxdig=0)

# --- 3. caption after needles ---
cap = m["Text Gauge 70"]
cap.set_rect_px(601, 228, 100, 14)
cap.set_texts("TURBO k RPM")
cap.set_fsize_for_h(14)
cap.set_arr(0, [TRANSP] * 6, flag=0)
cap.set_arr(2, [0xFFC7A25A] * 6, flag=0)
cap.set_tcolor(0xFFC7A25A)

# --- 4. needle tints ---
m["Needle Throttle"].set_arr(1, [NEON_BLUE] * 6, flag=0)
nt.set_arr(1, [NEON_RED] * 6, flag=0)

# --- order: caption + pad after needles, Image Gauge 1 stays last ---
names_tail = {"Text Gauge 70", "Text Gauge 71", "Image Gauge 1"}
body = [g for g in d.gauges if g.name not in names_tail]
order = body + [cap, m["Text Gauge 71"], m["Image Gauge 1"]]
assert len(order) == 128, len(order)
n, c = d.save(DST, order=order)
print("probe built:", n, c)
