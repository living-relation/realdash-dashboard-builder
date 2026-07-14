#!/usr/bin/env python3
"""
finish_layout.py - Window-aware RealDash editor driver for completing ST185 dash.

Scales rd.py's 1920x1080 reference coordinates to the actual RealDash window
rect so automation works whether RealDash is maximized or windowed.
"""
import ctypes
import subprocess
import sys
import time
import os

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

user32 = ctypes.windll.user32
SW_MAXIMIZE = 3

try:
    import pygetwindow as gw
    import pyautogui
except Exception as e:
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(2)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.2

REF_W, REF_H = 1920.0, 1080.0
SX, SY = 2.4, 2.25  # plan 800x480 -> editor ref

TOOLS = os.path.dirname(__file__)
SHOTS = os.path.join(os.path.dirname(TOOLS), "_build", "shots")

# rd.py reference coords (1920x1080 editor space)
MENU = {
    "file": (144, 84), "add": (416, 84), "look": (688, 84),
    "input": (960, 84), "info": (1232, 84), "settings": (1504, 84),
    "done": (1774, 84), "back": (81, 94),
}
FLD = {"x": (681, 917), "y": (943, 917), "w": (1219, 917), "h": (1554, 917)}
ADD_TEXT = (534, 590)
ADD_INDICATORS = (544, 197)
IND_BAR = (984, 371)
IV_DATASOURCE = (527, 356)
IV_MIN = (564, 690)
IV_MAX = (1352, 690)
IV_WARN_ABOVE = (1352, 842)
IV_CRIT_ABOVE = (1352, 992)
CAT_ECU = (534, 525)
NEXT_ARROW = (1819, 619)
INP_SEARCH = (960, 242)
INP_FIRST = (360, 349)
INP_CONFIRM = (960, 1001)
LNF_FONT = (170, 632)
FT_TEXTFIELD = (881, 214)
FT_DECIMALS = (1046, 600)
CONFIRM_YES = (1187, 727)
OVERLAY_EDIT = (1755, 70)
OVERLAY_TAP = (960, 400)


class RD:
    def __init__(self):
        self.win = None

    def find(self, prefer="1.92"):
        for t in gw.getAllTitles():
            if t and prefer in t and "RealDash" in t:
                wins = gw.getWindowsWithTitle(t)
                if wins:
                    self.win = wins[0]
                    return self.win
        for t in gw.getAllTitles():
            if t and "RealDash" in t:
                wins = gw.getWindowsWithTitle(t)
                if wins:
                    self.win = wins[0]
                    return self.win
        return None

    def focus(self):
        if not self.win:
            self.find()
        if not self.win:
            raise RuntimeError("RealDash window not found")
        user32.ShowWindow(self.win._hWnd, SW_MAXIMIZE)
        time.sleep(0.4)
        try:
            user32.keybd_event(0x12, 0, 0, 0)
            user32.keybd_event(0x12, 0, 2, 0)
        except Exception:
            pass
        user32.SetForegroundWindow(self.win._hWnd)
        time.sleep(0.5)
        return self.win

    def scale(self, x, y):
        w = self.win
        sx = w.width / REF_W
        sy = w.height / REF_H
        return int(w.left + x * sx), int(w.top + y * sy)

    def click(self, x, y, pause=0.4):
        self.focus()
        px, py = self.scale(x, y)
        pyautogui.click(px, py)
        time.sleep(pause)

    def clickp(self, pt, pause=0.4):
        self.click(pt[0], pt[1], pause)

    def typewrite(self, text):
        pyautogui.typewrite(text, interval=0.02)

    def key(self, name, n=1):
        pyautogui.press(name, presses=n, interval=0.02)

    def hotkey(self, *keys):
        pyautogui.hotkey(*keys)

    def clear_field(self):
        self.key("end")
        self.key("backspace", 12)

    def set_field(self, pt, value):
        self.clickp(pt, 0.2)
        self.clear_field()
        self.typewrite(str(value))
        self.key("enter")
        time.sleep(0.2)

    def shot(self, name):
        self.focus()
        path = os.path.join(SHOTS, name)
        pyautogui.screenshot().save(path)
        print("saved", path, "win=%dx%d@%d,%d" % (
            self.win.width, self.win.height, self.win.left, self.win.top))
        return path

    def enter_edit(self):
        """Open run-mode overlay then enter the visual editor (FILE menu bar)."""
        self.clickp(OVERLAY_TAP, 0.4)
        # EDIT is top-right of overlay; use window-relative fallback too
        w = self.win
        self.click(int(REF_W * 0.91), 70, 0.3)
        time.sleep(1.8)
        # If still on overlay (GALLERY visible), click EDIT again slightly lower
        self.click(int(REF_W * 0.91), 95, 1.5)

    def pplace(self, px, py, pw, ph):
        self.set_field(FLD["x"], round(px * SX))
        self.set_field(FLD["y"], round(py * SY))
        self.set_field(FLD["w"], round(pw * SX))
        self.set_field(FLD["h"], round(ph * SY))

    def bind(self, search):
        self.clickp(MENU["input"], 0.8)
        self.clickp(IV_DATASOURCE, 0.8)
        self.clickp(CAT_ECU, 0.4)
        self.clickp(NEXT_ARROW, 0.8)
        self.clickp(INP_SEARCH, 0.2)
        self.clear_field()
        self.typewrite(search)
        time.sleep(0.7)
        self.clickp(INP_FIRST, 0.4)
        self.clickp(INP_CONFIRM, 0.8)

    def settext(self, text):
        self.clickp(MENU["look"], 0.8)
        self.clickp(LNF_FONT, 0.8)
        self.clickp(FT_TEXTFIELD, 0.2)
        self.clear_field()
        self.typewrite(text)
        self.key("enter")
        time.sleep(0.2)
        self.clickp(MENU["back"], 0.4)
        self.clickp(MENU["back"], 0.6)

    def ranges(self, vmin, vmax, warn, crit):
        for pt, v in [(IV_MIN, vmin), (IV_MAX, vmax), (IV_WARN_ABOVE, warn), (IV_CRIT_ABOVE, crit)]:
            if v != "-":
                self.set_field(pt, v)

    def ivdone(self):
        self.clickp(MENU["done"], 0.8)

    def addtext(self):
        self.clickp(MENU["add"], 0.6)
        self.clickp(ADD_TEXT, 0.8)

    def save(self):
        self.hotkey("ctrl", "s")
        time.sleep(0.8)

    def select_gauge_in_list(self, row_from_top):
        # left panel gauge list: first item ~y=197, step ~38px at ref scale
        y = 197 + (row_from_top - 1) * 38
        self.click(120, y, 0.5)


LOAD_ITEM = (210, 250)
FILE_MENU = MENU["file"]


def cmd_load_st185(rd):
    path = r"C:\projects\st185-link-ecu-config\st185_dash.rd"
    rd.find()
    rd.focus()
    rd.enter_edit()
    time.sleep(0.5)
    rd.clickp(FILE_MENU, 0.6)
    rd.clickp(LOAD_ITEM, 1.0)
    # Windows file dialog: focus filename field via Alt+N or type path directly
    time.sleep(0.8)
    rd.hotkey("alt", "n")
    time.sleep(0.3)
    pyautogui.typewrite(path, interval=0.01)
    time.sleep(0.3)
    rd.key("enter")
    time.sleep(2.0)
    rd.shot("finish_loaded.png")


def cmd_status(rd):
    rd.find()
    rd.focus()
    w = rd.win
    title = w.title.encode("ascii", "replace").decode("ascii")
    print("window:", title, "| %dx%d @ %d,%d" % (w.width, w.height, w.left, w.top))


def cmd_edit(rd):
    rd.find()
    rd.focus()
    rd.enter_edit()
    rd.shot("finish_edit.png")


def cmd_fix_pills(rd):
    """Reposition top-strip status pills per PLAN 4.2."""
    rd.find()
    rd.focus()
    rd.enter_edit()
    rd.shot("finish_before_pills.png")
    # Pill positions (plan coords): x,y,w,h
    pills = [
        ("FLAT", 186, 12, 60, 30),
        ("FAN", 250, 12, 54, 30),
        ("LOFUEL", 308, 12, 70, 30),
        ("SBFLT", 382, 12, 64, 30),
        ("COOLP", 640, 12, 90, 30),
        ("OILP2", 734, 12, 66, 30),
    ]
    # Select each pill by clicking approximate center in plan space and reposition
    plan_centers = [(213, 27), (277, 27), (343, 27), (414, 27), (685, 27), (767, 27)]
    for i, (name, px, py, pw, ph) in enumerate(pills):
        cx, cy = plan_centers[i]
        rd.click(cx * SX, cy * SY, 0.4)
        rd.pplace(px, py, pw, ph)
        time.sleep(0.3)
    rd.shot("finish_after_pills.png")
    rd.save()


def cmd_fix_labels(rd):
    """Set static label text on gauges missing labels."""
    rd.find()
    rd.focus()
    rd.enter_edit()
    # Click R1C1 tile center (BOOST MAP slot) - plan 105,112
    rd.click(105 * SX, 112 * SY, 0.5)
    rd.settext("BOOST MAP")
    rd.shot("finish_label_boost.png")
    # R1C2 TC tile - plan 302,112
    rd.click(302 * SX, 112 * SY, 0.5)
    rd.settext("TC")
    rd.save()


def cmd_rebind_throttle_ac(rd):
    rd.find()
    rd.focus()
    rd.enter_edit()
    # Throttle R1C3
    rd.click(499 * SX, 112 * SY, 0.5)
    rd.bind("ST185: Throttle")
    rd.ranges(0, 100, "-", "-")
    rd.ivdone()
    # A/C R4C3-4 span center
    rd.click(597 * SX, 422 * SY, 0.5)
    rd.bind("ST185: AC Status")
    rd.ivdone()
    rd.shot("finish_rebind.png")
    rd.save()


def main():
    if len(sys.argv) < 2:
        print("usage: finish_layout.py <status|edit|load|fix_pills|fix_labels|rebind|all>")
        return 2
    rd = RD()
    cmd = sys.argv[1]
    cmds = {
        "status": cmd_status,
        "edit": cmd_edit,
        "load": cmd_load_st185,
        "fix_pills": cmd_fix_pills,
        "fix_labels": cmd_fix_labels,
        "rebind": cmd_rebind_throttle_ac,
    }
    if cmd == "all":
        for name in ("fix_pills", "fix_labels", "rebind"):
            print("===", name, "===")
            cmds[name](rd)
        rd.enter_edit()
        rd.shot("finish_final.png")
        return 0
    fn = cmds.get(cmd)
    if not fn:
        print("unknown", cmd)
        return 2
    fn(rd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
