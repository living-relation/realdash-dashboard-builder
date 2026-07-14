#!/usr/bin/env python3
"""b2_hdr_dump.py <file.rd> - dump header asset table structure (fonts+images).

Layout hypothesis (B1 font format + round-3 image decode, unified):
  ... lpstr '2.4.1' ... u32 asset_count, then per asset:
    u32 type_tag; lpstr filename; u32 data_size; <meta>; <data>; ...
  We walk generically: after each lpstr name, print surrounding u32s and
  locate the next name by scanning, so the true per-type meta size is
  measurable instead of assumed.
"""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str

d = Dash2(sys.argv[1])
h = bytes(d.header)
print("header=%d records=%d" % (len(h), len(d.gauges)))

# find version string '2.4.1'
i = 0
ver_end = None
while i < len(h) - 4:
    r = read_str(h, i)
    if r and r[0] == "2.4.1":
        ver_end = r[1]
        print("version '2.4.1' ends @%d" % ver_end)
        break
    i += 1
assert ver_end

cnt = struct.unpack_from("<I", h, ver_end + 36)[0]
print("u32 at ver_end+36 (asset_count?) = %d" % cnt)
p = ver_end + 40
for k in range(cnt):
    tag = struct.unpack_from("<I", h, p)[0]
    r = read_str(h, p + 4)
    if not r:
        print("  [%d] tag=%d @%d: NAME PARSE FAIL, next 32B: %s" %
              (k, tag, p, h[p:p+32].hex()))
        break
    name, nend = r
    size = struct.unpack_from("<I", h, nend)[0]
    after = h[nend + 4:nend + 4 + 28]
    print("  [%d] @%d tag=%d name=%r size=%d after_size_28B=%s" %
          (k, p, tag, name, size, after.hex()))
    # locate data start: font = size bytes AFTER 24B meta; image = size incl 4B pad
    # try both interpretations, report which magic matches
    fnt = h[nend + 4 + 24: nend + 4 + 24 + 4]
    img = h[nend + 4 + 4: nend + 4 + 8]
    print("       font-interp data[0:4]=%s  img-interp data[0:4]=%s" %
          (fnt.hex(), img.hex()))
    if name.lower().endswith((".ttf", ".otf")):
        p = nend + 4 + 24 + size
    else:
        p = nend + 4 + size
        # image blobs end AE 42 60 82 + u32 flag
        tailflag = struct.unpack_from("<I", h, p)[0]
        print("       png-end@%d last4=%s tailflag=%d" %
              (p, h[p-4:p].hex(), tailflag))
        p += 4
print("tail after last asset @%d: %s" % (p, h[p:p+40].hex()))
print("header last 40B: %s" % h[-40:].hex())
