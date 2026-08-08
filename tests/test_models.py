from nines import Budget, Task, run
from tests.fakes import FakeSolver, FakeSynthesizer


def test_run_models_filter_excludes_unlisted_tiers():
    """Caller can drop weak models so they do not drag the pooled rate."""
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.55,
        budget=Budget(max_cost_usd=1.0, max_attempts=9),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=FakeSolver(always_pass=True),
        models=("opus", "sonnet"),
        initial_batch=9,
        escalate=False,
        parallel=False,
    )
    used = {a.config["model"] for a in receipt.attempts}
    assert used == {"opus", "sonnet"}
    assert "haiku" not in used
    assert receipt.trials == 9


def test_run_models_rejects_empty():
    receipt = run(
        Task(prompt="implement add(a,b)"),
        target=0.55,
        budget=Budget(max_cost_usd=1.0, max_attempts=5),
        synthesizer=FakeSynthesizer.ok_checker(),
        solver=FakeSolver(always_pass=True),
        models=(),
        parallel=False,
    )
    assert receipt.verifiable is False
    assert "models" in (receipt.detail or "").lower()
