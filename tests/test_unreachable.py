from nines import run, Task, Budget
from nines.stats.wilson import max_achievable_lower_bound
from tests.fakes import FakeSolver, FakeSynthesizer


def test_max_achievable_five_below_point_six():
    assert max_achievable_lower_bound(5) < 0.6


def test_unreachable_target_short_circuits_without_solver_calls():
    solver = FakeSolver(always_pass=True)
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.99,
        budget=Budget(max_cost_usd=10.0, max_attempts=5),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=solver,
    )
    assert receipt.target_met is False
    assert receipt.attempts == []
    assert solver.calls == 0
    assert "unreachable" in (receipt.detail or "").lower()


def test_reachable_target_can_meet():
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.55,
        budget=Budget(max_cost_usd=10.0, max_attempts=5),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=FakeSolver(always_pass=True),
        initial_batch=5,
        escalate=False,
        parallel=False,
    )
    assert receipt.target_met is True
    assert receipt.wilson_low is not None and receipt.wilson_low >= 0.55
