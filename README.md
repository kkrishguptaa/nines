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

## Safety

Checker and solver code may run in a **subprocess sandbox** with timeouts. That sandbox is **not** safe for untrusted input — do not pass untrusted task text or candidate code into Nines in multi-tenant or production isolation scenarios.
