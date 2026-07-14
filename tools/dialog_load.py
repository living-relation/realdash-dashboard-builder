#!/usr/bin/env python3
"""dialog_load.py <filename.rd> <shot.png> - assumes the Windows Open dialog
is ALREADY open: types filename, Enter, DONE, dismiss overlay, screenshot."""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")
fname, shot = sys.argv[1], sys.argv[2]

user32 = ctypes.windll.user32
win = None
for t in gw.getAllTitles():
    if t and ("Open" == t.strip() or "RealDash" in t):
        ws = gw.getWindowsWithTitle(t)
        if ws:
            win = ws[0]
            break
assert win, "window not found"
user32.SetForegroundWindow(win._hWnd)
time.sleep(0.6)

pyautogui.click(572, 686)             # File-name field
time.sleep(0.5)
pyautogui.hotkey("ctrl", "a")
time.sleep(0.3)
pyautogui.typewrite(fname, interval=0.02)
time.sleep(0.4)
pyautogui.press("enter")
time.sleep(3.0)
pyautogui.click(1774, 165)            # DONE (exit editor)
time.sleep(2.0)
pyautogui.click(960, 300)             # dismiss overlay
time.sleep(1.2)
out = os.path.abspath(os.path.join(SHOTS, shot))
pyautogui.screenshot(out)
print("saved", out)
