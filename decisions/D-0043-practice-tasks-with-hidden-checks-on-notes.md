# D-0043 — Practice tasks with hidden checks on notes pages (ix-task in section.practice), piloted on W1D4; editor is CodeMirror 5.65.21 from a pinned jsDelivr URL (extends D-0042)

- Date: 2026-10-13
- Status: accepted
- Decision: Practice tasks with hidden checks on notes pages (ix-task in section.practice), piloted on W1D4; editor is CodeMirror 5.65.21 from a pinned jsDelivr URL (extends D-0042)
- Why: Trainer decision 2026-10-13 on seeing the D-0042 pilot: a Run button on the page's own examples is not the goal; learners should type a solution and have it run and checked. Seven short tasks, one per teaching section, sit in one Practice section before Check yourself. Each task carries its checks as plain asserts; the page reports pass or fail per check with expected and got. CodeMirror was chosen over a plain textarea for colours, line numbers and bracket matching; version 5 because it ships as single files that can be pinned exactly.
- Affects: harness/critics/notes.md items 5d and 17; tests/test_assets.py; docs/assets/js/widgets.js, pyworker.js, scrolly.js; docs/assets/css/style.css; docs/weeks/week-01/day-4-python-data-types.html; AGENTS.md; STATUS.md; trainer/week-01/day-4-python-data-types/solutions/practice.py
- Supersedes: —
- Superseded-by: —

## Notes

Amends D-0042, which stays in force for the runtime (Pyodide 314.0.7, Python 3.14.2), the ?run=1 gate, the no-fallback rule and the 27 runnable examples; its Not-in-the-pilot list no longer excludes typed solutions. Second external asset, same origin: cdn.jsdelivr.net/npm/codemirror@5.65.21, requested when the reader scrolls near the Practice section or clicks Edit on an example. Task text lives in data attributes and code in pre children, so the page's prose word count, reading minutes and humanizer rule are untouched; the section is not a section.step, so step counts, diagram captions and per-step bars are untouched. Work is kept in localStorage (tc_practice). The checks are readable in page source: the tasks are ungraded practice. This shifts D-0040's line that applying the concepts is the demos' job; whether it stays is decided with the exercise rework (O-14, O-17). Not in the pilot: the notes author prompt, the exemplar, notes_check.py, SQL.
