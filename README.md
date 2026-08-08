# Nines

Your agent is right ~70% of the time. Tell Nines you need a measured bar — and get a receipt when it refuses.

Nines is a **reliability compiler**. You declare a `target` and a `budget`; it synthesizes an independent checker, fans out diverse solvers, and escalates until a Wilson lower bound clears the target — or stops with `target_met: false` instead of a silent best-guess.

```python
from nines import run, Task, Budget

receipt = run(
    Task(prompt="Write is_palindrome(s: str) -> bool. Empty string is True. Code only."),
    target=0.7,
    budget=Budget(max_cost_usd=2.0, max_attempts=25),
    models=("opus", "sonnet"),  # optional: drop tiers that drag the pool
)
if receipt.target_met:
    use(receipt.best_output)
else:
    escalate_to_human(receipt.detail)
```

## Single-shot vs Nines

Same task (`is_palindrome`), same live Claude stack. Measured once on this machine — costs are adapter estimates, not invoices.

| | Without Nines (single-shot) | With Nines |
| --- | ---: | ---: |
| Calls | 1 | 15 (stops when bar clears) |
| Checker-gated pass | Failed | **15/15** |
| Declared target | — | **0.70** |
| Wilson interval | — | **[0.80, 1.00]** |
| `target_met` | unknown (ships hope) | **`true`** |
| Canary on checker | no | yes |
| Approx. cost | **~$0.001** | **~$0.03** |
| Wall time | ~9s | ~17s |
| When it fails | You may ship a wrong answer | Receipt says refuse — no silent guess |

Single-shot was cheaper. It was also wrong on the checker. Nines spent a few cents and returned a bar you can defend.

Hard tasks flip the story: strict `parse_money` often lands `target_met: false` with per-model rates (e.g. `opus: 5/8 · sonnet: 7/8 · haiku: 1/9`) and failure frequencies — so you know *why* the pool missed, and can drop weak models with `models=("opus", "sonnet")`.

## How it works

1. **Verifier-first** — synthesize a checker from the task alone; canary rejects checkers that accept known-bad (and known-good when available).
2. **Diverse fan-out** — vary model tier, effort, and framing (not temperature alone).
3. **Gate every candidate** — only checker-passing outputs count.
4. **Wilson gate** — `target_met` iff lower bound ≥ `target`. High targets force more samples.
5. **Budget stop** — cost / attempt ceiling; zero passes ⇒ `best_output is None`.

Public seam is one function: `nines.run(task, *, target, budget) -> Receipt`.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=...
python examples/demo_arc.py --models opus,sonnet
```

Keyless / CI paths inject labeled mocks (`tests/fakes.py`, demo `_Echo`) — never presented as live models.

## Demo

```bash
# Clean win → hard refuse (under ~2 min)
python examples/demo_arc.py

# Side-by-side single-shot vs Nines (rich live UI)
python -m demo.compare --fallback --trials 25 --target 0.7
```

## Claims

Real code map: [`docs/claims.md`](docs/claims.md).

**Claimed:** orchestration → inspectable `Receipt`; independent verifier + canary; budgeted diverse fan-out; Wilson-gated `target_met`.

**Not claimed:** a novel model, production SLAs, or multi-tenant sandbox isolation.

### Limits

- Target above the best Wilson lower bound for `max_attempts` → immediate unreachable refuse (no spend).
- Subjective tasks (poem / essay) → `verifiable=False`, no solver spend.
- Live checker quality depends on Claude; canary + one regenerate is the honesty gate.

## Safety

Checker and solver code may run in a **subprocess sandbox** with timeouts and a **scrubbed child environment** (API keys are not forwarded). That is still **not** safe for untrusted multi-tenant input — no containers; filesystem access remains possible.
