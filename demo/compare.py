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
        try:
            output, cost = solver(task, config)
            err = None
        except Exception as exc:  # noqa: BLE001 — match nines.run failure semantics
            output, cost, err = None, 0.0, str(exc)
        passed = False
        if err is None and meta is not None:
            try:
                passed = check_output(meta, output or "")
            except Exception as exc:  # noqa: BLE001
                err = str(exc)
                passed = False
        elif err is None:
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

    ports.setdefault("initial_batch", min(trials, 8))
    ports.setdefault("escalate", True)

    def _nines_cb(attempt: Attempt) -> None:
        if on_attempt:
            on_attempt("nines", attempt)

    ports["on_attempt"] = _nines_cb
    nines_receipt: Receipt = run(
        task,
        target=target,
        budget=b,
        **ports,
    )

    from nines.stats.wilson import target_met as wilson_target_met
    from nines.stats.wilson import wilson_interval

    ss_trials = len(ss_attempts)
    ss_low = ss_high = None
    ss_met = False
    if ss_trials > 0 and meta is not None:
        ss_low, ss_high = wilson_interval(ss_passes, ss_trials)
        ss_met = wilson_target_met(ss_passes, ss_trials, target)

    ss_detail = "single-shot baseline"
    if meta is None:
        ss_detail += " (soft-pass: no checker; non-empty output counts as pass)"

    ss_receipt = Receipt(
        task=task,
        target=target,
        verifiable=meta is not None,
        target_met=ss_met if meta is not None else False,
        attempts=ss_attempts,
        passes=ss_passes,
        trials=ss_trials,
        wilson_low=ss_low,
        wilson_high=ss_high,
        confidence="high",
        total_cost_usd=sum(a.cost_usd for a in ss_attempts),
        best_output=next((a.output for a in ss_attempts if a.passed), None),
        detail=ss_detail,
        checker_validated=bool(meta and meta.canary_passed),
        canary_detail=(
            "baseline uses shared checker"
            if meta is not None
            else "no checker (soft-pass)"
        ),
    )

    return {
        "single_shot": ss_receipt,
        "nines": nines_receipt,
        "single_shot_passes": ss_passes,
        "single_shot_trials": trials,
    }


def _print_summary(result: dict[str, Any]) -> None:
    from nines.report import format_config_line, format_failure_summary

    ss: Receipt = result["single_shot"]
    ni: Receipt = result["nines"]
    ss_rate = (ss.passes / ss.trials * 100) if ss.trials else 0.0
    wilson = (
        f"Wilson [{ni.wilson_low:.2f}, {ni.wilson_high:.2f}]"
        if ni.wilson_low is not None and ni.wilson_high is not None
        else "Wilson n/a"
    )
    soft = " [soft-pass, no checker]" if not ss.verifiable else ""
    print(
        f"[canary] validated={ni.checker_validated} detail={ni.canary_detail}"
    )
    print(f"single-shot: {ss.passes}/{ss.trials} ({ss_rate:.0f}%){soft} target_met={ss.target_met}")
    print(
        f"nines:       {ni.passes}/{ni.trials} ({wilson}) "
        f"target_met={ni.target_met} cost=${ni.total_cost_usd:.4f}"
    )
    print(f"by model:    {format_config_line(ni)}")
    print(format_failure_summary(ni))


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
    parser.add_argument("--trials", type=int, default=25)
    parser.add_argument("--target", type=float, default=0.7)
    parser.add_argument("--fallback", action="store_true", help="Use pre-seeded ADD task")
    parser.add_argument("--budget", type=float, default=5.0)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="No durable state; re-run is a clean reset (banner only)",
    )
    args = parser.parse_args(argv)
    if args.reset:
        print("reset: no durable state; this run is a clean demo slate", file=sys.stderr)

    checker = None
    if args.fallback or not args.task:
        task, checker = _load_fallback_task()
    elif args.task.endswith(":ADD") or args.task.endswith("fallback_tasks.py:ADD"):
        task, checker = _load_fallback_task()
    else:
        task = Task(prompt=args.task)

    import os

    from demo.rich_ui import DemoLive

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
        with DemoLive(target=args.target) as live:
            if checker is not None:
                live.set_canary(True, "fallback checker pre-validated")
            if live_solver is not None:
                synth = live_synth if checker is None else (lambda t, **k: checker)
                result = compare(
                    task,
                    trials=args.trials,
                    target=args.target,
                    single_shot=live_solver,
                    nines_ports={"synthesizer": synth, "solver": live_solver},
                    budget=Budget(max_cost_usd=args.budget, max_attempts=args.trials),
                    on_attempt=live.on_attempt,
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
                    on_attempt=live.on_attempt,
                    checker=checker,
                )
            live.finalize(result)
    except Exception as exc:  # noqa: BLE001
        print(f"compare failed: {exc}", file=sys.stderr)
        return 1

    _print_summary(result)
    print(json.dumps(asdict(result["nines"]), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
