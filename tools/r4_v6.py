#!/usr/bin/env python3
"""r4_v6.py - fix up probe_gm.rd into a keeper variant: st185_dash_v6.rd.

probe_gm is a pre-round-3 clone of v1 (same 4x3 grid + cruise/ac row).
- remove the wide TRIGGER ERR tile (row3 right)
- TARGET lambda tile grows to span rows 1-2 (col4); ENGINE LOAD % moves down
  to row3 col4; Turbo tile grows to span rows 2-3 (col3) with a big value
- chip convention: 'CHARGE IAT'+degC, 'COOLANT P'+kPa, 'FUEL TEMP'+degC,
  'Turbo'+'k RPM' (math =V/1000 already on TG40; ranges set post-math 0/255)
- CRUISE / A-C: framed state lenses with state words (v1 recipe)
- FAN pill: reachable alarms so the dynamic fill lights
- output renamed to st185_dash_v6.rd
"""
import struct
from r4_common import (Dash2, H, TRANSP, set_static, static_bg, panel, park)

SRC = r"C:\Users\danie\Downloads\probe_gm.rd"
DST = r"C:\Users\danie\Downloads\st185_dash_v6.rd"

d = Dash2(SRC)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]

CHIP = 0xFF7A8CA0
BEZEL = 0xFF4A607A
LENS_OFF = 0xFF10161F
DIM = 0xFF647A92
DARK = 0xFF06131F

CR_BG = [0xFF1B2836, 0xFF23507A, 0xFF2E9BFF, 0xFF1FC9A7, 0xFFFFC233]
CR_W = ["OFF", "STBY", "SET", "RES", "OVR"]
CR_TC = [DIM, 0xFFD6E6F5, DARK, DARK, DARK]
AC_BG = [0xFF1B2836, 0xFFFFC233, 0xFF35C4E8, 0xFFFF3226]
AC_W = ["OFF", "REQ", "ON", "FLT"]
AC_TC = [DIM, DARK, DARK, 0xFFFFFFFF]


def fill(gg, x, y, w, h, hash_, vmax, warn, crit, bgs):
    gg.set_rect_px(x, y, w, h)
    gg.set_texts("", ["", "", ""])
    set_static(gg, True)
    static_bg(gg, bgs[0])
    gg.set_arr(0, list(bgs) * 2, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(0, vmax, warn=warn, crit=crit,
                  warn_below=-999, crit_below=-999)


def word(gg, x, y, w, h, hash_, vmax, warn, crit, words, tcs):
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(words[0], list(words))
    set_static(gg, True)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, list(tcs) * 2, flag=0)
    gg.set_tcolor(tcs[0])
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(0, vmax, warn=warn, crit=crit,
                  warn_below=-999, crit_below=-999)


def chip(gg, x, y, w, h, text):
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(text, [text] * 3)
    set_static(gg, True)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [CHIP] * 6, flag=0)
    gg.set_tcolor(CHIP)
    gg.set_hash(0xFFFFFFFF)


# ---------- 1. chip convention on old-style labels ----------
g(25).set_texts("CHARGE IAT", ["CHARGE IAT"] * 3)
g(26).set_texts("COOLANT P", ["COOLANT P"] * 3)
g(29).set_texts("FUEL TEMP", ["FUEL TEMP"] * 3)
chip(g(184), 170, 216, 36, 20, "\u00b0C")     # charge IAT
chip(g(185), 352, 216, 44, 20, "kPa")         # coolant P
chip(g(188), 170, 320, 36, 20, "\u00b0C")     # fuel temp

# ---------- 2. TARGET lambda tile spans rows 1-2 (col4) ----------
g(73).set_rect_px(584, 63, 177, 200)          # outer
g(12).set_rect_px(586, 65, 174, 197)          # inner
g(163).set_rect_px(586, 67, 3, 195)           # accent bar
g(37).set_rect_px(596, 100, 154, 64)          # value taller
g(37).set_fsize_for_h(64)
g(200).set_rect_px(596, 172, 154, 12)         # TUNE TARGET caption

# ---------- 3. ENGINE LOAD % moves to row3 col4 ----------
g(77).set_rect_px(584, 270, 177, 97)
g(16).set_rect_px(586, 272, 174, 94)
g(97).set_rect_px(586, 272, 174, 40)
g(117).set_rect_px(586, 312, 174, 21)
g(137).set_rect_px(586, 272, 174, 2)
g(167).set_rect_px(586, 274, 3, 92)
g(28).set_rect_px(596, 279, 154, 12)
g(41).set_rect_px(596, 304, 154, 38)

# ---------- 4. Turbo tile spans rows 2-3 (col3), big value ----------
g(76).set_rect_px(403, 167, 177, 200)
g(15).set_rect_px(405, 168, 174, 197)
g(166).set_rect_px(405, 170, 3, 195)
g(27).set_texts("Turbo", ["Turbo"] * 3)
g(40).set_rect_px(415, 200, 154, 70)
g(40).set_fsize_for_h(70)
g(40).set_ranges(0, 255, warn=180, crit=190, warn_below=0, crit_below=0)
chip(g(186), 417, 280, 90, 22, "k RPM")

# ---------- 5. FAN pill fix ----------
g(4).set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)

# ---------- 6. CRUISE lens (cell 38,374 359x97) ----------
panel(g(80), 48, 400, 340, 62, BEZEL)
panel(g(19), 51, 403, 334, 56, LENS_OFF)
fill(g(45), 55, 407, 326, 48, H["cruise"], 4, 0.5, 1.5, CR_BG[0:3])
fill(g(140), 55, 407, 326, 48, H["cruise"], 4, 2.5, 3.5,
     [TRANSP, CR_BG[3], CR_BG[4]])
word(g(44), 175, 416, 130, 30, H["cruise"], 4, 0.5, 1.5,
     [CR_W[0], CR_W[1], ""], [CR_TC[0], CR_TC[1], TRANSP])
word(g(181), 175, 416, 130, 30, H["cruise"], 4, 1.5, 2.5,
     ["", CR_W[2], ""], [TRANSP, CR_TC[2], TRANSP])
word(g(182), 175, 416, 130, 30, H["cruise"], 4, 2.5, 3.5,
     ["", CR_W[3], CR_W[4]], [TRANSP, CR_TC[3], CR_TC[4]])

# ---------- 7. A/C lens (cell 403,374 359x97) ----------
panel(g(100), 413, 400, 340, 62, BEZEL)
panel(g(120), 416, 403, 334, 56, LENS_OFF)
fill(g(46), 420, 407, 326, 48, H["ac"], 3, 0.5, 1.5, AC_BG[0:3])
fill(g(170), 420, 407, 326, 48, H["ac"], 3, 2.5, 999,
     [TRANSP, AC_BG[3], AC_BG[3]])
word(g(31), 540, 416, 130, 30, H["ac"], 3, 0.5, 1.5,
     [AC_W[0], AC_W[1], ""], [AC_TC[0], AC_TC[1], TRANSP])
word(g(187), 540, 416, 130, 30, H["ac"], 3, 1.5, 2.5,
     ["", AC_W[2], AC_W[3]], [TRANSP, AC_TC[2], AC_TC[3]])

# ---------- 8. inert pads last ----------
park(g(189))
park(g(62))     # 2px header divider sacrificed as pad #2

tail_n = (80, 19, 45, 140, 44, 181, 182,       # cruise stack
          100, 120, 46, 170, 31, 187,          # a/c stack
          189, 62)                             # inert pads
tail = [m["Text Gauge %d" % n] for n in tail_n]
order = [x for x in d.gauges if x not in tail] + tail
n = d.save(DST, order=order)
print("saved v6", n)
