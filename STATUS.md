# Status

Single "what's next" surface for this repo. Read it at session start together with `decisions/README.md` (the *why*). Update it in the same commit as the work it describes. Per-day content progress lives in `harness/curriculum.json` (`status: planned | live`) and is not duplicated here.

**Phase:** pilot done; W1D2 is live. Training starts Tue 2026-10-13.
**Last updated:** 2026-10-11

## Milestones

| # | Milestone | Done | Notes |
|---|---|---|---|
| 1 | Scaffold: harness, templates, critics, tests, exemplar page | 2026-10-11 | commit `3ebdbf6` |
| 2 | Decision log (`decisions/`) | 2026-10-11 | D-0001; contract test `tests/test_decisions.py` |
| 3 | Real training dates, holidays, week 1/7/11 redistribution | 2026-10-11 | D-0013..D-0017; 51 teaching days |
| 4 | Site theme: Catppuccin Mocha dark default, IBM Plex, self-hosted fonts | 2026-10-11 | D-0018..D-0020 |
| 5 | Pilot: W1D2 single-day run, all five artifacts reviewed by hand | 2026-10-11 | run `wf_c27f2c3a-6ab`, 20 agents; research 2 passes, demos/notes/exercise 1 pass, runbook flagged after 3 and hand-fixed (4 nits); D-0021 |
| 6 | Promote the W1D2 page to the template; run W1 days 3–5 | — | set `template` arg to `docs/weeks/week-01/day-2-*.html`; page NOT yet promoted |
| 7 | Week-1 retrospective: AGENTS.md, metrics, critic specs | — | log bar changes as decisions; see O-7..O-9 |
| 8 | Weeks 2–4 | — | one day per invocation |
| 9 | Second pilot: W5D1 alone (first full gate, first LLM demos) | — | key-gated; rehearse manually |
| 10 | Weeks 5–11 | — | weeks 6–7 TF2/Keras mapping (D-0012); weeks 9–10 LangChain/LangGraph 1.x |

## Open items

| ID | Item | Owner | Needed by | Notes |
|---|---|---|---|---|
| O-1 | ~~Decide the W1D2 exercise shape~~ | — | closed 2026-10-11 | D-0021: tiny Python-orientation exercise; day-level `notes` in curriculum.json flows into every prompt as "Day note" |
| O-2 | Review-day prompt variant for `kind: review` (recap page, cumulative quiz, mini-project) | harness | before W2D5 (Fri 2026-10-23) | `day-fanout.js` only adds a runbook section today |
| O-3 | ~~Trial the Latte light mode on a real notes page~~ | — | closed 2026-10-11 | Latte checked on W1D2 (headless Chrome): ink reads fine, no darkening needed. Mocha bug found and fixed instead: `.d-example.hot text` used `--surface` (dark on dark) |
| O-4 | Site/brand wording: README still says "Revature"; topbar reads "2494·Gen-AI" | trainer | before publishing to trainees | branding colours already dropped (D-0020) |
| O-5 | Rehearse key-gated demos manually (Anthropic wk 5, Pinecone wk 8, Bedrock wk 9, SageMaker wk 11) | trainer | the week before each | critics compile-check only |
| O-6 | ~~`trainer/` private repo cloned on every machine~~ | — | closed 2026-10-11 | confirmed on this machine; W1D2 runbook + solutions committed there |
| O-7 | Phone-width layout overflows horizontally (h1 and side cards clipped at 400px) | trainer | before trainees read on phones | pre-existing in `day.exemplar.html`, not page-specific; `docs/assets/css/style.css` responsive rules |
| O-8 | NEXT links: `args_for.py` now points NEXT at the index unless the next day is already `live` (changed by the Verify FIX agent so `test_pages` passes); Wire step 4 must rewrite the previous page's NEXT when the next day ships — confirm it does on W1D3 | harness | W1D3 run | the quiz "next-day lock" (D-0009) lands on the index until then |
| O-9 | Runbook critic repeatedly caught arithmetic/date nits (float output, "tomorrow" vs Day 5, minute budgets); consider a runbook self-check line in the author prompt | harness | milestone 7 | not a bar change; prompt-only |

## Log

- 2026-10-11 — scaffold, decision log, dates, theme landed; STATUS.md created.
- 2026-10-11 — W1D2 pilot run (D-0021): 20 agents, 4/5 artifacts passed the critic, runbook hand-fixed; `tests/test_trainer.py` regex gained `re.M` (was unpassable); `args_for.py` NEXT-only-if-live; Mocha diagram text fix; page screenshots checked in Mocha and Latte.
