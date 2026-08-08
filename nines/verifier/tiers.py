from __future__ import annotations

from enum import IntEnum


class VerifierTier(IntEnum):
    HYPOTHESIS = 1
    DETERMINISTIC = 2
    LLM_RUBRIC = 3
