from __future__ import annotations

import os
from typing import Any

from nines.solver.call import RateLimitError
from nines.types import Task, VerifierMeta
from nines.verifier.preamble import wrap_checker_source

_MODEL_MAP = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-5-20250929",
    "opus": "claude-opus-4-6",
}

# Approximate USD per token (input, output). Not a billing API.
_RATE_USD = {
    "haiku": (1e-6, 5e-6),
    "sonnet": (3e-6, 15e-6),
    "opus": (15e-6, 75e-6),
}


def _estimate_cost(alias: str, in_tok: int, out_tok: int) -> float:
    inn, out = _RATE_USD.get(alias, _RATE_USD["sonnet"])
    return in_tok * inn + out_tok * out


def strip_code_fences(text: str) -> str:
    """Extract code from markdown fences when the whole reply is fenced."""
    text = text.strip()
    fence = "`" * 3
    if not text.startswith(fence):
        return text
    # Drop opening fence line, then cut at closing fence if present.
    rest = text[len(fence) :]
    if rest.startswith("python") or rest.startswith("py"):
        rest = rest.split("\n", 1)[1] if "\n" in rest else ""
    elif rest.startswith("\n"):
        rest = rest[1:]
    close = rest.rfind(fence)
    if close >= 0:
        rest = rest[:close]
    return rest.strip()


def _client():
    import anthropic

    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _unwrap_rate_limit(exc: Exception) -> None:
    name = type(exc).__name__
    status = getattr(exc, "status_code", None)
    if status == 429 or "RateLimit" in name or "rate_limit" in str(exc).lower():
        raise RateLimitError(str(exc)) from exc


class AnthropicSolver:
    """Live Claude solver. Costs are approximate token-based estimates."""

    def __init__(self, client: Any | None = None) -> None:
        self._client = client

    def __call__(self, task: Task, config: dict, **kwargs) -> tuple[str, float]:
        client = self._client or _client()
        model = _MODEL_MAP.get(config.get("model", "sonnet"), _MODEL_MAP["sonnet"])
        framing = config.get("framing", "direct")
        prompt = task.prompt
        if task.context:
            prompt = f"{prompt}\n\nContext:\n{task.context}"
        if framing.startswith("decompose"):
            prompt = f"Decompose then answer.\n\n{prompt}"
        elif framing.startswith("checklist"):
            prompt = f"Solve with a final checklist.\n\n{prompt}"
        prompt += (
            "\n\nRespond with ONLY the Python function source. No markdown "
            "fences, no explanation, no main(), no API client imports."
        )
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # noqa: BLE001
            _unwrap_rate_limit(exc)
            raise
        text = "".join(
            getattr(block, "text", "") for block in msg.content if hasattr(block, "text")
        )
        text = strip_code_fences(text)
        usage = getattr(msg, "usage", None)
        in_tok = getattr(usage, "input_tokens", 0) or 0
        out_tok = getattr(usage, "output_tokens", 0) or 0
        alias = config.get("model", "sonnet")
        cost = _estimate_cost(alias, in_tok, out_tok)
        return text, cost


class AnthropicSynthesizer:
    """Ask Claude for an independent check(output) script from the task alone."""

    def __init__(self, client: Any | None = None) -> None:
        self._client = client

    def __call__(self, task: Task, **kwargs) -> VerifierMeta | None:
        client = self._client or _client()
        prompt = (
            "From the following task description only, write a Python function "
            "`def check(output: str) -> bool` that returns True iff the candidate "
            "output solves the task.\n"
            "Rules:\n"
            "- Prefer deterministic assertions / exec + example calls\n"
            "- Call `_nines_strip_fences(output)` before exec (helper is pre-defined)\n"
            "- Do NOT write markdown fence characters in your source\n"
            "- MUST return False for empty output, syntax errors, missing function, "
            "identity/no-op wrong answers, and off-by-one bugs\n"
            "- Do NOT solve the task yourself\n"
            "- Return ONLY the function source starting at def check\n\n"
            f"Task:\n{task.prompt}"
        )
        if task.context:
            prompt += f"\n\nContext:\n{task.context}"
        if kwargs.get("regenerate"):
            prompt += (
                "\n\nCRITICAL: Previous checker accepted a known-bad canary "
                "(identity/wrong implementation). Write a NEW stricter check with "
                "concrete example assertions that that wrong answer fails."
            )
        try:
            msg = client.messages.create(
                model=_MODEL_MAP["sonnet"],
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # noqa: BLE001
            _unwrap_rate_limit(exc)
            raise
        text = "".join(
            getattr(block, "text", "") for block in msg.content if hasattr(block, "text")
        )
        text = strip_code_fences(text)
        if "UNSUPPORTED" in text and "def check" not in text:
            return None
        if "def check" not in text:
            return None
        start = text.find("def check")
        source = text[start:].strip()
        source = wrap_checker_source(source)
        return VerifierMeta(
            tier=2,
            source_code=source,
            rubric=None,
            canary_passed=False,
        )
