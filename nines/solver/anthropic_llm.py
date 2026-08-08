from __future__ import annotations

import os
from typing import Any

from nines.solver.call import RateLimitError
from nines.types import Task, VerifierMeta

_MODEL_MAP = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-5-20250929",
    "opus": "claude-opus-4-6",
}


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
        usage = getattr(msg, "usage", None)
        in_tok = getattr(usage, "input_tokens", 0) or 0
        out_tok = getattr(usage, "output_tokens", 0) or 0
        # Rough USD estimate; not a billing API.
        cost = in_tok * 3e-6 + out_tok * 15e-6
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
            "output solves the task. Prefer deterministic assertions. Do not solve "
            "the task. Return only the function source.\n\n"
            f"Task:\n{task.prompt}"
        )
        if task.context:
            prompt += f"\n\nContext:\n{task.context}"
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
        if "def check" not in text:
            return None
        start = text.find("def check")
        source = text[start:].strip()
        # Trim markdown fences if present.
        if "```" in source:
            source = source.split("```")[0].strip()
        return VerifierMeta(
            tier=2,
            source_code=source,
            rubric=None,
            canary_passed=False,
        )
