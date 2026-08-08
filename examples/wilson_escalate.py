#!/usr/bin/env python3
"""Show Wilson gating: higher targets force more attempts."""

from __future__ import annotations

from nines import Budget, Task, run
from tests.fakes import FakeSolver, FakeSynthesizer


def main() -> None:
    task = Task(prompt="implement add(a, b)")
    for target in (0.5, 0.95):
        receipt = run(
            task,
            target=target,
            budget=Budget(max_cost_usd=50.0, max_attempts=40),
            synthesizer=FakeSynthesizer.ok_checker(),
            solver=FakeSolver(pass_rate=0.7, seed=42, cost_usd=0.01),
            initial_batch=5,
        )
        print(
            f"target={target:.2f}  trials={receipt.trials:2d}  "
            f"passes={receipt.passes:2d}  "
            f"wilson_low={receipt.wilson_low!s:>8}  "
            f"target_met={receipt.target_met}  "
            f"detail={receipt.detail}"
        )


if __name__ == "__main__":
    main()
