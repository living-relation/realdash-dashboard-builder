#!/usr/bin/env python3
"""cf_donor.py - dump donor Image Gauge 1 record fully (strings + u32 grid)."""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str

d = Dash2(r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\backup\asset_donor_template.rd")
print("donor records:", [(g.name, g.type, len(g.b)) for g in d.gauges if g.type != 2][:10])
g = d.by_name()["Image Gauge 1"]
b = bytes(g.b)
print("=== Image Gauge 1 len=%d rect_anchor=%d text_end=%d arrmark=%d ===" %
      (len(b), g.rect_anchor, g.text_end, g._arr_marker()))
x, y, w, h = g.get_rect_px()
print("rect: %.1f,%.1f %.1fx%.1f  uv-slot:" % (x, y, w, h),
      struct.unpack_from("<4f", b, g.rect_anchor + 20))
# walk whole record compactly: strings + non-zero u32s
j = 0
zrun = 0
while j + 4 <= len(b):
    r = read_str(b, j)
    if r and len(r[0]) >= 3:
        if zrun:
            print("  ... %d zero-u32s" % zrun); zrun = 0
        print("  str @%d: %r" % (j, r[0]))
        j = r[1]
        continue
    v = struct.unpack_from("<I", b, j)[0]
    if v == 0:
        zrun += 1
    else:
        if zrun:
            print("  ... %d zero-u32s" % zrun); zrun = 0
        f = struct.unpack_from("<f", b, j)[0]
        print("  u32 @%4d: 0x%08X f=%.4g" % (j, v, f))
    j += 4
if zrun:
    print("  ... %d zero-u32s" % zrun)
