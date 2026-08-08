from __future__ import annotations


def accumulate(total: float, amount: float) -> float:
    return total + amount


def remaining(budget_max: float, spent: float) -> float:
    return max(0.0, budget_max - spent)
