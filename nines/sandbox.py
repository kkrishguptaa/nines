from __future__ import annotations

import json
import os
import subprocess
import sys


def _minimal_env() -> dict[str, str]:
    """Env for checker subprocesses — no project secrets.

    Keeps PATH/home/locale so the interpreter can start; strips API keys and
    other caller credentials. Still not multi-tenant isolation.
    """
    keep = (
        "PATH",
        "HOME",
        "USER",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "TMPDIR",
        "TEMP",
        "TMP",
        "SYSTEMROOT",  # Windows
        "WINDIR",
    )
    env = {k: os.environ[k] for k in keep if k in os.environ}
    # Prefer the same interpreter; do not forward ANTHROPIC_*/AWS_*/OPENAI_*/etc.
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_python(
    code: str,
    fn_name: str,
    args: list,
    *,
    timeout_s: float = 5.0,
    env: dict[str, str] | None = None,
) -> object:
    """Execute ``fn_name(*args)`` from ``code`` in a subprocess.

    Not safe for untrusted input — timeout + scrubbed env only, no containers.
    """
    payload = (
        "import json, sys\n"
        f"{code}\n"
        "args = json.loads(sys.argv[1])\n"
        f"result = {fn_name}(*args)\n"
        'print(json.dumps({"ok": True, "result": result}))\n'
    )
    child_env = env if env is not None else _minimal_env()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", payload, json.dumps(args)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
            env=child_env,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"sandbox timed out after {timeout_s}s") from exc

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "sandbox failed")

    line = proc.stdout.strip().splitlines()[-1]
    data = json.loads(line)
    return data["result"]
