from __future__ import annotations

from nines.types import Task, VerifierMeta


class FakeSolver:
    """Test double for solver attempts. Label: mock."""

    def __init__(
        self,
        *,
        pass_indices: set[int] | None = None,
        always_pass: bool = False,
        cost_usd: float = 0.01,
        seed: int | None = None,
        pass_rate: float | None = None,
    ) -> None:
        self.pass_indices = pass_indices or set()
        self.always_pass = always_pass
        self.cost_usd = cost_usd
        self.seed = seed
        self.pass_rate = pass_rate
        self.calls = 0
        self._rng = __import__("random").Random(seed)

    def __call__(self, task: Task, config: dict, **kwargs) -> tuple[str, float]:
        idx = self.calls
        self.calls += 1
        if self.always_pass:
            return "PASS", self.cost_usd
        if self.pass_rate is not None:
            ok = self._rng.random() < self.pass_rate
            return ("PASS" if ok else "FAIL"), self.cost_usd
        if idx in self.pass_indices:
            return "PASS", self.cost_usd
        return "FAIL", self.cost_usd


class FakeSynthesizer:
    """Test double for verifier synthesis. Label: mock."""

    def __init__(
        self,
        *,
        result: VerifierMeta | None = None,
        degenerate: bool = False,
    ) -> None:
        self._result = result
        self._degenerate = degenerate
        self.calls = 0

    @classmethod
    def ok_checker(cls) -> FakeSynthesizer:
        source = (
            "def check(output: str) -> bool:\n"
            "    return output.strip() == 'PASS'\n"
        )
        return cls(
            result=VerifierMeta(
                tier=2,
                source_code=source,
                rubric=None,
                canary_passed=False,
            )
        )

    def __call__(self, task: Task, **kwargs) -> VerifierMeta | None:
        self.calls += 1
        if self._degenerate:
            return VerifierMeta(
                tier=2,
                source_code=(
                    "def check(output: str) -> bool:\n"
                    "    return True\n"
                ),
                rubric=None,
                canary_passed=False,
            )
        return self._result
