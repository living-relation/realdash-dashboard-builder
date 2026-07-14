#!/usr/bin/env python3
"""round3_v5.py - "Carbon Forge" dark redesign of st185_dash_v5.rd (Plan A).

Pipeline (rebuilt FROM probe_base.rd - v5's own image record was poisoned by
an earlier in-app save; probe_base's Image Gauge 1 is render-proven):
 1. Replace embedded `_indicators.png_` asset bytes with carbonforge_bg.png
    (raw header splice: lpstr name + u32 size + [u32 0 + png bytes]).
 2. Image Gauge 1 -> full-screen background, painted FIRST. Safe writes ONLY:
    rect1, +20 UV (0,0,1,1), +36 UV2, arr1 blend white, hash, ranges.
    POISON (blanks the record AND kills every record painted after it):
    rect_anchor+72 subframe index, text_end+104/108 grid counts (probe4/6).
 3. Restyle every text gauge per _build/research/dark_dash_inspiration.md:
    hero THROTTLE % + sweep bar, 12 panels, unit chips, enum lens blocks,
    six 5-layer LED pills. All bindings from the known-hash table.
 4. Bar Gauge 1 = header sweep fill (throttle), painted last (on top).
Usage: python round3_v5.py [out.rd]  (default: overwrite Downloads v5)
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str

DL = r"C:\Users\danie\Downloads"
SRC = DL + r"\probe_base.rd"
DST = sys.argv[1] if len(sys.argv) > 1 else DL + r"\st185_dash_v5.rd"
PNG = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\cf_sheet.png"

# ---------------- palette ----------------
CANVAS = 0xFF0B0C0E
VAL = 0xFFF2F4F6
LAB = 0xFF8A9099
UNIT = 0xFF6F7680
HERO = 0xFFFFD400
WARN = 0xFFFFB300
CRIT = 0xFFFF3226
GREEN = 0xFF3DDC5A
BLUE = 0xFF2E9BFF
STEEL = 0xFF1B4E75          # dim steel blue (CRUISE STBY)
LENS_OFF = 0xFF15181C
LEG_OFF = 0xFF4A5058
LEG_DARK = 0xFF1A1400       # legend on lit amber lens
GLOW_R = 0xFF66120C
GLOW_A = 0xFF664A00
GLOW_B = 0xFF0E2E4D
CRITBG = 0xFF3D0800
GLOSS = 0x1FFFFFFF
TRANSP = 0x00000000
UNBOUND = 0xFFFFFFFF
BIG = 9e9

H = {
    "throttle": 0xA5AA7D05, "boostmap": 0xE1F72794, "tc": 0x4E28D27A,
    "lambda": 0x9ED3572B, "iat": 0x978E3E78, "coolp": 0xDD266D22,
    "turbo": 0x413F90BA, "load": 0x9007B539, "fuelt": 0x80D7FC73,
    "eth": 0xBDB0E378, "trig": 0x04B07E8E, "cruise": 0x18ECF9C1,
    "ac": 0xE975C645, "flat": 0x6B5F9216, "fan": 0xC44AB478,
    "lofuel": 0xDD06C8FD, "sbflt": 0x7F8E9FE9, "hicool": 0x3A7D877E,
    "looil": 0xAD193AD0,
}

# ---------------- 1. asset splice (raw bytes) ----------------
raw = open(SRC, "rb").read()
png = open(PNG, "rb").read()
name16 = "_indicators.png_".encode("utf-16-le")
ni = raw.find(struct.pack("<I", 16) + name16)          # lpstr in header
assert 0 < ni < 400000, "asset name not found"
size_off = ni + 4 + len(name16)
old_size = struct.unpack_from("<I", raw, size_off)[0]
assert old_size == 25425, old_size
new_blob = b"\x00\x00\x00\x00" + png
raw = (raw[:size_off] + struct.pack("<I", len(new_blob)) + new_blob +
       raw[size_off + 4 + old_size:])
TMP = DL + r"\_cf_tmp.rd"
open(TMP, "wb").write(raw)

d = Dash2(TMP)
m = d.by_name()
assert len(d.gauges) == 127, len(d.gauges)
d.set_canvas_bg(CANVAS)

# ---------------- 2. background image gauge (safe writes only) ----------
img = m["Image Gauge 1"]
img.rename("Image Background")
img.set_rect_px(0, 0, 800, 480)          # type 5: writes rect1 only
# The record's live UV window is the +36 quad (0.875..1, 0..0.125) —
# measured 2026-07-07 via calibration sheet. Writing +36 does NOT retarget
# it, and grid/index writes poison the loader. cf_sheet.png (6400x3840)
# carries the art inside that exact window. Only +20 (inner UV) is safe:
struct.pack_into("<4f", img.b, img.rect_anchor + 20, 0.0, 0.0, 1.0, 1.0)
img.set_arr(1, [0xFFFFFFFF] * 6, flag=0)                 # blend: true color
img.set_hash(UNBOUND)
img.set_ranges(0, 1, warn=BIG, crit=BIG, warn_below=-BIG, crit_below=-BIG)

# ---------------- helpers ----------------
def park(g):
    g.set_rect_px(797, 0, 2, 2)
    if g.type == 2:
        g.set_texts("")
        g.set_bg_states(TRANSP, TRANSP)
        g.set_arr(2, [TRANSP] * 6, flag=0)
        g.set_tcolor(TRANSP)
    g.set_hash(UNBOUND)
    return g


def _static_bg(g, argb):
    if g.type == 2:
        struct.pack_into("<I", g.b, g.nend + 0x5C, argb)


def label(g, x, y, w, h, text, color=LAB):
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    g.set_fsize_for_h(h)
    _static_bg(g, TRANSP)
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [color] * 6, flag=0)
    g.set_tcolor(color)
    g.set_hash(UNBOUND)
    return g


def set_static_text(g, on):
    """states_end+76: 0x20400000 static text / 0x00400000 live text.
    probe_base text gauges ship static=ON -> bound values freeze at baked
    text (discovered 2026-07-07 via probe_gm byte-diff)."""
    j = g._states_off()
    for _ in range(3):
        j = read_str(g.b, j)[1]
    cur = struct.unpack_from("<I", g.b, j + 76)[0]
    assert cur & 0x00400000, hex(cur)
    struct.pack_into("<I", g.b, j + 76,
                     (cur | 0x20000000) if on else (cur & ~0x20000000))


def value(g, x, y, w, h, hkey, dec, vmin, vmax, warn=None, crit=None,
          below=None, normal=VAL, wcol=WARN, ccol=CRIT, baked="0",
          critbg=False, math=None):
    if math:
        g.set_gauge_math(math)
    set_static_text(g, False)
    g.set_rect_px(x, y, w, h)
    g.set_texts(baked)
    g.set_fsize_for_h(h)
    bgs = [TRANSP, TRANSP, CRITBG if critbg else TRANSP]
    _static_bg(g, TRANSP)
    g.set_arr(0, bgs * 2, flag=0)
    g.set_arr(2, [normal, wcol, ccol] * 2, flag=0)
    g.set_tcolor(normal)
    g.set_hash(H[hkey])
    g.set_decimals(dec)
    g.set_ranges(vmin, vmax,
                 warn=warn if warn is not None else BIG,
                 crit=crit if crit is not None else BIG,
                 warn_below=below if below is not None else -BIG,
                 crit_below=below if below is not None else -BIG)
    return g


def lens_block(g, x, y, w, h, hkey, warn, crit, wbg, cbg):
    """Enum lens: bound block, invisible text, per-level bg colors."""
    g.set_rect_px(x, y, w, h)
    g.set_texts("")
    _static_bg(g, LENS_OFF)
    g.set_arr(0, [LENS_OFF, wbg, cbg] * 2, flag=0)
    g.set_arr(2, [TRANSP] * 6, flag=0)
    g.set_tcolor(TRANSP)
    g.set_hash(H[hkey])
    g.set_decimals(0)
    g.set_ranges(0, 4, warn=warn, crit=crit, warn_below=-BIG, crit_below=-BIG)
    return g


# ---------------- 3. layout ----------------
texts = [g for g in d.gauges if g.type == 2]
assert len(texts) == 122, len(texts)
for g in texts:
    park(g)
pool = list(texts)


def take():
    return pool.pop(0)


order_actives = []


def A(g):
    order_actives.append(g)
    return g


# turbo math FIRST on the gauge that will carry it (re-splices blob)
turbo_g = take()

# --- header hero: THROTTLE % + sweep bar ---
A(label(take(), 20, 16, 200, 18, "THROTTLE %"))
A(value(take(), 20, 38, 170, 50, "throttle", 0, 0, 100,
        normal=HERO, wcol=HERO, ccol=HERO))

# --- 12 grid panels ---
PANELS = [
    # (x, y, label, kind, args)
    (8, 108, "TC", "enum", dict(hkey="tc", warn=0.5, crit=BIG,
                                wbg=BLUE, cbg=BLUE)),
    (206, 108, "BOOST MAP", "val", dict(hkey="boostmap", dec=0, vmin=0, vmax=3,
                                        baked="0")),
    (404, 108, "TARGET \u03bb", "val", dict(hkey="lambda", dec=2, vmin=0.6,
                                            vmax=1.3, baked="0.60")),
    (602, 108, "CHARGE TEMP", "val", dict(hkey="iat", dec=0, vmin=0, vmax=120,
                                          warn=50, crit=60, below=-99,
                                          critbg=True, unit="\u00b0C")),
    (8, 204, "COOLANT P", "val", dict(hkey="coolp", dec=0, vmin=0, vmax=1000,
                                      warn=150, crit=250, critbg=True,
                                      unit="kPa")),
    (206, 204, "TURBO RPM", "val", dict(hkey="turbo", dec=0, vmin=0, vmax=255,
                                        warn=180, crit=190, critbg=True,
                                        math="=V/1000", unit="k")),
    (404, 204, "ENGINE LOAD %", "val", dict(hkey="load", dec=0, vmin=0,
                                            vmax=100)),
    (602, 204, "FUEL TEMP", "val", dict(hkey="fuelt", dec=0, vmin=-50,
                                        vmax=205, warn=55, crit=70, below=-99,
                                        critbg=True, unit="\u00b0C")),
    (8, 300, "ETHANOL %", "val", dict(hkey="eth", dec=0, vmin=0, vmax=100)),
    (206, 300, "TRIGGER ERR", "val", dict(hkey="trig", dec=0, vmin=0, vmax=255,
                                          warn=1, crit=5, normal=GREEN,
                                          critbg=True)),
    (404, 300, "CRUISE", "enum", dict(hkey="cruise", warn=0.5, crit=1.5,
                                      wbg=STEEL, cbg=BLUE)),
    (602, 300, "A/C", "enum", dict(hkey="ac", warn=0.5, crit=2.5,
                                   wbg=BLUE, cbg=CRIT)),
]
def gloss_over(g, x, y, w, h):
    g.set_rect_px(x, y, w, h)
    g.set_texts("")
    _static_bg(g, GLOSS)
    g.set_arr(0, [GLOSS] * 6, flag=0)
    g.set_arr(2, [TRANSP] * 6, flag=0)
    g.set_tcolor(TRANSP)
    g.set_hash(UNBOUND)
    return g


for x, y, lab, kind, kw in PANELS:
    A(label(take(), x + 12, y + 10, 166, 17, lab))
    if kind == "enum":
        A(lens_block(take(), x + 12, y + 34, 166, 42, **kw))
        A(gloss_over(take(), x + 12, y + 34, 166, 16))
    else:
        unit = kw.pop("unit", None)
        g = turbo_g if kw.get("math") else take()
        A(value(g, x + 12, y + 32, 118, 46, **kw))
        if unit:
            A(label(take(), x + 136, y + 58, 42, 18, unit, color=UNIT))

# --- 6 LED pills: halo, lens, gloss, legend ---
PILLS = [
    (8, "FLAT", "flat", "info"),
    (140, "FAN", "fan", "info"),
    (272, "LOFUEL", "lofuel", "warn"),
    (404, "SBFLT", "sbflt", "warn"),
    (536, "COOLANT P", "hicool", "crit"),
    (668, "OIL P", "looil", "crit"),
]
for x, txt, hk, cls in PILLS:
    halo, lens, gloss, leg = take(), take(), take(), take()
    y = 400
    # halo
    halo.set_rect_px(x + 6, y + 6, 112, 52)
    halo.set_texts("")
    halo.set_tcolor(TRANSP)
    halo.set_arr(2, [TRANSP] * 6, flag=0)
    halo.set_hash(H[hk])
    halo.set_decimals(0)
    # lens
    lens.set_rect_px(x + 10, y + 10, 104, 44)
    lens.set_texts("")
    lens.set_tcolor(TRANSP)
    lens.set_arr(2, [TRANSP] * 6, flag=0)
    lens.set_hash(H[hk])
    lens.set_decimals(0)
    # legend (text carrier)
    leg.set_rect_px(x + 14, y + 23, 96, 18)
    leg.set_texts(txt)
    leg.set_fsize_for_h(18)
    _static_bg(leg, TRANSP)
    leg.set_arr(0, [TRANSP] * 6, flag=0)
    leg.set_hash(H[hk])
    leg.set_decimals(0)
    if cls == "info":     # steady blue: dynamic fill, alarms unreachable
        glow, lit, legc = GLOW_B, BLUE, VAL
        for g in (halo, lens, leg):
            g.set_ranges(0, 1, warn=999, crit=999, warn_below=-999,
                         crit_below=-999)
        _static_bg(halo, TRANSP)
        halo.set_arr(0, [TRANSP] * 3 + [glow] * 3, flag=1)
        _static_bg(lens, LENS_OFF)
        lens.set_arr(0, [LENS_OFF] * 3 + [lit] * 3, flag=1)
        leg.set_arr(2, [LEG_OFF] * 3 + [legc] * 3, flag=1)
        leg.set_tcolor(LEG_OFF)
    else:
        if cls == "warn":
            glow, lit, legc = GLOW_A, WARN, LEG_DARK
            rng = dict(warn=0.5, crit=999, warn_below=-999, crit_below=-999)
        else:
            glow, lit, legc = GLOW_R, CRIT, VAL
            rng = dict(warn=0.5, crit=0.7, warn_below=0, crit_below=0)
        for g in (halo, lens, leg):
            g.set_ranges(0, 1, **rng)
        if cls == "crit":
            # Blink Speed, critical level: f32 @ range_anchor+48
            # (discovered 2026-07-07 via GUI probe byte-diff; GUI 500 ms
            # saved 1.0; +40/+44 = normal/warning slots, leave 0)
            for g in (halo, lens):
                struct.pack_into("<f", g.b, g._range_off() + 48, 1.0)
        _static_bg(halo, TRANSP)
        halo.set_arr(0, [TRANSP, glow, glow] * 2, flag=0)
        _static_bg(lens, LENS_OFF)
        lens.set_arr(0, [LENS_OFF, lit, lit] * 2, flag=0)
        leg.set_arr(2, [LEG_OFF, legc, legc] * 2, flag=0)
        leg.set_tcolor(LEG_OFF)
    # gloss: static glass highlight over top half of lens
    gloss.set_rect_px(x + 10, y + 10, 104, 20)
    gloss.set_texts("")
    _static_bg(gloss, GLOSS)
    gloss.set_arr(0, [GLOSS] * 6, flag=0)
    gloss.set_arr(2, [TRANSP] * 6, flag=0)
    gloss.set_tcolor(TRANSP)
    gloss.set_hash(UNBOUND)
    order_actives += [halo, lens, gloss, leg]

# ---------------- 4. sweep bar (Bar Gauge 1 -> throttle) ----------------
bar = m["Bar Gauge 1"]
bar.rename("Bar Sweep")
bar.set_rect_px(334, 28, 444, 48)
bar.set_hash(H["throttle"])
bar.set_decimals(0)
bar.set_ranges(0, 100, warn=85, crit=95, warn_below=-BIG, crit_below=-BIG)
nrep = bar.replace_level_colors(HERO, WARN, CRIT)   # factory green/amber/red
assert nrep >= 3, nrep

# park unused image-type gauges
for nm in ("Arc Gauge 1", "Graph Gauge 1", "Needle Gauge 1"):
    g = m[nm]
    g.set_rect_px(797, 0, 2, 2)
    g.set_hash(UNBOUND)

# ---------------- 5. order ----------------
# Proven shape (cf_probe3/5): image background FIRST, then text records.
# Bar directly after the visible texts (a visible record after parked
# image-types did not render - test9); parked arc/graph/needle at the end.
parked_texts = [g for g in pool]
order = ([img] + order_actives + [bar] + parked_texts +
         [m["Arc Gauge 1"], m["Graph Gauge 1"], m["Needle Gauge 1"]])
assert len(order) == 127, len(order)
n, c = d.save(DST, order=order)
print("built %s: %d bytes, %d records" % (DST, n, c))

# verify re-parse
chk = Dash2(DST)
print("re-parse: %d records; first=%s type=%d; last=%s type=%d" %
      (len(chk.gauges), chk.gauges[0].name, chk.gauges[0].type,
       chk.gauges[-1].name, chk.gauges[-1].type))
import os
os.remove(TMP)
