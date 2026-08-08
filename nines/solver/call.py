from __future__ import annotations

from typing import Any, Callable

from nines.types import Task

Solver = Callable[..., tuple[str, float]]


def solve_once(
    task: Task,
    config: dict,
    *,
    llm: Any = None,
    solver: Solver | None = None,
) -> tuple[str, float]:
    """Run one solver attempt; returns (output, cost_usd)."""
    if solver is not None:
        return solver(task, config, llm=llm)

    if llm is None:
        raise RuntimeError("no solver or llm provided")

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
