#!/usr/bin/env python3
"""audit_gauge.py <Text Gauge N> [close] - select gauge in editor list, open
INPUT & VALUES, screenshot to _build/shots/iv_<n>.png. 'close' first clicks the
X of an already-open INPUT & VALUES panel."""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui

pyautogui.FAILSAFE = False
SHOTS = os.path.join(os.path.dirname(__file__), "..", "_build", "shots")

name = sys.argv[1]
do_close = len(sys.argv) > 2 and sys.argv[2] == "close"

if do_close:
    pyautogui.click(1787, 109)   # X cancel of open IV panel
    time.sleep(1.3)

# search box in left gauge list
pyautogui.click(218, 265)
time.sleep(0.4)
pyautogui.press("end")
pyautogui.press("backspace", presses=20, interval=0.01)
pyautogui.typewrite(name, interval=0.02)
time.sleep(0.8)
# first result row
pyautogui.click(105, 329)
time.sleep(0.7)
pyautogui.keyDown("shift")
pyautogui.press("4")
pyautogui.keyUp("shift")
time.sleep(1.6)
out = os.path.abspath(os.path.join(SHOTS, "iv_%s.png" % name.replace(" ", "_")))
pyautogui.screenshot(out)
print("saved", out)
