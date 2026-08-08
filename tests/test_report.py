from nines.report import failure_frequencies, format_config_line, per_config_rates
from nines.types import Attempt, Receipt, Task


def _attempt(model: str, passed: bool, reason: str | None = None) -> Attempt:
    return Attempt(
        config={"model": model, "effort": "low", "framing": "direct"},
        output="x",
        passed=passed,
        cost_usd=0.01,
        fail_reason=reason,
    )


def test_per_config_rates_display():
    attempts = [
        _attempt("opus", True),
        _attempt("opus", True),
        _attempt("opus", False, "assert false"),
        _attempt("sonnet", False, "check returned False"),
        _attempt("haiku", False, "check returned False"),
    ]
    lines = per_config_rates(attempts)
    assert lines == ["opus: 2/3", "sonnet: 0/1", "haiku: 0/1"]
    receipt = Receipt(
        task=Task(prompt="x"),
        target=0.7,
        verifiable=True,
        target_met=False,
        attempts=attempts,
        passes=2,
        trials=5,
        wilson_low=0.1,
        wilson_high=0.7,
        confidence="high",
        total_cost_usd=0.05,
        best_output="x",
    )
    assert "opus: 2/3" in format_config_line(receipt)


def test_failure_frequencies():
    attempts = [
        _attempt("opus", False, "AssertionError: not palindrome"),
        _attempt("sonnet", False, "AssertionError: not palindrome"),
        _attempt("haiku", False, "check returned False"),
        _attempt("opus", True),
    ]
    freqs = failure_frequencies(attempts)
    assert freqs[0] == ("AssertionError: not palindrome", 2)
