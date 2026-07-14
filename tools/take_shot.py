#!/usr/bin/env python3
"""Screenshot the RealDash 1.92 window (foregrounds it first)."""
import ctypes
import os
import sys
import time

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

import pyautogui
import pygetwindow as gw

name = sys.argv[1] if len(sys.argv) > 1 else "now.png"
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")
os.makedirs(SHOTS, exist_ok=True)

win = None
for t in gw.getAllTitles():
    if t and "RealDash" in t and "1.92" in t:
        ws = gw.getWindowsWithTitle(t)
        if ws:
            win = ws[0]
            break
if win is None:
    for t in gw.getAllTitles():
        if t and "RealDash" in t:
            ws = gw.getWindowsWithTitle(t)
            if ws:
                win = ws[0]
                break
if win is None:
    print("RealDash window not found")
    sys.exit(1)

user32 = ctypes.windll.user32
user32.ShowWindow(win._hWnd, 3)
time.sleep(0.4)
user32.SetForegroundWindow(win._hWnd)
time.sleep(0.6)
path = os.path.abspath(os.path.join(SHOTS, name))
pyautogui.screenshot(path)
print("saved", path, "win=%dx%d@%d,%d title=%r" % (win.width, win.height, win.left, win.top, win.title))
