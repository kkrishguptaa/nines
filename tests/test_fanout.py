from nines import run, Task, Budget
from tests.fakes import FakeSolver, FakeSynthesizer


def test_five_attempts_have_distinct_configs():
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.5,
        budget=Budget(max_cost_usd=10.0, max_attempts=5),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=FakeSolver(pass_indices={0, 2, 4}),
        initial_batch=5,
        escalate=False,
    )
    assert len(receipt.attempts) == 5
    configs = [tuple(sorted(a.config.items())) for a in receipt.attempts]
    assert len(set(configs)) == 5
    assert receipt.passes == 3
    assert receipt.best_output is not None


def test_zero_passes_never_silent_success():
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.5,
        budget=Budget(max_cost_usd=10.0, max_attempts=3),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=FakeSolver(pass_indices=set()),
        initial_batch=3,
        escalate=False,
    )
    assert receipt.passes == 0
    assert receipt.target_met is False
    assert receipt.best_output is None
    assert receipt.detail
