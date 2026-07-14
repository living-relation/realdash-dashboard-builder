#!/usr/bin/env python3
"""probe_addgauge.py - enter editor, open ADD GAUGE, screenshot the type list."""
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
user32.ShowWindow(win._hWnd, 3)
time.sleep(0.4)
user32.SetForegroundWindow(win._hWnd)
time.sleep(0.6)

pyautogui.click(960, 55)          # raise overlay
time.sleep(0.9)
pyautogui.click(1835, 90)         # EDIT
time.sleep(2.2)
pyautogui.click(420, 165)         # ADD GAUGE
time.sleep(1.6)
out = os.path.abspath(os.path.join(SHOTS, "addgauge_menu.png"))
pyautogui.screenshot(out)
print("saved", out)
