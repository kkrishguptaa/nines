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
