from nines import run, Task, Budget
from tests.fakes import FakeSynthesizer


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
