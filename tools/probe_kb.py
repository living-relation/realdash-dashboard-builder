#!/usr/bin/env python3
"""probe_kb.py <action> - keyboard-driven editor probe with screenshots.

Actions:
  cancelpanel        click X of INPUT & VALUES panel
  addind <submenu_y> Shift+2 (ADD GAUGE), INDICATORS >, click submenu row
  addmain <row_y>    Shift+2 (ADD GAUGE), click main dropdown row
  save               Shift+1 (FILE), click SAVE row
  shot <name>
"""
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
user32.SetForegroundWindow(win._hWnd)
time.sleep(0.6)


def sh(name):
    out = os.path.abspath(os.path.join(SHOTS, name))
    pyautogui.screenshot(out)
    print("saved", out)


def shift(key):
    pyautogui.keyDown("shift")
    pyautogui.press(key)
    pyautogui.keyUp("shift")


act = sys.argv[1]
if act == "cancelpanel":
    pyautogui.click(1787, 109)
    time.sleep(1.4)
    sh("step.png")
elif act == "addind":
    shift("2")
    time.sleep(1.4)
    pyautogui.click(536, 214)      # INDICATORS >
    time.sleep(1.3)
    pyautogui.click(1018, int(sys.argv[2]))
    time.sleep(1.8)
    sh("step.png")
elif act == "addmain":
    shift("2")
    time.sleep(1.4)
    pyautogui.click(536, int(sys.argv[2]))
    time.sleep(1.8)
    sh("step.png")
elif act == "save":
    shift("1")
    time.sleep(1.4)
    pyautogui.click(206, 427)      # SAVE row
    time.sleep(2.5)
    sh("step.png")
elif act == "shot":
    sh(sys.argv[2])
else:
    raise SystemExit("unknown action")
