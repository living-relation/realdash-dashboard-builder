#!/usr/bin/env python3
"""rd_lib.py - shared library for direct binary editing of RealDash 1.92 .rd files.

File layout (reverse engineered from st185_dash.rd):
  header: canvas w/h u32 @0x34/0x38 (1920x1000 units), canvas bg ARGB @0x8A,
          gauge count u32 @0xAA
  record: marker 02 00 BD 0C + lpUTF16 name
          rect 4f x1,y1,x2,y2 normalized @nameEnd+0x10
          bg ARGB u32 @nameEnd+0x5C
          strs '$#V2#$', 'defaultdashfont', main text
          text color u32 @textEnd+0x04
          stored font size f32 @textEnd+0x28 (rendering uses rect height!)
          3 state text strs @textEnd+0x78
          binding hash u32 @arrmarker-12 (FFFFFFFF = static/unbound)
          decimal places u32 @arrmarker-8
          color groups after u32 0x01020304 marker: 4 x (u32 1, u32 flag,
            6 x u32 ARGB); group0=background, group2=text color
            (slots 1-3 = normal, 4-6 = active/lit state)
  footer: 46 bytes (u32 1, lpstr 'default_set1.ns', 8 zero bytes)
  paint order = record order (first record at bottom).
"""
import struct

MARK = b"\x02\x00\xBD\x0C"
FOOTER_LEN = 46


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


class G:
    def __init__(self, blob):
        self.b = bytearray(blob)
        self.parse()

    def parse(self):
        b = self.b
        r = read_str(b, 4)
        self.name, self.nend = r
        self.rect_off = self.nend + 0x10
        j = self.nend
        font_end = None
        while j < len(b) - 3:
            rr = read_str(b, j)
            if rr and rr[0] == "defaultdashfont":
                font_end = rr[1]
                break
            j += 1
        self.text_off = font_end
        self.text, self.text_end = read_str(b, font_end)

    def get_rect_px(self):
        x1, y1, x2, y2 = struct.unpack_from("<4f", self.b, self.rect_off)
        return x1 * 800, y1 * 480, (x2 - x1) * 800, (y2 - y1) * 480

    def set_rect_px(self, x, y, w, h):
        struct.pack_into("<4f", self.b, self.rect_off,
                         x / 800.0, y / 480.0, (x + w) / 800.0, (y + h) / 480.0)

    def set_bg(self, argb):
        struct.pack_into("<I", self.b, self.nend + 0x5C, argb)

    def set_tcolor(self, argb):
        struct.pack_into("<I", self.b, self.text_end + 4, argb)

    def set_fsize(self, f):
        struct.pack_into("<f", self.b, self.text_end + 0x28, f)

    def set_fsize_for_h(self, h_px):
        self.set_fsize(h_px / 480.0 * 1000.0)

    def set_texts(self, main, states=None):
        b = self.b
        st_off = self.text_end + 0x78
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

    def _arr_marker(self):
        b = self.b
        k = self.text_end
        while k < len(b) - 3:
            if struct.unpack_from("<I", b, k)[0] == 0x01020304:
                return k
            k += 1
        raise RuntimeError("array marker not found in %s" % self.name)

    def arr_offsets(self):
        k = self._arr_marker() + 4
        offs = []
        for _ in range(4):
            a, flag = struct.unpack_from("<2I", self.b, k)
            assert a == 1 and flag in (0, 1), "array sep broken in %s" % self.name
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
        self.set_bg(normal)
        self.set_arr(0, [normal] * 3 + [active] * 3, flag=1 if normal != active else 0)

    def set_tc_states(self, normal, active):
        self.set_tcolor(normal)
        self.set_arr(2, [normal] * 3 + [active] * 3, flag=1 if normal != active else 0)

    def get_decimals(self):
        return struct.unpack_from("<I", self.b, self._arr_marker() - 8)[0]

    def set_decimals(self, n):
        struct.pack_into("<I", self.b, self._arr_marker() - 8, n)

    def get_hash(self):
        return struct.unpack_from("<I", self.b, self._arr_marker() - 12)[0]

    def rename(self, newname):
        b = self.b
        self.b = bytearray(b[:4]) + pack_str(newname) + b[self.nend:]
        self.parse()

    def clone(self, newname):
        g = G(bytes(self.b))
        g.rename(newname)
        return g


class Dash:
    def __init__(self, path):
        data = open(path, "rb").read()
        self.footer = data[-FOOTER_LEN:]
        assert struct.unpack_from("<I", self.footer, 4)[0] == 15, "footer misaligned"
        body = data[:-FOOTER_LEN]
        name_offs = []
        i = 0
        while i < len(body) - 4:
            if body[i:i + 4] == MARK:
                r = read_str(body, i + 4)
                if r and r[0].startswith("Text Gauge "):
                    name_offs.append(i)
                    i = r[1]
                    continue
            i += 1
        self.header = bytearray(body[:name_offs[0]])
        self.gauges = []
        for k in range(len(name_offs)):
            stop = name_offs[k + 1] if k + 1 < len(name_offs) else len(body)
            self.gauges.append(G(body[name_offs[k]:stop]))

    def by_name(self):
        return {g.name: g for g in self.gauges}

    def set_canvas_bg(self, argb):
        struct.pack_into("<I", self.header, 0x8A, argb)

    def save(self, path, order=None):
        """order: list of G in desired paint order; default keeps self.gauges."""
        recs = order if order is not None else self.gauges
        struct.pack_into("<I", self.header, 0xAA, len(recs))
        out = bytes(self.header) + b"".join(bytes(g.b) for g in recs) + self.footer
        open(path, "wb").write(out)
        return len(out), len(recs)
