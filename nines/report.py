from __future__ import annotations

from collections import Counter
from nines.types import Attempt, Receipt


def per_config_rates(attempts: list[Attempt]) -> list[str]:
    """Return display lines like ``opus: 7/9`` grouped by model."""
    tallies: dict[str, list[int]] = {}
    for a in attempts:
        key = str(a.config.get("model", "unknown"))
        passes, trials = tallies.setdefault(key, [0, 0])
        trials += 1
        if a.passed:
            passes += 1
        tallies[key] = [passes, trials]
    # Stable order: opus, sonnet, haiku, then others
    order = ["opus", "sonnet", "haiku"]
    keys = [k for k in order if k in tallies] + sorted(
        k for k in tallies if k not in order
    )
    return [f"{k}: {tallies[k][0]}/{tallies[k][1]}" for k in keys]


def failure_frequencies(attempts: list[Attempt]) -> list[tuple[str, int]]:
    """Count fail reasons on rejected candidates."""
    c: Counter[str] = Counter()
    for a in attempts:
        if a.passed:
            continue
        reason = (a.fail_reason or a.error or "check returned False").strip()
        # Collapse long sandbox traces to first line
        reason = reason.splitlines()[0][:120]
        c[reason] += 1
    return c.most_common()


def format_config_line(receipt: Receipt) -> str:
    parts = per_config_rates(receipt.attempts)
    return " · ".join(parts) if parts else "(no attempts)"


def format_failure_summary(receipt: Receipt) -> str:
    freqs = failure_frequencies(receipt.attempts)
    if not freqs:
        return "failures: (none)"
    bits = [f"{n}× {reason}" for reason, n in freqs[:8]]
    return "failures: " + " | ".join(bits)
