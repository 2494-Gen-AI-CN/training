# Decision log

Append-only record of on-the-fly decisions (schedule changes, scope cuts, API-currency calls, naming). **Read this table at the start of every session before touching `harness/curriculum.json`, `metrics.json`, `config.json`, `harness/critics/*.md` or the calendar.** Never undo a logged decision; supersede it with a new entry.

- **Add an entry:** `python decisions/new.py "One-line decision" --why "..." --affects "files, weeks, days" [--supersedes D-00xx] [--status proposed]` → prints the new ID. Put that ID in the commit message.
- **Entry file:** `D-NNNN-<slug>.md` with fields Date, Status (proposed | accepted | superseded), Decision, Why, Affects, Supersedes, Superseded-by. Optional `## Notes`.
- **Contract test:** `tests/test_decisions.py` checks IDs are unique and sequential, fields present, supersede links resolve, and every `D-NNNN` cited in the repo exists.

Newest first.

| ID | Date | Status | Decision | Affects | Supersedes |
|---|---|---|---|---|---|
| D-0012 | 2026-10-11 | accepted | Currency flags: weeks 6-7 name TF1/TFLearn concepts, weeks 9-10 name pre-1.0 LangChain/LangGraph APIs; teach the current equivalents, keep the curriculum topic names in titles only | harness/curriculum.json notes on weeks 6, 7, 9, 10; harness/critics/research.md; every author/critic prompt for those weeks | — |
| D-0011 | 2026-10-11 | accepted | GitHub org 2494-Gen-AI-CN base permission is none; access is granted per repository | GitHub org settings, trainer repo collaborators | — |
| D-0010 | 2026-10-11 | accepted | Trainer-only material (runbooks, solutions) lives in a separate private repo cloned at trainer/ and gitignored here | .gitignore, harness/config.json trainerRepo, tests/test_trainer.py, harness/workflows/day-fanout.js | — |
| D-0009 | 2026-10-11 | accepted | Keep the quiz Next-day lock on notes pages | docs/assets/js/quiz.js, harness/templates/day.exemplar.html, harness/metrics.json quizQuestions | — |
| D-0008 | 2026-10-11 | accepted | The content workflow runs one training day per Workflow invocation | harness/workflows/day-fanout.js, harness/args_for.py, harness/README.md | — |
| D-0007 | 2026-10-11 | accepted | Directory naming is week-WW/day-N-slug everywhere; the short id (w01d1) is only for meta tags, localStorage keys and test keys | harness/curriculum.json slugs, harness/build_index.py day_paths, all per-day directories | — |
| D-0006 | 2026-10-11 | accepted | Tiered research gate: full web-verified gate for weeks 5, 8, 9, 10, 11; light gate for weeks 1-4, 6, 7 | harness/curriculum.json gate per day, harness/critics/research.md, tests/test_curriculum.py test_gate_tiers_match_decision | — |
| D-0005 | 2026-10-11 | accepted | Demo format: .py scripts by default, notebooks (.ipynb) where the topic is exploratory | harness/curriculum.json demoFormat per day, harness/critics/demos.md | — |
| D-0004 | 2026-10-11 | accepted | Site root is docs/, served natively by GitHub Pages from main; no CI | docs/, harness/build_index.py, docs/index.html WEEKS block | — |
| D-0003 | 2026-10-11 | accepted | Fork the reference site HTML/JS stack (style.css, quiz, diagram, scrolly, modals, glossary, codeviewer); strip everything backend-coupled | docs/assets/, harness/templates/day.exemplar.html, tests/test_assets.py | — |
| D-0002 | 2026-10-11 | accepted | Per-day artifact set: research brief, demo code, notes page with quiz, exercise with pytest checks, trainer runbook | harness/workflows/day-fanout.js, harness/critics/, harness/templates/, every week/day | — |
| D-0001 | 2026-10-11 | accepted | Adopt an append-only decision log in decisions/ | decisions/, AGENTS.md, harness/README.md, harness-walkthrough.html, tests/test_decisions.py | — |
