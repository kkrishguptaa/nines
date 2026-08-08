from __future__ import annotations

from nines.types import Task, VerifierMeta
from nines.verifier.execute import check_output

KNOWN_BAD = "__NINES_CANARY_BAD__"


def known_bad_for_task(task: Task) -> str:
    """Deliberately wrong candidate output shaped by the task text.

    Never calls a solver — independence preserved.
    """
    prompt = (task.prompt or "").lower()
    if "palindrome" in prompt:
        return (
            "def is_palindrome(s: str) -> bool:\n"
            "    return True  # always-true canary\n"
        )
    if "clamp" in prompt:
        return "def clamp(x, lo, hi):\n    return x  # identity canary\n"
    if "chunk" in prompt:
        return "def chunk(lst, n):\n    return [lst]  # no split canary\n"
    if "parse_money" in prompt or "cents" in prompt:
        return (
            "def parse_money(text: str) -> int:\n"
            "    return 0  # always-zero canary\n"
        )
    if any(k in prompt for k in ("add(", "sum of", "a + b")):
        return "def add(a, b):\n    return a - b  # off-by-sign canary\n"
    if any(k in prompt for k in ("sort", "sorted")) and "palindrome" not in prompt:
        return "[3, 1, 2]"
    if "reverse_string" in prompt or (
        "reverse" in prompt and "palindrome" not in prompt
    ):
        return "def reverse_string(s):\n    return s  # identity canary\n"
    if any(k in prompt for k in ("flatten", "dict", "json", "transform")):
        return "{}"
    if not prompt.strip():
        return ""
    return KNOWN_BAD


def known_good_for_task(task: Task) -> str | None:
    """Trivial correct candidate for positive canary (optional)."""
    prompt = (task.prompt or "").lower()
    if "palindrome" in prompt:
        return "def is_palindrome(s: str) -> bool:\n    return s == s[::-1]\n"
    if "clamp" in prompt:
        return (
            "def clamp(x, lo, hi):\n"
            "    if lo > hi:\n"
            "        lo, hi = hi, lo\n"
            "    return min(max(x, lo), hi)\n"
        )
    if "chunk" in prompt:
        return (
            "def chunk(lst, n):\n"
            "    if n < 1:\n"
            "        raise ValueError('n')\n"
            "    return [lst[i:i+n] for i in range(0, len(lst), n)]\n"
        )
    if "reverse_string" in prompt:
        return "def reverse_string(s: str) -> str:\n    return s[::-1]\n"
    return None


def canary_rejects(meta: VerifierMeta, known_bad: str = KNOWN_BAD) -> bool:
    """Return True if the checker correctly fails known-bad output."""
    try:
        return check_output(meta, known_bad) is False
    except Exception:
        return False


def canary_accepts_good(meta: VerifierMeta, known_good: str) -> bool:
    """Return True if the checker accepts a known-correct candidate."""
    try:
        return check_output(meta, known_good) is True
    except Exception:
        return False


def canary_ok(meta: VerifierMeta, task: Task) -> tuple[bool, str]:
    """Full canary: reject known_bad, and accept known_good when available."""
    bad = known_bad_for_task(task)
    if not canary_rejects(meta, bad):
        return False, f"canary failed: checker accepted known_bad {bad!r}"
    good = known_good_for_task(task)
    if good is not None and not canary_accepts_good(meta, good):
        return False, f"canary failed: checker rejected known_good {good!r}"
    detail = f"canary rejected known_bad {bad!r}"
    if good is not None:
        detail += " and accepted known_good"
    return True, detail
