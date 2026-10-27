# D-0070 — The demo repo carries trainer-guided activity workbooks under activities/<week>-<slug>/, learner-facing and outside the thread folder; first use is the W3D3 normalization workbooks (guided college sheet, group clinic activity) that replace the whiteboard facilitations

- Date: 2026-10-27
- Status: accepted
- Decision: The demo repo carries trainer-guided activity workbooks under activities/<week>-<slug>/, learner-facing and outside the thread folder; first use is the W3D3 normalization workbooks (guided college sheet, group clinic activity) that replace the whiteboard facilitations
- Why: The room had seen the desk ERD on Monday, so normalizing the desk on the board was rediscovering a known answer; the trainer's established method (a guided workbook on an unrelated theme, one sheet per form, then groups normalizing ambiguous data and presenting their process) needs a learner-facing home for non-code files, which did not exist. D-0069 is the precedent for assets on demos main; close_day.py diffs only the thread folder, so activities/ never pollutes a block diffstat. Walkthroughs 05 to 10, the plan, the exit map and the notes page are untouched.
- Affects: demo-repo activities/week-03-normalization/ (README.md, college-normalization.xlsx, clinic-normalization.xlsx), trainer week-03/day-3 runbook (facilitation and sprint slot) and activities/ (keys, build_workbooks.py, clinic-key.md), trainer week-03/day-4 runbook (R-05 carry-over), AGENTS.md
- Supersedes: —
- Superseded-by: —
