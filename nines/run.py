from __future__ import annotations

from .cost import accumulate, remaining
from .solver.call import solve_once
from .solver.diverse import diversity_configs
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

    batch_size = initial_batch
    while True:
        configs = diversity_configs(batch_size)
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
        budget_exhausted = (
            trials >= max_attempts or remaining(b.max_cost_usd, total_cost) <= 0
        )

        # Task 4 will replace this with Wilson gating; for now never claim met
        # unless escalate is disabled after a fixed batch.
        if not escalate or budget_exhausted:
            break
        # Placeholder escalate: one more batch then stop (filled in Task 4).
        if trials >= max_attempts:
            break
        batch_size = min(batch_size, max_attempts - trials)
        if batch_size <= 0:
            break
        # Without Wilson yet, do not infinite-loop.
        break

    trials = len(attempts)
    detail = None
    if passes == 0:
        detail = "zero passing candidates; refusing silent best-guess"
    elif not escalate:
        detail = "fixed batch complete"

    return Receipt(
        task=t,
        target=target,
        verifiable=True,
        target_met=False,
        attempts=attempts,
        passes=passes,
        trials=trials,
        wilson_low=None,
        wilson_high=None,
        confidence=confidence,
        total_cost_usd=total_cost,
        best_output=best_output,
        detail=detail,
    )
