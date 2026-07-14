#!/usr/bin/env python3
"""Calibration 2: magenta disc over roundface on the CURRENT fixed v9
(rects 214x246.5) -> throwaway probe; measures the true rendered rect."""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rd_lib2 import Dash2, read_str

BUILD = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build"
FACE = BUILD + r"\r5_calib_face.png"
SRC = r"C:\Users\danie\Downloads\st185_dash_v9.rd"
OUT = r"C:\Users\danie\Downloads\r5_probe_aspect.rd"

d = Dash2(SRC)


def splice_asset(dash, name, png_path):
    h = bytes(dash.header)
    i = 0
    while i < len(h) - 8:
        r = read_str(h, i)
        if r and r[0] == name:
            size_off = r[1]
            old = struct.unpack_from("<I", h, size_off)[0]
            blob = b"\x00\x00\x00\x00" + open(png_path, "rb").read()
            dash.header = bytearray(
                h[:size_off] + struct.pack("<I", len(blob)) + blob
                + h[size_off + 4 + old:])
            return old, len(blob)
        i += 1
    raise KeyError(name)


print("face:", splice_asset(d, "roundface.png", FACE))
d.save(OUT)
print("saved", OUT)
