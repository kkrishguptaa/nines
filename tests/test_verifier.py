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
        parallel=False,
    )
    assert receipt.checker_validated is True
    assert receipt.canary_detail


def test_overstrict_checker_fails_known_good_canary():
    """Checker that rejects everything fails positive canary when known_good exists."""
    from nines.types import VerifierMeta

    source = (
        "def check(output: str) -> bool:\n"
        "    return False\n"
    )
    synth = FakeSynthesizer(
        result=VerifierMeta(
            tier=2, source_code=source, rubric=None, canary_passed=False
        )
    )
    receipt = run(
        Task(
            prompt=(
                "Write is_palindrome(s: str) -> bool. Empty string is True. Code only."
            )
        ),
        target=0.7,
        budget=Budget(max_cost_usd=1.0, max_attempts=25),
        synthesizer=synth,
        solver=FakeSolver(always_pass=True),
        parallel=False,
    )
    assert receipt.verifiable is False
    assert "known_good" in (receipt.canary_detail or "").lower()
    assert receipt.attempts == []
    assert receipt.target_met is False


def test_subjective_poem_short_circuits_without_solver():
    solver = FakeSolver(always_pass=True)
    receipt = run(
        Task(prompt="Write a short poem about the ocean at dusk."),
        target=0.7,
        budget=Budget(max_cost_usd=2.0, max_attempts=25),
        synthesizer=FakeSynthesizer.ok_checker(),  # would otherwise "work"
        solver=solver,
    )
    assert receipt.verifiable is False
    assert receipt.attempts == []
    assert solver.calls == 0
    assert "subjective" in (receipt.detail or "").lower()
