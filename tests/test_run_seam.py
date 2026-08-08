from nines import run, Task, Budget, Receipt


def test_run_returns_receipt_echoing_target():
    receipt = run(
        Task(prompt="return 2+2"),
        target=0.9,
        budget=Budget(max_cost_usd=1.0, max_attempts=1),
    )
    assert isinstance(receipt, Receipt)
    assert receipt.target == 0.9
    assert receipt.verifiable is False
    assert receipt.target_met is False
    assert receipt.attempts == []
    assert receipt.detail
