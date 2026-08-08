from __future__ import annotations

import math


def wilson_interval(
    passes: int, trials: int, z: float = 1.96
) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if trials <= 0:
        return (0.0, 1.0)
    p = passes / trials
    z2 = z * z
    denom = 1.0 + z2 / trials
    center = p + z2 / (2.0 * trials)
    margin = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * trials)) / trials)
    low = (center - margin) / denom
    high = (center + margin) / denom
    return (max(0.0, low), min(1.0, high))


def target_met(passes: int, trials: int, target: float, z: float = 1.96) -> bool:
    """True iff Wilson lower bound ≥ target."""
    if trials <= 0 or passes <= 0:
        return False
    low, _ = wilson_interval(passes, trials, z=z)
    return low >= target


def max_achievable_lower_bound(
    max_attempts: int | None, z: float = 1.96
) -> float:
    """Best possible Wilson lower bound if every attempt passes."""
    if max_attempts is None:
        return 1.0
    if max_attempts <= 0:
        return 0.0
    low, _ = wilson_interval(max_attempts, max_attempts, z=z)
    return low
