#!/usr/bin/env python3
"""probe_add_types.py - add one gauge of each new type via ADD GAUGE menu,
with a screenshot after each step. Assumes editor open on probe dash."""
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


def reset():
    # close any open dropdown/popup and deselect
    pyautogui.press("esc")
    time.sleep(0.6)
    pyautogui.click(960, 600)
    time.sleep(0.8)


def add_indicator(row_y, tag):
    reset()
    pyautogui.click(960, 40)      # reveal top menu
    time.sleep(1.0)
    pyautogui.click(420, 165)     # ADD GAUGE
    time.sleep(1.3)
    pyautogui.click(536, 214)     # INDICATORS >
    time.sleep(1.3)
    pyautogui.click(1018, row_y)  # submenu row
    time.sleep(1.6)
    shot("added_%s.png" % tag)


def add_main(row_y, tag):
    reset()
    pyautogui.click(960, 40)
    time.sleep(1.0)
    pyautogui.click(420, 165)
    time.sleep(1.3)
    pyautogui.click(536, row_y)   # main dropdown row
    time.sleep(1.6)
    shot("added_%s.png" % tag)


add_indicator(231, "needle")
add_indicator(283, "arc")
add_indicator(379, "bar")
add_indicator(525, "indlight")
add_main(428, "graph")
print("done")
