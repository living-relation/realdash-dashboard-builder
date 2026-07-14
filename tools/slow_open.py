#!/usr/bin/env python3
import time, ctypes, pyautogui
ctypes.windll.shcore.SetProcessDpiAwareness(2)
pyautogui.FAILSAFE = False
# Open dialog should be in Downloads - typeahead to st185_dash.rd
pyautogui.click(400, 350)
time.sleep(0.3)
pyautogui.typewrite("st185_dash", interval=0.06)
time.sleep(0.5)
pyautogui.press("enter")
time.sleep(3)
out = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\shots\step01_loaded.png"
pyautogui.screenshot(out)
print("saved", out)
