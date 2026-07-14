#!/usr/bin/env python3
"""diff_gm.py - compare Text Gauge 40's record bytes between probe_gm.rd
(gauge math =V/1000 entered via GUI) and st185_dash.rd (no gauge math)."""
import struct
from rd_lib2 import Dash2, read_str

A = Dash2(r"C:\Users\danie\Downloads\st185_dash.rd")
B = Dash2(r"C:\Users\danie\Downloads\probe_gm.rd")
ga = A.by_name()["Text Gauge 40"]
gb = B.by_name()["Text Gauge 40"]
print("len A=%d  B=%d  delta=%d" % (len(ga.b), len(gb.b), len(gb.b) - len(ga.b)))

a, b = bytes(ga.b), bytes(gb.b)
# walk from front to find first divergence, from back for last
i = 0
while i < min(len(a), len(b)) and a[i] == b[i]:
    i += 1
j = 0
while j < min(len(a), len(b)) - i and a[len(a)-1-j] == b[len(b)-1-j]:
    j += 1
print("first divergence @ +0x%X; common tail %d bytes" % (i, j))
print("A[%x:%x] = %s" % (max(0,i-16), len(a)-j, a[max(0,i-16):len(a)-j+16].hex(' ')))
print("B[%x:%x] = %s" % (max(0,i-16), len(b)-j, b[max(0,i-16):len(b)-j+16].hex(' ')))

# also try to decode any strings near the divergence in B
for k in range(max(0, i - 8), min(len(b) - 4, i + 120)):
    r = read_str(b, k)
    if r and r[0]:
        print("B str @0x%X: %r" % (k, r[0]))

# context: where is divergence relative to known anchors in A?
print("A anchors: name_end=0x%X text_off=0x%X text_end=0x%X arrmark=0x%X reclen=0x%X"
      % (ga.nend, ga.text_off, ga.text_end, ga._arr_marker(), len(a)))
print("B anchors: name_end=0x%X text_off=0x%X text_end=0x%X arrmark=0x%X reclen=0x%X"
      % (gb.nend, gb.text_off, gb.text_end, gb._arr_marker(), len(b)))
