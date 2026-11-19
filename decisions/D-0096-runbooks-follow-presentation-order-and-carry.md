# D-0096 — Runbooks follow presentation order and carry content notes, not a script: one section per glance-table row in the order the day runs, Notes / Covering blocks in place of Teach, Say and Bridge lines, three to five If asked lines per block, and a crib-sheet link on line 3

- Date: 2026-11-18
- Status: accepted
- Decision: Runbooks follow presentation order and carry content notes, not a script: one section per glance-table row in the order the day runs, Notes / Covering blocks in place of Teach, Say and Bridge lines, three to five If asked lines per block, and a crib-sheet link on line 3
- Why: The trainer asked on 2026-11-18, after reading the D-0089 shape on the week-6 runbooks: the place in the day was easy to lose because breaks, lunch and the split notebook pass were not in file order, and scripted Teach / Say lines were not wanted. What is wanted is notes on what each block covers and what each thing is, deep enough that a substitute trainer can deliver from the file; a longer runbook is acceptable.
- Affects: harness/templates/runbook.md, harness/critics/runbook.md (items 1, 1b, 3b, 3c, 6, 7), harness/templates/crib-sheet.md, harness/critics/crib-sheet.md (item 3), harness/workflows/day-fanout.js (runbook author, humanizer, runbook critic and crib prompts), tests/test_trainer.py, AGENTS.md, trainer/week-06 runbooks for W6D3 to W6D5 (restructured by hand), every day authored from week 7
- Supersedes: —
- Superseded-by: —

## Notes

Amends D-0089 and D-0092 without superseding them. D-0089 stands in that a Facilitation block is the presenter's lecture notes and a trainer who opened neither the brief nor the notes page can teach from it; its Teach and Bridge labels and the notebook sections' Teach and Say lines are replaced by Notes (Facilitation topics) and Covering plus one bullet per term (notebook sections). D-0092 stands in that the crib sheet is a harness artifact and dagger lines live only there; the runbook's If asked count rises from one or two to three to five per notebook section, a Facilitation block gains an If asked list, and Heads-up lines are allowed in the runbook. The notebook pass is split into Notebook part sections placed where they run; the exact '## Notebook: <file>.ipynb' heading stays as a short overview section above part 1. Breaks and lunch get their own short sections when they are glance rows. Common questions and If running long / short stay last as reference. Sourcing is unchanged: brief or notes page only. Runbooks delivered before 2026-11-18 keep their shape and are not re-judged.
