#!/usr/bin/env python3
"""a2_extract_assets.py - extract v4 header assets to _build/assets/v4_assets/,
plus dump Needle Turbo / Arc CoolP structure (strings, arr groups, angles,
autoscale) for Stage A2 planning."""
import struct
import sys
import os

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str

SRC = r"C:\Users\danie\Downloads\st185_dash_v4.rd"
OUT = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\assets\v4_assets"
os.makedirs(OUT, exist_ok=True)

d = Dash2(SRC)
h = bytes(d.header)
i = 0
while i < len(h) - 8:
    r = read_str(h, i)
    if r and (r[0].lower().endswith((".png", ".jpg")) or r[0].endswith("_")) and 3 < len(r[0]) < 64:
        size = struct.unpack_from("<I", h, r[1])[0]
        if 0 < size < 2_000_000 and r[1] + 4 + size <= len(h):
            blob = h[r[1] + 4:r[1] + 4 + size]
            png = blob[4:]  # skip u32 0 prefix
            fn = os.path.join(OUT, r[0].strip("_") or "unnamed")
            if not fn.lower().endswith(".png"):
                fn += ".png"
            open(fn, "wb").write(png)
            print("asset %-22s size=%-7d -> %s" % (r[0], size, os.path.basename(fn)))
            i = r[1] + 4 + size
            continue
    i += 1

m = d.by_name()
for nm in ("Needle Turbo", "Arc CoolP"):
    g = m[nm]
    print("\n=== %s (type %d, len %d) ===" % (nm, g.type, len(g.b)))
    # strings between name end and rect anchor + after V2
    b = bytes(g.b)
    j = g.nend
    while j < len(b) - 4:
        r = read_str(b, j)
        if r and len(r[0]) >= 3:
            print("  str @%-5d %r" % (j, r[0]))
            j = r[1]
        else:
            j += 1
    try:
        ao = g._angles_off()
        a, s = struct.unpack_from("<2f", b, ao)
        print("  angles @%d: start=%.4f rad sweep=%.4f rad" % (ao, a, s))
    except Exception as e:
        print("  angles: %s" % e)
    try:
        off = g._autoscale_off()
        vals = struct.unpack_from("<8f", b, off)
        u32s = struct.unpack_from("<8I", b, off + 32)
        print("  autoscale @%d floats=%s" % (off, ["%.3g" % v for v in vals]))
        print("    +32 u32s=%s (+44 seg=%d +52 maxdig=%d +56 use_auto=%d)" % (
            list(u32s), u32s[3], u32s[5], u32s[6]))
    except Exception as e:
        print("  autoscale: %s" % e)
    ro = g._range_off()
    rv = struct.unpack_from("<7f", b, ro + 4)
    print("  ranges critB=%g critA=%g warnB=%g warnA=%g min=%g max=%g cur=%g" % rv)
    print("  math=%r hash=%08X" % (g.get_gauge_math(), g.get_hash()))
    offs = g.arr_offsets(count=6)
    for k, o in enumerate(offs):
        flag = struct.unpack_from("<I", b, o - 4)[0]
        cols = struct.unpack_from("<6I", b, o)
        print("  arr%d flag=%d cols=%s" % (k, flag, ["%08X" % c for c in cols]))
