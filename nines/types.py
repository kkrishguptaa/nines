from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Task:
    prompt: str
    context: str | None = None


@dataclass
class Budget:
    max_cost_usd: float
    max_attempts: int | None = None


@dataclass
class Attempt:
    config: dict
    output: str | None
    passed: bool | None
    cost_usd: float
    error: str | None = None


@dataclass
class VerifierMeta:
    tier: int
    source_code: str | None
    rubric: str | None
    canary_passed: bool


@dataclass
class Receipt:
    task: Task
    target: float
    verifiable: bool
    target_met: bool
    attempts: list[Attempt]
    passes: int
    trials: int
    wilson_low: float | None
    wilson_high: float | None
    confidence: Literal["high", "low"]
    total_cost_usd: float
    best_output: str | None
    detail: str | None = None
