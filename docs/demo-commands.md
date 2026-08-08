# Demo commands (hackathon)

## Stage answer (15/15 suspicion)

> Nothing failed because the task is easy — that's the point. One shot gives
> you an answer; we give you the fact that it's safe. On the hard task, look
> what happens.

Then pivot to `parse_money` refuse (`python examples/demo_arc.py`).

## Clean win — use this live (shill this)

The smallest explainable demo — open `examples/minimal.py` on stage, then:

```bash
python examples/minimal.py
```

Expect: `target_met: True`, `15/15`, `wilson_low` ≈ 0.80, ~$0.02.  
Stage line if asked about 15/15: see above, then pivot to the full arc.

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
