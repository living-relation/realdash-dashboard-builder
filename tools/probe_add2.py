#!/usr/bin/env python3
"""probe_add2.py - add Needle, Bar, Indicator Light via ADD GAUGE (no Esc),
then FILE->SAVE. Editor must already be open."""
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
user32.SetForegroundWindow(win._hWnd)
time.sleep(0.6)


def shot(name):
    pyautogui.screenshot(os.path.join(SHOTS, name))


def add_indicator(row_y, tag):
    pyautogui.click(960, 40)      # reveal top menu
    time.sleep(1.0)
    pyautogui.click(420, 165)     # ADD GAUGE
    time.sleep(1.3)
    pyautogui.click(536, 214)     # INDICATORS >
    time.sleep(1.3)
    pyautogui.click(1018, row_y)  # submenu row
    time.sleep(1.8)
    shot("added2_%s.png" % tag)


add_indicator(231, "needle")
add_indicator(379, "bar")
add_indicator(525, "indlight")

# FILE -> SAVE
pyautogui.click(960, 40)
time.sleep(1.0)
pyautogui.click(146, 165)         # FILE
time.sleep(1.2)
pyautogui.click(206, 427)         # SAVE
time.sleep(2.5)
shot("probe_saved.png")
print("done")
