from __future__ import annotations

from nines.sandbox import run_python
from nines.types import VerifierMeta


def check_output(meta: VerifierMeta, candidate: str) -> bool:
    """Run the checker against candidate output only (no solver reasoning)."""
    ok, _ = check_output_detailed(meta, candidate)
    return ok


def check_output_detailed(
    meta: VerifierMeta, candidate: str
) -> tuple[bool, str | None]:
    """Return (passed, fail_reason). fail_reason is set when not passed."""
    if meta.tier == 3 and not meta.source_code:
        return False, "no checker source (tier-3 stub)"
    if not meta.source_code:
        return False, "no checker source"
    try:
        result = run_python(meta.source_code, "check", [candidate], timeout_s=5.0)
    except Exception as exc:  # noqa: BLE001
        msg = str(exc).strip().splitlines()[-1] if str(exc).strip() else type(exc).__name__
        # Prefer AssertionError message when present in sandbox stderr text.
        text = str(exc)
        if "AssertionError" in text:
            for line in text.splitlines():
                if "AssertionError" in line:
                    msg = line.strip()
                    break
        return False, msg[:200]
    if bool(result):
        return True, None
    return False, "check returned False"
