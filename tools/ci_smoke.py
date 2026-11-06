#!/usr/bin/env python3
"""CI smoke: parse every dashboards/*.rd with tools/rd_lib2.Dash2.

Stdlib + in-repo rd_lib2 only. No PyAutoGUI. Exit non-zero if any file fails
to load or reports zero gauges.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DASHBOARDS = ROOT / "dashboards"


def load_rd_lib2():
    path = TOOLS / "rd_lib2.py"
    spec = importlib.util.spec_from_file_location("rd_lib2", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = load_rd_lib2()
    files = sorted(DASHBOARDS.glob("*.rd"))
    if not files:
        print("no dashboards/*.rd found", file=sys.stderr)
        return 1

    failed = 0
    for path in files:
        try:
            dash = mod.Dash2(str(path))
            gauges = getattr(dash, "gauges", None)
            n = len(gauges) if gauges is not None else 0
            if n <= 0:
                raise RuntimeError("zero gauges")
            print(f"OK  {path.name}  gauges={n}  bytes={path.stat().st_size}")
        except Exception as exc:  # noqa: BLE001 - report each file, keep going
            failed += 1
            print(f"FAIL {path.name}: {exc}", file=sys.stderr)

    if failed:
        print(f"{failed}/{len(files)} dashboard(s) failed", file=sys.stderr)
        return 1
    print(f"parsed {len(files)} dashboard(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
