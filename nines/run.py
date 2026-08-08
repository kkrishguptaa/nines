from __future__ import annotations

from .types import Budget, Receipt, Task


def run(
    task: Task | str,
    *,
    target: float = 0.8,
    budget: Budget | None = None,
    **ports,
) -> Receipt:
    t = task if isinstance(task, Task) else Task(prompt=task)
    _ = budget or Budget(max_cost_usd=5.0, max_attempts=8)
    _ = ports
    return Receipt(
        task=t,
        target=target,
        verifiable=False,
        target_met=False,
        attempts=[],
        passes=0,
        trials=0,
        wilson_low=None,
        wilson_high=None,
        confidence="high",
        total_cost_usd=0.0,
        best_output=None,
        detail="stub: not implemented",
    )
