#!/usr/bin/env python3
"""r4_common.py - shared helpers for round-4 stage A1 edits."""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rd_lib2 import Dash2, G2, read_str, pack_str  # noqa: E402

TRANSP = 0x00000000
UNBOUND = 0xFFFFFFFF

H = {
    "throttle": 0xA5AA7D05, "boostmap": 0xE1F72794, "tc": 0x4E28D27A,
    "tci": 0x5A59FBBD, "lambda": 0x9ED3572B, "iat": 0x978E3E78,
    "coolp": 0xDD266D22, "turbo": 0x413F90BA, "load": 0x9007B539,
    "fuelt": 0x80D7FC73, "eth": 0xBDB0E378, "trig": 0x04B07E8E,
    "cruise": 0x18ECF9C1, "ac": 0xE975C645, "flat": 0x6B5F9216,
    "fan": 0xC44AB478,
}


def set_static(g, on):
    """states_end+76: bit 0x20000000 = Static Text (state strings render)."""
    j = g._states_off()
    for _ in range(3):
        j = read_str(g.b, j)[1]
    cur = struct.unpack_from("<I", g.b, j + 76)[0]
    struct.pack_into("<I", g.b, j + 76,
                     (cur | 0x20000000) if on else (cur & ~0x20000000))


def static_bg(g, argb):
    if g.type == 2:
        struct.pack_into("<I", g.b, g.nend + 0x5C, argb)


def panel(g, x, y, w, h, argb):
    """Plain colored rectangle (unbound, no text)."""
    g.set_rect_px(x, y, w, h)
    g.set_texts("", ["", "", ""])
    static_bg(g, argb)
    g.set_arr(0, [argb] * 6, flag=0)
    g.set_arr(2, [TRANSP] * 6, flag=0)
    g.set_tcolor(TRANSP)
    g.set_hash(UNBOUND)


def label(g, x, y, w, h, text, color):
    g.set_rect_px(x, y, w, h)
    g.set_texts(text, [text, text, text])
    static_bg(g, TRANSP)
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [color] * 6, flag=0)
    g.set_tcolor(color)
    g.set_hash(UNBOUND)


def park(g):
    g.set_rect_px(797, 0, 2, 2)
    g.set_texts("", ["", "", ""])
    static_bg(g, TRANSP)
    g.set_arr(0, [TRANSP] * 6, flag=0)
    g.set_arr(2, [TRANSP] * 6, flag=0)
    g.set_tcolor(TRANSP)
    g.set_hash(UNBOUND)


def state_lens(g, x, y, w, h, hash_, vmax, warn, crit, states, bgs, tcs):
    """Bound lens with per-level bg colors AND per-level state TEXT.
    states/bgs/tcs are 3-lists (normal, warning, critical)."""
    g.set_rect_px(x, y, w, h)
    g.set_texts(states[0], list(states))
    set_static(g, True)
    static_bg(g, bgs[0])
    g.set_arr(0, list(bgs) * 2, flag=0)
    g.set_arr(2, list(tcs) * 2, flag=0)
    g.set_tcolor(tcs[0])
    g.set_hash(hash_)
    g.set_decimals(0)
    g.set_ranges(0, vmax, warn=warn, crit=crit, warn_below=-999,
                 crit_below=-999)


def fix_fan(g):
    """Make the FAN bit pill actually light: finite alarm levels engage the
    flag=1 dynamic fill; blink fields are 0 so the pill stays steady."""
    g.set_ranges(0, 1, warn=0.5, crit=0.7, warn_below=0, crit_below=0)
