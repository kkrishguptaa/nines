from __future__ import annotations

from dataclasses import dataclass, field

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nines.stats.wilson import wilson_interval
from nines.types import Attempt, Receipt


@dataclass
class _Side:
    passes: int = 0
    trials: int = 0
    cost: float = 0.0
    last: str = "—"
    wilson: str = "n/a"


@dataclass
class DemoLive:
    """Projector-friendly dual-column live table for single-shot vs Nines."""

    target: float
    console: Console = field(default_factory=Console)
    single: _Side = field(default_factory=_Side)
    nines: _Side = field(default_factory=_Side)
    canary_line: str = "canary: pending"
    _live: Live | None = field(default=None, repr=False)

    def __enter__(self) -> DemoLive:
        self._live = Live(
            self._render(),
            console=self.console,
            refresh_per_second=8,
            transient=False,
        )
        self._live.__enter__()
        return self

    def __exit__(self, *exc) -> None:
        if self._live is not None:
            self._live.__exit__(*exc)
            self._live = None

    def set_canary(self, validated: bool, detail: str | None) -> None:
        self.canary_line = f"canary: validated={validated} detail={detail}"
        self._refresh()

    def on_attempt(self, path: str, attempt: Attempt) -> None:
        side = self.single if path == "single_shot" else self.nines
        side.trials += 1
        side.cost += attempt.cost_usd
        if attempt.passed:
            side.passes += 1
            side.last = "PASS"
        else:
            side.last = "FAIL"
        if side.trials > 0:
            low, high = wilson_interval(side.passes, side.trials)
            side.wilson = f"[{low:.2f}, {high:.2f}]"
        self._refresh()

    def finalize(self, result: dict) -> None:
        ni: Receipt = result["nines"]
        ss: Receipt = result["single_shot"]
        self.set_canary(ni.checker_validated, ni.canary_detail)
        if self._live is not None:
            self._live.update(self._render())
        best = (ni.best_output or "")[:200].replace("\n", "\\n")
        panel = Panel.fit(
            Text.from_markup(
                f"[bold]target_met[/]={ni.target_met}  "
                f"checker_validated={ni.checker_validated}\n"
                f"nines attempts={ni.trials} passes={ni.passes} "
                f"cost=${ni.total_cost_usd:.4f}\n"
                f"single-shot={ss.passes}/{ss.trials} "
                f"target_met={ss.target_met}\n"
                f"best_output={best!r}\n"
                f"detail={ni.detail}"
            ),
            title="Nines receipt",
            border_style="green" if ni.target_met else "yellow",
        )
        self.console.print(panel)

    def _refresh(self) -> None:
        if self._live is not None:
            self._live.update(self._render())

    def _render(self) -> Group:
        table = Table(title=f"single-shot vs nines  (target={self.target})", expand=True)
        table.add_column("metric", style="bold")
        table.add_column("single-shot", justify="center")
        table.add_column("nines", justify="center")
        table.add_row("last", self.single.last, self.nines.last)
        table.add_row(
            "passes/trials",
            f"{self.single.passes}/{self.single.trials}",
            f"{self.nines.passes}/{self.nines.trials}",
        )
        table.add_row("Wilson", self.single.wilson, self.nines.wilson)
        table.add_row(
            "cost",
            f"${self.single.cost:.4f}",
            f"${self.nines.cost:.4f}",
        )
        status = Text(self.canary_line)
        return Group(status, table)
