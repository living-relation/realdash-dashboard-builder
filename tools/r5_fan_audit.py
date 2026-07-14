#!/usr/bin/env python3
"""Round 5 Task 1: audit (and optionally fix) FAN blink slots on all dashes.

Finds every record whose text/states mention FAN, collects their binding
hashes, then audits ALL records sharing those hashes (lens/fill/glow
sub-records included). Prints blink triples @range_anchor+40/44/48.
With --fix: zeroes all three blink slots on every matched record and saves.
"""
import glob
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2, read_str

FIX = "--fix" in sys.argv
DASHES = [r"C:\Users\danie\Downloads\st185_dash.rd"] + [
    r"C:\Users\danie\Downloads\st185_dash_v%d.rd" % i for i in range(2, 10)]


def states(g):
    out = []
    j = g._states_off()
    for _ in range(3):
        r = read_str(g.b, j)
        out.append(r[0])
        j = r[1]
    return out


def blinks(g):
    off = g._range_off()
    return struct.unpack_from("<3f", g.b, off + 40)


def zero_blinks(g):
    off = g._range_off()
    struct.pack_into("<3f", g.b, off + 40, 0.0, 0.0, 0.0)


for path in DASHES:
    if not os.path.exists(path):
        print("MISSING", path)
        continue
    d = Dash2(path)
    fan_hashes = set()
    fan_recs = []
    for i, g in enumerate(d.gauges):
        try:
            txt = (g.text or "") + " " + " ".join(states(g)) + " " + g.name
        except Exception:
            txt = (g.text or "") + " " + g.name
        if "FAN" in txt.upper():
            fan_recs.append(i)
            h = g.get_hash()
            if h != 0xFFFFFFFF:
                fan_hashes.add(h)
    # second pass: records sharing a fan hash
    for i, g in enumerate(d.gauges):
        if i in fan_recs:
            continue
        try:
            if g.get_hash() in fan_hashes:
                fan_recs.append(i)
        except Exception:
            pass
    dirty = False
    lines = []
    for i in sorted(fan_recs):
        g = d.gauges[i]
        try:
            b = blinks(g)
        except Exception as e:
            lines.append("  [%d] %s: RANGE PARSE FAIL %s" % (i, g.name, e))
            continue
        mark = ""
        if any(abs(x) > 1e-9 for x in b):
            mark = "  <== NONZERO"
            if FIX:
                zero_blinks(g)
                dirty = True
                mark += " -> ZEROED"
        lines.append("  [%d] t%d %-18s hash=%08X txt=%-10r blink=%s%s"
                     % (i, g.type, g.name[:18], g.get_hash(),
                        (g.text or "")[:10], tuple(round(x, 3) for x in b), mark))
    print(os.path.basename(path), "fan_hashes=%s" % [hex(h) for h in fan_hashes])
    for ln in lines:
        print(ln)
    if FIX and dirty:
        n, cnt = d.save(path)
        print("  SAVED %d bytes, %d records" % (n, cnt))
