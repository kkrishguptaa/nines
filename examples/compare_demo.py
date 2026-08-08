#!/usr/bin/env python3
"""Run the single-shot vs Nines comparison harness (fallback task).

Uses ANTHROPIC_API_KEY when set; otherwise labeled mocks.
"""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "demo.compare",
        "--fallback",
        "--trials",
        "3",
        "--target",
        "0.5",
        "--budget",
        "2.0",
    ]
    print("running:", " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
