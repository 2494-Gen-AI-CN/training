# D-0056 — Author stages demos and runbook start on opus/high instead of sonnet/medium; the escalate tier stays for the other sonnet stages

- Date: 2026-10-15
- Status: accepted
- Decision: Author stages demos and runbook start on opus/high instead of sonnet/medium; the escalate tier stays for the other sonnet stages
- Why: In the two week-2 runs (wf_a9dff101-58c, wf_33347264-07e) the sonnet first-pass author failed its opus critic on 8 of 9 walkthrough blocks and 3 of 5 runbooks, so the pass-2 opus author ran anyway; the sonnet pass was a wasted author plus a wasted critic and a third of the run's wall-clock. The trainer asked for opus from the start (O-20).
- Affects: harness/config.json models.stages.demos + runbook, harness/workflows/demo-series.js, harness/workflows/day-fanout.js (tiers only), STATUS.md O-20
- Supersedes: —
- Superseded-by: —

## Notes

exercise, research-light, fix and humanize stay sonnet: no run has shown the same pass-2 pattern for them. escalateOn 2 -> opus/high stays as the safety net. Revisit when a run journal shows a sonnet stage escalating on most of its items.
