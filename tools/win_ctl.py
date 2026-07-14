#!/usr/bin/env python3
"""
win_ctl.py - Windows window-management helper for the RealDash build.

Supplements automation_helper.py by letting the agent see which window is
active, list windows, activate/focus the RealDash window, and read its
geometry. Uses pygetwindow (installed as a PyAutoGUI dependency) plus ctypes
for reliable foreground activation and DPI awareness.

Usage:
  python win_ctl.py active                 # active window title + rect
  python win_ctl.py list                   # all visible window titles
  python win_ctl.py geom "<substr>"        # rect of first window matching substr
  python win_ctl.py activate "<substr>"    # bring matching window to foreground
  python win_ctl.py maximize "<substr>"    # maximize matching window
  python win_ctl.py foreground             # ensure RealDash is foreground (matches 'RealDash')
"""
import sys
import ctypes
from ctypes import wintypes

# Ensure Unicode window titles (e.g. LTR marks) don't crash console output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Make this process DPI-aware so screen coords match physical pixels / screenshots.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

user32 = ctypes.windll.user32

try:
    import pygetwindow as gw
except Exception as e:
    sys.stderr.write("ERROR: pygetwindow not available: %s\n" % e)
    sys.exit(2)


def _rect(w):
    try:
        return "left=%d top=%d width=%d height=%d right=%d bottom=%d" % (
            w.left, w.top, w.width, w.height, w.left + w.width, w.top + w.height)
    except Exception:
        return "(no rect)"


def _force_foreground(hwnd):
    # ALT key trick to bypass SetForegroundWindow restrictions.
    SW_RESTORE = 9
    user32.ShowWindow(hwnd, SW_RESTORE)
    try:
        user32.keybd_event(0x12, 0, 0, 0)   # ALT down
        user32.keybd_event(0x12, 0, 2, 0)   # ALT up
    except Exception:
        pass
    user32.SetForegroundWindow(hwnd)


def _find(substr):
    substr = substr.lower()
    for t in gw.getAllTitles():
        if t and substr in t.lower():
            wins = gw.getWindowsWithTitle(t)
            if wins:
                return wins[0]
    return None


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0].lower()

    if cmd == "active":
        w = gw.getActiveWindow()
        if w is None:
            print("ACTIVE: <none>")
        else:
            print("ACTIVE: '%s' | %s" % (w.title, _rect(w)))
        return 0

    if cmd == "list":
        for t in gw.getAllTitles():
            if t and t.strip():
                print(repr(t))
        return 0

    if cmd == "geom":
        w = _find(argv[1])
        if w is None:
            print("NOTFOUND: %s" % argv[1]); return 1
        print("'%s' | %s" % (w.title, _rect(w)))
        return 0

    if cmd in ("activate", "foreground"):
        target = argv[1] if len(argv) > 1 else "RealDash"
        w = _find(target)
        if w is None:
            print("NOTFOUND: %s" % target); return 1
        _force_foreground(w._hWnd)
        print("ACTIVATED: '%s' | %s" % (w.title, _rect(w)))
        return 0

    if cmd == "maximize":
        w = _find(argv[1])
        if w is None:
            print("NOTFOUND: %s" % argv[1]); return 1
        try:
            w.maximize()
        except Exception as e:
            print("maximize failed: %s" % e)
        _force_foreground(w._hWnd)
        print("MAXIMIZED: '%s' | %s" % (w.title, _rect(w)))
        return 0

    sys.stderr.write("Unknown command: %s\n" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
