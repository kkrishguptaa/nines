#!/usr/bin/env python3
"""Live smoke: five unseen task shapes against bare nines.run (API key required)."""

from __future__ import annotations

import json
import os
import sys

from nines import Budget, Task, run

TASKS = [
    Task(
        prompt=(
            "Write a Python function reverse_string(s: str) -> str that returns "
            "s reversed. Respond with ONLY the function source."
        )
    ),
    Task(
        prompt=(
            "Write a Python function clamp(x, lo, hi) that returns x limited to "
            "[lo, hi]. Handle lo>hi by swapping. Edge cases: negatives, equals. "
            "Code only."
        )
    ),
    Task(
        prompt=(
            "Write a Python function flatten_dict(d) that flattens one level of "
            "nested dicts into dot-keys, e.g. {'a': {'b': 1}} -> {'a.b': 1}. "
            "Code only."
        )
    ),
    Task(
        prompt=(
            "Write a Python function ensure_sorted(nums: list[int]) -> list[int] "
            "that returns a new list sorted ascending. Output MUST be sorted. "
            "Code only."
        )
    ),
    Task(
        prompt="Write a short poem about the ocean at dusk.",
    ),
]


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY unset; skipping live smoke", file=sys.stderr)
        return 2
    budget = Budget(max_cost_usd=2.0, max_attempts=25)
    results = []
    for task in TASKS:
        receipt = run(task, target=0.7, budget=budget, initial_batch=5)
        row = {
            "task": task.prompt[:80],
            "verifiable": receipt.verifiable,
            "target_met": receipt.target_met,
            "trials": receipt.trials,
            "passes": receipt.passes,
            "checker_validated": receipt.checker_validated,
            "detail": receipt.detail,
            "canary_detail": receipt.canary_detail,
        }
        print(json.dumps(row))
        results.append((task, receipt))

    verifiable = sum(1 for _, r in results if r.verifiable)
    poem = results[-1][1]
    print(
        json.dumps(
            {
                "summary": {
                    "verifiable_count": verifiable,
                    "poem_verifiable": poem.verifiable,
                    "poem_attempts": len(poem.attempts),
                }
            }
        )
    )
    ok = verifiable >= 4 and poem.verifiable is False and poem.attempts == []
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
