# Product Spec

**The reliability compiler for agent tasks.**
*Push to Prod: Building at the Frontier — Bengaluru, 8 August 2026*

---

## Problem Statement

Agent developers today choose a **model** and hope for a reliability level. There is no way to specify the reliability you need and have the system spend compute to reach it. The result is that agents get deployed only where a ~70–90% success rate is tolerable, and every high-stakes workflow — migrations, financial operations, production changes — stays manual or stays behind a human approval gate that erases most of the automation value.

The pain is structural, not a model-quality problem. Per-step errors compound: a 20-step task at 95% per-step reliability completes end-to-end only 36% of the time. As agent runs got longer through mid-2026, this went from a nuisance to the binding constraint on deployment. Gartner's June 2025 projection that over 40% of agentic AI projects will be cancelled by end of 2027 — citing inadequate risk controls among the causes — is the enterprise-side symptom of the same thing.

The existing tooling layer **measures** reliability (Braintrust, LangSmith, Langfuse, Arize) or **retries** on failure (Temporal). Nothing spends compute at runtime to *reach a caller-specified target*.

---

## Goals

1. **Prove the mechanism works on an unseen task.** A judge supplies a task; Quorum demonstrably lifts measured pass rate over single-shot Claude on that task, live.
2. **Make reliability a declared parameter.** The caller writes `target=0.95`, not a model name. Demonstrate that the same API call produces different compute spend for different targets.
3. **Produce an inspectable receipt.** Every run returns how the number was reached: attempts, verifier votes, measured pass rate, cost. Not a vibe — an auditable artifact.
4. **Show adaptive spend.** Easy tasks resolve in ~1 attempt; hard tasks escalate. Prove the cost multiplier is not flat.
5. **Ship a repo whose code substantiates every claim in the submission.** (See *Submission Integrity*.)

---

## Non-Goals

1. **Not building an eval platform.** No dashboards, no trace history, no dataset management. That space is occupied and it is not the bet.
2. **Not solving subjective tasks.** If correctness cannot be checked by an executable or a rubric-driven independent grader, Quorum is out of scope for v1. Say this out loud rather than overclaim.
3. **Not durable execution.** No retries-on-crash, no state persistence, no workflow engine. That is Temporal's problem and conflating them weakens the pitch.
4. **Not a model.** No training, no fine-tuning. Orchestration plus verifier synthesis only. Claiming otherwise gets the Originality score docked.
5. **Not multi-language.** Python-only task surface for v1.

---

## User Stories

**Primary persona: the agent developer shipping something consequential.**

- As an agent developer, I want to declare a target reliability so that I can ship an agent into a workflow where a 30% failure rate is unacceptable.
- As an agent developer, I want a cost ceiling on the reliability attempt so that a hard task cannot silently burn my budget.
- As an agent developer, I want to see *why* the system believes the output is correct so that I can decide whether to trust it without rerunning the task myself.
- As an agent developer, I want to know when the target was **not** reached so that I can route to a human instead of shipping a confident wrong answer.

**Secondary persona: the platform/infra engineer evaluating adoption.**

- As a platform engineer, I want to see the measured pass rate rather than a claimed one so that I can put a number in an internal SLA.
- As a platform engineer, I want the verifier to be independent of the solver so that the system cannot mark its own homework.

**Edge cases**

- As a developer with an unverifiable task, I want Quorum to tell me it cannot synthesize a usable checker so that I do not get false confidence.
- As a developer whose budget runs out mid-escalation, I want the best-so-far result plus an explicit "target not met" flag.

---

## Requirements

### P0 — Must have. No demo without these.

**R1. Verifier synthesis**
Given a task description (and optional code context), produce an executable checker: property-based tests, invariants, or a deterministic script. Falls back to an independent LLM grader with an explicit rubric when execution is impossible.

- Given a task with checkable output, when Quorum runs, then it emits a checker as a code artifact the user can read.
- Given a task with no checkable structure, when Quorum runs, then it returns `verifiable: false` and does not proceed to escalation.
- The checker must not receive the solver's reasoning — only the candidate output.

**R2. Diverse solver fan-out**
Run N attempts across varied configurations — model tier, effort/thinking setting, and prompt framing. Diversity must be real; N identical calls do not decorrelate errors.

- Given `n=5`, when the run executes, then the receipt lists 5 attempts with distinct configurations.

**R3. Gate and measure**
Every candidate passes through the checker. Compute an empirical pass rate.

- Given 5 attempts of which 3 pass, when the run completes, then the receipt reports 3/5 and returns a passing candidate.
- Given zero candidates pass, then the system returns `target_met: false` with the failure detail, never a silent best-guess.

**R4. Target-driven escalation with budget ceiling**
Escalate attempts until measured pass rate clears `target` or `budget` is exhausted.

- Given `target=0.99` on a hard task, when the run executes, then more attempts occur than for `target=0.80` on the same task.
- Given budget exhaustion, then the run halts and reports best-so-far plus `target_met: false`.

**R5. The reliability receipt**
Structured, inspectable output: attempts made, configurations used, verifier verdicts, measured pass rate, total cost, target met yes/no.

**R6. Comparison harness (the demo)**
Run single-shot Claude and Quorum against the same judge-supplied task over the same trial count, and display both pass rates.

### P1 — Ship if time allows.

- **Mixed-tier routing.** Cheap models for solver diversity, frontier model for verification. This is the cost story made visible.
- **Verifier independence check.** Flag when the checker appears correlated with the solver (e.g. both derived from identical framing) — this is the intellectually honest feature and it will impress the Anthropic judges specifically.
- **Cost projection.** Estimate spend before running.

### P2 — Roadmap slide only. Do not build.

- Persistent per-task-family verifier library that compounds across runs (this is the real moat, and saying so is stronger than faking it).
- SLA billing and contractual reliability guarantees.
- Non-Python language support.
- Correlated-failure detection across attempts.

---

## Success Metrics

Adapted to a five-hour hackathon rather than a product launch.

**Leading — measurable during the event**

| Metric | Success | Stretch |
|---|---|---|
| Judge-supplied task runs end to end without intervention | Yes | Yes, twice, on different tasks |
| Measured lift over single-shot on judge's task | Any positive lift | ≥20 percentage points |
| Time from judge input to visible result | <90 seconds | <45 seconds |
| Adaptive spend visible (easy ≠ hard cost) | Demonstrated | Shown as a live counter |

**Lagging — post-event**

- Shortlisted in top 5.
- Anthropic judges ask an architecture question rather than a "how is this different from X" question. (A differentiation question means the positioning failed.)
- Elevation office hours.

---

## Timeline — the five hours

**0:00–0:20 — Lock the narrative before writing code.**
Write the one-liner, the "what breaks if Claude is removed" answer, and the cost objection response. If you cannot say these cleanly you are not ready to build.

**0:20–1:30 — The core loop.** R1 + R2 + R3. Verifier synthesis, fan-out, gate. Nothing else. This is the product; everything after is presentation.

**1:30–2:15 — Measurement and receipt.** R5. Structured output with real numbers.

**2:15–3:00 — Target-driven escalation and budget.** R4. This is what makes it a *compiler* rather than a for-loop. Do not skip it to build UI.

**3:00–3:45 — Comparison harness.** R6. Split screen, two pass rates climbing. This is the entire demo.

**3:45–4:20 — Harden.** Rate-limit backoff, one-click reset, a pre-seeded fallback task if the judge's input breaks something, tested on slow network. Remove every dead button.

**4:20–5:00 — Submission and rehearsal.** Write the submission (see below), rehearse the 90 seconds, rehearse the cost objection.

**Cut order if behind:** P1 features first, then escalation logic (fall back to fixed N), then the receipt UI (fall back to JSON printed to console). Never cut R1 or R3 — without verifier synthesis and gating there is no product.

---

## Submission Integrity

Devfolio runs an agentic evaluator that clones the repo, greps it, and checks each claim against code with `file:line` citations. Their published example docks Originality 7→4 for claiming a "custom architecture" that turned out to be a stock pretrained model call. A polished README is a longer list of claims to check.

**Claim exactly this:** orchestration layer, verifier synthesis, budgeted fan-out, measured pass rate against a declared target.

**Do not claim:** a novel model, a custom architecture, production SLAs, million-scale inference, or any integration that is mocked. Label mocks as mocks in the README — an honest mock costs nothing; a mock described as real is a scored mismatch.

Sell the company in the live pitch to humans. Keep the written submission to what the repo substantiates.

---

## Open Questions

**Blocking — resolve before 0:20**

- *Which task family?* Needs a cheap, high-precision executable checker. Candidates: Python functions with hidden properties, structured data transforms with ground truth, bug fixes in a supplied file. **Pick one and only one.**
- *What does "measured pass rate" mean concretely?* Pass rate over held-out probe instances, or verifier agreement across attempts? These are different claims. Decide and be consistent.

**Non-blocking — resolve during build**

- How much solver diversity is enough to decorrelate errors? Empirical; tune during the build.
- Does mixed-tier routing hold quality? Test if P1 is reached.
- What fallback when verifier synthesis produces a trivially-passing checker (e.g. `assert True`)? At minimum, detect and reject empty checkers.

**For the mentors — ask these on the floor**

- To Anthropic: "What would make this look like real reliability infrastructure rather than best-of-N with extra steps?"
- To Elevation: "What evidence would you need that the market is low-volume/high-stakes rather than high-volume/low-value?"

Make one visible change based on the best answer and mention it in the demo.

---

## The Pitch (90 seconds)

> Every agent today ships at whatever reliability the model happens to give you. You pick a model and hope. That's why agents are stuck doing low-stakes work — nobody lets a 70%-reliable system touch a migration or a refund.
>
> Quorum makes reliability a parameter. You declare 99%, and we spend compute to get there: synthesizing an independent checker for your task, running diverse solvers against it, escalating until the measured pass rate clears your target or your budget stops us.
>
> [Judge supplies a task. Split screen. Two pass rates climb.]
>
> You get back a receipt, not a vibe — attempts, verdicts, measured rate, cost.
>
> Yes, it costs more compute. It costs less than not shipping the agent at all. And spend is adaptive: easy tasks cost 1x, only the hard tail escalates.
>
> The hard problem isn't running things five times. It's writing checkers that catch what matters and can't be gamed. That's the company.

**If asked "what breaks if Claude is removed?"** — Verifier synthesis collapses, and the amplification math stops working: below a certain base reliability, stacking attempts amplifies correlated errors instead of climbing. The whole mechanism depends on a frontier-quality solver and grader.

**The honest weakness, if asked** — With a weak or correlated verifier, this yields diminishing or negative returns; there is published evidence for that. Which is exactly why verifier quality is the moat rather than the orchestration.
