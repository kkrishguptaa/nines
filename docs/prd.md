# PRD: Nines — reliability compiler for agent tasks

**Product:** Nines  
**Event:** Push to Prod: Building at the Frontier — Bengaluru, 8 August 2026  
**Source:** `docs/spec.md`, `docs/system-design.md`  
**Test seam (primary):** `nines.run(task, *, target, budget) -> Receipt`

---

## Problem Statement

Agent developers pick a model and hope for a reliability level. There is no way to declare the reliability you need and have the system spend compute to reach it. Agents therefore ship only where ~70–90% success is tolerable; high-stakes workflows stay manual or behind human gates that erase automation value.

Per-step errors compound (a 20-step task at 95% per-step reliability finishes end-to-end ~36% of the time). Existing tooling measures reliability or retries on crash — nothing spends compute at runtime to hit a caller-specified target.

## Solution

Nines is a reliability compiler: the caller declares `target` (and optional `budget`), and Nines synthesizes an independent checker from the task, fans out diverse solver attempts, gates every candidate on the checker, escalates until the Wilson lower bound clears the target or the budget is exhausted, and returns an inspectable receipt — not a vibe.

## User Stories

1. As an agent developer, I want to declare a target reliability (`target=0.95`), so that I can ship into workflows where a 30% failure rate is unacceptable.
2. As an agent developer, I want a cost ceiling on the reliability attempt, so that a hard task cannot silently burn my budget.
3. As an agent developer, I want to see why the system believes the output is correct (attempts, verdicts, measured rate), so that I can trust the result without re-running the task myself.
4. As an agent developer, I want to know when the target was not reached, so that I can route to a human instead of shipping a confident wrong answer.
5. As a platform engineer, I want a measured pass rate (with honest statistics), so that I can put a number in an internal SLA.
6. As a platform engineer, I want the verifier to be independent of the solver, so that the system cannot mark its own homework.
7. As a developer with an unverifiable task, I want Nines to return `verifiable: false` before spending solver budget, so that I do not get false confidence.
8. As a developer whose budget runs out mid-escalation, I want the best-so-far result plus an explicit `target_met: false` flag.
9. As a hackathon judge, I want to supply an unseen task and see Nines lift pass rate over single-shot Claude on the same trial count, so that the mechanism is proven live.
10. As a hackathon judge, I want adaptive spend visible (easy tasks ~1 attempt; hard tasks escalate), so that the cost multiplier is not flat.
11. As a demo operator, I want a comparison harness (single-shot vs Nines) with progressive attempt UI, so that the 90-second pitch is visual and live.
12. As a demo operator, I want rate-limit backoff and a pre-seeded fallback task, so that the live demo does not die on 429s or a bad judge input.
13. As a submission auditor / agentic evaluator, I want every pitch claim to map to real code with honest mocks labeled as mocks, so that Originality is not docked.
14. As a solver-diversity consumer, I want attempts to vary across model tier, effort/thinking, and prompt framing, so that errors decorrelate rather than fail together.
15. As a credibility-conscious user, I want target-met defined as Wilson lower bound ≥ target, so that five lucky passes cannot claim 99%.
16. As a verifier-quality consumer, I want canary rejection of checkers that pass known-bad output, so that `assert True` cannot inflate the pass rate.
17. As a caller using tier-3 LLM grading, I want the receipt to label low confidence, so that executable checks and opinions are not conflated.

## Implementation Decisions

- **Primary seam:** one public entrypoint `nines.run(task, *, target, budget) -> Receipt`. Prefer this single seam for all acceptance tests; avoid proliferating internal test seams.
- **Verifier-first:** synthesize the checker from the task spec alone, before any solving. Checker modules never receive solver reasoning — only candidate output (separate module / type boundary).
- **Canary check:** before trusting a checker, run it against a deliberately wrong output; if it passes, discard and regenerate once, then fail loudly.
- **Checker tiers (degrade explicitly):** (1) Hypothesis property tests, (2) deterministic assertion script, (3) independent LLM grader + rubric — tier 3 flagged low-confidence in the receipt.
- **Unverifiable tasks:** detect at synthesis; return `verifiable: false` and do not escalate.
- **Diverse fan-out:** vary model tier, effort/thinking, and prompt framing (decomposition), not temperature alone.
- **Honest stats:** report Wilson score interval; `target_met` iff lower bound ≥ `target`. High targets force more samples.
- **Escalation + budget:** escalate attempts until target met or budget exhausted; on exhaustion return best-so-far + `target_met: false` (never silent best-guess when zero pass).
- **Sandbox:** subprocess with timeout and resource caps — not containers. Document as unsafe for untrusted input.
- **Concurrency:** `asyncio` + semaphore + 429 backoff; keep parallelism low for demo stability.
- **Persistence:** none for v1 (in-memory only).
- **Language:** Python-only task surface for v1.
- **Comparison harness (demo):** same judge task, same trial count, single-shot Claude vs Nines, progressive UI.
- **P1 if time:** mixed-tier routing, verifier independence flag, cost projection. **P2 slide only:** verifier cache, SLA billing, non-Python, correlated-failure learning.
- **Product naming:** ship as **Nines** (repo/brand); positioning phrase “reliability compiler.”

## Testing Decisions

- Test external behavior at the `nines.run` seam: given task + target + budget, assert receipt fields (`verifiable`, `target_met`, attempts, pass counts, Wilson bounds, cost, confidence tier).
- Prefer behavioral tests over mocking internal modules; when LLM calls must be stubbed, inject a solver/verifier port at the seam boundary.
- Good tests assert observable outcomes (receipt shape, escalation under higher target, budget halt, canary rejection, unverifiable short-circuit) — not private helpers.
- Comparison harness tests: same fixtures yield measurable lift or at least a complete dual run with both receipts.
- Prior art: greenfield repo — establish `tests/` around the public API first; no existing suite to mirror.

## Out of Scope

- Eval platforms / dashboards / trace history / dataset management
- Subjective tasks without executable or rubric-driven grading
- Durable execution / crash retries / workflow engines (Temporal’s problem)
- Training or fine-tuning a model
- Multi-language task surfaces
- Production isolation claims beyond subprocess sandboxing
- Persistent verifier library, SLA billing, correlated-failure learning (P2)

## Further Notes

- Blocking open questions from the product spec: pick **one** task family with a cheap high-precision executable checker; define “measured pass rate” consistently (Wilson-gated empirical rate over attempts against the synthesized verifier).
- Cut order if behind: P1 → escalation (fall back to fixed N) → receipt UI (JSON console). Never cut verifier synthesis or gating.
- Submission integrity: claim orchestration, verifier synthesis, budgeted fan-out, measured pass rate vs declared target. Do not claim a novel model or production SLAs.
