#!/usr/bin/env python3
"""dump_ranges.py <file.rd> <gauge> [gauge...] - print range block + color arrays."""
import struct
import sys
from rd_lib2 import Dash2

d = Dash2(sys.argv[1])
m = d.by_name()
for nm in sys.argv[2:]:
    g = m[nm]
    off = g._range_off()
    vals = struct.unpack_from("<I7f", g.b, off)
    print("%s: critBelow=%g critAbove=%g warnBelow=%g warnAbove=%g min=%g max=%g cur=%g"
          % (nm, *vals[1:]))
    print("   hash=%08X dec=%d" % (g.get_hash(),
          struct.unpack_from("<I", g.b, g._arr_marker() - 8)[0]))
    k = g._arr_marker() + 4
    for i in range(4):
        a, flag = struct.unpack_from("<2I", g.b, k)
        if a != 1 or flag not in (0, 1):
            break
        cols = struct.unpack_from("<6I", g.b, k + 8)
        print("   arr%d flag=%d %s" % (i, flag, " ".join("%08X" % c for c in cols)))
        k += 32
