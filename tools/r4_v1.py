#!/usr/bin/env python3
"""r4_v1.py - round-4 fixes for st185_dash.rd (v1).

- remove wide TRIGGER ERR tile; FUEL TEMP / ETHANOL % widen to fill the row
- CRUISE / A/C: framed state lenses - per-value bg color AND state word
  (CRUISE: OFF/STBY/SET/RES/OVR; A/C: OFF/REQ/ON/FLT) via stacked level gauges
- Turbo notation: label 'Turbo', chip 'k RPM'
- FAN pill: reachable alarm levels so the flag=1 dynamic fill actually lights

Level-banding trick (3 text slots per gauge, open-ended crit):
  fills stack (later paints over): fill1 [c0,c1,c2](w.5,c1.5) then
  fill2 [T,c3,c4](w2.5,c3.5) covers 5 enum values with 2 records.
  words must not overlap: wordA [w0,w1,hide](w.5,c1.5),
  wordB [hide,w2,hide](w1.5,c2.5), wordC [hide,w3,w4](w2.5,c3.5).
"""
import struct
from r4_common import (Dash2, H, TRANSP, set_static, static_bg, panel, park)

SRC = r"C:\Users\danie\Downloads\st185_dash.rd"

d = Dash2(SRC)
m = d.by_name()
g = lambda n: m["Text Gauge %d" % n]

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


# ---------- 1. remove TRIGGER ERR; widen FUEL TEMP / ETHANOL row ----------
g(78).set_rect_px(38, 270, 359, 97)     # fuel temp outer
g(79).set_rect_px(403, 270, 359, 97)    # ethanol outer
g(17).set_rect_px(40, 272, 356, 94)     # fuel temp inner
g(18).set_rect_px(405, 272, 356, 94)    # ethanol inner
g(98).set_rect_px(40, 272, 356, 40)     # top shade bars
g(99).set_rect_px(405, 272, 357, 40)
g(118).set_rect_px(40, 312, 356, 21)    # mid shade
g(119).set_rect_px(405, 312, 357, 21)
g(138).set_rect_px(40, 272, 356, 2)     # top edge
g(139).set_rect_px(405, 272, 357, 2)
g(169).set_rect_px(405, 274, 3, 92)     # ethanol accent bar
g(29).set_rect_px(50, 279, 336, 12)     # FUEL TEMP label
g(30).set_rect_px(415, 279, 337, 12)    # ETHANOL % label
g(42).set_rect_px(50, 304, 336, 38)     # fuel temp value
g(43).set_rect_px(415, 304, 337, 38)    # ethanol value

# ---------- 2. Turbo "k RPM" notation ----------
g(27).set_texts("Turbo", ["Turbo"] * 3)
g(186).set_rect_px(484, 216, 76, 20)
g(186).set_texts("k RPM", ["k RPM"] * 3)

# ---------- 3. FAN pill: make the fill reachable (steady, blink=0) ----------
g(4).set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)

# ---------- 4. CRUISE lens (cell 38,374 359x97; label TG32 kept) ----------
panel(g(80), 48, 400, 340, 62, BEZEL)
panel(g(19), 51, 403, 334, 56, LENS_OFF)
fill(g(45), 55, 407, 326, 48, H["cruise"], 4, 0.5, 1.5, CR_BG[0:3])
fill(g(100), 55, 407, 326, 48, H["cruise"], 4, 2.5, 3.5,
     [TRANSP, CR_BG[3], CR_BG[4]])
word(g(120), 175, 416, 130, 30, H["cruise"], 4, 0.5, 1.5,
     [CR_W[0], CR_W[1], ""], [CR_TC[0], CR_TC[1], TRANSP])
word(g(140), 175, 416, 130, 30, H["cruise"], 4, 1.5, 2.5,
     ["", CR_W[2], ""], [TRANSP, CR_TC[2], TRANSP])
word(g(181), 175, 416, 130, 30, H["cruise"], 4, 2.5, 3.5,
     ["", CR_W[3], CR_W[4]], [TRANSP, CR_TC[3], CR_TC[4]])

# ---------- 5. A/C lens (cell 403,374 359x97; label TG33 kept) ----------
panel(g(170), 413, 400, 340, 62, BEZEL)
panel(g(187), 416, 403, 334, 56, LENS_OFF)
fill(g(46), 420, 407, 326, 48, H["ac"], 3, 0.5, 1.5, AC_BG[0:3])
fill(g(31), 420, 407, 326, 48, H["ac"], 3, 2.5, 999,
     [TRANSP, AC_BG[3], AC_BG[3]])
word(g(44), 540, 416, 130, 30, H["ac"], 3, 0.5, 1.5,
     [AC_W[0], AC_W[1], ""], [AC_TC[0], AC_TC[1], TRANSP])
word(g(182), 540, 416, 130, 30, H["ac"], 3, 1.5, 2.5,
     ["", AC_W[2], AC_W[3]], [TRANSP, AC_TC[2], AC_TC[3]])

park(g(189))

# ---------- 6. paint order: lens stacks last ----------
tail_n = (80, 19, 45, 100, 120, 140, 181,      # cruise
          170, 187, 46, 31, 44, 182, 189)      # a/c + spare pad
tail = [m["Text Gauge %d" % n] for n in tail_n]
order = [x for x in d.gauges if x not in tail] + tail
n = d.save(SRC, order=order)
print("saved v1", n)
