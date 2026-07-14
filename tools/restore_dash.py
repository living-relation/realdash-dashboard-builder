#!/usr/bin/env python3
"""Reload st185_dash.rd from disk without saving broken in-memory state."""
import sys, time
sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
from finish_layout import RD
import pyautogui

rd = RD()
rd.find()
rd.focus()
# discard unsaved changes if dialog appears
rd.clickp((733, 727), 0.6)
rd.enter_edit()
time.sleep(0.5)
rd.clickp((144, 84), 0.6)
rd.click(210, 260, 0.8)
time.sleep(0.8)
pyautogui.hotkey("alt", "up")
time.sleep(0.5)
pyautogui.typewrite("st185", interval=0.05)
time.sleep(0.4)
pyautogui.press("enter")
time.sleep(2.5)
rd.shot("finish_restored.png")
print("restored")
