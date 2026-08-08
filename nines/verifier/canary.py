from __future__ import annotations

from nines.types import Task, VerifierMeta
from nines.verifier.execute import check_output

KNOWN_BAD = "__NINES_CANARY_BAD__"


def known_bad_for_task(task: Task) -> str:
    """Deliberately wrong candidate output shaped by the task text.

    Never calls a solver — independence preserved.
    """
    prompt = (task.prompt or "").lower()
    if any(k in prompt for k in ("add", "sum", "integer", "number", "count")):
        return "def add(a, b):\n    return a - b  # off-by-sign canary\n"
    if any(k in prompt for k in ("sort", "sorted", "order")):
        return "[3, 1, 2]"
    if any(k in prompt for k in ("reverse", "string")):
        return "def reverse_string(s):\n    return s  # identity canary\n"
    if any(k in prompt for k in ("dict", "list", "json", "transform")):
        return "{}"
    if not prompt.strip():
        return ""
    return KNOWN_BAD


def canary_rejects(meta: VerifierMeta, known_bad: str = KNOWN_BAD) -> bool:
    """Return True if the checker correctly fails known-bad output.

    Checker crashes are treated as rejection failures (not validated).
    """
    try:
        return check_output(meta, known_bad) is False
    except Exception:
        # A crashing checker is not a trustworthy reject — force regenerate/fail.
        return False
