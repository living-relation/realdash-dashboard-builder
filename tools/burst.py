#!/usr/bin/env python3
"""burst.py <prefix> [frames] [interval_s] - rapid screenshot burst of the
RealDash window to _build/shots/<prefix>_f00.png... Use in simulation mode
to verify animation: compare frames for movement."""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")

prefix = sys.argv[1]
frames = int(sys.argv[2]) if len(sys.argv) > 2 else 10
interval = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4

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

paths = []
for i in range(frames):
    p = os.path.abspath(os.path.join(SHOTS, "%s_f%02d.png" % (prefix, i)))
    pyautogui.screenshot(p)
    paths.append(p)
    time.sleep(interval)
print("saved %d frames: %s .. %s" % (frames, paths[0], paths[-1]))
