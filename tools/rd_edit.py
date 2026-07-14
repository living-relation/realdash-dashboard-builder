#!/usr/bin/env python3
"""rd_edit.py - direct binary editor for st185_dash.rd (RealDash 1.92 text-gauge dash).

usage: rd_edit.py <src> <dst> <phase a|b>
  phase a: fix existing gauges only (title/stray removal, fonts, colors, labels)
  phase b: phase a + cloned decor gauges (strip bg, tile borders/gradients/rails)

Structure (reverse engineered from st185_dash.rd, RealDash 1.92 / dash v2.4.1):
  header (0..first marker):
    u32 canvas w @0x34 (1920), u32 canvas h @0x38 (1000)
    u32 ARGB canvas bg @0x8A
    u32 gauge count @0xAA
  record: marker 02 00 BD 0C, lpUTF16 name ('Text Gauge N')
    rect 4f x1,y1,x2,y2 normalized @nameEnd+0x10
    bg color u32 ARGB @nameEnd+0x5C
    strs '$#V2#$', 'defaultdashfont', main text
    text color u32 @textEnd+0x04
    font size f32 @textEnd+0x28  (em px = fs/1000 * 480 in design space)
    3 state text strs @textEnd+0x78
    color arrays after u32 0x01020304: +12 -> arr0[6], then (1,0,arr[6]) x3
      arr0=bg per state (slots 1-3 inactive, 4-6 active), arr2=text color
  footer: last 46 bytes (u32 1, lpstr 'default_set1.ns', 8 zero bytes)
  paint order = record order (first record at bottom).
"""
import struct
import sys

SRC = sys.argv[1]
DST = sys.argv[2]
PHASE = sys.argv[3] if len(sys.argv) > 3 else "b"

data = open(SRC, "rb").read()
MARK = b"\x02\x00\xBD\x0C"
FOOTER = data[-46:]
body = data[:-46]


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

assert len(name_offs) == 46, "expected 46 records, got %d" % len(name_offs)
assert struct.unpack_from("<I", FOOTER, 4)[0] == 15, "footer misaligned"
header = bytearray(body[:name_offs[0]])
records = []
for k in range(len(name_offs)):
    stop = name_offs[k + 1] if k + 1 < len(name_offs) else len(body)
    records.append(bytes(body[name_offs[k]:stop]))


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

    def arr_offsets(self):
        """4 color groups, each: u32 1, u32 useStatesFlag, 6 x u32 ARGB.
        First group is preceded by u32 0x01020304 marker."""
        b = self.b
        k = self.text_end
        while k < len(b) - 3:
            if struct.unpack_from("<I", b, k)[0] == 0x01020304:
                break
            k += 1
        else:
            raise RuntimeError("array marker not found in %s" % self.name)
        offs = []
        k += 4
        for _ in range(4):
            a, flag = struct.unpack_from("<2I", b, k)
            assert a == 1 and flag in (0, 1), "array separator broken in %s" % self.name
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

    def rename(self, newname):
        b = self.b
        self.b = bytearray(b[:4]) + pack_str(newname) + b[self.nend:]
        self.parse()


gs = [G(r) for r in records]
by_name = {g.name: g for g in gs}

# palette (realdash-simulation-REFERENCE.html)
PANEL = 0xFF243243
PANEL_HI = 0xFF2C3C50
PANEL_MID = 0xFF283A4A
EDGE = 0xFF3C5066
STRIP_TOP = 0xFF26384C
STRIP_BOT = 0xFF1D2B3A
PILL_BG = 0xFF1B2836
PILL_TXT = 0xFF647A92
BLUE = 0xFF34A8FF
AMBER = 0xFFFFC233
RED = 0xFFFF4D57
DIM = 0xFF9FB1C6
TEXT = 0xFFF3F8FF
LIT_TXT = 0xFFEAF4FF
AMBER_TXT = 0xFF211900
WHITE = 0xFFFFFFFF
CHROME = 0x96C3CCD8
TRANSP = 0x00000000

# NOTE: RealDash auto-fits text em-size to the gauge rect HEIGHT and ignores
# the stored font-size float (verified by measurement). Font size is therefore
# controlled by the rect. Text wider than the rect CLIPS (no shrink).
def fs_for(h):
    return h / 480.0 * 1000.0  # keep stored fs consistent with editor


# ---------- canvas background #1A2430 ----------
struct.pack_into("<I", header, 0x8A, 0xFF1A2430)

# ---------- pills: compact chips, title removed -> left group from x=14 ----
# h=18 -> ~18px text (sim: 12px text in 30px pill; text gauge = box+text)
pill_geo = {
    "Text Gauge 3": ("FLAT", 14, 18, 54, 18, BLUE, LIT_TXT),
    "Text Gauge 4": ("FAN", 74, 18, 46, 18, BLUE, LIT_TXT),
    "Text Gauge 6": ("LOFUEL", 126, 18, 76, 18, AMBER, AMBER_TXT),
    "Text Gauge 5": ("SBFLT", 208, 18, 66, 18, AMBER, AMBER_TXT),
    "Text Gauge 7": ("COOLANT P", 604, 18, 108, 18, RED, WHITE),
    "Text Gauge 8": ("OIL P 2", 718, 18, 78, 18, RED, WHITE),
}
for nm, (txt, x, y, w, h, active_bg, active_tc) in pill_geo.items():
    g = by_name[nm]
    g.set_rect_px(x, y, w, h)
    g.set_fsize(fs_for(h))
    g.set_bg_states(PILL_BG, active_bg)
    g.set_tc_states(PILL_TXT, active_tc)

# ---------- tile panels: blank the ghost '-' glyphs ----------
panel_names = ["Text Gauge %d" % n for n in range(9, 22)]
for nm in panel_names:
    g = by_name[nm]
    g.set_texts("")
    g.set_tcolor(PANEL)
    g.set_arr(2, [PANEL] * 6)

tiles = {}
for nm in panel_names:
    x, y, w, h = by_name[nm].get_rect_px()
    tiles[nm] = (round(x, 1), round(y, 1), round(w, 1), round(h, 1))


def owner_tile(gx, gy):
    best, bd = None, 1e9
    for nm, (x, y, w, h) in tiles.items():
        d = abs(gx - x) + abs(gy - y)
        if d < bd:
            best, bd = (x, y, w, h), d
    return best


# ---------- labels: h=12 (~ sim 10.5px), snapped to owner tile ----------
label_names = ["Text Gauge %d" % n for n in range(22, 34)]
for nm in label_names:
    g = by_name[nm]
    gx, gy, gw, gh = g.get_rect_px()
    tx, ty, tw, th = owner_tile(gx, gy)
    g.set_rect_px(tx + 10, ty + 7, tw - 20, 12)
    g.set_fsize(fs_for(12))
    g.set_bg_states(TRANSP, TRANSP)
    g.set_tc_states(DIM, DIM)

by_name["Text Gauge 22"].set_texts("BOOST MAP")  # R1C1 was mislabeled 'TC'

# ---------- values: h=38 (~ sim 35px), centered-low in tile ----------
# color arrays untouched: gauges 38/42 already carry red alarm text states
value_names = ["Text Gauge %d" % n for n in range(34, 45)]
for nm in value_names:
    g = by_name[nm]
    gx, gy, gw, gh = g.get_rect_px()
    tx, ty, tw, th = owner_tile(gx, gy)
    g.set_rect_px(tx + 10, ty + 32, tw - 20, 38)
    g.set_fsize(fs_for(38))

for nm in ("Text Gauge 45", "Text Gauge 46"):  # CRUISE / A-C enum values
    g = by_name[nm]
    gx, gy, gw, gh = g.get_rect_px()
    tx, ty, tw, th = owner_tile(gx, gy)
    g.set_rect_px(tx + 10, ty + 34, tw - 20, 34)
    g.set_fsize(fs_for(34))

by_name["Text Gauge 35"].set_texts("0.0")   # states were 'BOOST MABOOST MAP'
by_name["Text Gauge 36"].set_texts("0.0")   # states were 'ST185 / DASH'


def clone_panel(name, x, y, w, h, bg):
    g = G(bytes(by_name["Text Gauge 9"].b))
    g.rename(name)
    g.set_rect_px(x, y, w, h)
    g.set_bg_states(bg, bg)
    g.set_tcolor(bg)
    g.set_arr(2, [bg] * 6)
    return g


def clone_label(name, x, y, w, h, text):
    g = G(bytes(by_name["Text Gauge 23"].b))
    g.rename(name)
    g.set_rect_px(x, y, w, h)
    g.set_texts(text)
    return g


strip, borders, bands1, bands2, rails, accents = [], [], [], [], [], []
tc_label = None
if PHASE == "b":
    strip = [
        clone_panel("Text Gauge 60", 0, 0, 800, 28, STRIP_TOP),
        clone_panel("Text Gauge 61", 0, 28, 800, 26, STRIP_BOT),
        clone_panel("Text Gauge 62", 0, 53, 800, 1.6, EDGE),
    ]
    tlist = [tiles[nm] for nm in panel_names]
    for i, (x, y, w, h) in enumerate(tlist):
        borders.append(clone_panel("Text Gauge %d" % (70 + i), x - 1.5, y - 1.5, w + 3, h + 3, EDGE))
        bands1.append(clone_panel("Text Gauge %d" % (90 + i), x, y, w, h * 0.42, PANEL_HI))
        bands2.append(clone_panel("Text Gauge %d" % (110 + i), x, y + h * 0.42, w, h * 0.22, PANEL_MID))
        rails.append(clone_panel("Text Gauge %d" % (130 + i), x, y, w, 2.2, CHROME))
        # left accent stripe: blue on active drive tiles (R1 c1-c3), chrome else
        acc = BLUE if i in (0, 1, 2) else 0xC8C3CCD8
        accents.append(clone_panel("Text Gauge %d" % (160 + i), x, y + 2, 3, h - 2, acc))
        # bottom mini-bar track (sim .tbar) on the bar-carrying tiles
        if i in (1, 2, 4, 5, 6, 7, 8, 9):
            accents.append(clone_panel("Text Gauge %d" % (180 + i), x + 11, y + h - 14, w - 22, 5, 0xFF15212E))
    # add missing TC label on R1C2 (tile index 1)
    tx, ty, tw, th = tlist[1]
    tc_label = clone_label("Text Gauge 150", tx + 10, ty + 7, tw - 20, 12, "TC")
    tc_label.set_fsize(fs_for(12))

# ---------- assemble (paint order: first = bottom) ----------
# 'Text Gauge 1' (title) and 'Text Gauge 2' (stray box) intentionally dropped.
out_records = []
out_records += [g.b for g in strip]
out_records += [by_name[n].b for n in pill_geo]
out_records += [g.b for g in borders]
out_records += [by_name[n].b for n in panel_names]
out_records += [g.b for g in bands1]
out_records += [g.b for g in bands2]
out_records += [g.b for g in rails]
out_records += [g.b for g in accents]
out_records += [by_name[n].b for n in label_names]
if tc_label is not None:
    out_records.append(tc_label.b)
out_records += [by_name[n].b for n in value_names]
out_records += [by_name["Text Gauge 45"].b, by_name["Text Gauge 46"].b]

struct.pack_into("<I", header, 0xAA, len(out_records))
out = bytes(header) + b"".join(bytes(r) for r in out_records) + FOOTER
open(DST, "wb").write(out)
print("phase %s -> %s: %d bytes, %d gauges" % (PHASE, DST, len(out), len(out_records)))
