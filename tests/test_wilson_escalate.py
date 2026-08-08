from nines import run, Task, Budget
from nines.stats.wilson import wilson_interval, target_met
from tests.fakes import FakeSolver, FakeSynthesizer


def test_wilson_five_of_five_not_99():
    low, high = wilson_interval(5, 5)
    assert low < 0.99
    assert target_met(5, 5, 0.99) is False


def test_higher_target_spends_more_attempts():
    easy_synth = FakeSynthesizer.ok_checker()
    solver_low = FakeSolver(pass_rate=0.7, seed=42, cost_usd=0.01)
    solver_high = FakeSolver(pass_rate=0.7, seed=42, cost_usd=0.01)
    r_low = run(
        Task(prompt="implement add(a,b)"),
        target=0.5,
        budget=Budget(max_cost_usd=50.0, max_attempts=40),
        synthesizer=easy_synth,
        solver=solver_low,
        initial_batch=5,
    )
    r_high = run(
        Task(prompt="implement add(a,b)"),
        target=0.95,
        budget=Budget(max_cost_usd=50.0, max_attempts=40),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=solver_high,
        initial_batch=5,
    )
    assert r_high.trials >= r_low.trials


def test_budget_exhaustion_flags_target_not_met():
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.99,
        budget=Budget(max_cost_usd=0.01, max_attempts=2),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=FakeSolver(always_pass=True, cost_usd=0.01),
        initial_batch=5,
    )
    assert receipt.target_met is False
    assert receipt.trials <= 2
