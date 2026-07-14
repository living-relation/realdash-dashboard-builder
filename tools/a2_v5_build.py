#!/usr/bin/env python3
"""a2_v5_build.py - Stage A2 rework of st185_dash_v5.rd.

 1. Splice cf_sheet2.png (REAL ShareTextures 45-deg twill base, square
    pill wells) over the header asset (name `_indicators.png_`).
 2. Pills: park the 6 halo records (square glow corners over the rounded
    bezel = the wonk); lenses now sit in exact-fit square wells with a 2px
    dark reveal. FAN + FLAT get finite alarms (warn .5 / crit .7 / below 0)
    so the flag=1 fill actually lights (steady, blink=0).
 3. CRUISE / A-C state words + full per-state colors (r4_v1 level-banding
    recipe): fills stack, words render via static state strings.
 4. Turbo notation: label 'Turbo', chip 'k RPM'.
Usage: python a2_v5_build.py [out.rd]  default overwrite Downloads v5.
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str

DL = r"C:\Users\danie\Downloads"
SRC = DL + r"\st185_dash_v5.rd"
DST = sys.argv[1] if len(sys.argv) > 1 else SRC
PNG = (r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan"
       r"\_build\cf_sheet2.png")

VAL = 0xFFF2F4F6
WARN = 0xFFFFB300
CRIT = 0xFFFF3226
BLUE = 0xFF2E9BFF
STEEL = 0xFF1B4E75
TEAL = 0xFF1FC9A7
LENS_OFF = 0xFF15181C
LEG_OFF = 0xFF4A5058
DARK = 0xFF06131F
NEARWHITE = 0xFFD6E6F5
UNIT = 0xFF6F7680
TRANSP = 0x00000000
UNBOUND = 0xFFFFFFFF
H_CRUISE = 0x18ECF9C1
H_AC = 0xE975C645

# ---------- 1. asset splice ----------
raw = open(SRC, "rb").read()
png = open(PNG, "rb").read()
name16 = "_indicators.png_".encode("utf-16-le")
ni = raw.find(struct.pack("<I", 16) + name16)
assert 0 < ni < 600000, "asset name not found"
size_off = ni + 4 + len(name16)
old_size = struct.unpack_from("<I", raw, size_off)[0]
new_blob = b"\x00\x00\x00\x00" + png
raw = (raw[:size_off] + struct.pack("<I", len(new_blob)) + new_blob +
       raw[size_off + 4 + old_size:])
TMP = DL + r"\_a2v5_tmp.rd"
open(TMP, "wb").write(raw)
print("sheet spliced: old=%d new=%d" % (old_size, len(new_blob)))

d = Dash2(TMP)
m = d.by_name()
assert len(d.gauges) == 83, len(d.gauges)
g = lambda n: m["Text Gauge %d" % n]


def set_static(gg, on):
    j = gg._states_off()
    for _ in range(3):
        j = read_str(gg.b, j)[1]
    cur = struct.unpack_from("<I", gg.b, j + 76)[0]
    struct.pack_into("<I", gg.b, j + 76,
                     (cur | 0x20000000) if on else (cur & ~0x20000000))


def static_bg(gg, argb):
    struct.pack_into("<I", gg.b, gg.nend + 0x5C, argb)


def park(gg):
    gg.set_rect_px(797, 0, 2, 2)
    gg.set_texts("", ["", "", ""])
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(UNBOUND)


def zero_blink(gg):
    """Repurposed pill-halo records carry critical blink=1.0 from round 3;
    zero all three blink slots or state words vanish half the time."""
    off = gg._range_off()
    struct.pack_into("<3f", gg.b, off + 40, 0.0, 0.0, 0.0)


def fill(gg, x, y, w, h, hash_, vmax, warn, crit, bgs):
    zero_blink(gg)
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
    zero_blink(gg)
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(words[0], list(words))
    set_static(gg, True)
    gg.set_fsize_for_h(h)
    static_bg(gg, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, list(tcs) * 2, flag=0)
    gg.set_tcolor(tcs[0])
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(0, vmax, warn=warn, crit=crit,
                  warn_below=-999, crit_below=-999)


# ---------- 2. pills ----------
HALOS = [20, 92, 96, 100, 111, 115]
for n in HALOS:
    park(g(n))
# FAN + FLAT: reachable alarms -> steady lit (blink fields are 0)
for n in (21, 91):     # FLAT lens + legend
    g(n).set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
for n in (93, 95):     # FAN lens + legend
    g(n).set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)

# ---------- 3. CRUISE / A-C state lenses ----------
# repurpose parked halos (they are probe_base text records, static ON)
cr_fill2, ac_fill2 = g(20), g(92)
cr_wA, cr_wB, cr_wC = g(96), g(100), g(111)
ac_wA, ac_wB = g(115), None
# one more record from the parked pool for ac_wB
pool = [x for x in d.gauges if x.type == 2
        and x.get_rect_px()[0] > 790 and x.name not in
        ("Text Gauge 20", "Text Gauge 92", "Text Gauge 96",
         "Text Gauge 100", "Text Gauge 111", "Text Gauge 115")]
ac_wB = pool[0]
print("ac_wB uses", ac_wB.name, "| parked pool", len(pool))

# CRUISE: 0 OFF / 1 STBY / 2 SET / 3 RES / 4 OVR
CRX, CRY, CRW, CRH = 416, 334, 166, 42
# existing lens TG15 = fill1 [OFF, STBY, SET]
g(15).set_arr(0, [LENS_OFF, STEEL, BLUE] * 2, flag=0)
g(15).set_ranges(0, 4, warn=0.5, crit=1.5, warn_below=-999, crit_below=-999)
fill(cr_fill2, CRX, CRY, CRW, CRH, H_CRUISE, 4, 2.5, 3.5,
     [TRANSP, TEAL, WARN])
word(cr_wA, CRX, CRY + 10, CRW, 22, H_CRUISE, 4, 0.5, 1.5,
     ["OFF", "STBY", ""], [LEG_OFF, NEARWHITE, TRANSP])
word(cr_wB, CRX, CRY + 10, CRW, 22, H_CRUISE, 4, 1.5, 2.5,
     ["", "SET", ""], [TRANSP, DARK, TRANSP])
word(cr_wC, CRX, CRY + 10, CRW, 22, H_CRUISE, 4, 2.5, 3.5,
     ["", "RES", "OVR"], [TRANSP, DARK, DARK])

# A/C: 0 OFF / 1 REQ / 2 ON / 3 FLT
ACX, ACY = 614, 334
g(18).set_arr(0, [LENS_OFF, WARN, BLUE] * 2, flag=0)
g(18).set_ranges(0, 3, warn=0.5, crit=1.5, warn_below=-999, crit_below=-999)
fill(ac_fill2, ACX, ACY, CRW, CRH, H_AC, 3, 2.5, 999,
     [TRANSP, CRIT, CRIT])
word(ac_wA, ACX, ACY + 10, CRW, 22, H_AC, 3, 0.5, 1.5,
     ["OFF", "REQ", ""], [LEG_OFF, DARK, TRANSP])
word(ac_wB, ACX, ACY + 10, CRW, 22, H_AC, 3, 1.5, 2.5,
     ["", "ON", "FLT"], [TRANSP, DARK, VAL])

# ---------- 4. turbo notation ----------
g(77).set_texts("Turbo")
kchip = g(78)
kchip.set_rect_px(342, 262, 56, 18)
kchip.set_texts("k RPM")
kchip.set_fsize_for_h(18)
kchip.set_arr(2, [UNIT] * 6, flag=0)
kchip.set_tcolor(UNIT)

# ---------- 5. paint order ----------
# insert: cruise fill2 after TG15, words after gloss TG16; same for A/C.
moved = {x.name for x in (cr_fill2, cr_wA, cr_wB, cr_wC, ac_fill2,
                          ac_wA, ac_wB)}
order = []
for x in d.gauges:
    if x.name in moved:
        continue
    order.append(x)
    if x.name == "Text Gauge 15":
        order.append(cr_fill2)
    elif x.name == "Text Gauge 16":
        order += [cr_wA, cr_wB, cr_wC]
    elif x.name == "Text Gauge 18":
        order.append(ac_fill2)
    elif x.name == "Text Gauge 19":
        order += [ac_wA, ac_wB]
assert len(order) == 83, len(order)
n, c = d.save(DST, order=order)
print("built %s: %d bytes, %d records" % (DST, n, c))
import os
os.remove(TMP)
