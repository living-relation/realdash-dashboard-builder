#!/usr/bin/env python3
"""
rd.py - high-level RealDash editor driver for the ST185 build.

Encapsulates the (empirically verified) click sequences + coordinates of the
RealDash editor running FULLSCREEN at 1920x1080, so the agent can issue high
level operations instead of dozens of raw clicks. Coordinates are REAL screen
pixels (the editor reference == 1920x1080 in fullscreen).

All ST185 dashboard-plan coordinates are given in an 800x480 space; RealDash's
reference is 1920x1080, so plan coords are scaled by SX=2.4, SY=2.25. Use the
`plot`/`plabel`/etc helpers which accept PLAN coordinates and scale them.

Subcommands (assume RealDash is fullscreen + foreground, in EDIT mode):
  menu <file|add|look|input|info|settings|done|back>
  shot <path>
  pos <X> <Y> <W> <H>            # set selected gauge position (editor px)
  pplace <px> <py> <pw> <ph>     # set position from PLAN (800x480) coords
  addtext                        # Add Gauge -> Text Gauge (new gauge selected)
  addlight                       # Add Gauge -> Indicators -> Indicator Light
  addbar                         # Add Gauge -> Indicators -> Bar Gauge
  bind <exact search text>       # bind selected gauge to ECU-SPECIFIC channel (first match)
  ranges <min> <max> <warnAbove> <critAbove>   # on Input&Values panel; use - to skip
  ivdone                         # DONE on Input&Values panel
  settext <text>                 # set text-gauge static text (Look'nFeel>Font&Text)
  align <left|center|right>      # set text align (Look'nFeel>Font&Text>Formatting)
  decimals <n>                   # set decimal places (Look'nFeel>Font&Text)
  del                            # delete selected gauge (confirms)
  save                           # Ctrl+S (may open Save As if new)
"""
import sys, time, subprocess, os

HELPER = os.path.join(os.path.dirname(__file__), "automation_helper.py")
PY = sys.executable

SX, SY = 2.4, 2.25  # plan(800x480) -> editor(1920x1080)

# --- top menu (fullscreen) real coords ---
MENU = {
    "file": (144, 84), "add": (416, 84), "look": (688, 84),
    "input": (960, 84), "info": (1232, 84), "settings": (1504, 84),
    "done": (1774, 84), "back": (81, 94),
}
# --- bottom position fields ---
FLD = {"x": (681, 917), "y": (943, 917), "w": (1219, 917), "h": (1554, 917)}
# --- Add Gauge menu ---
ADD_TEXT = (534, 590)
ADD_INDICATORS = (544, 197)
IND_BAR = (984, 371)
IND_LIGHT = (1013, 525)
# --- Input & Values panel ---
IV_DATASOURCE = (527, 356)
IV_MIN = (564, 690); IV_MAX = (1352, 690)
IV_WARN_ABOVE = (1352, 842); IV_CRIT_ABOVE = (1352, 992)
IV_WARN_BELOW = (564, 842); IV_CRIT_BELOW = (564, 992)
# --- Select Category / Input ---
CAT_ECU = (534, 525)
NEXT_ARROW = (1819, 619)
INP_SEARCH = (960, 242)
INP_FIRST = (360, 349)
INP_CONFIRM = (960, 1001)
# --- Look'n Feel ---
LNF_FONT = (170, 632)
FT_TEXTFIELD = (881, 214)
FT_DECIMALS = (1046, 600)
FT_STATIC_TOGGLE = (1100, 342)
FT_FORMATTING = (174, 435)
FMT_ALIGN = (881, 86)
# --- dialogs ---
CONFIRM_YES = (1187, 727)


def h(*args):
    subprocess.run([PY, HELPER] + [str(a) for a in args],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def click(x, y, pause=0.5):
    h("click", x, y); time.sleep(pause)


def clickp(pt, pause=0.5):
    click(pt[0], pt[1], pause)


def clear_field():
    h("key", "end"); h("key", "backspace", 12)


def set_field(pt, value):
    clickp(pt, 0.25); clear_field(); h("type", str(value)); h("key", "enter"); time.sleep(0.25)


def screenshot(path):
    subprocess.run([PY, HELPER, "screenshot", path])


def main(a):
    cmd = a[0]
    if cmd == "menu":
        clickp(MENU[a[1]], 1.2)
    elif cmd == "shot":
        screenshot(a[1])
    elif cmd == "pos":
        set_field(FLD["x"], a[1]); set_field(FLD["y"], a[2])
        set_field(FLD["w"], a[3]); set_field(FLD["h"], a[4])
    elif cmd == "pplace":
        px, py, pw, ph = float(a[1]), float(a[2]), float(a[3]), float(a[4])
        set_field(FLD["x"], round(px*SX)); set_field(FLD["y"], round(py*SY))
        set_field(FLD["w"], round(pw*SX)); set_field(FLD["h"], round(ph*SY))
    elif cmd == "addtext":
        clickp(MENU["add"], 0.8); clickp(ADD_TEXT, 1.2)
    elif cmd == "addlight":
        clickp(MENU["add"], 0.8); clickp(ADD_INDICATORS, 1.0); clickp(IND_LIGHT, 1.2)
    elif cmd == "addbar":
        clickp(MENU["add"], 0.8); clickp(ADD_INDICATORS, 1.0); clickp(IND_BAR, 1.2)
    elif cmd == "bind":
        search = a[1]
        clickp(MENU["input"], 1.0)     # open Input & Values
        clickp(IV_DATASOURCE, 1.0)     # open data source -> Select Category
        clickp(CAT_ECU, 0.6)           # highlight ECU SPECIFIC
        clickp(NEXT_ARROW, 1.0)        # -> Select Input
        clickp(INP_SEARCH, 0.3); clear_field(); h("type", search); time.sleep(0.8)
        clickp(INP_FIRST, 0.6)         # first result
        clickp(INP_CONFIRM, 1.0)       # confirm -> back on Input & Values
    elif cmd == "ranges":
        vals = a[1:5]
        pts = [IV_MIN, IV_MAX, IV_WARN_ABOVE, IV_CRIT_ABOVE]
        for pt, v in zip(pts, vals):
            if v != "-":
                set_field(pt, v)
    elif cmd == "ivdone":
        clickp(MENU["done"], 1.2)
    elif cmd == "settext":
        clickp(MENU["look"], 1.0); clickp(LNF_FONT, 1.0)
        clickp(FT_TEXTFIELD, 0.3); clear_field(); h("type", a[1]); h("key", "enter"); time.sleep(0.3)
        clickp(MENU["back"], 0.6); clickp(MENU["back"], 0.8)
    elif cmd == "decimals":
        clickp(MENU["look"], 1.0); clickp(LNF_FONT, 1.0)
        set_field(FT_DECIMALS, a[1])
        clickp(MENU["back"], 0.6); clickp(MENU["back"], 0.8)
    elif cmd == "del":
        h("key", "delete"); time.sleep(0.8); clickp(CONFIRM_YES, 0.8)
    elif cmd == "save":
        h("hotkey", "ctrl", "s"); time.sleep(1.0)
    else:
        print("unknown", cmd); return 2
    print("ok", cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
