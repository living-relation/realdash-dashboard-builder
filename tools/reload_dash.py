#!/usr/bin/env python3
"""Reload st185_dash.rd from Downloads in RealDash 1.92 and screenshot.

Sequence (coords verified on this 1920x1080 setup, RealDash maximized):
  top tap -> EDIT -> FILE -> LOAD... -> double-click st185_dash.rd -> DONE
Handles the 'save?' confirm dialog by clicking the X (discard) if it appears.
"""
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

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")
name = sys.argv[1] if len(sys.argv) > 1 else "reload_result.png"

user32 = ctypes.windll.user32
win = None
for t in gw.getAllTitles():
    if t and "RealDash" in t and "1.92" in t:
        ws = gw.getWindowsWithTitle(t)
        if ws:
            win = ws[0]
            break
assert win, "RealDash 1.92 not found"
user32.ShowWindow(win._hWnd, 3)
time.sleep(0.4)
user32.SetForegroundWindow(win._hWnd)
time.sleep(0.6)

# 1. top tap to raise overlay, then EDIT
pyautogui.click(960, 55)
time.sleep(0.9)
pyautogui.click(1835, 90)   # EDIT top-right of overlay
time.sleep(2.2)

# 2. FILE menu
pyautogui.click(144, 165)
time.sleep(1.0)

# 3. LOAD...
pyautogui.click(221, 270)
time.sleep(2.0)

shot = os.path.abspath(os.path.join(SHOTS, "reload_dialog.png"))
pyautogui.screenshot(shot)

# 4. Open-file dialog defaults to Downloads; st185_dash.rd is the first
#    'Today' row -> double-click it
pyautogui.doubleClick(306, 186)
time.sleep(2.5)

# 5. DONE (exit editor)
pyautogui.click(1774, 165)
time.sleep(2.0)

path = os.path.abspath(os.path.join(SHOTS, name))
pyautogui.screenshot(path)
print("saved", path)
