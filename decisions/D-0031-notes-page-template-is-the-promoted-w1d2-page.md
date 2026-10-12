# D-0031 — Notes-page template is the promoted W1D2 page: config.json template names docs/weeks/week-01/day-2-orientation-agile-and-git.html, args_for.py passes it as args template, and harness/templates/day.exemplar.html stays the fallback when that file is missing and the structure gold standard for the tests

- Date: 2026-10-11
- Status: accepted
- Decision: Notes-page template is the promoted W1D2 page: config.json template names docs/weeks/week-01/day-2-orientation-agile-and-git.html, args_for.py passes it as args template, and harness/templates/day.exemplar.html stays the fallback when that file is missing and the structure gold standard for the tests
- Why: Codify plan Stage 3 step 5 / milestone 6: after the W1D2 pilot and its re-author under D-0030 the real page carries every later fix (Markdown-style code D-0022, humanized prose D-0029, pending demo card D-0030) that the hand-written exemplar only approximates; future authors copy a page that has passed the critics. Promotion is a config value so a better page can replace it by decision, never by editing prompts
- Affects: harness/config.json (template), harness/args_for.py (template resolution + fallback), harness/workflows/day-fanout.js (TEMPLATE reads args.template, unchanged), harness/critics/notes.md (structure gold standard = the template named in the prompt), harness/README.md Changing the bar, tests/test_pages.py test_configured_template_exists
- Supersedes: —
- Superseded-by: —

## Notes

Same commit also adds args_for.py --skip-research (args.skipResearch): day-fanout.js returns the research stage as cached and reuses the committed brief, for re-runs from a new session where Workflow resumeFromRunId cannot replay the old journal. Not a bar change; recorded here for traceability.
