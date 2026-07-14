#!/usr/bin/env python3
"""r4_v3.py - round-4 rework of st185_dash_v3.rd per user's annotations.

- left column: TARGET λ / THROTTLE % / ENGINE LOAD % moved up, Turbo value
  enlarged (h44 -> h78) with 'Turbo' + 'k RPM' chip notation
- center: TRIGGER ERR + SYNC HEALTH removed; TC panel fills the space:
  mode number (ST185: TC Setting), intervention % (ST185: TC Intervention,
  hash 0x5A59FBBD harvested via GUI probe), engagement lens that lights
  amber with 'TC ACTIVE' whenever intervention >= 1%
- top strip: small TC tile removed (TC now center); CRUISE / A-C tiles
  re-spaced to balance the strip
- FAN pill: reachable alarms so the dynamic fill lights
"""
import struct
from r4_common import Dash2, H, TRANSP, set_static, static_bg, panel, park

SRC = r"C:\Users\danie\Downloads\st185_dash_v3.rd"

d = Dash2(SRC)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]

PANEL = 0xFF14122A
LAB = 0xFF9070C8
VAL = 0xFFF0E8FF
CYAN = 0xFF00F0FF
AMBER = 0xFFFCEE0A
CRIT = 0xFFFF2A6D
DARKTX = 0xFF0A0818
CHIP = 0xFF8878B8

# ---------- 1. left column: shift up, tall Turbo ----------
g(24).set_rect_px(32, 56, 200, 15)     # TARGET λ label
g(37).set_rect_px(32, 74, 200, 40)     # value
g(70).set_rect_px(32, 120, 200, 1)     # divider
g(23).set_rect_px(32, 128, 200, 15)    # THROTTLE % label
g(34).set_rect_px(32, 146, 200, 40)    # value
g(181).set_rect_px(32, 192, 200, 6)    # track
g(28).set_rect_px(32, 204, 200, 15)    # ENGINE LOAD % label
g(41).set_rect_px(32, 222, 200, 40)    # value
g(182).set_rect_px(32, 268, 200, 6)    # track
g(27).set_rect_px(32, 280, 200, 15)    # Turbo label
g(27).set_texts("Turbo", ["Turbo"] * 3)
g(40).set_rect_px(32, 298, 200, 78)    # tall turbo value
g(40).set_fsize_for_h(78)
g(112).set_rect_px(168, 352, 64, 20)   # chip
g(112).set_texts("k RPM", ["k RPM"] * 3)

# ---------- 2. top strip: drop TC tile, re-space CRUISE / A-C ----------
park(g(96)); park(g(150)); park(g(36))
g(97).set_rect_px(153, 10, 170, 32)
g(32).set_rect_px(167, 19, 80, 14)
g(45).set_rect_px(253, 16, 56, 20)
g(98).set_rect_px(477, 10, 170, 32)
g(33).set_rect_px(491, 19, 80, 14)
g(46).set_rect_px(577, 16, 56, 20)

# ---------- 3. center TC panel (replaces TRIGGER ERR / SYNC HEALTH) ------
panel(g(200), 270, 272, 260, 148, PANEL)

gg = g(31)                              # header
gg.set_rect_px(278, 280, 244, 13)
gg.set_texts("TRACTION CONTROL", ["TRACTION CONTROL"] * 3)
gg.set_tcolor(LAB)
gg.set_arr(2, [LAB] * 6, flag=0)
gg.set_hash(0xFFFFFFFF)

gg = g(21)                              # MODE caption
gg.set_rect_px(282, 302, 70, 12)
gg.set_texts("MODE", ["MODE"] * 3)
gg.set_tcolor(LAB)
gg.set_arr(2, [LAB] * 6, flag=0)
gg.set_hash(0xFFFFFFFF)

gg = g(44)                              # mode value (TC Setting 0-4)
gg.set_rect_px(282, 318, 70, 52)
gg.set_fsize_for_h(52)
gg.set_texts("0", ["0"] * 3)
set_static(gg, False)
gg.set_tcolor(CYAN)
gg.set_arr(2, [CYAN] * 6, flag=0)
gg.set_hash(H["tc"])
gg.set_decimals(0)
gg.set_ranges(0, 4, warn=999, crit=999, warn_below=-999, crit_below=-999)

gg = g(17)                              # INTERVENTION % caption
gg.set_rect_px(380, 302, 142, 12)
gg.set_texts("INTERVENTION %", ["INTERVENTION %"] * 3)
static_bg(gg, TRANSP)
gg.set_arr(0, [TRANSP] * 6, flag=0)
gg.set_tcolor(LAB)
gg.set_arr(2, [LAB] * 6, flag=0)
gg.set_hash(0xFFFFFFFF)

gg = g(18)                              # intervention value (0-100 %)
gg.set_rect_px(380, 318, 120, 52)
gg.set_fsize_for_h(52)
gg.set_texts("0", ["0"] * 3)
set_static(gg, False)
static_bg(gg, TRANSP)
gg.set_arr(0, [TRANSP] * 6, flag=0)
gg.set_tcolor(VAL)
gg.set_arr(2, [VAL, AMBER, CRIT] * 2, flag=0)
gg.set_hash(H["tci"])
gg.set_decimals(0)
gg.set_ranges(0, 100, warn=50, crit=80, warn_below=-999, crit_below=-999)

gg = g(19)                              # engagement lens + state word
gg.set_rect_px(278, 384, 244, 28)
gg.set_texts("", ["", "TC ACTIVE", "TC ACTIVE"])
set_static(gg, True)
static_bg(gg, 0xFF0D0B1E)
gg.set_arr(0, [0xFF0D0B1E, AMBER, AMBER] * 2, flag=0)
gg.set_tcolor(TRANSP)
gg.set_arr(2, [TRANSP, DARKTX, DARKTX] * 2, flag=0)
gg.set_hash(H["tci"])
gg.set_decimals(0)
gg.set_ranges(0, 100, warn=1, crit=999, warn_below=-999, crit_below=-999)

park(g(78))                             # old SYNC divider
park(g(20))                             # spare pad stays parked

# ---------- 4. FAN pill fix ----------
g(4).set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)

n = d.save(SRC)
print("saved v3", n)
