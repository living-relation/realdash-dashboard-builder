#!/usr/bin/env python3
"""rd_fields.py - dump binding hash + decimals for every gauge record."""
import struct
import sys

PATH = sys.argv[1]
data = open(PATH, "rb").read()
MARK = b"\x02\x00\xBD\x0C"


def read_str(buf, off):
    if off + 4 > len(buf):
        return None
    n = struct.unpack_from("<I", buf, off)[0]
    if n > 256:
        return None
    end = off + 4 + n * 2
    if end > len(buf):
        return None
    try:
        s = buf[off + 4:end].decode("utf-16-le")
    except Exception:
        return None
    if n and not all(9 <= ord(c) < 0x3000 for c in s):
        return None
    return s, end


offs = []
i = 0
while i < len(data) - 4:
    if data[i:i + 4] == MARK:
        r = read_str(data, i + 4)
        if r and r[0].startswith("Text Gauge "):
            offs.append((i, r[0], r[1]))
            i = r[1]
        else:
            i += 1
    else:
        i += 1

for k, (o, nm, ne) in enumerate(offs):
    stop = offs[k + 1][0] if k + 1 < len(offs) else len(data)
    rec = data[o:stop]
    # main text
    j = 0
    text = ""
    while j < len(rec) - 3:
        r = read_str(rec, j)
        if r and r[0] == "defaultdashfont":
            t = read_str(rec, r[1])
            text = t[0]
            j = t[1]
            break
        j += 1
    # marker
    m = j
    while m < len(rec) - 3:
        if struct.unpack_from("<I", rec, m)[0] == 0x01020304:
            break
        m += 1
    hash_v = struct.unpack_from("<I", rec, m - 12)[0]
    dec = struct.unpack_from("<I", rec, m - 8)[0]
    pre = struct.unpack_from("<I", rec, m - 16)[0]
    print("%-15s text=%-12r pre=%08X hash=%08X dec=%d" % (nm, text[:12], pre, hash_v, dec))
