#!/usr/bin/env python3
"""cf_tail.py - dump structure of image-type records: head strings + final tail."""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str

d = Dash2(r"C:\Users\danie\Downloads\st185_dash_v5.rd")
m = d.by_name()

for nm in ("Image TrigWarn", "Needle IAT", "Arc Ethanol"):
    g = m[nm]
    b = bytes(g.b)
    print("=== %s len=%d rect_anchor=%d ===" % (nm, len(b), g.rect_anchor))
    # walk strings from name end to rect anchor
    j = g.nend
    print(" head region %d..%d:" % (j, g.rect_anchor))
    while j < g.rect_anchor:
        r = read_str(b, j)
        if r and len(r[0]) >= 3:
            print("  str @%d: %r" % (j, r[0]))
            j = r[1]
        else:
            v = struct.unpack_from("<I", b, j)[0]
            f = struct.unpack_from("<f", b, j)[0]
            print("  u32 @%d: 0x%08X f=%.4g" % (j, v, f))
            j += 4

print()
# final 200 bytes of the LAST record (Image TrigWarn) as u32 grid
g = d.gauges[-1]
b = bytes(g.b)
start = len(b) - 200
start -= start % 4
print("=== last record final bytes @%d..%d ===" % (start, len(b)))
j = start
while j + 4 <= len(b):
    r = read_str(b, j)
    if r and len(r[0]) >= 3:
        print("  str @%d: %r" % (j, r[0]))
        j = r[1]
    else:
        v = struct.unpack_from("<I", b, j)[0]
        f = struct.unpack_from("<f", b, j)[0]
        print("  u32 @%d: 0x%08X f=%.4g" % (j, v, f))
        j += 4

# also: last 60 bytes of the header (after last asset blob)
h = bytes(d.header)
print("=== header last 60 bytes ===")
j = len(h) - 60
while j + 4 <= len(h):
    v = struct.unpack_from("<I", h, j)[0]
    f = struct.unpack_from("<f", h, j)[0]
    print("  u32 @-%d: 0x%08X f=%.4g" % (len(h) - j, v, f))
    j += 4
print("=== footer 46 bytes hex ===")
print(d.footer.hex())
