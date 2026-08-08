from __future__ import annotations

from typing import Any, Callable

from nines.types import Task, VerifierMeta
from nines.verifier.canary import canary_rejects
from nines.verifier.tiers import VerifierTier

Synthesizer = Callable[..., VerifierMeta | None]


def synthesize_verifier(
    task: Task,
    *,
    llm: Any = None,
    synthesizer: Synthesizer | None = None,
) -> VerifierMeta | None:
    """Produce an independent checker from the task alone.

    Returns None when the task is unverifiable or canary fails after retry.
    """
    if synthesizer is not None:
        meta = synthesizer(task, llm=llm)
    else:
        meta = _default_synthesize(task, llm=llm)

    if meta is None:
        return None

    if canary_rejects(meta):
        meta.canary_passed = True
        return meta

    # Regenerate once, then unverifiable.
    if synthesizer is not None:
        meta = synthesizer(task, llm=llm, regenerate=True)
    else:
        meta = _default_synthesize(task, llm=llm, regenerate=True)

    if meta is None:
        return None

    if canary_rejects(meta):
        meta.canary_passed = True
        return meta

    return None


def _default_synthesize(
    task: Task,
    *,
    llm: Any = None,
    regenerate: bool = False,
) -> VerifierMeta | None:
    """Live path: ask LLM for a check(output) script. Optional for unit tests."""
    if llm is None:
        return None
    prompt = (
        "From the following task description only, write a Python function "
        "`def check(output: str) -> bool` that returns True iff the candidate "
        "output solves the task. Prefer Hypothesis properties or deterministic "
        "assertions. Do not solve the task. Return only the function source.\n\n"
        f"Task:\n{task.prompt}"
    )
    if task.context:
        prompt += f"\n\nContext:\n{task.context}"
    if regenerate:
        prompt += (
            "\n\nPrevious checker failed a known-bad canary (it accepted bad "
            "output). Emit a stricter check that rejects empty/placeholder "
            "strings and requires real task evidence."
        )
    text = llm(prompt)
    if not text or "def check" not in text:
        return None
    source = _extract_check_source(text)
    if not source:
        return None
    tier = VerifierTier.DETERMINISTIC
    if "hypothesis" in source.lower():
        tier = VerifierTier.HYPOTHESIS
    if "rubric" in source.lower() or getattr(llm, "tier", None) == 3:
        tier = VerifierTier.LLM_RUBRIC
    return VerifierMeta(
        tier=int(tier),
        source_code=source,
        rubric=None,
        canary_passed=False,
    )


def _extract_check_source(text: str) -> str | None:
    start = text.find("def check")
    if start < 0:
        return None
    source = text[start:].strip()
    # Drop a trailing markdown fence if the model wrapped the function.
    if "```" in source:
        source = source.split("```", 1)[0].rstrip()
    return source or None
