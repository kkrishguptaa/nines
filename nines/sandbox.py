from __future__ import annotations

import subprocess
import sys
import textwrap


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
    payload = textwrap.dedent(
        f"""
        import json, sys
        {code}
        args = json.loads(sys.argv[1])
        result = {fn_name}(*args)
        print(json.dumps({{"ok": True, "result": result}}))
        """
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", payload, __import__("json").dumps(args)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"sandbox timed out after {timeout_s}s") from exc

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "sandbox failed")

    import json

    line = proc.stdout.strip().splitlines()[-1]
    data = json.loads(line)
    return data["result"]
