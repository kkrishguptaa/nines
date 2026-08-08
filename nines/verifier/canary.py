from __future__ import annotations

from nines.types import VerifierMeta
from nines.verifier.execute import check_output

KNOWN_BAD = "__NINES_CANARY_BAD__"


def canary_rejects(meta: VerifierMeta, known_bad: str = KNOWN_BAD) -> bool:
    """Return True if the checker correctly fails known-bad output."""
    try:
        return check_output(meta, known_bad) is False
    except Exception:
        return False
