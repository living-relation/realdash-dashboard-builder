#!/usr/bin/env python3
import time
import ctypes
import pyautogui

ctypes.windll.shcore.SetProcessDpiAwareness(2)
pyautogui.FAILSAFE = False

path = r"C:\projects\st185-link-ecu-config\rd-build\realdash-root\st185_dash.rd"
# filename field in Open dialog
pyautogui.click(650, 545)
time.sleep(0.2)
pyautogui.hotkey("ctrl", "a")
pyautogui.typewrite(path, interval=0.01)
time.sleep(0.3)
pyautogui.press("enter")
time.sleep(3)
out = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\shots\finish_restored2.png"
pyautogui.screenshot(out)
print("saved", out)
