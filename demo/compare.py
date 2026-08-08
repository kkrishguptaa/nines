from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import Any, Callable

from nines import Budget, Receipt, Task, run
from nines.types import Attempt, VerifierMeta
from nines.verifier.canary import canary_rejects
from nines.verifier.execute import check_output

Solver = Callable[..., tuple[str, float]]


def compare(
    task: Task,
    *,
    trials: int,
    target: float,
    single_shot: Solver | None = None,
    nines_ports: dict[str, Any] | None = None,
    budget: Budget | None = None,
    on_attempt: Callable[[str, Attempt], None] | None = None,
    checker: VerifierMeta | None = None,
) -> dict[str, Any]:
    """Run single-shot and Nines over the same trial count."""
    ports = dict(nines_ports or {})
    b = budget or Budget(max_cost_usd=5.0, max_attempts=trials)

    # Single-shot path: N independent solves gated by the same checker when available.
    synth = ports.get("synthesizer")
    meta = checker
    if meta is None and synth is not None:
        meta = synth(task)
        if meta is not None and not canary_rejects(meta):
            meta = None

    ss_passes = 0
    ss_attempts: list[Attempt] = []
    solver = single_shot or ports.get("solver")
    if solver is None:
        raise ValueError("single_shot solver required (or nines_ports['solver'])")

    for i in range(trials):
        config = {"model": "sonnet", "effort": "medium", "framing": "direct", "trial": i}
        output, cost = solver(task, config)
        passed = False
        err = None
        if meta is not None:
            try:
                passed = check_output(meta, output)
            except Exception as exc:  # noqa: BLE001
                err = str(exc)
                passed = False
        else:
            # Without a checker, treat non-empty as a soft pass for demo visibility.
            passed = bool(output and output.strip())
        attempt = Attempt(
            config=config,
            output=output,
            passed=passed,
            cost_usd=cost,
            error=err,
        )
        ss_attempts.append(attempt)
        if passed:
            ss_passes += 1
        if on_attempt:
            on_attempt("single_shot", attempt)

    ports.setdefault("initial_batch", trials)
    ports.setdefault("escalate", False)
    nines_receipt: Receipt = run(
        task,
        target=target,
        budget=b,
        **ports,
    )
    for attempt in nines_receipt.attempts:
        if on_attempt:
            on_attempt("nines", attempt)

    ss_receipt = Receipt(
        task=task,
        target=target,
        verifiable=meta is not None,
        target_met=False,
        attempts=ss_attempts,
        passes=ss_passes,
        trials=len(ss_attempts),
        wilson_low=None,
        wilson_high=None,
        confidence="high",
        total_cost_usd=sum(a.cost_usd for a in ss_attempts),
        best_output=next((a.output for a in ss_attempts if a.passed), None),
        detail="single-shot baseline",
    )

    return {
        "single_shot": ss_receipt,
        "nines": nines_receipt,
        "single_shot_passes": ss_passes,
        "single_shot_trials": trials,
    }


def _print_summary(result: dict[str, Any]) -> None:
    ss: Receipt = result["single_shot"]
    ni: Receipt = result["nines"]
    ss_rate = (ss.passes / ss.trials * 100) if ss.trials else 0.0
    wilson = (
        f"Wilson [{ni.wilson_low:.2f}, {ni.wilson_high:.2f}]"
        if ni.wilson_low is not None and ni.wilson_high is not None
        else "Wilson n/a"
    )
    print(f"single-shot: {ss.passes}/{ss.trials} ({ss_rate:.0f}%)")
    print(
        f"nines:       {ni.passes}/{ni.trials} ({wilson}) "
        f"target_met={ni.target_met} cost=${ni.total_cost_usd:.4f}"
    )


def _load_fallback_task() -> tuple[Task, VerifierMeta]:
    from demo.fallback_tasks import ADD, ADD_CHECKER

    meta = VerifierMeta(
        tier=2,
        source_code=ADD_CHECKER,
        rubric=None,
        canary_passed=True,
    )
    return ADD, meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare single-shot Claude vs Nines")
    parser.add_argument("--task", help="Task prompt text (or demo/fallback_tasks.py:ADD)")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--target", type=float, default=0.8)
    parser.add_argument("--fallback", action="store_true", help="Use pre-seeded ADD task")
    parser.add_argument("--budget", type=float, default=5.0)
    args = parser.parse_args(argv)

    checker = None
    if args.fallback or not args.task:
        task, checker = _load_fallback_task()
    elif args.task.endswith(":ADD") or args.task.endswith("fallback_tasks.py:ADD"):
        task, checker = _load_fallback_task()
    else:
        task = Task(prompt=args.task)

    def on_attempt(path: str, attempt: Attempt) -> None:
        status = "PASS" if attempt.passed else "FAIL"
        print(f"[{path}] {status} model={attempt.config.get('model')} cost=${attempt.cost_usd:.4f}")

    import os

    class _Echo:
        """Labeled mock solver for demo shape without live API spend."""

        def __call__(self, task: Task, config: dict, **kwargs):
            return "def add(a, b):\n    return a + b\n", 0.0

    live_solver = None
    live_synth = None
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            from nines.solver.anthropic_llm import AnthropicSolver, AnthropicSynthesizer

            live_solver = AnthropicSolver()
            live_synth = AnthropicSynthesizer()
        except ImportError:
            print(
                "Live Anthropic adapter not available; using labeled mock solver.",
                file=sys.stderr,
            )

    try:
        if live_solver is not None:
            synth = live_synth if checker is None else (lambda t, **k: checker)
            result = compare(
                task,
                trials=args.trials,
                target=args.target,
                single_shot=live_solver,
                nines_ports={"synthesizer": synth, "solver": live_solver},
                budget=Budget(max_cost_usd=args.budget, max_attempts=args.trials),
                on_attempt=on_attempt,
                checker=checker,
            )
        else:
            if not os.environ.get("ANTHROPIC_API_KEY"):
                print(
                    "ANTHROPIC_API_KEY not set; using labeled mock solver.",
                    file=sys.stderr,
                )
            echo = _Echo()
            result = compare(
                task,
                trials=args.trials,
                target=args.target,
                single_shot=echo,
                nines_ports={
                    "synthesizer": (lambda t, **k: checker) if checker else None,
                    "solver": echo,
                },
                budget=Budget(max_cost_usd=args.budget, max_attempts=args.trials),
                on_attempt=on_attempt,
                checker=checker,
            )
    except Exception as exc:  # noqa: BLE001
        print(f"compare failed: {exc}", file=sys.stderr)
        return 1

    _print_summary(result)
    print(json.dumps(asdict(result["nines"]), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
