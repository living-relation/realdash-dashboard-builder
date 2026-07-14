#!/usr/bin/env python3
import time, ctypes, pyautogui
ctypes.windll.shcore.SetProcessDpiAwareness(2)
pyautogui.FAILSAFE = False
# Open dialog should be at rd-build - double-click realdash-root folder
pyautogui.doubleClick(420, 300)
time.sleep(0.8)
# double-click st185_dash.rd
pyautogui.doubleClick(520, 418)
time.sleep(3)
out = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\shots\finish_restored3.png"
pyautogui.screenshot(out)
print("saved", out)
