## The five decisions that actually matter

**1. Verifier is synthesized before any solving happens.**

This is the load-bearing architectural choice, not an implementation detail. If the checker is generated after seeing candidate outputs, it converges toward "whatever the solver produced" and you've built an expensive echo. Generating from the task spec alone is what makes the verdict independent.

Practical consequence: the checker function never receives the solver's reasoning, only the candidate output. Enforce it at the type level — separate module, no shared context object.

**2. The canary check — reject checkers that pass garbage.**

The obvious failure is Claude emitting `assert True` or a test with an empty body, and every attempt "passing." So before trusting a checker, run it against a deliberately wrong output you generate on purpose.

```
checker(known_bad) must fail, else discard and regenerate
```

This is mutation testing in miniature, it costs one extra call, and it's the single most impressive thing in the demo — it's the system catching *itself* being useless. Judges from Anthropic will recognize the reward-hacking mitigation immediately.

**3. Checker tiers, degrade explicitly.**

| Tier | Mechanism | Precision |
|---|---|---|
| 1 | Property tests (Hypothesis) | High |
| 2 | Deterministic assertion script | High |
| 3 | Independent LLM grader + rubric | Low, flag it |

Tier 3 must be labeled in the receipt as low-confidence. Silently sliding from executable checks to an LLM opinion while reporting the same "97%" is the dishonest version of this product.

**4. Diversity has to be real, across three axes.**

Model tier, effort/thinking setting, and prompt framing. Five identical calls at temperature 1.0 give you correlated errors — you'll measure a high pass rate and be confidently wrong together. Varying the *decomposition* of the prompt matters more than varying temperature.

**5. The statistics have to be honest, and this is your credibility moment.**

With 5 samples you cannot establish 99% reliability. You literally can't — 5/5 successes gives a 95% Wilson lower bound around 57%. If your receipt prints "99%" off five trials, anyone in that room with a stats background dismisses the whole thing.

So: report a **Wilson score interval**, and define target-met as *lower bound ≥ target*. That means high targets force more samples, which is exactly the behavior you want — and it makes the escalation loop principled rather than arbitrary.

```
target=0.80 → maybe 8 attempts
target=0.95 → maybe 40 attempts
```

Ten lines of code. Enormous credibility return.

## Trade-offs I'd flag out loud

**Sandboxing:** subprocess with a timeout and resource caps, not containers. You're executing model-generated code. Say plainly in the README that this is unsafe for untrusted input — don't claim isolation you didn't build, because the auditor greps for exactly that.

**Concurrency:** `asyncio` with a semaphore, and backoff on 429s. Rate limits are the most likely thing to kill your live demo, not logic bugs. Cap parallelism low and make the UI show attempts arriving progressively so slowness reads as *working* rather than *hung*.

**Persistence:** none. In-memory only. A checker cache keyed by task hash is the P2 moat, and saying "that's the compounding asset, we didn't build it today" is stronger than a SQLite table nobody looks at.

## What breaks

| Failure | Handling |
|---|---|
| Rate limited | Semaphore + backoff, degrade N, keep UI moving |
| Checker synthesis fails | Tier down, flag confidence |
| Degenerate checker | Canary catches it, regenerate once, then fail loudly |
| All attempts fail | `target_met: false`, return failure detail — never a silent best guess |
| All pass at n=3 | Either genuinely easy or the checker is weak; canary result disambiguates |
| Task unverifiable | Detect at synthesis, return `verifiable: false` before spending anything |

That last row is a feature, not an error path. "This task can't be verified, so I won't pretend" is a strong thing to show a judge.

## What I'd revisit at scale

Verifier caching per task family (the actual moat), correlated-failure detection across attempts, and learning escalation policy from history instead of doubling blindly. All P2 — roadmap slide, not code.

Want the module layout and function signatures next, or the demo UI?
