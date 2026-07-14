#!/usr/bin/env python3
"""rd_gauge.py - parse RealDash .rd text gauge blocks.

Walks the file, segmenting on 'Text Gauge N' name strings, and inside each
block interprets the byte stream as floats / u32 colors / UTF-16 strings to
locate geometry, font size and color fields.
"""
import struct
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\danie\Downloads\st185_dash.rd"
data = open(PATH, "rb").read()


def read_str(buf, off):
    """Try to read a length-prefixed UTF-16LE string at off. Return (s, end) or None."""
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


# find gauge name offsets
names = []
i = 0
while i < len(data) - 4:
    r = read_str(data, i)
    if r:
        s, end = r
        if s.startswith("Text Gauge "):
            names.append((i, s))
            i = end
            continue
    i += 1

print("gauges:", len(names))

mode = sys.argv[2] if len(sys.argv) > 2 else "geom"

if mode == "walk":
    # detailed field walk of one gauge
    idx = int(sys.argv[3])
    start = names[idx][0]
    stop = names[idx + 1][0] if idx + 1 < len(names) else len(data)
    print("=== %s block 0x%X..0x%X (%d bytes)" % (names[idx][1], start, stop, stop - start))
    off = start
    r = read_str(data, off)
    print("0x%06X name %r" % (off, r[0]))
    off = r[1]
    # dump remainder as mixed: try string first, else print float+u32 per 4 bytes
    while off < stop - 3:
        r = read_str(data, off)
        if r and r[0] and len(r[0]) >= 2:
            print("0x%06X (+%04X) STR %r" % (off, off - start, r[0]))
            off = r[1]
            continue
        u = struct.unpack_from("<I", data, off)[0]
        f = struct.unpack_from("<f", data, off)[0]
        tag = ""
        if 0xFF000000 <= u:
            tag = "ARGB(%02X,%02X,%02X)" % ((u >> 16) & 255, (u >> 8) & 255, u & 255)
        fs = "%.6g" % f
        if 1e-6 < abs(f) < 1e6:
            tag += " f=%s" % fs
        print("0x%06X (+%04X) %08X %s" % (off, off - start, u, tag))
        off += 4
else:
    # geometry summary: first 8 floats after name are candidate x,y,w,h etc.
    for k, (noff, name) in enumerate(names):
        r = read_str(data, noff)
        off = r[1]
        vals = struct.unpack_from("<12f", data, off)
        # find the first text string in the block after the font name
        stop = names[k + 1][0] if k + 1 < len(names) else len(data)
        texts = []
        j = off
        while j < stop - 3:
            rr = read_str(data, j)
            if rr and rr[0] and rr[0] not in ("$#V2#$", "defaultdashfont"):
                texts.append(rr[0])
                j = rr[1]
                continue
            j += 1
        print("%2d %-14s @0x%06X floats: %s | %r" % (
            k, name, noff,
            " ".join("%.4f" % v if abs(v) < 100000 else "big" for v in vals[:10]),
            texts[:2]))
