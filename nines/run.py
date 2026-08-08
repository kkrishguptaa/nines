from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from .cost import accumulate, remaining
from .solver.call import MAX_WORKERS, solve_once
from .solver.diverse import diversity_configs
from .stats.wilson import max_achievable_lower_bound
from .stats.wilson import target_met as wilson_target_met
from .stats.wilson import wilson_interval
from .types import Attempt, Budget, Receipt, Task
from .verifier.execute import check_output_detailed
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
    parallel = bool(ports.get("parallel", True))
    on_attempt = ports.get("on_attempt")
    max_workers = int(ports.get("max_workers") or MAX_WORKERS)
    models = ports.get("models")
    if models is not None:
        models = tuple(models)
        if not models:
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
                detail="models: empty selection; pass at least one of opus/sonnet/haiku",
                checker_validated=False,
                canary_detail="skipped: empty models",
            )

    cap = max_achievable_lower_bound(b.max_attempts)
    if target > cap:
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
            detail=(
                f"unreachable: target {target} exceeds best Wilson lower bound "
                f"{cap:.4f} for max_attempts={b.max_attempts}"
            ),
            checker_validated=False,
            canary_detail="skipped: unreachable target",
        )

    # Default live ports only when nothing is injected and a key is present.
    if (
        synthesizer is None
        and solver is None
        and llm is None
        and os.environ.get("ANTHROPIC_API_KEY")
    ):
        from nines.solver.anthropic_llm import AnthropicSolver, AnthropicSynthesizer

        synthesizer = AnthropicSynthesizer()
        solver = AnthropicSolver()

    meta, canary_detail = synthesize_verifier(
        t, llm=llm, synthesizer=synthesizer, return_detail=True
    )

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
            detail=canary_detail
            or "unverifiable: no usable checker after synthesis/canary",
            checker_validated=False,
            canary_detail=canary_detail or "canary failed or synthesis returned None",
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
    checker_validated = bool(meta.canary_passed)
    canary_ok_detail = canary_detail or "canary rejected known_bad"

    def _solve_one(config: dict) -> Attempt:
        try:
            output, cost = solve_once(t, config, llm=llm, solver=solver)
        except Exception as exc:  # noqa: BLE001
            return Attempt(
                config=config,
                output=None,
                passed=False,
                cost_usd=0.0,
                error=str(exc),
                fail_reason=str(exc),
            )
        ok, reason = check_output_detailed(meta, output)
        return Attempt(
            config=config,
            output=output,
            passed=ok,
            cost_usd=cost,
            error=None if ok else reason,
            fail_reason=None if ok else reason,
        )

    batch_size = max(1, initial_batch)
    while True:
        room = max_attempts - len(attempts)
        if room <= 0 or remaining(b.max_cost_usd, total_cost) <= 0:
            break
        before = len(attempts)
        configs = diversity_configs(
            min(batch_size, room), start=len(attempts), models=models
        )
        if not configs:
            break

        batch_attempts: list[Attempt]
        if parallel and len(configs) > 1:
            batch_attempts = []
            with ThreadPoolExecutor(max_workers=max(1, min(max_workers, len(configs)))) as pool:
                futures = [pool.submit(_solve_one, cfg) for cfg in configs]
                for fut in as_completed(futures):
                    batch_attempts.append(fut.result())
            # Stable display order by original config sequence
            order = {json_key(c): i for i, c in enumerate(configs)}
            batch_attempts.sort(key=lambda a: order.get(json_key(a.config), 0))
        else:
            batch_attempts = [_solve_one(cfg) for cfg in configs]

        for attempt in batch_attempts:
            if len(attempts) >= max_attempts:
                break
            total_cost = accumulate(total_cost, attempt.cost_usd)
            attempts.append(attempt)
            if attempt.passed:
                passes += 1
                if best_output is None and attempt.output:
                    best_output = attempt.output
            if on_attempt is not None:
                on_attempt(attempt)

        trials = len(attempts)
        if trials == before:
            break

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

        next_size = max(batch_size * 2, batch_size + 1)
        batch_size = min(next_size, max_attempts - trials)
        if batch_size <= 0:
            break

    trials = len(attempts)
    if passes == 0:
        detail = "zero passing candidates; refusing silent best-guess"
    elif met:
        detail = "target met via Wilson lower bound"
    elif not escalate:
        detail = "fixed batch complete; Wilson lower bound did not clear target"
    else:
        detail = "budget exhausted before Wilson lower bound cleared target"

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
        checker_validated=checker_validated,
        canary_detail=canary_ok_detail,
    )


def json_key(config: dict) -> tuple:
    return (
        config.get("model"),
        config.get("effort"),
        config.get("framing"),
        config.get("trial"),
    )
