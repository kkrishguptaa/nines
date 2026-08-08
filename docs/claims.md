# Submission claims → code map

Only claims that map to real code. Mocks in `tests/fakes.py` are labeled as mocks.

| Claim | Where |
| --- | --- |
| Orchestration layer (`nines.run` → Receipt) | `nines/run.py`, `nines/types.py` |
| Independent verifier synthesis from task alone | `nines/verifier/synthesize.py` |
| Canary rejects checkers that pass known-bad output | `nines/verifier/canary.py` |
| Unverifiable short-circuit (no solver spend) | `nines/run.py` (early return) |
| Diverse fan-out (model × effort × framing) | `nines/solver/diverse.py` |
| Checker gates every candidate (output only) | `nines/verifier/execute.py` |
| Wilson lower bound gates `target_met` | `nines/stats/wilson.py` |
| Escalation until target or budget | `nines/run.py` |
| Zero passes ⇒ no silent best-guess | `nines/run.py` (`best_output is None`) |
| Comparison harness single-shot vs Nines | `demo/compare.py` |
| Pre-seeded fallback task | `demo/fallback_tasks.py` |
| 429 backoff + concurrency cap | `nines/solver/call.py` |
| Subprocess sandbox (not multi-tenant safe) | `nines/sandbox.py`, README |

## Explicit non-claims

- Not a novel model or trained weights.
- Not a production SLA or multi-tenant isolation boundary.
- Cost figures from the Anthropic adapter are approximate token estimates, not invoices.
