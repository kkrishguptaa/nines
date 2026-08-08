from __future__ import annotations

from .types import Budget, Receipt, Task
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
    _ = budget or Budget(max_cost_usd=5.0, max_attempts=8)

    synthesizer = ports.get("synthesizer")
    llm = ports.get("llm")
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
    return Receipt(
        task=t,
        target=target,
        verifiable=True,
        target_met=False,
        attempts=[],
        passes=0,
        trials=0,
        wilson_low=None,
        wilson_high=None,
        confidence=confidence,
        total_cost_usd=0.0,
        best_output=None,
        detail="verifier ready; solver fan-out not yet implemented",
    )
