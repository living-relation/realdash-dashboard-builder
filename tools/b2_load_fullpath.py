#!/usr/bin/env python3
"""b2_load_fullpath.py <fullpath.rd> <shot.png> [ok] - recover from an open
Load dialog (optionally dismissing a File-not-found modal first), type the
FULL path, load, exit editor, screenshot."""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")
path = sys.argv[1]
shot = sys.argv[2]
dismiss = len(sys.argv) > 3 and sys.argv[3] == "ok"

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

if dismiss:
    pyautogui.click(1082, 533)        # File-not-found OK
    time.sleep(0.8)

pyautogui.click(572, 686)             # File-name field
time.sleep(0.5)
pyautogui.press("end")
for _ in range(60):
    pyautogui.press("backspace")
time.sleep(0.3)
pyautogui.typewrite(path, interval=0.015)
time.sleep(0.4)
pyautogui.press("enter")
time.sleep(3.0)
pyautogui.click(1774, 165)            # DONE (exit editor)
time.sleep(2.0)
pyautogui.click(960, 300)             # dismiss run-mode overlay
time.sleep(1.2)
out = os.path.abspath(os.path.join(SHOTS, shot))
pyautogui.screenshot(out)
print("saved", out)
