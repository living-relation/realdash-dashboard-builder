#!/usr/bin/env python3
"""cf_assets.py - asset region + header-prefix layout details."""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str

d = Dash2(sys.argv[1] if len(sys.argv) > 1 else
          r"C:\Users\danie\Downloads\st185_dash_v5.rd")
h = bytes(d.header)

# first 122 bytes before the first asset name, as u32/f32 grid
print("header prefix (0..122):")
j = 0
while j + 4 <= 122:
    v = struct.unpack_from("<I", h, j)[0]
    f = struct.unpack_from("<f", h, j)[0]
    r = read_str(h, j)
    s = " str=%r" % r[0] if r and len(r[0]) >= 2 else ""
    print("  @%3d: 0x%08X f=%-10.4g%s" % (j, v, f, s))
    j += 4

# asset region walk
i = 0
while i < len(h) - 8:
    r = read_str(h, i)
    if r and (r[0].lower().endswith((".png", ".jpg")) or r[0].endswith("_")) and 3 < len(r[0]) < 64:
        size = struct.unpack_from("<I", h, r[1])[0]
        if 0 < size < 2_000_000 and r[1] + 4 + size <= len(h):
            blob = h[r[1] + 4:r[1] + 4 + size]
            sig = blob.find(b"\x89PNG")
            print("asset %-20s nameoff=%d size=%d blob@%d pngsig_at_blob+%d first16=%s" %
                  (r[0], i, size, r[1] + 4, sig, blob[:16].hex()))
            i = r[1] + 4 + size
            continue
    i += 1
print("bytes after last asset blob to header end: 60 (known)")
