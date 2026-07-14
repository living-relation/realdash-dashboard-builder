#!/usr/bin/env python3
"""probe_parse.py - explore the probe .rd: find all records incl. new gauge
types, print structure of the non-text types."""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib import read_str, MARK

PATH = r"C:\Users\danie\Downloads\probe_base.rd"
data = open(PATH, "rb").read()
print("file size", len(data))

# scan every marker occurrence and try to read a name
recs = []
i = 0
while i < len(data) - 4:
    if data[i:i + 4] == MARK:
        r = read_str(data, i + 4)
        if r and len(r[0]) >= 3 and any(c.isalpha() for c in r[0]):
            recs.append((i, r[0]))
            i = r[1]
            continue
    i += 1

print("records found:", len(recs))
for off, name in recs:
    if not name.startswith("Text Gauge"):
        print("  @%d %r" % (off, name))
print("first:", recs[0], "last:", recs[-1])

# structure dump for new types: from record start to +0x120 as mixed view
for off, name in recs:
    if name.startswith("Text Gauge"):
        continue
    end = None
    for o2, n2 in recs:
        if o2 > off:
            end = o2
            break
    if end is None:
        end = len(data) - 46
    blob = data[off:end]
    print("=== %r len=%d" % (name, len(blob)))
    # find all embedded strings
    j = 4
    strs = []
    while j < len(blob) - 4:
        r = read_str(blob, j)
        if r and len(r[0]) >= 3:
            strs.append((j, r[0][:40]))
            j = r[1]
        else:
            j += 1
    for so, s in strs[:12]:
        print("   str @+%d: %r" % (so, s))
    # find 0x01020304 markers
    k = 4
    marks = []
    while k < len(blob) - 3:
        if struct.unpack_from("<I", blob, k)[0] == 0x01020304:
            marks.append(k)
        k += 1
    print("   colorarr markers:", marks[:8])
