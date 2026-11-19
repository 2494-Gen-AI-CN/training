# D-0097 — A notebook day's runbook carries the direct Colab link to its notebook: on line 3, in the Setup check step where learners open it, and in the Notebook overview section

- Date: 2026-11-19
- Status: accepted
- Decision: A notebook day's runbook carries the direct Colab link to its notebook: on line 3, in the Setup check step where learners open it, and in the Notebook overview section
- Why: The trainer asked on 2026-11-19 for the Colab links in the runbooks. Delivery is remote, so the fastest recovery for a learner who cannot find the notebook through File > Open notebook > GitHub is a link pasted in the chat, and a substitute trainer should not have to build that URL.
- Affects: harness/templates/runbook.md, harness/critics/runbook.md (items 1b, 3c), harness/workflows/day-fanout.js (runbook author prompt), tests/test_trainer.py, trainer/week-06 runbooks for W6D3 to W6D5 (links added by hand), every notebook day authored from week 7
- Supersedes: —
- Superseded-by: —

## Notes

The link is https://colab.research.google.com/github/<demoRepo.org>/<demoRepo.name>/blob/<demoRepo.branch>/<notebook path>, built from config.json demoRepo and the day's notebook path; no config change. Applies to demoFormat notebook days only, from W6D3; W6D1 and W6D2 were delivered without it and are not re-judged. Extends D-0085 and D-0096.
