# Nines

Your agent is right 70% of the time. Tell Nines you need 99%.

Nines is a **reliability compiler**: declare a `target` reliability and optional `budget`, and `nines.run` synthesizes an independent verifier, fans out diverse solvers, and escalates until a Wilson lower bound clears the target (or the budget stops it).

```python
from nines import run, Task, Budget

receipt = run(
    Task(prompt="implement add(a, b) -> int"),
    target=0.95,
    budget=Budget(max_cost_usd=5.0, max_attempts=20),
)
print(receipt.target_met, receipt.best_output, receipt.detail)
```

## Comparison demo

```bash
python -m demo.compare --fallback --trials 5 --target 0.8
```

Runs single-shot vs Nines on a pre-seeded `add(a,b)` task, prints progressive attempt lines, then a side-by-side summary and the Nines receipt JSON. With `ANTHROPIC_API_KEY` set and the live adapter present, both paths call Claude; without a key, a labeled mock solver exercises the harness shape.

## Safety

Checker and solver code may run in a **subprocess sandbox** with timeouts. That sandbox is **not** safe for untrusted input — do not pass untrusted task text or candidate code into Nines in multi-tenant or production isolation scenarios.
