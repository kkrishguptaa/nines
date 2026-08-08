from __future__ import annotations

from typing import Any, Callable, Literal, overload

from nines.types import Task, VerifierMeta
from nines.verifier.canary import canary_ok
from nines.verifier.preamble import wrap_checker_source
from nines.verifier.tiers import VerifierTier

Synthesizer = Callable[..., VerifierMeta | None]


@overload
def synthesize_verifier(
    task: Task,
    *,
    llm: Any = None,
    synthesizer: Synthesizer | None = None,
    return_detail: Literal[False] = False,
) -> VerifierMeta | None: ...


@overload
def synthesize_verifier(
    task: Task,
    *,
    llm: Any = None,
    synthesizer: Synthesizer | None = None,
    return_detail: Literal[True],
) -> tuple[VerifierMeta | None, str]: ...


def synthesize_verifier(
    task: Task,
    *,
    llm: Any = None,
    synthesizer: Synthesizer | None = None,
    return_detail: bool = False,
) -> VerifierMeta | None | tuple[VerifierMeta | None, str]:
    """Produce an independent checker from the task alone.

    Returns None when the task is unverifiable or canary fails after retry.
    With return_detail=True, also returns a canary_detail string.
    """
    if _looks_subjective(task):
        detail = "unverifiable: task appears subjective / not mechanically checkable"
        return (None, detail) if return_detail else None

    if synthesizer is not None:
        meta = synthesizer(task, llm=llm)
    else:
        meta = _default_synthesize(task, llm=llm)

    if meta is None:
        detail = "unverifiable: synthesis returned no checker"
        return (None, detail) if return_detail else None

    ok, detail = canary_ok(meta, task)
    if ok:
        meta.canary_passed = True
        return (meta, detail) if return_detail else meta

    # Regenerate once, then unverifiable.
    if synthesizer is not None:
        meta = synthesizer(task, llm=llm, regenerate=True)
    else:
        meta = _default_synthesize(task, llm=llm, regenerate=True)

    if meta is None:
        detail = "canary failed: regeneration returned no checker"
        return (None, detail) if return_detail else None

    ok, detail = canary_ok(meta, task)
    if ok:
        meta.canary_passed = True
        detail = detail + " after regenerate"
        return (meta, detail) if return_detail else meta

    return (None, detail + " after retry") if return_detail else None


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
        "assertions. Call `_nines_strip_fences(output)` before exec (helper is "
        "pre-defined). Do not write markdown fence characters. Do not solve "
        "the task. Return only the function source.\n\n"
        f"Task:\n{task.prompt}"
    )
    if task.context:
        prompt += f"\n\nContext:\n{task.context}"
    if regenerate:
        prompt += (
            "\n\nPrevious checker failed canary (accepted known-bad or rejected "
            "known-good). Emit a stricter, correct check with concrete examples."
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
    if "UNSUPPORTED" in text and "def check" not in text:
        return None
    start = text.find("def check")
    if start < 0:
        return None
    source = text[start:].strip()
    fence = "`" * 3
    if source.endswith(fence):
        source = source[: -len(fence)].rstrip()
    return wrap_checker_source(source) if source else None


_SUBJECTIVE_MARKERS = (
    "poem",
    "poetry",
    "haiku",
    "essay",
    "story",
    "opinion",
    "review a movie",
    "what do you feel",
    "creative writing",
    "love letter",
)


def _looks_subjective(task: Task) -> bool:
    text = f"{task.prompt} {task.context or ''}".lower()
    return any(m in text for m in _SUBJECTIVE_MARKERS)
