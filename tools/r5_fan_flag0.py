#!/usr/bin/env python3
"""Round 5 Task 1 definitive fix: FAN must never pulse/strobe.
Root cause: flag=1 'dynamic color range' bg fill lerps off->lit with the
CHANNEL VALUE; sim sweeps the fan bit as an analog 0..1..0 ramp, so the
pill fades continuously (reads as strobing). Fix: flag=0 STATIC per-level
colors [off, lit, lit] - hard off below warn 0.5, hard steady lit above.
Applies to every record bound to the FAN hash on all nine dashes; also
converts a flag=1 text-color group the same way and re-asserts the steady
ranges + zero blink."""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2

H_FAN = 0xC44AB478
DASHES = [r"C:\Users\danie\Downloads\st185_dash.rd"] + [
    r"C:\Users\danie\Downloads\st185_dash_v%d.rd" % i for i in range(2, 10)]

for path in DASHES:
    d = Dash2(path)
    touched = []
    for g in d.gauges:
        try:
            if g.get_hash() != H_FAN:
                continue
        except Exception:
            continue
        offs = g.arr_offsets()
        for idx, off in enumerate(offs[:3]):
            flag = struct.unpack_from("<I", g.b, off - 4)[0]
            cols = list(struct.unpack_from("<6I", g.b, off))
            if flag == 1 and cols[0] != cols[3]:
                offc, lit = cols[0], cols[3]
                g.set_arr(idx, [offc, lit, lit] * 2, flag=0)
                touched.append("%s.arr%d(%08X->%08X)" % (g.name, idx, offc, lit))
        g.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
        off = g._range_off()
        struct.pack_into("<3f", g.b, off + 40, 0.0, 0.0, 0.0)
    if touched:
        n, c = d.save(path)
        print(os.path.basename(path), "; ".join(touched), "-> saved")
    else:
        print(os.path.basename(path), "no flag=1 FAN groups (ranges/blink re-asserted, NOT saved)")
