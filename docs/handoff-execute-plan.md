# Handoff: Execute Nines implementation plan

**Date:** 2026-08-08  
**Workspace:** `/Users/krish/git/kkrishguptaa/nines`  
**Branch:** `cursor/skills-prd-and-plan` (tracks `origin/cursor/skills-prd-and-plan`)  
**Base:** `main`  
**Focus for next session:** Execute `docs/plan/01.md` task-by-task (implementation). Do not re-plan unless the plan is wrong against the PRD.

---

## What is already done

- Product framing and architecture written: `docs/spec.md`, `docs/system-design.md` (on `main` as `09ba7bd`).
- Matt Pocock skills + Impeccable installed; agent config wired (`AGENTS.md`, `docs/agents/*`).
- PRD synthesized via `to-spec` and published: `docs/prd.md` + GitHub [#1](https://github.com/kkrishguptaa/nines/issues/1).
- Tracer-bullet issues via `to-tickets`: [#2](https://github.com/kkrishguptaa/nines/issues/2)–[#7](https://github.com/kkrishguptaa/nines/issues/7) with `Blocked by` edges and native GitHub dependencies where available. All labeled `ready-for-agent`.
- Implementation plan written: **`docs/plan/01.md`** (user-requested path; supersedes default `docs/superpowers/plans/...`).
- Skills/PRD/plan committed and pushed: `8bbb849` on `cursor/skills-prd-and-plan`.

**Repo state:** almost empty of product code (README + LICENSE + docs + skills only). Plan starts at scaffold.

**Untracked local noise (ignore):** `.cursor/hooks/state/continual-learning.json`

---

## What to do next

1. Read `docs/plan/01.md` end-to-end, then PRD `#1` / `docs/prd.md` only as needed for constraints.
2. Execute Tasks 1→6 in order (maps to issues #2→#7). Prefer **subagent-driven-development** (fresh subagent per task + review) unless the user asks for inline `executing-plans`.
3. Keep the single public seam: `nines.run(task, *, target, budget) -> Receipt`.
4. Honor Global Constraints in the plan (Wilson `target_met`, verifier-first, no silent best-guess, Python-only, honest README claims).
5. Close or comment on GitHub issues as tasks complete; do not reopen the PRD unless requirements change.
6. Open a PR from `cursor/skills-prd-and-plan` → `main` when implementation is ready (or when the user asks); skills-only PR is optional if implementation continues on this same branch.

---

## Key references (do not re-copy)

| Artifact | Location |
|---|---|
| Implementation plan | `docs/plan/01.md` |
| PRD | `docs/prd.md`, https://github.com/kkrishguptaa/nines/issues/1 |
| Tickets | https://github.com/kkrishguptaa/nines/issues/2 … `/7` |
| Product spec | `docs/spec.md` |
| Architecture notes | `docs/system-design.md` |
| Issue tracker config | `docs/agents/issue-tracker.md` |
| Triage labels | `docs/agents/triage-labels.md` |
| Branch / commit | `cursor/skills-prd-and-plan` @ `8bbb849` |

---

## Decisions already locked

- Product name: **Nines** (spec sometimes said “Quorum”; ship as Nines).
- Issue tracker: GitHub via `gh`.
- Primary test seam: `nines.run` only.
- Stats: Wilson lower bound ≥ target for `target_met`.
- Cut order if behind: P1 → escalation (fixed N) → receipt UI. Never cut verifier synthesis or gating.

---

## Suggested skills

Invoke these in order as you start / execute:

1. **`superpowers:subagent-driven-development`** (recommended) — or **`superpowers:executing-plans`** if staying inline.
2. **`tdd`** (Matt Pocock / `.agents/skills/tdd`) — plan steps are write-failing-test → implement → pass.
3. **`implement`** (`.agents/skills/implement`) — when picking up a `ready-for-agent` ticket.
4. **`verification-before-completion`** — before claiming a task/PR done.
5. **`code-review`** — after each vertical slice lands.
6. **`impeccable`** / `/impeccable init` — only when building the comparison demo UI (Task 5+); core loop is CLI/API first.

Optional later: `diagnosing-bugs` on failures; `handoff` again when pausing mid-plan.
