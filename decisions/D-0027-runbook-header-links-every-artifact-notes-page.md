# D-0027 — Runbook header links every artifact: notes page on the public site (config.json siteUrl, new), demos, exercise and research brief on the public repo as absolute URLs, solutions/ relatively

- Date: 2026-10-11
- Status: accepted
- Decision: Runbook header links every artifact: notes page on the public site (config.json siteUrl, new), demos, exercise and research brief on the public repo as absolute URLs, solutions/ relatively
- Why: Runbooks live in the separate private trainer repo, so the plain paths in the header did not resolve when read on GitHub or in an editor; the trainer wants one-click access to the day's artifacts from the runbook.
- Affects: harness/config.json (siteUrl), harness/args_for.py, harness/templates/runbook.md, harness/workflows/day-fanout.js runbook prompt, harness/critics/runbook.md item 1b, tests/test_trainer.py, trainer/week-01/day-2-orientation-agile-and-git/runbook.md
- Supersedes: —
- Superseded-by: —
