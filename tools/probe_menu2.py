#!/usr/bin/env python3
"""probe_menu2.py <shot.png> <x1,y1> [x2,y2 ...] - reveal editor top menu,
click ADD GAUGE, then click the given sequence of points, screenshot at end."""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")

shot = sys.argv[1]
points = [tuple(int(v) for v in a.split(",")) for a in sys.argv[2:]]

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

pyautogui.click(960, 40)          # reveal top menu
time.sleep(1.0)
pyautogui.click(420, 165)         # ADD GAUGE
time.sleep(1.4)
base = os.path.abspath(os.path.join(SHOTS, shot))
pyautogui.screenshot(base.replace(".png", "_0.png"))
for i, (x, y) in enumerate(points, 1):
    pyautogui.click(x, y)
    time.sleep(1.4)
    pyautogui.screenshot(base.replace(".png", "_%d.png" % i))
print("saved steps to", base)
