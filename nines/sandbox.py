from __future__ import annotations

import json
import subprocess
import sys


def run_python(
    code: str,
    fn_name: str,
    args: list,
    *,
    timeout_s: float = 5.0,
) -> object:
    """Execute ``fn_name(*args)`` from ``code`` in a subprocess.

    Not safe for untrusted input — timeout only, no container isolation.
    """
    payload = (
        "import json, sys\n"
        f"{code}\n"
        "args = json.loads(sys.argv[1])\n"
        f"result = {fn_name}(*args)\n"
        'print(json.dumps({"ok": True, "result": result}))\n'
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", payload, json.dumps(args)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"sandbox timed out after {timeout_s}s") from exc

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "sandbox failed")

    line = proc.stdout.strip().splitlines()[-1]
    data = json.loads(line)
    return data["result"]
