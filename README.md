# Nines

Your agent is right 70% of the time. Tell Nines you need 99%.

Nines is a **reliability compiler**: declare a `target` reliability and optional `budget`, and `nines.run` synthesizes an independent verifier, fans out diverse solvers, and escalates until a Wilson lower bound clears the target (or the budget stops it).

```python
from nines import run, Task, Budget

# With ANTHROPIC_API_KEY set, bare run defaults to live Claude ports.
# Unit tests inject FakeSynthesizer / FakeSolver (labeled mocks).
receipt = run(
    Task(prompt="implement add(a, b) -> int"),
    target=0.7,
    budget=Budget(max_cost_usd=5.0, max_attempts=25),
    # Optional: restrict fan-out (default is opus+sonnet+haiku).
    # Drop haiku when per-model rates show it dragging the pool:
    models=("opus", "sonnet"),
)
print(receipt.target_met, receipt.best_output, receipt.checker_validated)
```

## What this repo claims

Real code (see `docs/claims.md`):

- Orchestration layer around `nines.run` → inspectable `Receipt`
- Verifier synthesis from the task alone, with canary rejection
- Budgeted diverse fan-out gated by the checker
- Measured pass rate vs a declared target (`target_met` iff Wilson lower bound ≥ target)

**Not claimed:** a novel model, production SLAs, or multi-tenant sandbox isolation. Unit tests and keyless demo paths use **labeled mocks** (`tests/fakes.py`, demo `_Echo` solver).

### Known limits

- Targets above the best Wilson lower bound for `max_attempts` return immediately as unreachable (no API spend).
- Subjective tasks (e.g. poems) return `verifiable=False` without solving.
- Live checker synthesis can fail canary after one regenerate; that is reported honestly, not papered over.

## Comparison demo

```bash
python -m demo.compare --fallback --trials 25 --target 0.7
```

Runs single-shot vs Nines on a pre-seeded `add(a,b)` task, prints progressive attempt lines, then a side-by-side summary and the Nines receipt JSON. Defaults are `target=0.7` / `trials=25` so a perfect batch can clear the Wilson lower bound (5/5 cannot clear 0.6).

- `--fallback` / omit `--task`: use the pre-seeded property-checkable task if judge input would break synthesis.
- Re-run the same command to reset (no durable state).
- With `ANTHROPIC_API_KEY` and the live adapter, both paths call Claude; 429s retry with backoff under a small concurrency semaphore. Without a key (or without the adapter), a **labeled mock** solver exercises the harness shape.

## Safety

Checker and solver code may run in a **subprocess sandbox** with timeouts and a **scrubbed child environment** (API keys are not forwarded). That sandbox is still **not** safe for untrusted input — no containers, filesystem access remains possible. Do not pass untrusted task text or candidate code into Nines in multi-tenant or production isolation scenarios.

## Install / test

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```
