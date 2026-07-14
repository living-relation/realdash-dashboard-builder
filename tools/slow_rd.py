#!/usr/bin/env python3
"""
slow_rd.py - Deliberate, one-step RealDash helper.

Rules:
- Top overlay menu: ONE tap near top-center to show; tap again hides it.
- EDIT enters the editor; do NOT double-tap the overlay.
- All coords scaled to the RealDash window rect (1920x1080 reference).
"""
import ctypes, os, sys, time

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.35

REF_W, REF_H = 1920.0, 1080.0
SX, SY = 2.4, 2.25
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")

user32 = ctypes.windll.user32


def find_rd():
    for t in gw.getAllTitles():
        if t and "1.92" in t and "RealDash" in t:
            w = gw.getWindowsWithTitle(t)
            if w:
                return w[0]
    for t in gw.getAllTitles():
        if t and "RealDash" in t:
            w = gw.getWindowsWithTitle(t)
            if w:
                return w[0]
    return None


class RD:
    def __init__(self):
        self.w = None

    def focus(self):
        self.w = find_rd()
        if not self.w:
            raise RuntimeError("RealDash not found")
        user32.ShowWindow(self.w._hWnd, 3)
        time.sleep(0.3)
        user32.SetForegroundWindow(self.w._hWnd)
        time.sleep(0.4)
        return self.w

    def scale(self, x, y):
        w = self.w
        return int(w.left + x * w.width / REF_W), int(w.top + y * w.height / REF_H)

    def click(self, x, y, wait=0.5):
        self.focus()
        px, py = self.scale(x, y)
        pyautogui.click(px, py)
        time.sleep(wait)

    def shot(self, name):
        self.focus()
        path = os.path.join(SHOTS, name)
        pyautogui.screenshot(path)
        print("saved", path)

    def show_menu(self):
        """Single tap near top to reveal overlay menu."""
        self.click(960, 55, 0.6)

    def enter_edit(self):
        """Reveal overlay with one top tap, then click EDIT once."""
        self.click(960, 55, 0.7)
        self.click(1820, 90, 2.0)

    def exit_edit(self):
        self.click(1774, 84, 1.0)


def main():
    if len(sys.argv) < 2:
        print("usage: slow_rd.py <shot|menu|edit|exit|click X Y>")
        return 2
    rd = RD()
    cmd = sys.argv[1]
    if cmd == "shot":
        rd.focus()
        rd.shot(sys.argv[2] if len(sys.argv) > 2 else "slow_now.png")
    elif cmd == "menu":
        rd.show_menu()
        rd.shot("slow_menu.png")
    elif cmd == "edit":
        rd.enter_edit()
        rd.shot("slow_edit.png")
    elif cmd == "exit":
        rd.exit_edit()
        rd.shot("slow_run.png")
    elif cmd == "click":
        rd.click(float(sys.argv[2]), float(sys.argv[3]))
        rd.shot("slow_after_click.png")
    else:
        print("unknown", cmd)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
