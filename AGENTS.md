# AGENTS

## Agent skills

### Issue tracker

GitHub Issues for `kkrishguptaa/nines` via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: root `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.

## Cursor Cloud specific instructions

Cloud environment is defined by `.cursor/environment.json` + `.cursor/Dockerfile` (Python 3 on Ubuntu, `git`, `gh`, `sudo`).

1. **Mission brief:** read `docs/cloud-agent-brief.md`, then execute `docs/plan/01.md` task-by-task.
2. **Constraints:** public seam is `nines.run` only; Wilson lower bound gates `target_met`; verifier-first; never silent best-guess when zero passes. Details in `docs/prd.md` and issue #1.
3. **Secrets:** use `ANTHROPIC_API_KEY` from the environment for live model calls. Prefer fake solver/synthesizer ports in unit tests so CI-like runs work without spending.
4. **Verify:** after each task, run `pytest -v` (or the task’s named test file). Do not claim done without a green relevant suite.
5. **Tracker:** comment on / close GitHub issues #2–#7 as matching plan tasks complete; use labels from `docs/agents/triage-labels.md`.
6. **Install:** if `pyproject.toml` exists, `pip install -e ".[dev]"` (also run by the environment `install` script on Builds).

## Learned User Preferences

- Prefer TDD when implementing `nines.run` and plan tasks; open a PR to `main` when the relevant suite is green.
- Ship setup and product work through PRs into `main` rather than landing directly on `main`.
- Never lower the reliability target, widen the Wilson interval, or soften a checker to manufacture a green `target_met` for demos.
- Keep buyer-facing copy plain-language, but retain a technical spine (Wilson lower bound, canary/known-bad, claims limits) — do not CEO-wash the mechanism for technical judges.
- Do not present `nines.run` as an owned web domain in video or marketing; the public seam is the Python `nines.run` API.
- When verifying work, prefer runnable `examples/` that show live library usage, not only unit tests.

## Learned Workspace Facts

- License is Apache-2.0 (chosen so others can embed Nines as infrastructure).
- Matt Pocock skills live under `.agents/skills/` (`to-spec` for PRDs, `to-tickets` for issues); Impeccable is at `.cursor/skills/impeccable`.
- Comparison/demo CLI is `python -m demo.compare`; demo honesty and claim boundaries live in `docs/claims.md`.
- Cross-agent plan handoff is documented in `docs/handoff-execute-plan.md` (plus the `handoff` skill).
- Runnable samples live under `examples/` (`basic_run.py`, `wilson_escalate.py`, `compare_demo.py`, and related demo helpers).
