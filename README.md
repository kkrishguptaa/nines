# Nines

Your AI team ships answers that are *usually* right.  
**Nines makes “usually” a number you can put in front of a board.**

Tell Nines the reliability you need (70%, 80%, 90%…). It tries, measures, and either hands you something that cleared the bar — or **refuses** instead of quietly shipping a wrong answer.

```python
from nines import run, Task, Budget

receipt = run(
    Task(prompt="Write is_palindrome(s: str) -> bool. Empty string is True. Code only."),
    target=0.8,                                 # “I need ~80% confidence this works”
    budget=Budget(max_cost_usd=2.0, max_attempts=25),
    models=("opus", "sonnet"),                  # which AI models to hire for the job
)

if receipt.target_met:
    ship(receipt.best_output)                   # cleared the bar — safe to use
else:
    send_to_human(receipt.detail)               # did not clear — do not fake it
```

## Ask once vs ask Nines (real run, same task)

Task: “write a palindrome checker.” Live Claude models. Costs are ballpark API spend, not an invoice.

| Approach | Models used | Reliability bar you asked for | Did it clear the bar? | How many answers passed QA? | Approx. cost | What a CEO should hear |
| --- | --- | --- | --- | ---: | ---: | --- |
| **Without Nines** (one shot) | Sonnet once | None — you hope | Unknown | 1 try, no audit trail | **~$0.001** | Cheap. Blind. |
| **Nines** | Opus + Sonnet + Haiku | **70%** | **Yes** | 15 / 15 | **~$0.02** | Pennies to prove “good enough.” |
| **Nines** | Opus + Sonnet (no Haiku) | **70%** | **Yes** | 15 / 15 | **~$0.03** | Skip the weak model; still clears. |
| **Nines** | Opus + Sonnet | **80%** | **Yes** | 25 / 25 | **~$0.06** | Higher bar → more checks → a bit more spend. |
| **Nines** | Opus only | **90%** | **Yes** | 40 / 40 | **~$0.13** | Top model + more samples to defend 90%. |
| **Nines** (honest refuse) | Opus only, capped at 25 tries | **90%** | **No — refused up front** | 0 (didn’t bother) | **$0** | You asked for proof the budget can’t buy. We say so. We don’t invent a green light. |

**Two words on the receipt — in English:**

| What you see | What it means (no math) |
| --- | --- |
| **Checker pass** | “Did this answer survive an independent QA test?” Think of a second employee who only knows the *rules*, not the draft. They mark pass or fail. A high pass count means many drafts survived QA — not that we graded our own homework. |
| **`target_met`** | “Did we hit the reliability you paid for?” Not “we got lucky once.” Nines keeps trying until the *statistics* say you’re at least as reliable as the bar you set — or it stops and tells you it didn’t. Green means ship. Red means escalate to a human. |

Hard jobs (e.g. strict money parsing) often come back red on purpose — with a breakdown like “Opus 5/8 · Sonnet 7/8 · Haiku 1/9.” That isn’t failure of the product; it’s the product refusing to rubber-stamp a flaky process. Drop the weak model with `models=("opus", "sonnet")` and try again, or raise the budget.

## What you are buying

1. **An independent checker** — QA that doesn’t trust the model’s smile.
2. **Several models, several angles** — so one bad habit doesn’t fool the whole pool.
3. **A number you named** — 70 / 80 / 90 — not a vibe.
4. **A hard stop** — when it can’t clear the bar, you get a refusal, not a confident wrong answer.

One call: `nines.run(...)` → a receipt. Green ship / red human.

## Get it running

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=...

# Easy task clears → hard task shows an honest refuse (~2 min)
python examples/demo_arc.py --models opus,sonnet

# Side-by-side: one-shot hope vs Nines
python -m demo.compare --fallback --trials 25 --target 0.7
```

## Fine print (still plain English)

- We **orchestrate and measure**. We did not invent a new AI brain. See [`docs/claims.md`](docs/claims.md).
- If you ask for a bar that your attempt budget *mathematically cannot* prove, Nines says no immediately and spends nothing.
- Poems and “make it beautiful” tasks can’t be machine-checked fairly — Nines says “not verifiable” and won’t burn money pretending.
- Sandbox is a safety seatbelt for demos, **not** a bank vault. Don’t feed it untrusted stranger code in production multi-tenant setups.
