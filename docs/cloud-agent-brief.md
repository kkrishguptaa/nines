# Cloud agent: execute Nines plan

**Branch to start from:** `cursor/skills-prd-and-plan`  
**Primary plan:** `docs/plan/01.md`  
**PRD / tickets:** GitHub issues #1–#7 (`ready-for-agent`)

## Mission

Implement Nines end-to-end per `docs/plan/01.md` (Tasks 1→6). Prefer TDD at the public seam `nines.run(task, *, target, budget) -> Receipt`. Comment on / close matching GitHub issues (#2–#7) as each task lands. Open a PR to `main` when the suite is green or when blocked and needing review.

## Do not

- Re-write the PRD or plan unless a requirement is wrong.
- Commit secrets or `.env` files.
- Claim novel models / production SLAs in README.

## Secrets expected

- `ANTHROPIC_API_KEY` — real Claude calls for synthesis/solvers (tests may use fakes without it).
