#!/usr/bin/env python3
"""Round 5 Tasks 2+3 on v4:
- Aspect compensation K=1.152 (canvas renders 1920x1000 px): needles and
  4 small arcs resized h=K*w around their centers -> circular render.
- Tick DOTS -> thin radial LINE glyphs (box-drawing chars via the 3
  per-level state strings), threshold-lit text colors [dim/cream/red].
Coolant arc goes 6->5 ticks (0/75/150/225/300); the spare dot is parked.
Tick positions: x = cx + r*cos(th), y = cy - r*K*sin(th) so the ring of
ticks renders circular around the now-circular arc.
"""
import math
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2

K = 1.152
PATH = r"C:\Users\danie\Downloads\st185_dash_v4.rd"

OLD_DOT_BG = 0xFF564B39
DIM = 0xFF57493A
CREAM = 0xFFF2EAD9
RED = 0xFFE8482B
TRANSP = 0x00000000
BIG = 9e9
ARC_START, ARC_SWEEP = 220.0, 282.0

d = Dash2(PATH)
m = d.by_name()

# ---- Task 3: needles (keep centers) ----
for nm in ("Needle Throttle", "Needle Turbo"):
    g = m[nm]
    x, y, w, h = g.get_rect_px()
    cx, cy = x + w / 2, y + h / 2
    nh = w * K
    g.set_rect_px(cx - w / 2, cy - nh / 2, w, nh)
    print(nm, "h %.0f -> %.1f (center %.0f,%.0f)" % (h, nh, cx, cy))

# ---- Task 3: arcs (keep centers) ----
ARCS = {
    "Arc Gauge 1": dict(vmin=0, vmax=120, crit=60, ticks=[0, 30, 60, 90, 120]),
    "Arc CoolP":  dict(vmin=0, vmax=300, crit=250, ticks=[0, 75, 150, 225, 300]),
    "Arc Gauge 2": dict(vmin=0, vmax=100, crit=70, ticks=[0, 25, 50, 75, 100]),
    "Arc Gauge 3": dict(vmin=0, vmax=100, crit=None, ticks=[0, 25, 50, 75, 100]),
}
centers = {}
for nm, spec in ARCS.items():
    g = m[nm]
    x, y, w, h = g.get_rect_px()
    cx, cy = x + w / 2, y + h / 2
    nh = w * K
    g.set_rect_px(cx - w / 2, cy - nh / 2, w, nh)
    centers[nm] = (cx, cy, w / 2)
    print(nm, "-> %.0fx%.1f center (%.0f,%.0f)" % (w, nh, cx, cy))

# ---- Task 2: dots -> line glyphs ----
arc_hashes = {m[nm].get_hash() for nm in ARCS}
dots = []
for g in d.gauges:
    x, y, w, h = g.get_rect_px()
    if (g.type == 2 and w < 13 and g.get_hash() in arc_hashes
            and g.name not in ("Text Gauge 38", "Text Gauge 42", "Text Gauge 43")):
        dots.append(g)
# plus the previously parked 21st dot, if this is a re-run
for g in d.gauges:
    if len(dots) >= 21:
        break
    x, y, w, h = g.get_rect_px()
    if g.type == 2 and x > 790 and w < 3 and g.get_hash() == 0xFFFFFFFF \
            and g.text == "" and g not in dots:
        dots.append(g)
print("dot records found:", len(dots))
assert len(dots) == 21, len(dots)


def glyph_for(theta):
    dirdeg = theta % 180.0
    return min(((min(abs(dirdeg - a), 180 - abs(dirdeg - a)), ch) for a, ch in
                ((0, "-"), (45, "/"), (90, "|"), (135, "\\"))))[1]


def make_tick(g, cx, cy, r, theta_deg, ch, hash_, vmin, vmax, tv, crit):
    th = math.radians(theta_deg)
    px_ = cx + r * math.cos(th)
    py = cy - r * K * math.sin(th)
    sz = 9.0
    g.set_texts(ch, [ch, ch, ch])
    g.set_rect_px(px_ - sz / 2, py - sz / 2, sz, sz)
    g.set_fsize_for_h(sz)
    struct.pack_into("<I", g.b, g.nend + 0x5C, TRANSP)
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [DIM, CREAM, RED] * 2, flag=0)
    g.set_tcolor(DIM)
    g.set_hash(hash_)
    g.set_decimals(0)
    warn = tv if tv > vmin else vmin - 1e-3
    cr = max(tv, crit) if crit is not None else BIG
    g.set_ranges(vmin, vmax, warn=warn, crit=cr, warn_below=-BIG, crit_below=-BIG)


it = iter(dots)
R_EXTRA = 4.0
for nm, spec in ARCS.items():
    g_arc = m[nm]
    h_arc = g_arc.get_hash()
    cx, cy, half_w = centers[nm]
    r = half_w + R_EXTRA
    for tv in spec["ticks"]:
        frac = (tv - spec["vmin"]) / float(spec["vmax"] - spec["vmin"])
        theta = ARC_START - frac * ARC_SWEEP
        make_tick(next(it), cx, cy, r, theta, glyph_for(theta),
                  h_arc, spec["vmin"], spec["vmax"], tv, spec["crit"])

# park the leftover 21st dot (coolant went 6->5 ticks)
left = next(it)
left.set_texts("", ["", "", ""])
left.set_rect_px(797, 0, 2, 2)
struct.pack_into("<I", left.b, left.nend + 0x5C, TRANSP)
left.set_arr(0, [TRANSP] * 6, flag=0)
left.set_arr(2, [TRANSP] * 6, flag=0)
left.set_tcolor(TRANSP)
left.set_hash(0xFFFFFFFF)

n, c = d.save(PATH)
print("saved %d bytes %d records" % (n, c))
