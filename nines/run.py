from __future__ import annotations

from .cost import accumulate, remaining
from .solver.call import solve_once
from .solver.diverse import diversity_configs
from .stats.wilson import target_met as wilson_target_met
from .stats.wilson import wilson_interval
from .types import Attempt, Budget, Receipt, Task
from .verifier.execute import check_output
from .verifier.synthesize import synthesize_verifier
from .verifier.tiers import VerifierTier


def run(
    task: Task | str,
    *,
    target: float = 0.8,
    budget: Budget | None = None,
    **ports,
) -> Receipt:
    t = task if isinstance(task, Task) else Task(prompt=task)
    b = budget or Budget(max_cost_usd=5.0, max_attempts=8)

    synthesizer = ports.get("synthesizer")
    llm = ports.get("llm")
    solver = ports.get("solver")
    initial_batch = int(ports.get("initial_batch") or min(b.max_attempts or 8, 8))
    escalate = ports.get("escalate", True)

    meta = synthesize_verifier(t, llm=llm, synthesizer=synthesizer)

    if meta is None:
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
            detail="unverifiable: no usable checker after synthesis/canary",
        )

    confidence = "low" if meta.tier == int(VerifierTier.LLM_RUBRIC) else "high"
    attempts: list[Attempt] = []
    passes = 0
    total_cost = 0.0
    best_output: str | None = None
    max_attempts = b.max_attempts if b.max_attempts is not None else 10**9
    wilson_low: float | None = None
    wilson_high: float | None = None
    met = False

    batch_size = max(1, initial_batch)
    while True:
        room = max_attempts - len(attempts)
        if room <= 0 or remaining(b.max_cost_usd, total_cost) <= 0:
            break
        configs = diversity_configs(min(batch_size, room))
        for config in configs:
            if len(attempts) >= max_attempts:
                break
            if remaining(b.max_cost_usd, total_cost) <= 0:
                break
            try:
                output, cost = solve_once(t, config, llm=llm, solver=solver)
            except Exception as exc:  # noqa: BLE001 — record and continue
                attempts.append(
                    Attempt(
                        config=config,
                        output=None,
                        passed=False,
                        cost_usd=0.0,
                        error=str(exc),
                    )
                )
                continue
            # Pre-check cost ceiling: if this attempt would exceed, stop before spend.
            if total_cost + cost > b.max_cost_usd and attempts:
                break
            total_cost = accumulate(total_cost, cost)
            try:
                ok = check_output(meta, output)
            except Exception as exc:  # noqa: BLE001
                attempts.append(
                    Attempt(
                        config=config,
                        output=output,
                        passed=False,
                        cost_usd=cost,
                        error=f"checker error: {exc}",
                    )
                )
                continue
            attempts.append(
                Attempt(
                    config=config,
                    output=output,
                    passed=ok,
                    cost_usd=cost,
                    error=None,
                )
            )
            if ok:
                passes += 1
                if best_output is None:
                    best_output = output

        trials = len(attempts)
        if trials > 0:
            wilson_low, wilson_high = wilson_interval(passes, trials)
            met = wilson_target_met(passes, trials, target)
        else:
            met = False

        if met:
            break

        budget_exhausted = (
            trials >= max_attempts or remaining(b.max_cost_usd, total_cost) <= 0
        )
        if not escalate or budget_exhausted:
            break

        # Escalate batch size (capped by remaining attempts).
        batch_size = min(max(batch_size, initial_batch), max_attempts - trials)
        if batch_size <= 0:
            break

    trials = len(attempts)
    detail = None
    if passes == 0:
        detail = "zero passing candidates; refusing silent best-guess"
    elif not met:
        detail = "budget exhausted before Wilson lower bound cleared target"
    else:
        detail = "target met via Wilson lower bound"

    return Receipt(
        task=t,
        target=target,
        verifiable=True,
        target_met=met,
        attempts=attempts,
        passes=passes,
        trials=trials,
        wilson_low=wilson_low,
        wilson_high=wilson_high,
        confidence=confidence,
        total_cost_usd=total_cost,
        best_output=best_output if passes > 0 else None,
        detail=detail,
    )
