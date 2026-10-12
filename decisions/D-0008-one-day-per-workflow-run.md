# D-0008 — The content workflow runs one training day per Workflow invocation

- Date: 2026-10-11
- Status: superseded
- Decision: The content workflow runs one training day per Workflow invocation
- Why: About 12 agents on a clean pass and about 27 worst case per day; week-sized runs blow the agent budget and lose resumability.
- Affects: harness/workflows/day-fanout.js, harness/args_for.py, harness/README.md
- Supersedes: —
- Superseded-by: D-0038

## Notes

Walkthrough section 1 (Agent budget) and section 7. Re-runs pass resumeFromRunId.
