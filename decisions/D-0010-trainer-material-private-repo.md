# D-0010 — Trainer-only material (runbooks, solutions) lives in a separate private repo cloned at trainer/ and gitignored here

- Date: 2026-10-11
- Status: accepted
- Decision: Trainer-only material (runbooks, solutions) lives in a separate private repo cloned at trainer/ and gitignored here
- Why: The training repo is public; solutions and talk tracks must never be committed to it.
- Affects: .gitignore, harness/config.json trainerRepo, tests/test_trainer.py, harness/workflows/day-fanout.js
- Supersedes: —
- Superseded-by: —

## Notes

Tests that need trainer/ skip when it is absent. Walkthrough section 1 (Trainer material).
