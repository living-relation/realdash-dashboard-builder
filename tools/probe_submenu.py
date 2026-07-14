#!/usr/bin/env python3
"""probe_submenu.py <x> <y> <shot.png> - click a point (submenu entry in the
already-open ADD GAUGE dropdown) and screenshot. Assumes editor is open."""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")

x, y, shot = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]

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
time.sleep(0.5)

pyautogui.click(x, y)
time.sleep(1.4)
out = os.path.abspath(os.path.join(SHOTS, shot))
pyautogui.screenshot(out)
print("saved", out)
