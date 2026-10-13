# D-0042 — Runnable Python blocks on notes pages (pre data-run), piloted on W1D4; runtime is Pyodide 314.0.7 from a pinned jsDelivr URL

- Date: 2026-10-13
- Status: accepted
- Decision: Runnable Python blocks on notes pages (pre data-run), piloted on W1D4; runtime is Pyodide 314.0.7 from a pinned jsDelivr URL
- Why: Trainer decision 2026-10-13 after a feasibility study. A reader can run, edit and re-run a page's examples in the browser with no backend. No stable Pyodide ships Python 3.15, so the widget runs 3.14.2 and says so; the 72 Python blocks of the week-1 pages gave identical output on CPython 3.14.4 and 3.15.0 apart from two stdout-encoding artifacts. jsDelivr was chosen over vendoring 13.5 MB of runtime into a repo trainees pull every morning.
- Affects: harness/critics/notes.md item 17; tests/helpers.py ALLOWED_JS; tests/test_assets.py; docs/assets/js/widgets.js and new docs/assets/js/pyworker.js; docs/assets/css/style.css; docs/weeks/week-01/day-4-python-data-types.html; AGENTS.md; STATUS.md
- Supersedes: —
- Superseded-by: —

## Notes

Pilot scope: W1D4 only, and the widget stays off unless the URL carries ?run=1 (or localStorage tc_run is 1) until it is checked on the live URL and on a trainee laptop on the classroom network. First third-party origin on the site: cdn.jsdelivr.net/npm/pyodide@314.0.7, requested only when a reader clicks Run. No fallback in the pilot: a runtime or worker failure is shown as it is, in the page and in the console. Convention: pre data-run=python marks a complete script; data-continues runs the nearest preceding runnable block first, silently. Not in the pilot: the notes author prompt, the exemplar template, input() blocks, multi-file blocks, SQL (bespoke solution later).
