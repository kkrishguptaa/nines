# Demo commands (hackathon)

## Stage answer (15/15 suspicion)

> Nothing failed because the task is easy — that's the point. One shot gives
> you an answer; we give you the fact that it's safe. On the hard task, look
> what happens.

Then pivot to `parse_money` refuse (`python examples/demo_arc.py`).

## Clean win (T5) — use this live

```bash
python -c "from nines import run,Task,Budget; r=run(Task(prompt='Write a Python function is_palindrome(s: str) -> bool that returns True iff s equals its reverse. Case-sensitive, spaces matter. Empty string is True. Code only.'), target=0.7, budget=Budget(max_cost_usd=2.0, max_attempts=25)); print(r.target_met, r.passes, r.trials, r.wilson_low)"
```

Verified: `target_met=True` in ~33s (15/15, Wilson low ≈ 0.80).

## Full arc (T9)

```bash
python examples/demo_arc.py
```

Drop weaker models when per-config rates show them dragging the pool:

```bash
python examples/demo_arc.py --models opus,sonnet
```

1. `is_palindrome` → clears `target=0.7` (mechanism works)
2. Strict `parse_money` → usually refuses; always prints per-model rates + failure reasons
