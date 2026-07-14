#!/usr/bin/env python3
"""One fix at a time: set BOOST MAP label on R1C1 tile."""
import sys, time
sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
from slow_rd import RD, SX, SY

rd = RD()
rd.focus()
rd.enter_edit()
time.sleep(0.5)

# R1C1 tile center (plan coords)
rd.click(105 * SX, 112 * SY, 0.6)

# LOOK'N FEEL -> Font&Text -> set label
rd.click(688, 84, 0.8)   # LOOK'N FEEL menu
rd.click(170, 632, 0.8)  # Font & Text
rd.click(881, 214, 0.3)  # text field
import pyautogui
pyautogui.keyDown("ctrl"); pyautogui.press("a"); pyautogui.keyUp("ctrl")
pyautogui.press("backspace")
pyautogui.typewrite("BOOST MAP", interval=0.02)
pyautogui.press("enter")
time.sleep(0.3)
rd.click(81, 94, 0.5)    # back
rd.click(81, 94, 0.5)    # back to editor

rd.shot("step02_boost_label.png")
print("done - BOOST MAP label set")
