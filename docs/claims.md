# Submission claims → code map

Only claims that map to real code. Mocks in `tests/fakes.py` and the demo `_Echo` solver are labeled as mocks.

| Claim | Where |
| --- | --- |
| Orchestration layer (`nines.run` → Receipt) | `nines/run.py`, `nines/types.py` |
| Independent verifier synthesis from task alone | `nines/verifier/synthesize.py` |
| Canary rejects checkers that pass known-bad output | `nines/verifier/canary.py` |
| `checker_validated` / `canary_detail` on every Receipt | `nines/types.py`, `nines/run.py` |
| Unreachable Wilson target refused without spend | `nines/stats/wilson.py` `max_achievable_lower_bound`, `nines/run.py` |
| Unverifiable / subjective short-circuit (no solver spend) | `nines/run.py`, `nines/verifier/synthesize.py` |
| Diverse fan-out (model × effort × framing) | `nines/solver/diverse.py` |
| Checker gates every candidate (output only) | `nines/verifier/execute.py` |
| Wilson lower bound gates `target_met` | `nines/stats/wilson.py` |
| Escalation until target or budget | `nines/run.py` |
| Zero passes ⇒ no silent best-guess | `nines/run.py` (`best_output is None`) |
| Bare `run` defaults to Anthropic when key set | `nines/run.py` |
| Comparison harness single-shot vs Nines (rich live) | `demo/compare.py`, `demo/rich_ui.py` |
| Pre-seeded fallback task | `demo/fallback_tasks.py` |
| 429 backoff + concurrency cap | `nines/solver/call.py` |
| Subprocess sandbox (not multi-tenant safe) | `nines/sandbox.py`, README |
| Checker subprocess uses scrubbed env (no API keys) | `nines/sandbox.py` `_minimal_env` |

## Explicit non-claims

- Not a novel model or trained weights.
- Not a production SLA or multi-tenant isolation boundary.
- Cost figures from the Anthropic adapter are approximate token estimates, not invoices.
- Subprocess sandbox still inherits a minimal OS env and can touch the filesystem — **not** safe for untrusted multi-tenant input; secrets are scrubbed from the child env but this is not container isolation.

## Known limits

- Subjective tasks (poem/essay/…) short-circuit as unverifiable by heuristic markers.
- Live checker quality depends on Claude; canary + one regenerate is the honesty gate.
- `target` above the best Wilson lower bound for `max_attempts` is refused immediately.
