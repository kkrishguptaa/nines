from __future__ import annotations

import random
import threading
import time
from typing import Any, Callable

from nines.types import Task

Solver = Callable[..., tuple[str, float]]

# Cap live concurrency for demo stability (T8: 4–5).
_SEMAPHORE = threading.Semaphore(5)
MAX_WORKERS = 5


class RateLimitError(Exception):
    """Raised when an upstream model API returns HTTP 429."""


def solve_once(
    task: Task,
    config: dict,
    *,
    llm: Any = None,
    solver: Solver | None = None,
    max_retries: int = 5,
    base_delay_s: float = 0.05,
) -> tuple[str, float]:
    """Run one solver attempt with semaphore + exponential backoff on 429."""
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            with _SEMAPHORE:
                if solver is not None:
                    return solver(task, config, llm=llm)
                if llm is None:
                    raise RuntimeError("no solver or llm provided")
                return _call_llm(task, config, llm=llm)
        except RateLimitError as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            delay = base_delay_s * (2**attempt) + random.uniform(0, base_delay_s)
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def _call_llm(task: Task, config: dict, *, llm: Any) -> tuple[str, float]:
    framing = config.get("framing", "direct")
    prompt = _framed_prompt(task, framing)
    model = config.get("model", "sonnet")
    effort = config.get("effort", "medium")
    text, cost = llm(prompt, model=model, effort=effort)
    return text, float(cost)


def _framed_prompt(task: Task, framing: str) -> str:
    base = task.prompt
    if task.context:
        base = f"{base}\n\nContext:\n{task.context}"
    if framing.startswith("decompose"):
        return (
            "Decompose the task into steps, then produce the final answer only "
            f"after reasoning.\n\nTask:\n{base}"
        )
    if framing.startswith("checklist"):
        return (
            "Solve the task. Before finalizing, checklist: correctness, edge "
            f"cases, format.\n\nTask:\n{base}"
        )
    return f"Solve the following task.\n\nTask:\n{base}"
