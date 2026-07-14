#!/usr/bin/env python3
"""cf_inspect.py - inventory v5: header assets, records, image-record tail."""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str, TYPE_NAMES

PATH = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\danie\Downloads\st185_dash_v5.rd"
d = Dash2(PATH)
print("header %d bytes, %d records, footer %d" % (len(d.header), len(d.gauges), 46))

# --- header asset scan: lpstr name ending .png + u32 size + blob ---
h = bytes(d.header)
i = 0
assets = []
while i < len(h) - 8:
    r = read_str(h, i)
    if r and r[0].lower().endswith((".png", ".jpg", "_")) and 3 < len(r[0]) < 64:
        size = struct.unpack_from("<I", h, r[1])[0]
        if 0 < size < 2_000_000 and r[1] + 4 + size <= len(h):
            blob = h[r[1] + 4:r[1] + 4 + size]
            # locate the real PNG signature inside the blob region
            sigpos = h.find(b"\x89PNG", r[1], r[1] + 64)
            assets.append((r[0], i, size, r[1] + 4, sigpos))
            i = r[1] + 4 + size
            continue
    i += 1
print("assets:")
for name, off, size, blob_off, sigpos in assets:
    print("  %-24s off=%d size=%d blob@%d pngsig@%s delta=%s" %
          (name, off, size, blob_off, sigpos, (sigpos - blob_off) if sigpos >= 0 else "?"))
print("header tail after last asset: %d bytes" %
      (len(h) - (assets[-1][3] + assets[-1][2])) if assets else "no assets")

# --- record inventory ---
print("records (order):")
for k, g in enumerate(d.gauges):
    x, y, w, hh = g.get_rect_px()
    print("%3d t%-2d %-18s (%4.0f,%4.0f %4.0fx%3.0f) hash=%08X len=%d txt=%r" %
          (k, g.type, g.name, x, y, w, hh, g.get_hash(), len(g.b), g.text[:12]))

# --- tail of last record: find where its color-group array ends, dump structure after ---
last = d.gauges[-1]
b = bytes(last.b)
am = last._arr_marker()
k = am + 4
narr = 0
while k + 32 <= len(b):
    a, flag = struct.unpack_from("<2I", b, k)
    if a != 1 or flag not in (0, 1):
        break
    narr += 1
    k += 32
print("last rec %s: len=%d arr_marker=%d arrays=%d post-array bytes=%d" %
      (last.name, len(b), am, narr, len(b) - k))
# walk the post-array region for strings/u32s (bounded output)
j = k
steps = 0
while j < len(b) and steps < 40:
    r = read_str(b, j)
    if r and len(r[0]) >= 2:
        print("  str @%d: %r" % (j, r[0]))
        j = r[1]
    else:
        v = struct.unpack_from("<I", b, j)[0] if j + 4 <= len(b) else None
        f = struct.unpack_from("<f", b, j)[0] if j + 4 <= len(b) else None
        print("  u32 @%d: 0x%08X (f=%.4g)" % (j, v, f))
        j += 4
    steps += 1
