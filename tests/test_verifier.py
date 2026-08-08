from nines import run, Task, Budget
from tests.fakes import FakeSolver, FakeSynthesizer


def test_unverifiable_task_does_not_spend_solvers():
    synth = FakeSynthesizer(result=None)
    receipt = run(
        Task(prompt="write a poem"),
        target=0.9,
        budget=Budget(max_cost_usd=1.0),
        synthesizer=synth,
    )
    assert receipt.verifiable is False
    assert receipt.attempts == []
    assert receipt.detail  # explains unverifiable
    assert receipt.checker_validated is False
    assert receipt.canary_detail


def test_degenerate_checker_fails_canary_and_short_circuits():
    synth = FakeSynthesizer(degenerate=True)  # emits assert True
    receipt = run(
        Task(prompt="def add(a,b): ..."),
        target=0.8,
        budget=Budget(max_cost_usd=1.0),
        synthesizer=synth,
    )
    assert receipt.verifiable is False
    assert receipt.attempts == []
    assert receipt.checker_validated is False
    assert "canary" in (receipt.canary_detail or "").lower()


def test_ok_checker_sets_checker_validated_true():
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.55,
        budget=Budget(max_cost_usd=1.0, max_attempts=5),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=FakeSolver(always_pass=True),
        initial_batch=5,
        escalate=False,
    )
    assert receipt.checker_validated is True
    assert receipt.canary_detail
