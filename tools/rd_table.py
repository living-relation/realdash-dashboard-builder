#!/usr/bin/env python3
"""rd_table.py - structured field table for RealDash .rd text gauges.

Anchors per record (name = length-prefixed UTF-16LE 'Text Gauge N'):
  name_end+0x10 : 4 floats x1,y1,x2,y2 (normalized to canvas)
  name_end+0x58 : u32 colorA (white?)
  name_end+0x5C : u32 background color (ARGB)
  '$#V2#$' str, 'defaultdashfont' str, then first text string
  text_end+0x04 : u32 text color (ARGB)
  text_end+0x28 : float font size
  text_end+0x78 : 3 consecutive strings (state texts)
  first u32==0x01020304 after that: +12 -> 6 u32 color array 1,
     then u32 1, u32 0, 6 u32 array 2, ... (repeat while pattern holds)
"""
import struct
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\danie\Downloads\st185_dash.rd"
data = open(PATH, "rb").read()


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


def find_names(buf):
    names = []
    i = 0
    while i < len(buf) - 4:
        r = read_str(buf, i)
        if r and r[0].startswith("Text Gauge "):
            names.append((i, r[0], r[1]))
            i = r[1]
            continue
        i += 1
    return names


def parse_gauge(buf, noff, nend, stop):
    g = {"name_off": noff}
    g["rect_off"] = nend + 0x10
    g["rect"] = struct.unpack_from("<4f", buf, g["rect_off"])
    g["bg_off"] = nend + 0x5C
    g["bg"] = struct.unpack_from("<I", buf, g["bg_off"])[0]
    # find font marker then first text
    j = nend
    font_end = None
    while j < stop - 3:
        r = read_str(buf, j)
        if r and r[0] == "defaultdashfont":
            font_end = r[1]
            break
        j += 1
    g["text_off"] = font_end
    r = read_str(buf, font_end)
    g["text"], text_end = r
    g["text_end"] = text_end
    g["tcolor_off"] = text_end + 4
    g["tcolor"] = struct.unpack_from("<I", buf, g["tcolor_off"])[0]
    g["fsize_off"] = text_end + 0x28
    g["fsize"] = struct.unpack_from("<f", buf, g["fsize_off"])[0]
    g["st_off"] = text_end + 0x78
    sts = []
    j = g["st_off"]
    for _ in range(3):
        r = read_str(buf, j)
        if not r:
            sts.append(None)
            break
        sts.append(r[0])
        j = r[1]
    g["state_texts"] = sts
    g["st_end"] = j
    # color arrays
    arrays = []
    k = j
    while k < stop - 3:
        if struct.unpack_from("<I", buf, k)[0] == 0x01020304:
            k += 12
            first = struct.unpack_from("<6I", buf, k)
            arrays.append((k, first))
            k += 24
            # subsequent arrays: 1,0 then 6 colors
            while k + 32 <= stop:
                a, b = struct.unpack_from("<2I", buf, k)
                if a == 1 and b == 0:
                    cols = struct.unpack_from("<6I", buf, k + 8)
                    arrays.append((k + 8, cols))
                    k += 32
                else:
                    break
            break
        k += 4
    g["arrays"] = arrays
    return g


names = find_names(data)
gs = []
for idx, (noff, name, nend) in enumerate(names):
    stop = names[idx + 1][0] if idx + 1 < len(names) else len(data)
    g = parse_gauge(data, noff, nend, stop)
    g["name"] = name
    gs.append(g)

W, H = 800, 480
for i, g in enumerate(gs):
    x1, y1, x2, y2 = g["rect"]
    print("%2d %-14s px(%3.0f,%3.0f %3.0fx%3.0f) bg=%08X tc=%08X fs=%5.1f text=%-18r st=%r" % (
        i, g["name"], x1 * W, y1 * H, (x2 - x1) * W, (y2 - y1) * H,
        g["bg"], g["tcolor"], g["fsize"], g["text"][:18], g["state_texts"]))
    if len(sys.argv) > 2 and sys.argv[2] == "arrays":
        for off, cols in g["arrays"]:
            print("      arr@0x%06X %s" % (off, " ".join("%08X" % c for c in cols)))
