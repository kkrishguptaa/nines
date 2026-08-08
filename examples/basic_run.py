#!/usr/bin/env python3
"""Minimal nines.run example with labeled mock ports (no API spend)."""

from __future__ import annotations

from nines import Budget, Task, run
from tests.fakes import FakeSolver, FakeSynthesizer


def main() -> None:
    task = Task(prompt="implement add(a, b) that returns a + b")
    receipt = run(
        task,
        target=0.5,
        budget=Budget(max_cost_usd=1.0, max_attempts=5),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=FakeSolver(pass_indices={0, 2, 4}),
        initial_batch=5,
        escalate=False,
    )

    print("=== nines.run receipt ===")
    print(f"verifiable:   {receipt.verifiable}")
    print(f"target:       {receipt.target}")
    print(f"target_met:   {receipt.target_met}")
    print(f"passes/trials:{receipt.passes}/{receipt.trials}")
    print(f"wilson:       [{receipt.wilson_low}, {receipt.wilson_high}]")
    print(f"best_output:  {receipt.best_output!r}")
    print(f"detail:       {receipt.detail}")
    print("attempts:")
    for i, a in enumerate(receipt.attempts):
        print(
            f"  [{i}] passed={a.passed} model={a.config.get('model')} "
            f"effort={a.config.get('effort')} framing={a.config.get('framing')} "
            f"output={a.output!r}"
        )


if __name__ == "__main__":
    main()
