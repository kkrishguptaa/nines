from __future__ import annotations

from nines.types import Task, VerifierMeta


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
