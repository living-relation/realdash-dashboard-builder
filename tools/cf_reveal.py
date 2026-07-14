#!/usr/bin/env python3
"""Reveal run-mode top menu and screenshot."""
import ctypes
import sys
import time

import pyautogui
import pygetwindow as gw

ctypes.windll.shcore.SetProcessDpiAwareness(2)
w = [x for x in gw.getWindowsWithTitle("RealDash") if "5.3" not in x.title][0]
try:
    w.activate()
except Exception:
    pass
time.sleep(0.8)
pyautogui.click(960, 55)
time.sleep(1.2)
pyautogui.screenshot(sys.argv[1] if len(sys.argv) > 1 else
                     r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\shots\cf_reveal.png")
print("done")
