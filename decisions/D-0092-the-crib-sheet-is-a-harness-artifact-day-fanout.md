# D-0092 — The crib sheet is a harness artifact: day-fanout.js writes trainer/<day>/crib-sheet.md after the runbook (author and critic on the runbook tiers), and each notebook section of the runbook carries a Trap line and one or two If asked lines

- Date: 2026-11-18
- Status: accepted
- Decision: The crib sheet is a harness artifact: day-fanout.js writes trainer/<day>/crib-sheet.md after the runbook (author and critic on the runbook tiers), and each notebook section of the runbook carries a Trap line and one or two If asked lines
- Why: The trainer asked on 2026-11-18 to apply the split recommended for the hand-made week-6 crib sheets: the sayable part (key idea, trap, likeliest question) belongs in the file the trainer presents from, and the reference part (full hard-question list, dagger-marked background, numbers, worked arithmetic, page-against-demo heads-ups) stays a separate sheet that every week gets without asking.
- Affects: harness/templates/crib-sheet.md (new), harness/critics/crib-sheet.md (new), harness/critics/runbook.md (item 3c), harness/templates/runbook.md, harness/workflows/day-fanout.js (crib stage, runbook author prompt, run record artifacts), AGENTS.md, trainer/week-06 runbooks for W6D3 to W6D5 (Teach, Trap and If asked lines folded in by hand), every day authored from week 7
- Supersedes: —
- Superseded-by: —

## Notes

No config.json change: the stage reuses the runbook and critic tiers. No humanizer pass on the sheet (reference text, not spoken). A notes-only run writes no crib sheet; a runbook-only run does. The run record gains an artifact named crib. The existing week-6 crib sheets are kept as written. Dagger lines are allowed in the sheet only, never in the runbook, and never assert an API default, version, limit or price.
