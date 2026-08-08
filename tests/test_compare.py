from nines import Budget, Task
from tests.fakes import FakeSolver, FakeSynthesizer
from demo.compare import compare


def test_compare_returns_both_paths():
    result = compare(
        Task(prompt="add"),
        trials=6,
        target=0.5,
        single_shot=FakeSolver(pass_indices={0}),
        nines_ports={
            "synthesizer": FakeSynthesizer.ok_checker(),
            "solver": FakeSolver(pass_indices={0, 1, 2, 3}),
            "initial_batch": 6,
            "escalate": False,  # fixed batch for deterministic counts
            "parallel": False,
        },
        budget=Budget(max_cost_usd=10.0, max_attempts=6),
    )
    assert "single_shot" in result and "nines" in result
    assert result["nines"].trials == 6
    assert result["nines"].passes == 4
    assert result["single_shot_passes"] == 1
    assert result["single_shot_trials"] == 6
    assert result["single_shot"].verifiable is True
