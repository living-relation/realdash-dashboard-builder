#!/usr/bin/env python3
"""cf_diff_bind.py - compare a GUI-bound live-updating text gauge (probe_gm
Text Gauge 40) with a binarily-bound one (current v5 turbo) field by field."""
import struct
import sys

sys.path.insert(0, r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\tools")
from rd_lib2 import Dash2, read_str

ga = Dash2(r"C:\Users\danie\Downloads\probe_gm.rd").by_name()["Text Gauge 40"]
d5 = Dash2(r"C:\Users\danie\Downloads\st185_dash_v5.rd")
# find the turbo gauge: hash 413F90BA
gb = next(g for g in d5.gauges if g.type == 2 and g.get_hash() == 0x413F90BA)
print("A=probe_gm TG40 len=%d   B=v5 turbo %s len=%d" %
      (len(ga.b), gb.name, len(gb.b)))

def fields(g):
    out = {}
    b = bytes(g.b)
    out["nend"] = g.nend
    # region between name end and rect anchor
    out["head"] = b[g.nend:g.rect_anchor].hex()
    am = g._arr_marker()
    out["pre_arr_32"] = b[am - 32:am].hex()
    # after state strings: range block
    j = g._states_off()
    for _ in range(3):
        j = read_str(b, j)[1]
    out["range"] = struct.unpack_from("<8f", b, j + 8)
    out["between_range_arr"] = b[j + 40:am - 32].hex()
    # region between text color and math slot
    out["textmeta"] = b[g.text_end:g.text_end + 0x74].hex()
    return out

fa, fb = fields(ga), fields(gb)
for k in fa:
    if k == "range":
        print("range A:", ["%.6g" % v for v in fa[k]])
        print("range B:", ["%.6g" % v for v in fb[k]])
        continue
    va, vb = fa[k], fb[k]
    if va == vb:
        print("%s: IDENTICAL (%d bytes)" % (k, len(va) // 2 if isinstance(va, str) else 0))
    else:
        print("%s: DIFFERS" % k)
        if isinstance(va, str) and len(va) == len(vb):
            # show differing u32-aligned chunks
            for i in range(0, len(va), 8):
                if va[i:i+8] != vb[i:i+8]:
                    print("  +%3d: A=%s B=%s" % (i // 2, va[i:i+8], vb[i:i+8]))
        else:
            print("  lenA=%s lenB=%s" % (len(va), len(vb)))
            print("  A=%s" % va[:160])
            print("  B=%s" % vb[:160])
