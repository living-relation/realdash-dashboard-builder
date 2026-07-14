#!/usr/bin/env python3
"""probe_step.py <action> [arg] - single idempotent editor action + screenshot.

Actions:
  shot <name>        screenshot only
  menu               ensure editor top menu is visible
  click <x,y>        raw click
  addtype <maindrop_y> ensure menu, ADD GAUGE, click main dropdown row
  addind <submenu_y> ensure menu, ADD GAUGE, INDICATORS >, click submenu row
  filerow <y>        ensure menu, FILE, click dropdown row at (206, y)
Always saves _build/shots/step.png at the end.
"""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")

user32 = ctypes.windll.user32
win = None
for t in gw.getAllTitles():
    if t and "RealDash" in t:
        ws = gw.getWindowsWithTitle(t)
        if ws:
            win = ws[0]
            break
assert win, "RealDash not found"
user32.SetForegroundWindow(win._hWnd)
time.sleep(0.6)


def menu_visible():
    im = pyautogui.screenshot(region=(400, 75, 40, 30))
    # ADD GAUGE plus icon (physical ~(415,90)) is teal when the menu is shown
    for xy in ((15, 15), (20, 15), (15, 20)):
        r, g, b = im.getpixel(xy)[:3]
        if b > 120 and g > 110 and r < 90:
            return True
    return False


def ensure_menu():
    for _ in range(3):
        if menu_visible():
            return True
        pyautogui.click(960, 40)
        time.sleep(1.1)
    return menu_visible()


act = sys.argv[1]
if act == "menu":
    print("menu:", ensure_menu())
elif act == "click":
    x, y = (int(v) for v in sys.argv[2].split(","))
    pyautogui.click(x, y)
    time.sleep(1.2)
elif act == "addtype":
    assert ensure_menu(), "menu not visible"
    pyautogui.click(420, 165)
    time.sleep(1.3)
    pyautogui.click(536, int(sys.argv[2]))
    time.sleep(1.8)
elif act == "addind":
    assert ensure_menu(), "menu not visible"
    pyautogui.click(420, 165)
    time.sleep(1.3)
    pyautogui.click(536, 214)
    time.sleep(1.3)
    pyautogui.click(1018, int(sys.argv[2]))
    time.sleep(1.8)
elif act == "filerow":
    assert ensure_menu(), "menu not visible"
    pyautogui.click(146, 165)
    time.sleep(1.3)
    pyautogui.click(206, int(sys.argv[2]))
    time.sleep(2.5)
elif act == "shot":
    pass
else:
    raise SystemExit("unknown action " + act)

name = sys.argv[2] if act == "shot" and len(sys.argv) > 2 else "step.png"
out = os.path.abspath(os.path.join(SHOTS, name))
pyautogui.screenshot(out)
print("saved", out)
