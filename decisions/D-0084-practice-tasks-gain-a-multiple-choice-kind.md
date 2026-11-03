# D-0084 — Practice tasks gain a multiple-choice kind ('choice'): a concept step may carry a radio-button question checked in the page by JavaScript (no Pyodide), with 3-5 options, one right answer and an explanation; the suitability pass may propose it where a Python task does not fit; metrics.json practice carries choiceOptionsMin/Max

- Date: 2026-11-03
- Status: accepted
- Decision: Practice tasks gain a multiple-choice kind ('choice'): a concept step may carry a radio-button question checked in the page by JavaScript (no Pyodide), with 3-5 options, one right answer and an explanation; the suitability pass may propose it where a Python task does not fit; metrics.json practice carries choiceOptionsMin/Max
- Why: Week 5 is a concept week (D-0082) whose steps teach judgement about AI-assisted development, not code behaviour; the trainer asked (2026-11-03) for multiple-choice practice so every teaching step can carry a task instead of returning none
- Affects: harness/practice_tasks.py, docs/assets/js/widgets.js, docs/assets/css/style.css, harness/practice_browser.py, harness/practice_browser.js, harness/critics/practice.md, harness/workflows/practice-tasks.js, harness/metrics.json, tests/test_practice.py, tests/test_assets.py, AGENTS.md
- Supersedes: —
- Superseded-by: —
