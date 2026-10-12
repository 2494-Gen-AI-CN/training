# Status

Single "what's next" surface for this repo. Read it at session start together with `decisions/README.md` (the *why*). Update it in the same commit as the work it describes. Per-day content progress lives in `harness/curriculum.json` (`status: planned | live`) and is not duplicated here.

**Phase:** codify Stage 3 done (W1D2 re-authored under D-0030, page promoted to template, D-0031); W1D2 is `live`. Next: codify Stage 2 (week plan for week 1) before W1D3 is authored, then run W1D3 (Wed 2026-10-14); Stage 4 (delivery-day close) Tue evening regardless. Training starts Tue 2026-10-13.
**Last updated:** 2026-10-12

## Milestones

| # | Milestone | Done | Notes |
|---|---|---|---|
| 1 | Scaffold: harness, templates, critics, tests, exemplar page | 2026-10-11 | commit `3ebdbf6` |
| 2 | Decision log (`decisions/`) | 2026-10-11 | D-0001; contract test `tests/test_decisions.py` |
| 3 | Real training dates, holidays, week 1/7/11 redistribution | 2026-10-11 | D-0013..D-0017; 51 teaching days |
| 4 | Site theme: Catppuccin Mocha dark default, IBM Plex, self-hosted fonts | 2026-10-11 | D-0018..D-0020 |
| 5 | Pilot: W1D2 single-day run, all five artifacts reviewed by hand | 2026-10-11 | run `wf_c27f2c3a-6ab`, 20 agents; research 2 passes, demos/notes/exercise 1 pass, runbook flagged after 3 and hand-fixed (4 nits); D-0021 |
| 6 | Promote the W1D2 page to the template; run W1 days 3–5 | first half 2026-10-12 | W1D2 re-authored under D-0030 and `live` again (run `wf_c89736b4-05f`, 17+15 agents across a usage-limit restart, 0 flagged); `config.json` `template` = the W1D2 page (D-0031). Second half: W1D3–W1D5, one invocation each, after codify Stage 2 writes `harness/plans/week-01.md` |
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
| O-10 | Codify the mined TRNG-2442 rules: staged plan with per-session prompts in `docs/process/codify-plan.md` (Stage 1 demo contract → Stage 3 W1D2 re-author → Stage 2 week plan → W1D3 → Stage 4 delivery close → Stages 7, 5, 6; reordered 2026-10-12) | trainer | Stage 2 before W1D3 is authored (Wed 2026-10-14 morning at the latest; fallback: W1D3 first, Stage 2 before W1D4); Stage 4 Tue 2026-10-13 evening | Stage 0 (humanizer, D-0029) done 2026-10-11. Stage 1 (demo contract, D-0030) done 2026-10-11: scripts + answer keys in `trainer/<rel>/demos/`, `demo_check.py`, `publish_demos.py` gated on `taught`, `demoFormat: none`; W1D2 set to `planned` because its five old-shape `.py` demos (public, no scripts) fail the new tests; Stage 3 (D-0031) done 2026-10-12: `demos/week-01/day-2-*/` removed, three typed scripts + keys (1 `.py`, 2 transcripts) in `trainer/week-01/day-2-*/demos/`, notes/exercise/runbook regenerated, page promoted to template. Stage 4 must set `taught` and run `publish_demos.py` in the close |

## Log

- 2026-10-12 — Codify Stage 2 widened to demo threads (catalog A7, A10, A12, A23, A24): demos become rungs of one growing codebase across days and weeks; the stage now asks four questions first (thread scope, demo domain, week 1 start, enforcement) and amends the demo contract (`Thread:` / `Starts from:` header bullets, carried-lines both-ways check, chain test). Prompt-only change in `docs/process/codify-plan.md`; nothing built yet, the decisions are minted in the Stage 2 session. Known limit recorded there: single-file keys only until a later stage.
- 2026-10-12 — D-0032: `config.json` `models.stages` gains `week-plan` and `week-plan-critic`, both inherit/high, ahead of codify Stage 2 (the workflow that reads them does not exist yet; the Stage 2 prompt in `docs/process/codify-plan.md` now names them).
- 2026-10-12 — Codify plan reordered: Stage 2 (week plan) moves ahead of the W1D3 run. The old order authored W1D3 before any week plan existed, while Stage 2's own prompt assumes D3–D5 are still unauthored; three of week 1's four teaching days now get the demo ladder, anti-spoiler ledger, coverage map and stop points before they are written. Stage 4 stays Tue evening. Doc-only change (`docs/process/codify-plan.md`), no decision entry.
- 2026-10-12 — D-0031 (codify Stage 3): W1D2 demos re-authored under the demo contract. Old public `demos/week-01/day-2-*/` (five `.py`) removed; `trainer/week-01/day-2-*/demos/` now holds `01_tooling_check.md` (15 min, `.py` key), `02_local_git_loop.md` (40 min, transcript key), `03_remote_round_trip.md` (30 min, transcript key); SDLC/Agile/Scrum/story points/professionalism/SCM are eight runbook Facilitation blocks. Run `wf_c89736b4-05f`: research reused via new `args_for.py --skip-research` (cross-session `resumeFromRunId` cannot replay), demos 2 passes (pass-1 critic caught a `git pull` refusal that does not reproduce on Git for Windows and a `set-url` ordering break), notes 1 pass (humanizer: 4 sentences, 1711 words), exercise 1 pass, runbook 2 passes (pass 1: Facilitation 10 misplaced, 7 objectives, interpreter-vs-compiler twice); first run lost runbook/wire/verify to a usage limit, resume finished them; 0 flagged, 39 tests green. Page promoted to the notes template via `config.json` `template` (exemplar stays fallback + test gold standard). Brief's two old-contract hint lines (subprocess runner) rewritten by hand.
- 2026-10-11 — D-0030 (codify Stage 1): demo contract. A demo is the walkthrough script the trainer types (`trainer/<rel>/demos/NN_<slug>.md`, template `demo-script.md`), the code is its answer key (`key/`), checked both ways by `harness/demo_check.py`; keys publish to `demos/<rel>/` via `harness/publish_demos.py` only once `taught` is set; concept subtopics are runbook Facilitation blocks; `demoFormat: none`. Critics (demos rewrite, notes, runbook), metrics, templates, day-fanout, build_index, tests updated. W1D2 → `planned` (old demos fail the new contract; Stage 3 re-authors). 38 tests green.
- 2026-10-11 — scaffold, decision log, dates, theme landed; STATUS.md created.
- 2026-10-11 — W1D2 pilot run (D-0021): 20 agents, 4/5 artifacts passed the critic, runbook hand-fixed; `tests/test_trainer.py` regex gained `re.M` (was unpassable); `args_for.py` NEXT-only-if-live; Mocha diagram text fix; page screenshots checked in Mocha and Latte.
- 2026-10-11 — D-0023/D-0024/D-0025: learner persona (config.json audience), week-1 arc + W1D2 reshape (30-min on-ramp, then SDLC → Agile → Scrum → story points → Git), rubric exercise kind (Git exercise is the exercise). W1D2 re-run `wf_ce312ce5-ce9`: 20 agents, 40.5 min, 0 flagged, tests green; page is 1 on-ramp step + 5 team-practice steps, 1766 words.
- 2026-10-11 — D-0029: humanizer pass on every notes page (workflow stage after the notes author, critic item 18, AGENTS.md rule); W1D2 page humanized by hand (5 sentences). `docs/process/codify-plan.md` written: kickoff prompt + 7 stage prompts for clean sessions.
- 2026-10-11 — D-0028: mined the TRNG-2442 prep repo for reusable process rules; catalog at `docs/process/mined-rules-catalog.md` (A–I: demo authoring, notes, exercises, governance, delivery model, machinery, lessons, gap map, candidate skills). Nothing codified; O-10 opened.
- 2026-10-11 — D-0022: Markdown-style code on notes pages (inline chips, fenced `<pre><code>` command blocks); CSS, exemplar example, notes author prompt line, W1D2 retrofitted with 6 blocks (1779 words, still in band).
