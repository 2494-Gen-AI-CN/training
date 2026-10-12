# D-0032 — Model tiers for the week-plan workflow: config.json models.stages gains week-plan (author) and week-plan-critic, both inheriting the session model at high effort

- Date: 2026-10-12
- Status: accepted
- Decision: Model tiers for the week-plan workflow: config.json models.stages gains week-plan (author) and week-plan-critic, both inheriting the session model at high effort
- Why: Codify Stage 2 adds harness/workflows/week-plan.js (one author, one critic, run once per week). The plan's content (demo ladder with dependency guarantees, anti-spoiler ledger, coverage map across every day of the week) is the judgment-heavy part and every day of that week is authored against it, so neither agent goes on a cheap tier; inheriting means both follow whichever model the session is launched on. The generic critic tier stays at medium for per-day critics
- Affects: harness/config.json (models.stages week-plan, week-plan-critic), harness/workflows/week-plan.js (to be written in codify Stage 2), docs/process/codify-plan.md Stage 2 prompt
- Supersedes: —
- Superseded-by: —
