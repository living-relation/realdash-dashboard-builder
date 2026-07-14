#!/usr/bin/env python3
"""rd_lib2.py - generalized RealDash 1.92 .rd binary library.

Extends rd_lib to handle ALL gauge record types and asset-carrying headers:
  record marker: <u16 type> BD 0C   (type: 1=Needle 2=Text 3=Bar 5=Image
                                     8=Arc 12=Graph)
  header: everything before the first record. Gauge count = LAST u32 of the
          header; canvas bg ARGB = header_end-36. Image assets (lpstr name +
          u32 size + PNG blob) live inside the header and are preserved
          verbatim.
  record skeleton (all types):
    lpstr name; [f2 0] pad; optional lpstr image; u32 0x11 rect anchor;
    rect1 4f; rect2 4f (normalized to 800x480); [uv 4f for image types
    inside rect2 slot? no - uv at anchor+36..52]; ... '$#V2#$'; lpstr font
    (may be empty); lpstr text; text color @text_end+4; fsize f32
    @text_end+0x28; 3 state lpstrs @text_end+0x78; range block after +4:
    u32 0x10, critBelow, critAbove, warnBelow, warnAbove, min, max, cur;
    binding hash u32 @arrmarker-12; decimals u32 @arrmarker-8; color groups
    after u32 0x01020304: n x (u32 1, u32 flag, 6 x ARGB).
  type extras (located by byte-pattern search inside the record):
    Needle/Arc: two consecutive f32 angles (start_rad, sweep_rad) right
      after an "f32 x, 0, 0.03, 0.05" block following the indicator image
      strings; autoscale block f32[0.15,0.07] then [1,0,0,u32 maxdig,
      u32 segments, 0, u32 midseg].
    Bar/Arc/Graph: default level colors FF46FF64/FFFFAA46/FFFF4664
      (green/amber/red) - replace to restyle fills.
"""
import struct

FOOTER_LEN = 46
TYPE_NAMES = {1: "needle", 2: "text", 3: "bar", 5: "image", 8: "arc", 12: "graph"}


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


def pack_str(s):
    return struct.pack("<I", len(s)) + s.encode("utf-16-le")


class G2:
    def __init__(self, blob):
        self.b = bytearray(blob)
        self.parse()

    def parse(self):
        b = self.b
        self.type = struct.unpack_from("<H", b, 0)[0]
        self.name, self.nend = read_str(b, 4)
        # rect anchor: first u32 == 0x11 after name end
        j = self.nend
        self.rect_anchor = None
        while j < min(len(b), self.nend + 0x80):
            if struct.unpack_from("<I", b, j)[0] == 0x11:
                self.rect_anchor = j
                break
            j += 1
        assert self.rect_anchor is not None, "rect anchor missing in %s" % self.name
        # find '$#V2#$', then font lpstr, then text lpstr
        j = self.nend
        v2_end = None
        while j < len(b) - 3:
            r = read_str(b, j)
            if r and r[0] == "$#V2#$":
                v2_end = r[1]
                break
            j += 1
        assert v2_end, "V2 marker missing in %s" % self.name
        rf = read_str(b, v2_end)
        self.font, font_end = rf
        rt = read_str(b, font_end)
        self.text_off = font_end
        self.text, self.text_end = rt

    # ---------- geometry ----------
    def get_rect_px(self):
        x1, y1, x2, y2 = struct.unpack_from("<4f", self.b, self.rect_anchor + 4)
        return x1 * 800, y1 * 480, (x2 - x1) * 800, (y2 - y1) * 480

    def set_rect_px(self, x, y, w, h):
        vals = (x / 800.0, y / 480.0, (x + w) / 800.0, (y + h) / 480.0)
        struct.pack_into("<4f", self.b, self.rect_anchor + 4, *vals)
        if self.type != 5:  # image types keep uv data in the rect2 slot
            struct.pack_into("<4f", self.b, self.rect_anchor + 20, *vals)

    # ---------- text ----------
    def set_tcolor(self, argb):
        struct.pack_into("<I", self.b, self.text_end + 4, argb)

    def set_fsize_for_h(self, h_px):
        struct.pack_into("<f", self.b, self.text_end + 0x28, h_px / 480.0 * 1000.0)

    def set_font(self, fontname):
        """Set the per-gauge font lp-string (right after $#V2#$).
        Value = embedded font asset FILENAME (e.g. 'RaceHead.ttf') or
        'defaultdashfont'. Re-splices the record (offsets shift; re-parses)."""
        b = self.b
        j = self.nend
        v2_end = None
        while j < len(b) - 3:
            r = read_str(b, j)
            if r and r[0] == "$#V2#$":
                v2_end = r[1]
                break
            j += 1
        assert v2_end, "V2 marker missing in %s" % self.name
        r = read_str(b, v2_end)
        self.b = b[:v2_end] + pack_str(fontname) + b[r[1]:]
        self.parse()

    def set_level_fonts(self, fontname):
        """Set the 3 per-level font lpstrs (normal/warn/crit) that the
        RENDERER actually uses. They live after the 4 color groups:
        arr_marker+4 + 4*32 + 12 fixed bytes, then 3 consecutive lpstrs.
        Empty = default font. The GUI font picker writes all three (plus the
        post-$#V2#$ string, which alone does NOT change rendering).
        Text gauges (type 2) only."""
        am = self._arr_marker()
        base = am + 4 + 4 * 32 + 12
        j = base
        for _ in range(3):
            r = read_str(self.b, j)
            assert r is not None, "level font slot parse fail in %s" % self.name
            j = r[1]
        self.b = (self.b[:base] + pack_str(fontname) * 3 + self.b[j:])
        self.parse()

    def _math_off(self):
        """Gauge-math lpstr slot at text_end+0x74 (empty u32 0 when unset).
        When set (e.g. '=V/1000') the 3 state strings shift right by its
        length, so ALWAYS walk strings from here, never from +0x78."""
        return self.text_end + 0x74

    def get_gauge_math(self):
        r = read_str(self.b, self._math_off())
        assert r is not None, "gauge math slot parse fail in %s" % self.name
        return r[0]

    def set_gauge_math(self, expr):
        off = self._math_off()
        r = read_str(self.b, off)
        assert r is not None, "gauge math slot parse fail in %s" % self.name
        self.b = self.b[:off] + pack_str(expr) + self.b[r[1]:]
        self.parse()

    def _states_off(self):
        """Offset of the first of the 3 state strings (after gauge math)."""
        r = read_str(self.b, self._math_off())
        assert r is not None, "gauge math slot parse fail in %s" % self.name
        return r[1]

    def set_texts(self, main, states=None):
        b = self.b
        st_off = self._states_off()
        offs = []
        j = st_off
        for _ in range(3):
            r = read_str(b, j)
            assert r is not None, "state string parse fail in %s" % self.name
            offs.append((j, r[1]))
            j = r[1]
        if states is None:
            states = [main, main, main]
        new = bytearray()
        new += b[:self.text_off]
        new += pack_str(main)
        new += b[self.text_end:st_off]
        for s in states:
            new += pack_str(s)
        new += b[offs[2][1]:]
        self.b = new
        self.parse()

    # ---------- ranges / binding ----------
    def _range_off(self):
        j = self._states_off()
        for _ in range(3):
            j = read_str(self.b, j)[1]
        off = j + 4
        assert struct.unpack_from("<I", self.b, off)[0] == 0x10, \
            "range anchor bad %s" % self.name
        return off

    def set_ranges(self, vmin, vmax, warn=None, crit=None,
                   warn_below=None, crit_below=None, cur=None):
        off = self._range_off()
        if crit_below is not None:
            struct.pack_into("<f", self.b, off + 4, crit_below)
        if crit is not None:
            struct.pack_into("<f", self.b, off + 8, crit)
        if warn_below is not None:
            struct.pack_into("<f", self.b, off + 12, warn_below)
        if warn is not None:
            struct.pack_into("<f", self.b, off + 16, warn)
        struct.pack_into("<f", self.b, off + 20, vmin)
        struct.pack_into("<f", self.b, off + 24, vmax)
        if cur is not None:
            struct.pack_into("<f", self.b, off + 28, cur)

    def _arr_marker(self):
        b = self.b
        k = self.text_end
        while k < len(b) - 3:
            if struct.unpack_from("<I", b, k)[0] == 0x01020304:
                return k
            k += 1
        raise RuntimeError("array marker not found in %s" % self.name)

    def set_hash(self, h):
        struct.pack_into("<I", self.b, self._arr_marker() - 12, h)

    def get_hash(self):
        return struct.unpack_from("<I", self.b, self._arr_marker() - 12)[0]

    def set_decimals(self, n):
        struct.pack_into("<I", self.b, self._arr_marker() - 8, n)

    # ---------- color groups (0x01020304 block) ----------
    def arr_offsets(self, count=4):
        k = self._arr_marker() + 4
        offs = []
        for _ in range(count):
            a, flag = struct.unpack_from("<2I", self.b, k)
            if a != 1 or flag not in (0, 1):
                break
            offs.append(k + 8)
            k += 32
        return offs

    def set_arr(self, idx, colors6, flag=None):
        off = self.arr_offsets()[idx]
        if flag is not None:
            struct.pack_into("<I", self.b, off - 4, flag)
        for n, c in enumerate(colors6):
            struct.pack_into("<I", self.b, off + n * 4, c)

    def set_bg_states(self, normal, active):
        if self.type == 2:
            struct.pack_into("<I", self.b, self.nend + 0x5C, normal)
        self.set_arr(0, [normal] * 3 + [active] * 3,
                     flag=1 if normal != active else 0)

    def set_tc_states(self, normal, active):
        self.set_tcolor(normal)
        self.set_arr(2, [normal] * 3 + [active] * 3,
                     flag=1 if normal != active else 0)

    # ---------- pattern helpers for type extras ----------
    def find_u32_runs(self, value):
        out = []
        for k in range(0, len(self.b) - 3, 1):
            if struct.unpack_from("<I", self.b, k)[0] == value:
                out.append(k)
        return out

    def replace_level_colors(self, normal, warn, crit):
        """Replace ALL default level triads FF46FF64/FFFFAA46/FFFF4664."""
        n = 0
        for k in range(0, len(self.b) - 3):
            v = struct.unpack_from("<I", self.b, k)[0]
            if v == 0xFF46FF64:
                struct.pack_into("<I", self.b, k, normal); n += 1
            elif v == 0xFFFFAA46:
                struct.pack_into("<I", self.b, k, warn); n += 1
            elif v == 0xFFFF4664:
                struct.pack_into("<I", self.b, k, crit); n += 1
        return n

    def _angles_off(self):
        """Two consecutive f32 angles: search known defaults."""
        for k in range(0, len(self.b) - 7):
            a, s = struct.unpack_from("<2f", self.b, k)
            if 3.5 < a < 4.5 and 4.4 < s < 5.2:
                return k
        raise RuntimeError("angles not found in %s" % self.name)

    def set_angles(self, start_deg, sweep_deg):
        import math
        struct.pack_into("<2f", self.b, self._angles_off(),
                         math.radians(start_deg), math.radians(sweep_deg))

    def _autoscale_off(self):
        """Block: f[?, 0.75, 1, 1, 1, 0.15, 0.07, 1] then 0 0 u32 maxdig,
        u32 segments, 0, u32 midseg. Returns offset of first float."""
        for k in range(0, len(self.b) - 11):
            v1, v2, v3 = struct.unpack_from("<3f", self.b, k)
            if abs(v1 - 0.75) < 1e-5 and abs(v2 - 1.0) < 1e-5 and abs(v3 - 1.0) < 1e-5:
                return k - 4
        raise RuntimeError("autoscale not found in %s" % self.name)

    def set_autoscale(self, size_scale=None, segments=None,
                      maxdig=None, use_auto=None):
        """Field map verified by render experiments on Needle Gauge:
        off+0 size_scale f32, +44 segments u32,
        +52 MAX DIGITS u32 (labels truncate to this many chars: 1 turns
        '10'..'18' into '1' - keep >= widest label), +56 use_auto u32.
        WARNING: +40 (u32, default 3) is NOT midseg - writing 1 there makes
        the needle gauge vanish entirely. Leave it alone.
        WARNING: use_auto=False blanks needle gauges entirely (verified);
        it is safe on arc gauges (hides scale digits)."""
        off = self._autoscale_off()
        if size_scale is not None:
            struct.pack_into("<f", self.b, off, size_scale)
        if segments is not None:
            struct.pack_into("<I", self.b, off + 44, segments)
        if maxdig is not None:
            struct.pack_into("<I", self.b, off + 52, maxdig)
        if use_auto is not None:
            struct.pack_into("<I", self.b, off + 56, 1 if use_auto else 0)

    def rename(self, newname):
        b = self.b
        self.b = bytearray(b[:4]) + pack_str(newname) + b[self.nend:]
        self.parse()

    def clone(self, newname):
        g = G2(bytes(self.b))
        g.rename(newname)
        return g


class Dash2:
    def __init__(self, path):
        data = open(path, "rb").read()
        self.footer = data[-FOOTER_LEN:]
        body = data[:-FOOTER_LEN]
        recs = []
        i = 0
        while i < len(body) - 4:
            if body[i + 2:i + 4] == b"\xBD\x0C":
                t = struct.unpack_from("<H", body, i)[0]
                if t in TYPE_NAMES:
                    r = read_str(body, i + 4)
                    if r and len(r[0]) >= 3 and all(32 <= ord(c) < 0x3000 for c in r[0]):
                        recs.append(i)
                        i = r[1]
                        continue
            i += 1
        self.header = bytearray(body[:recs[0]])
        self.gauges = []
        for k in range(len(recs)):
            stop = recs[k + 1] if k + 1 < len(recs) else len(body)
            self.gauges.append(G2(body[recs[k]:stop]))

    def by_name(self):
        return {g.name: g for g in self.gauges}

    def set_canvas_bg(self, argb):
        struct.pack_into("<I", self.header, len(self.header) - 36, argb)

    def save(self, path, order=None):
        recs = order if order is not None else self.gauges
        struct.pack_into("<I", self.header, len(self.header) - 4, len(recs))
        out = bytes(self.header) + b"".join(bytes(g.b) for g in recs) + self.footer
        open(path, "wb").write(out)
        return len(out), len(recs)
