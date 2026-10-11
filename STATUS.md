# Status

Single "what's next" surface for this repo. Read it at session start together with `decisions/README.md` (the *why*). Update it in the same commit as the work it describes. Per-day content progress lives in `harness/curriculum.json` (`status: planned | live`) and is not duplicated here.

**Phase:** pilot not yet run. Training starts Tue 2026-10-13.
**Last updated:** 2026-10-11

## Milestones

| # | Milestone | Done | Notes |
|---|---|---|---|
| 1 | Scaffold: harness, templates, critics, tests, exemplar page | 2026-10-11 | commit `3ebdbf6` |
| 2 | Decision log (`decisions/`) | 2026-10-11 | D-0001; contract test `tests/test_decisions.py` |
| 3 | Real training dates, holidays, week 1/7/11 redistribution | 2026-10-11 | D-0013..D-0017; 51 teaching days |
| 4 | Site theme: Catppuccin Mocha dark default, IBM Plex, self-hosted fonts | 2026-10-11 | D-0018..D-0020 |
| 5 | Pilot: W1D2 single-day run, all five artifacts reviewed by hand | — | `python harness/args_for.py 1 2 --today 2026-10-13` → Workflow `harness/workflows/day-fanout.js` |
| 6 | Promote the W1D2 page to the template; run W1 days 3–5 | — | set `template` arg to `docs/weeks/week-01/day-2-*.html` |
| 7 | Week-1 retrospective: AGENTS.md, metrics, critic specs | — | log bar changes as decisions |
| 8 | Weeks 2–4 | — | one day per invocation |
| 9 | Second pilot: W5D1 alone (first full gate, first LLM demos) | — | key-gated; rehearse manually |
| 10 | Weeks 5–11 | — | weeks 6–7 TF2/Keras mapping (D-0012); weeks 9–10 LangChain/LangGraph 1.x |

## Open items

| ID | Item | Owner | Needed by | Notes |
|---|---|---|---|---|
| O-1 | Decide the W1D2 exercise shape (orientation/git day; pytest exercise is awkward) | trainer | before milestone 5 | proposal: parse a `git log --oneline` fixture so the exercise contract holds on day one |
| O-2 | Review-day prompt variant for `kind: review` (recap page, cumulative quiz, mini-project) | harness | before W2D5 (Fri 2026-10-23) | `day-fanout.js` only adds a runbook section today |
| O-3 | Trial the Latte light mode on a real notes page; darken ink if it reads weak | trainer | during milestone 5 | Latte ink is 7.1:1, weakest of the candidates (D-0020) |
| O-4 | Site/brand wording: README still says "Revature"; topbar reads "2494·Gen-AI" | trainer | before publishing to trainees | branding colours already dropped (D-0020) |
| O-5 | Rehearse key-gated demos manually (Anthropic wk 5, Pinecone wk 8, Bedrock wk 9, SageMaker wk 11) | trainer | the week before each | critics compile-check only |
| O-6 | `trainer/` private repo: confirm it is cloned on every machine the workflow runs on | trainer | before milestone 5 | tests skip when absent |

## Log

- 2026-10-11 — scaffold, decision log, dates, theme landed; STATUS.md created.
