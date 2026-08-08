#!/usr/bin/env python3
"""Two-task demo arc: clean win (is_palindrome) then hard billing parse.

Demo command (live API key required):

    python examples/demo_arc.py

1) is_palindrome @ target=0.7 — should clear (mechanism works)
2) parse_money (strict) @ target=0.7 — usually refuses; always prints
   per-model rates + failure reasons
"""

from __future__ import annotations

import json
import os
import sys
import time

from nines import Budget, Task, run
from nines.report import format_config_line, format_failure_summary

PALINDROME = Task(
    prompt=(
        "Write a Python function is_palindrome(s: str) -> bool that returns True "
        "iff s equals its reverse. Case-sensitive, spaces matter. Empty string is True. "
        "Code only."
    )
)

# Strict billing parser — many edges; models usually miss some under the checker.
PARSE_MONEY = Task(
    prompt=(
        "Write a Python function parse_money(text: str) -> int for checkout.\n"
        "Return integer cents. Rules (all mandatory):\n"
        "1) Accept only an optional leading '$', optional thousands commas in US "
        "grouping (e.g. 1,234,567), and optional '.' with 0–2 decimal digits.\n"
        "2) Examples that MUST work: '$1,234.56'->123456, '1234.5'->123450, "
        "'12'->1200, '  $0.99 '->99, '$.5'->50, '0'->0.\n"
        "3) MUST raise ValueError for: '', '  ', '-1', '+1', '1.2.3', 'abc', "
        "'1.234' (>2 decimals), '1,23' (EU-style), '12,34.56' (bad grouping), "
        "'$€1', '1 234.56' (spaces inside), '--1', 'NaN'.\n"
        "4) Do not accept bare commas as decimal separators.\n"
        "Respond with ONLY the function source."
    ),
    context="Wrong cents = wrong charges. Checker is strict.",
)


def _print_receipt(label: str, receipt, elapsed: float) -> None:
    wilson = (
        f"[{receipt.wilson_low:.2f}, {receipt.wilson_high:.2f}]"
        if receipt.wilson_low is not None and receipt.wilson_high is not None
        else "n/a"
    )
    print("=" * 60)
    print(f"{label}")
    print("=" * 60)
    print(
        json.dumps(
            {
                "elapsed_s": round(elapsed, 1),
                "verifiable": receipt.verifiable,
                "checker_validated": receipt.checker_validated,
                "target": receipt.target,
                "target_met": receipt.target_met,
                "passes": receipt.passes,
                "trials": receipt.trials,
                "wilson": wilson,
                "total_cost_usd": round(receipt.total_cost_usd, 4),
                "detail": receipt.detail,
                "canary_detail": receipt.canary_detail,
                "by_model": format_config_line(receipt),
                "failures": format_failure_summary(receipt),
                "best_output_preview": (receipt.best_output or "")[:240],
            },
            indent=2,
        )
    )


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY required for demo_arc", file=sys.stderr)
        return 2

    budget = Budget(max_cost_usd=3.0, max_attempts=25)
    t0 = time.time()
    r1 = run(PALINDROME, target=0.7, budget=budget, initial_batch=5, max_workers=5)
    _print_receipt("1/2 CLEAN WIN — is_palindrome (target=0.7)", r1, time.time() - t0)

    t1 = time.time()
    r2 = run(PARSE_MONEY, target=0.7, budget=budget, initial_batch=5, max_workers=5)
    _print_receipt(
        "2/2 HARD TASK — parse_money strict (target=0.7)", r2, time.time() - t1
    )

    total = time.time() - t0
    print("=" * 60)
    print(
        f"TOTAL {total:.1f}s | "
        f"palindrome target_met={r1.target_met} | "
        f"parse_money target_met={r2.target_met}"
    )
    # Non-negotiable: clean task must clear. Hard task prints why either way.
    return 0 if r1.target_met else 1


if __name__ == "__main__":
    raise SystemExit(main())
