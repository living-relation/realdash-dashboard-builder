#!/usr/bin/env python3
"""exit_editor.py - leave the editor discarding changes, back to run mode."""
import ctypes
import os
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

pyautogui.click(960, 40)          # reveal editor top menu
time.sleep(0.9)
pyautogui.click(1774, 165)        # DONE
time.sleep(1.6)
pyautogui.click(733, 727)         # discard (X) if save prompt appeared
time.sleep(1.6)
pyautogui.click(960, 300)         # dismiss any run-mode overlay
time.sleep(1.0)
out = os.path.abspath(os.path.join(SHOTS, "exit_editor.png"))
pyautogui.screenshot(out)
print("saved", out)
