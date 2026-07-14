#!/usr/bin/env python3
"""rd_parse.py - hex/structure explorer for RealDash .rd binary dashboards."""
import struct
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\danie\Downloads\st185_dash.rd"
data = open(PATH, "rb").read()
print("size", len(data))


def hexdump(buf, start, length, label=""):
    print("--- %s @ 0x%X ---" % (label, start))
    for off in range(start, min(start + length, len(buf)), 16):
        chunk = buf[off:off + 16]
        hexs = " ".join("%02X" % b for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print("%06X  %-48s  %s" % (off, hexs, asc))


if len(sys.argv) > 3 and sys.argv[2] == "dump":
    start = int(sys.argv[3], 0)
    length = int(sys.argv[4], 0) if len(sys.argv) > 4 else 256
    hexdump(data, start, length)
    sys.exit(0)

# Find all length-prefixed UTF-16LE strings: guess prefix is int32 char count
# Scan: for each offset, read int32 n (1..64), check next n*2 bytes decode as UTF-16LE printable
found = []
i = 0
while i < len(data) - 4:
    n = struct.unpack_from("<I", data, i)[0]
    if 1 <= n <= 64:
        raw = data[i + 4:i + 4 + n * 2]
        if len(raw) == n * 2:
            try:
                s = raw.decode("utf-16-le")
                if all(32 <= ord(c) < 0x2600 for c in s) and any(c.isalnum() for c in s):
                    found.append((i, n, s))
                    i = i + 4 + n * 2
                    continue
            except Exception:
                pass
    i += 1

for off, n, s in found:
    print("0x%06X len=%2d  %r" % (off, n, s))
