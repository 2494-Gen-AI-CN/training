# D-0057 — Week plan carries a Conventions table (Convention, Kind, Applies from, Rule, Why) between Threads and Standalone demos, parsed by plan_check.py, judged by week-plan critic item 2a and passed to every day and demo author and the trainer README; week-plan.js runs up to three in-run critic passes

- Date: 2026-10-16
- Status: accepted
- Decision: Week plan carries a Conventions table (Convention, Kind, Applies from, Rule, Why) between Threads and Standalone demos, parsed by plan_check.py, judged by week-plan critic item 2a and passed to every day and demo author and the trainer README; week-plan.js runs up to three in-run critic passes
- Why: O-11: the week-1 plan needed 7 critic passes and the week-2 plan 5, each pass finding one layer deeper. Week 1's gaps were carried-line fates; week 2's were conventions a day author could not infer (pylint docstring and encoding= rules, the JSON record keys the pandas rungs select, basicConfig ordering, pushes after slid merges, typed-line tallies), and the week-2 plan already carried two of them as ad-hoc bullets under the thread. Listing every such rule up front, before the block table is sized, turns a line-level hunt into a one-row fix; a third in-run pass (two more agents at most, escalateOn 2 already puts passes 2 and 3 on opus/high) absorbs the round that used to be done by hand.
- Affects: harness/templates/week-plan.md, harness/plan_check.py (SECTIONS, CONVENTION_COLS, CONVENTION_KINDS, load_plan, check_plan, day_rows), harness/critics/week-plan.md (items 1, 2, 2a, 8), harness/workflows/week-plan.js (gated 3 passes, author prompt), harness/workflows/day-fanout.js planCtx, harness/workflows/demo-series.js header, harness/args_for.py (demos_args conventions, no-plan fallback), harness/series_readme.py, harness/plans/week-01.md and week-02.md (backfilled Conventions sections), tests/test_plans.py, tests/test_series_readme.py, trainer/week-02/demos/README.md (regenerated), harness/README.md, STATUS.md O-11
- Supersedes: —
- Superseded-by: —

## Notes

Kinds: tally | lint | schema | git | config | tooling | carried-lines. plan_check requires at least one tally and one git row, every Kind in the vocabulary, Applies from = all or a walkthrough of the ladder, no empty Rule, no pipe characters in cells. Verify on the week-3 plan run: the pass count at which the critic passed, and whether any hand round was needed.
