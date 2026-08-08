from nines import run, Task, Budget
from nines.solver.call import RateLimitError, solve_once
from tests.fakes import FakeSynthesizer, FlakyRateLimitSolver


def test_solver_retries_on_rate_limit():
    solver = FlakyRateLimitSolver(fail_times=2)
    task = Task(prompt="implement add(a,b)")
    output, cost = solve_once(
        task,
        {"model": "sonnet", "effort": "low", "framing": "direct"},
        solver=solver,
    )
    assert output == "PASS"
    assert cost == solver.cost_usd
    assert solver.calls >= 3


def test_run_survives_rate_limits_via_retry():
    solver = FlakyRateLimitSolver(fail_times=1)
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.1,
        budget=Budget(max_cost_usd=10.0, max_attempts=2),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=solver,
        initial_batch=2,
        escalate=False,
    )
    assert receipt.trials == 2
    assert receipt.passes >= 1
    assert not any(
        a.error and "rate" in (a.error or "").lower() for a in receipt.attempts
    )


def test_rate_limit_error_type_exported():
    assert issubclass(RateLimitError, Exception)
