#!/usr/bin/env python3
"""The whole product in ~15 lines. Live Claude. ~$0.02.

    python examples/minimal.py
"""

from nines import Budget, Task, run

task = Task(
    prompt=(
        "Write is_palindrome(s: str) -> bool. "
        "Empty string is True. Code only."
    )
)

receipt = run(
    task,
    target=0.7,
    budget=Budget(max_cost_usd=1.0, max_attempts=15),
)

print("target_met:", receipt.target_met)
print("passes/trials:", f"{receipt.passes}/{receipt.trials}")
print("wilson_low:", receipt.wilson_low)
print("--- best_output ---")
print(receipt.best_output)
