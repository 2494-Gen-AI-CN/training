# D-0045 — Python in the page is switched on for every reader: the ?run=1 gate is removed (amends D-0042)

- Date: 2026-10-13
- Status: accepted
- Decision: Python in the page is switched on for every reader: the ?run=1 gate is removed (amends D-0042)
- Why: Trainer decision 2026-10-13. The pilot was checked locally and on the live URL behind the gate: the 27 W1D4 examples match CPython 3.15, the 7 practice tasks pass the contract tests and the agent-driven browser pass (57 cases in the real page), in the Full, Compact and Focus views.
- Affects: docs/assets/js/widgets.js; harness/practice_browser.py, practice_browser.js; AGENTS.md; STATUS.md
- Supersedes: —
- Superseded-by: —

## Notes

D-0042 said the widget stays off until it is checked on the live URL and on a trainee laptop on the classroom network. The live URL was checked. The trainee laptop check is dropped, not deferred (trainer, 2026-10-13): learners read the notes at home after the classroom day, on personal laptops that no IT department manages or provisions, so the client site's network and browser policy do not apply to this feature. If the runtime cannot be fetched on some machine, Run and Check show the browser's load error and the rest of the page works. Scope is unchanged: only pages that carry the markup show anything, which is W1D4. localStorage tc_run is no longer read. The practice section keeps its hidden attribute in the markup so it does not show where scripts do not run.
