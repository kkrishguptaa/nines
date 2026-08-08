from __future__ import annotations

from nines.sandbox import run_python
from nines.types import VerifierMeta


def check_output(meta: VerifierMeta, candidate: str) -> bool:
    """Run the checker against candidate output only (no solver reasoning)."""
    if meta.tier == 3:
        # Rubric graders are handled by the synthesizer/llm port; stub false
        # unless source_code provides an executable check.
        if not meta.source_code:
            return False
    if not meta.source_code:
        return False
    result = run_python(meta.source_code, "check", [candidate], timeout_s=5.0)
    return bool(result)
