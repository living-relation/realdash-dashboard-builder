#!/usr/bin/env python3
"""load_dash.py <filename.rd> <shot.png> - load a dash by filename via
FILE->LOAD dialog (types name into File-name field) and screenshot run mode."""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")
fname = sys.argv[1]
shot = sys.argv[2] if len(sys.argv) > 2 else "load_result.png"

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
pyautogui.click(146, 165)         # FILE
time.sleep(1.1)
pyautogui.click(221, 270)         # LOAD...
time.sleep(2.2)
# File-name field of the Open dialog
pyautogui.click(572, 686)
time.sleep(0.5)
pyautogui.typewrite(fname, interval=0.02)
time.sleep(0.4)
pyautogui.press("enter")
time.sleep(3.0)
pyautogui.click(1774, 165)        # DONE (exit editor)
time.sleep(2.0)
pyautogui.click(960, 300)         # dismiss run-mode overlay if raised
time.sleep(1.2)
out = os.path.abspath(os.path.join(SHOTS, shot))
pyautogui.screenshot(out)
print("saved", out)
