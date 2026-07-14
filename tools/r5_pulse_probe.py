#!/usr/bin/env python3
"""Pulse isolation probe (throwaway copy of v9):
- FAN records (hash C44AB478): crit -> 2.0 (bit=1 stays WARNING only)
- SBFLT records (hash 7F8E9FE9): arr0 flag=0 static [off,lit,lit]
- FLAT (6B5F9216): untouched control (flag=1 gradient + crit 0.7)
Burst then tells which config pulses."""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2

SRC = r"C:\Users\danie\Downloads\st185_dash_v9.rd"
OUT = r"C:\Users\danie\Downloads\r5_probe_aspect.rd"

H_FAN, H_SBF = 0xC44AB478, 0x7F8E9FE9
OFF = 0xFF121A22
LIT_AMBER = 0xFFFFB300

d = Dash2(SRC)
for g in d.gauges:
    try:
        h = g.get_hash()
    except Exception:
        continue
    if h == H_FAN:
        off = g._range_off()
        struct.pack_into("<f", g.b, off + 8, 2.0)   # critAbove = 2.0
        print("FAN crit->2.0 on", g.name)
    elif h == H_SBF:
        offs = g.arr_offsets()
        if offs:
            g.set_arr(0, [OFF, LIT_AMBER, LIT_AMBER] * 2, flag=0)
            print("SBFLT arr0 flag0 static on", g.name)
d.save(OUT)
print("saved", OUT)
