#!/usr/bin/env python3
"""cf_blink_probe.py <step> - GUI probe for the Blink Speed binary field.
Steps: sel (enter editor+select Text Gauge 40), special (open LNF Special),
shot <name>, click <x> <y> [shotname], type <text>, save (FILE->SAVE),
exit (DONE, discard)."""
import ctypes
import os
import sys
import time

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = False
SHOTS = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\shots"
user32 = ctypes.windll.user32
win = None
for t in gw.getAllTitles():
    if t and "RealDash" in t:
        win = gw.getWindowsWithTitle(t)[0]
        break
assert win
user32.SetForegroundWindow(win._hWnd)
time.sleep(0.6)


def sh(name):
    p = os.path.join(SHOTS, name)
    pyautogui.screenshot(p)
    print("saved", p)


step = sys.argv[1]
if step == "sel":
    pyautogui.keyDown("shift"); pyautogui.press("6"); pyautogui.keyUp("shift")
    time.sleep(2.5)
    pyautogui.click(218, 265)          # gauge-list search box
    time.sleep(0.7)
    pyautogui.typewrite("Text Gauge 40", interval=0.03)
    time.sleep(0.9)
    pyautogui.click(105, 329)          # first result
    time.sleep(0.9)
    sh("blink_sel.png")
elif step == "special":
    pyautogui.keyDown("shift"); pyautogui.press("3"); pyautogui.keyUp("shift")
    time.sleep(1.5)
    pyautogui.click(163, 708)          # SPECIAL submenu
    time.sleep(1.3)
    sh("blink_special.png")
elif step == "click":
    pyautogui.click(int(sys.argv[2]), int(sys.argv[3]))
    time.sleep(1.0)
    sh(sys.argv[4] if len(sys.argv) > 4 else "blink_click.png")
elif step == "type":
    pyautogui.typewrite(sys.argv[2], interval=0.04)
    time.sleep(0.5)
    pyautogui.press("enter")
    time.sleep(0.8)
    sh("blink_type.png")
elif step == "save":
    pyautogui.keyDown("shift"); pyautogui.press("1"); pyautogui.keyUp("shift")
    time.sleep(1.4)
    pyautogui.click(206, 427)
    time.sleep(2.5)
    sh("blink_save.png")
elif step == "exit":
    pyautogui.click(960, 40)
    time.sleep(0.8)
    pyautogui.click(1774, 165)
    time.sleep(1.8)
    pyautogui.click(733, 727)          # discard if prompted
    time.sleep(1.5)
    sh("blink_exit.png")
elif step == "shot":
    sh(sys.argv[2])
