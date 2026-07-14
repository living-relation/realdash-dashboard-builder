#!/usr/bin/env python3
"""a2_v4_build.py - Stage A2 full v4 rework (from v4p.rd, the app-saved
probe that already carries: turbo needle math =V/1000 + 0-160 ranges,
3 GUI-added Arc Gauge 1/2/3, caption TG70 painted after the needles).

Does:
 1. Splice roundface_v2.png (matte face, slim bezel, 5 majors + minors,
    red band 93.75-100%) over the roundface.png header asset.
 2. Needles: segments=5 both (labels 0/25/50/75/100 and 0/40/80/120/160),
    face blend arr1 white (true color), needle-tint test via arr2.
 3. Turbo: remove external readout/label/'k' chip; in-dial caption
    "TURBO k RPM" at dial bottom.
 4. Four small arc blocks (charge/coolant/fuel/ethanol): numbers hidden
    (maxdig=0), threshold-lit tick dots, digital readout + unit chip +
    label per block. New arcs bound binarily (iat/fuelt/eth hashes).
 5. FAN pill fix (finite alarms, steady lit).
Usage: python a2_v4_build.py [out.rd]   default C:\\Users\\danie\\Downloads\\v4p2.rd
"""
import math
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str, pack_str

DL = r"C:\Users\danie\Downloads"
SRC = DL + r"\v4p.rd"
DST = sys.argv[1] if len(sys.argv) > 1 else DL + r"\v4p2.rd"
FACE = (r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan"
        r"\_build\assets\v4_assets\roundface_v2.png")

CREAM = 0xFFF2EAD9
BRASS = 0xFFC7A25A
DIMBRASS = 0xFF7A6A4C
AMBER = 0xFFF2A33C
RED = 0xFFE8482B
ARC_FILL = 0xFFE8D9B8
DOT_DIM = 0xFF3A3226
CHIPC = 0xFF9A8F80
NEON_RED = 0xFFFF2A2A
NEON_BLUE = 0xFF00C8FF
WHITE = 0xFFFFFFFF
TRANSP = 0x00000000
UNBOUND = 0xFFFFFFFF
BIG = 9e9

H = {"iat": 0x978E3E78, "coolp": 0xDD266D22, "fuelt": 0x80D7FC73,
     "eth": 0xBDB0E378}

# ---------- 1. raw asset splice ----------
raw = open(SRC, "rb").read()
png = open(FACE, "rb").read()
name16 = "roundface.png".encode("utf-16-le")
ni = raw.find(struct.pack("<I", 13) + name16)
assert 0 < ni < 400000, "roundface asset name not found"
size_off = ni + 4 + len(name16)
old_size = struct.unpack_from("<I", raw, size_off)[0]
new_blob = b"\x00\x00\x00\x00" + png
raw = (raw[:size_off] + struct.pack("<I", len(new_blob)) + new_blob +
       raw[size_off + 4 + old_size:])
TMP = DL + r"\_a2_tmp.rd"
open(TMP, "wb").write(raw)
print("face spliced: old=%d new=%d" % (old_size, len(new_blob)))

d = Dash2(TMP)
m = d.by_name()
assert len(d.gauges) == 131, len(d.gauges)
g = lambda n: m["Text Gauge %d" % n]

# ---------- helpers ----------
def park(gg):
    gg.set_rect_px(797, 0, 2, 2)
    gg.set_texts("")
    struct.pack_into("<I", gg.b, gg.nend + 0x5C, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(UNBOUND)


def dot(gg, x, y, sz, hash_, vmin, vmax, warnval):
    gg.set_rect_px(x - sz / 2, y - sz / 2, sz, sz)
    gg.set_texts("")
    struct.pack_into("<I", gg.b, gg.nend + 0x5C, DOT_DIM)
    gg.set_arr(0, [DOT_DIM, CREAM, CREAM] * 2, flag=0)
    gg.set_arr(2, [TRANSP] * 6, flag=0)
    gg.set_tcolor(TRANSP)
    gg.set_hash(hash_)
    gg.set_decimals(0)
    gg.set_ranges(vmin, vmax, warn=warnval, crit=BIG,
                  warn_below=-BIG, crit_below=-BIG)


def chip(gg, x, y, w, h, text):
    gg.set_rect_px(x, y, w, h)
    gg.set_texts(text)
    gg.set_fsize_for_h(h)
    struct.pack_into("<I", gg.b, gg.nend + 0x5C, TRANSP)
    gg.set_arr(0, [TRANSP] * 6, flag=0)
    gg.set_arr(2, [CHIPC] * 6, flag=0)
    gg.set_tcolor(CHIPC)
    gg.set_hash(UNBOUND)


# parked pool (rect 797,0 2x2, type 2), excluding the 2 pads we keep last
parked = [x for x in d.gauges if x.type == 2 and x.get_rect_px()[0] > 790]
print("parked pool:", len(parked))
pool = list(parked)
take = lambda: pool.pop(0)

# ---------- 2. needles ----------
nt = m["Needle Turbo"]
nth = m["Needle Throttle"]
for n in (nt, nth):
    n.set_autoscale(segments=5, maxdig=3)
    n.set_arr(1, [WHITE] * 6, flag=0)          # face: true color
nth.set_arr(2, [NEON_BLUE] * 6, flag=0)        # needle tint test
nt.set_arr(2, [NEON_RED] * 6, flag=0)

# ---------- 3. turbo external readout removal + caption ----------
park(g(40))     # external digital readout
park(g(133))    # 'k' chip
park(g(27))     # 'TURBO RPM' label
cap = g(70)     # already painted after needles
cap.set_rect_px(596, 242, 110, 14)
cap.set_texts("TURBO k RPM")
cap.set_fsize_for_h(14)
cap.set_arr(2, [BRASS] * 6, flag=0)
cap.set_tcolor(BRASS)

# throttle dial caption for symmetry (painted after needles too - use TG71
# which sits at index 126; replace its pad role, pads re-added at save)
cap2 = m["Text Gauge 71"]
cap2.set_rect_px(94, 242, 110, 14)
cap2.set_texts("THROTTLE %")
cap2.set_fsize_for_h(14)
struct.pack_into("<I", cap2.b, cap2.nend + 0x5C, TRANSP)
cap2.set_arr(0, [TRANSP] * 6, flag=0)
cap2.set_arr(2, [BRASS] * 6, flag=0)
cap2.set_tcolor(BRASS)
park(g(23))     # old 'THROTTLE %' label under dial
# throttle readout moves under dial center (kept - annotation kept it)
g(34).set_rect_px(114, 306, 70, 30)

# ---------- 4. arc blocks ----------
ARC_START, ARC_SWEEP = 220.0, 282.0    # deg (matches 3.8397/4.9218 rad)


def arc_style(a, x, y, sz, hkey, vmin, vmax, warn, crit, below):
    a.set_rect_px(x, y, sz, sz)
    a.set_hash(H[hkey])
    a.set_decimals(0)
    a.set_ranges(vmin, vmax,
                 warn=warn if warn is not None else BIG,
                 crit=crit if crit is not None else BIG,
                 warn_below=below if below is not None else -BIG,
                 crit_below=below if below is not None else -BIG)
    a.set_autoscale(maxdig=0)
    n = a.replace_level_colors(ARC_FILL, AMBER, RED)
    try:
        ao = a._angles_off()
        sa, sw = struct.unpack_from("<2f", a.b, ao)
        print("  %s angles %.4f/%.4f colors_replaced=%d" % (a.name, sa, sw, n))
    except Exception as e:
        print("  %s angles: %s" % (a.name, e))


def dots_for(cx, cy, r, hash_, vmin, vmax, ticks):
    for tv in ticks:
        frac = (tv - vmin) / float(vmax - vmin)
        ang = math.radians(ARC_START - frac * ARC_SWEEP)
        x = cx + r * math.cos(ang)
        y = cy - r * math.sin(ang)
        dot(take(), x, y, 5, hash_, vmin, vmax, tv if tv > vmin else vmin - 1e-3)


# charge temp block (new Arc Gauge 1)
arc_style(m["Arc Gauge 1"], 24, 352, 64, "iat", 0, 120, 50, 60, -99)
dots_for(56, 384, 21, H["iat"], 0, 120, [0, 30, 60, 90, 120])
g(38).set_rect_px(94, 360, 46, 26)
g(38).set_fsize_for_h(26)
chip(g(130), 94, 390, 26, 13, "\u00b0C")
g(25).set_rect_px(20, 430, 120, 11)

# coolant block (existing Arc CoolP), numbers off + dots
arc_style(m["Arc CoolP"], 146, 352, 70, "coolp", 0, 300, 150, 250, None)
dots_for(181, 387, 23, H["coolp"], 0, 300, [0, 60, 120, 180, 240, 300])

# fuel temp block (Arc Gauge 2)
arc_style(m["Arc Gauge 2"], 540, 352, 64, "fuelt", 0, 100, 55, 70, -99)
dots_for(572, 384, 21, H["fuelt"], 0, 100, [0, 25, 50, 75, 100])
g(42).set_rect_px(610, 360, 46, 26)
g(42).set_fsize_for_h(26)
chip(g(132), 610, 390, 26, 13, "\u00b0C")
g(29).set_rect_px(540, 430, 120, 11)

# ethanol block (Arc Gauge 3)
arc_style(m["Arc Gauge 3"], 665, 352, 64, "eth", 0, 100, None, None, None)
dots_for(697, 384, 21, H["eth"], 0, 100, [0, 25, 50, 75, 100])
g(43).set_rect_px(735, 360, 46, 26)
g(43).set_fsize_for_h(26)
g(30).set_rect_px(665, 430, 120, 11)

# ---------- 5. FAN pill fix ----------
g(4).set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)

# ---------- order: unchanged except 2 fresh inert pads at the very end
# (TG71 became a caption; steal 2 parked records as pads) ----------
pad1, pad2 = take(), take()
park(pad1)
park(pad2)
rest = [x for x in d.gauges if x not in (pad1, pad2)]
order = rest + [pad1, pad2]
assert len(order) == 131, len(order)
n, c = d.save(DST, order=order)
print("built %s: %d bytes, %d records" % (DST, n, c))
import os
os.remove(TMP)
