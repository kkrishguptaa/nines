from nines import Task, Budget
from tests.fakes import FakeSolver, FakeSynthesizer
from demo.compare import compare


def test_compare_returns_both_paths():
    result = compare(
        Task(prompt="add"),
        trials=3,
        target=0.5,
        single_shot=FakeSolver(pass_indices={0}),
        nines_ports={
            "synthesizer": FakeSynthesizer.ok_checker(),
            "solver": FakeSolver(pass_indices={0, 1}),
            "initial_batch": 3,
            "escalate": False,
        },
        budget=Budget(max_cost_usd=10.0, max_attempts=3),
    )
    assert "single_shot" in result and "nines" in result
    assert result["nines"].trials >= 1
    assert "single_shot_passes" in result
    assert result["single_shot_trials"] == 3
