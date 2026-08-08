from nines import run, Task, Budget
from tests.fakes import FakeSolver, FakeSynthesizer


def test_defaults_use_anthropic_when_key_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    called = {"synth": 0, "solve": 0}

    class S:
        def __call__(self, task, **kw):
            called["synth"] += 1
            return FakeSynthesizer.ok_checker()(task)

    class V:
        def __call__(self, task, config, **kw):
            called["solve"] += 1
            return "PASS", 0.01

    monkeypatch.setattr("nines.solver.anthropic_llm.AnthropicSynthesizer", lambda: S())
    monkeypatch.setattr("nines.solver.anthropic_llm.AnthropicSolver", lambda: V())
    r = run(
        Task(prompt="implement add"),
        target=0.55,
        budget=Budget(max_cost_usd=1.0, max_attempts=5),
        initial_batch=5,
        escalate=False,
        parallel=False,
    )
    assert called["synth"] >= 1 and called["solve"] >= 1
    assert r.verifiable is True


def test_injected_ports_still_override(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    r = run(
        Task(prompt="poem"),
        target=0.9,
        budget=Budget(max_cost_usd=1.0),
        synthesizer=FakeSynthesizer(result=None),
        solver=FakeSolver(),
    )
    assert r.verifiable is False and r.attempts == []
