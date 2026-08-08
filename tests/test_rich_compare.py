from nines import Budget, Task
from nines.types import Attempt
from tests.fakes import FakeSolver, FakeSynthesizer
from demo.compare import compare
from demo.rich_ui import DemoLive


def test_compare_with_rich_callback_smoke():
    live = DemoLive(target=0.55)
    live.on_attempt(
        "single_shot",
        Attempt(
            config={"model": "sonnet"},
            output="PASS",
            passed=True,
            cost_usd=0.01,
        ),
    )
    live.on_attempt(
        "nines",
        Attempt(
            config={"model": "haiku"},
            output="PASS",
            passed=True,
            cost_usd=0.01,
        ),
    )
    assert live.single.passes == 1
    assert live.nines.passes == 1
    assert "[" in live.nines.wilson

    result = compare(
        Task(prompt="add"),
        trials=6,
        target=0.55,
        single_shot=FakeSolver(pass_indices={0, 1}),
        nines_ports={
            "synthesizer": FakeSynthesizer.ok_checker(),
            "solver": FakeSolver(always_pass=True),
            "initial_batch": 6,
            "escalate": False,
        },
        budget=Budget(max_cost_usd=10.0, max_attempts=6),
        on_attempt=live.on_attempt,
    )
    assert "single_shot" in result and "nines" in result
    assert result["nines"].trials == 6
