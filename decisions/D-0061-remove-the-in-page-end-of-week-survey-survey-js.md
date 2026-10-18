# D-0061 — Remove the in-page end-of-week survey (survey.js and the #survey section on the last teaching day); the MS Forms feedback link in the index rail and the runbook stays; closing the learner-feedback loop into the author pipeline is deferred as STATUS O-22

- Date: 2026-10-17
- Status: accepted
- Decision: Remove the in-page end-of-week survey (survey.js and the #survey section on the last teaching day); the MS Forms feedback link in the index rail and the runbook stays; closing the learner-feedback loop into the author pipeline is deferred as STATUS O-22
- Why: survey.js saved answers to localStorage only and then told the learner to fill in the form linked above: a dead end that doubled the work and sent nothing back. Every prose pain point in D-0060 was inferred from the text, none from a learner, because no learner signal reaches the harness. Removing the widget is cheap and honest; choosing a channel (Forms export, issues, something else) is a separate decision.
- Affects: docs/assets/js/survey.js (deleted), docs/weeks/week-01/day-5 and week-02/day-5 pages (div.survey removed), harness/workflows/day-fanout.js (notes author survey clause), harness/critics/notes.md item 9, tests/helpers.py ALLOWED_JS, tests/test_pages.py, STATUS.md O-22
- Supersedes: —
- Superseded-by: —
