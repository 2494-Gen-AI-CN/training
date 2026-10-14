# Codify plan: turning the mined rules into this harness, one stage per clean session

Companion to `mined-rules-catalog.md` (D-0028). Row IDs below (A1, D16, F5 ...) point at that catalog.
Each stage is sized for one Claude Code session. Run them in the recommended order; each stage's exit criteria
are the next stage's entry conditions. Training starts Tue 2026-10-13, so stages 1 and 3 came first; Stage 2 (week
plan) now runs before W1D3 so the three unauthored days of week 1 are written against a plan (reordered 2026-10-12).
Target cadence since D-0038: week N is fully authored by the close of week N-1 (one batch run per week), every
delivery day ends with the close audit of Stage 4, and Stage 8's Friday gate releases the next week.

## Kickoff prompt (paste at the top of every clean session, then the stage block)

```
You are working in C:\Users\JonathanDeLaCruz\Documents\Revature\CGZT-Canada\2494-Gen-AI-CN (public repo 2494-Gen-AI-CN/training;
trainer/ is a separate private repo, gitignored). Read, in this order: STATUS.md, decisions/README.md, AGENTS.md,
docs/process/codify-plan.md, then only the catalog rows the stage names in docs/process/mined-rules-catalog.md.
Run `python -m unittest discover -s tests -v` before and after every change; keep it green.

Facts already established (do not re-derive): dates derive from curriculum.json startDate + holidays (D-0013, D-0014);
one Workflow invocation per week batch or per single day, args only from `python harness/args_for.py <week> <day...> --today <date>` (D-0038);
learner persona lives in config.json audience (D-0023); exerciseKind pytest|rubric (D-0025); per-stage model tiers in
config.json models (D-0026); every notes page gets a humanizer pass before its critic (D-0029).

Rules for this session: use Edit/Write for code (no sed, no heredocs with escapes). Any change to curriculum.json,
metrics.json, config.json, critics/*.md, templates or the calendar needs `python decisions/new.py ...` and the ID in
the commit message. Update STATUS.md in the same commit, then run `python harness/build_tracker.py` (D-0035; the
staleness test fails otherwise). tracker.html is a local, gitignored file (D-0036): never commit it. After any
Workflow run, complete its run record:
`python harness/log_run.py amend --last --run-id <wf_...> --minutes M --tokens T --tiers-verified yes|no`.
Ask before any action that costs more than ~30 agents.
Push only if tests are green; otherwise stop and report. Do not run any training day the stage does not name.

Execute ONLY the stage below. Stop at its exit criteria and report: what changed (paths), decision IDs minted,
test result, anything left undone and why.
```

## Recommended order and sizing

| Order | Stage | Why first | Size |
|---|---|---|---|
| ~~1~~ | ~~Stage 1 Demo contract~~ | ~~Everything downstream (W1D2 re-author, W1D3–5) depends on what a demo is~~ | ~~1 session, no agents~~ done 2026-10-11, D-0030 |
| ~~2~~ | ~~Stage 3 Re-author W1D2 demos + promote page~~ | ~~Tue 2026-10-13 is W1D2; must be taught from the new contract~~ | ~~1 session, ~20 agents~~ done 2026-10-12, D-0031 |
| ~~3~~ | ~~Stage 2 Week plan artifact + demo threads~~ | ~~W1D3–W1D5 are still unauthored: plan week 1 (demo ladder, anti-spoiler ledger, coverage map, stop points) and make the demos one growing thread (rungs that extend the previous rung's key) before any of them is written. Must land before Wed 2026-10-14 morning; if it cannot, run W1D3 first and Stage 2 before W1D4~~ | ~~1 long session, ~3 agents; amends the demo contract (`demo_check.py`, demos critic, demo-script template, metrics)~~ done 2026-10-12, D-0033 (demo threads) + D-0034 (week plan); `harness/plans/week-01.md` written by `week-plan.js` |
| ~~4~~ | ~~Week-1 batch run W1D3–W1D5 (milestone 6)~~ | ~~Wed 2026-10-14 needs its material; first use of the week batch (D-0038): demos in day order, the rest in parallel~~ | ~~1 session, ~60 agents (approved 2026-10-12)~~ done 2026-10-12, run `wf_55423fc5-aa6`, 67 agents, 0 flagged |
| ~~5~~ | ~~Stage 4 Daily close audit~~ | ~~Needed Tue 2026-10-13 evening after the first delivery; audits the classroom repo against the keys, sets `taught`, carries unreached steps to the next day, re-checks later rungs~~ | ~~1 session, no agents~~ loose close built 2026-10-14, D-0050 (`close_day.py`; W1D2 and W1D3 closed); the rung-diff close for thread days is deferred to week 3 (O-18) |
| ~~6~~ | ~~Stage 8 Hidden week, Friday gate, series review, drift check~~ | ~~Week-ahead authoring needs pages that stay unlinked until the Friday release; by Thu 2026-10-15~~ | ~~1 session, no agents~~ done 2026-10-14, D-0052, D-0053 |
| 7 | Week-2 plan and batch | By Fri 2026-10-16; settle O-11 and O-12 first | 2 sessions, ~5 + ~100 agents (ask first) |
| ~~8~~ | ~~Stage 7 Notes depth (interview sections)~~ | ~~Fits the persona; touches critic + template. Notes keep their delivery references for now (trainer decision 2026-10-12: wait for learner feedback)~~ | ~~1 session~~ done 2026-10-13, D-0040, widened to the reference-notes rework (4500–7000 words, Check yourself, citations, no delivery references) + notes QC (`notes_check.py`, notes-verify agent, pinned tiers); the stance of 2026-10-12 was reversed by the trainer on 2026-10-13 |
| 9 | Stage 5 Rules registry + OVERRIDE state | Governance; no delivery dependency | 1 session |
| 10 | Stage 6 Skills | After the processes have run at least once by hand | 1–2 sessions |

Stage 0 (humanizer pass, D-0029) was done on 2026-10-11 in the session that wrote this plan.

---

## Stage 1 — Demo contract (catalog A1, A3, A5, A13, A17, A21, A22, A27, A28, A29, A30, C1, H)

```
STAGE 1 — Demo contract.
Read catalog rows A1, A3, A5, A13, A17, A21, A22, A27, A28, A29, A30, C1 and section H. Read harness/critics/demos.md,
harness/metrics.json (demos), harness/templates/demo-README.md, harness/workflows/day-fanout.js demosStage() and
materialsStage(), tests/test_demos.py, tests/test_pages.py (demo-card and popup checks), and the current W1D2 demos in
demos/week-01/day-2-orientation-agile-and-git/.

BEFORE any edit, ask me these with AskUserQuestion (one call), recommended answers from the catalog in parentheses:
1. Visibility: trainer-only until taught then published (A21: recommended), public from day one (current), or never published.
2. Process/concept days (SDLC, Scrum; later MLOps concepts): no code demo + facilitation script in the runbook (A22: recommended),
   keep print-style scripts, or reference artefacts (tables/markdown) in the demo folder.
3. Git/terminal demos: live-typed command script the trainer types (A1/A3: recommended), keep subprocess runners as
   trainer rehearsal only, or both.
4. Scope: change the contract for all days (recommended) or W1D2 only.

Then implement the answers as ONE decision (python decisions/new.py ..., status accepted) that states the new demo contract:
- What a demo IS: a live-typed script (walkthrough) the trainer performs; the committed code is the answer key (A1).
  Per-subtopic choice by the CONSULT-vs-WRITE test (A3): fluency topics are typed live, look-up topics are notes.
- Script format (A28 header + A2 body, keep our `# --- STEP n ---` idea as "## Step n (M min)" headings): Objective, Time,
  Before the room arrives, Delivery mode (typed | lecture-over-file | facilitation), Audience, Prerequisite reading,
  Hand-typed vs tool-generated files; then timed steps with the exact code/commands in fenced blocks and
  "talking points while typing", Common pitfalls (symptom + fix), What we did NOT cover (intentional), Wrap-up questions,
  Sequence pointer. New template: harness/templates/demo-script.md. Retire demo-README.md or reduce it to the run-order table.
- Answer key: one file per demo as today (NN_<slug>.py, <=90 lines, runnable) OR a transcript (.md) for terminal demos;
  both-ways check (A5): every fenced code/command block in the script appears in the answer key and vice versa (critic runs it).
- Pre-flight (A17) becomes critic items: every token introduced before first use (walk as a learner); first script that uses a
  tool carries install + version + config steps, proven by running; every command states its cwd; tool-generated claims
  proven by running the tool.
- Visibility per answer 1. If trainer-only-until-taught: authors write to trainer/<rel>/demos/ (scripts + answer key);
  add a `publish` step to the Wire stage that copies the answer key to demos/<rel>/ only when a day's `taught: <date>`
  flag is set in curriculum.json (set by the delivery-day close, Stage 4); the notes page demo card reads
  "published after class" until then. Update tests/test_pages.py and tests/test_demos.py accordingly.
- Non-code days per answer 2: demoFormat gains a value "none" (or "facilitation"); day-fanout skips the demos stage and the
  runbook author writes a timed facilitation script per subtopic instead; the notes page demo card is omitted.
- Keep A29/A30: the critic still RUNS every answer-key file; keep size caps.
Update: harness/critics/demos.md (rewrite around the script), harness/metrics.json demos (scripts per day, minutes per
script), harness/templates/demo-script.md, harness/templates/day.exemplar.html demo card variants, day-fanout.js demosStage
prompt + Wire publish step, tests. Do NOT re-author W1D2 in this stage; do NOT run any day.
Exit criteria: decision minted and cited in the commit; tests green with the W1D2 day temporarily marked status planned
if its old-shape demos no longer satisfy the new tests (say so in STATUS.md); STATUS.md O-10 updated; pushed.
```

## Stage 2 — Week plan artifact and demo threads (catalog A7, A10, A12, A13, A16, A23, A24, A25, A27, D4, F1, F7)

```
STAGE 2 — Week plan before any day, with demo threads.
Read catalog rows A7, A10, A12, A13, A16, A23, A24, A25, A27, D4, F1, F7 and the "Old-repo vocabulary" line (thread,
rung, ladder). Read harness/workflows/day-fanout.js, harness/args_for.py, harness/demo_check.py, harness/critics/demos.md,
harness/templates/demo-script.md, tests/test_demos.py, harness/curriculum.json (projects, week 1 notes), the three W1D2
demo scripts and keys in trainer/week-01/day-2-orientation-agile-and-git/demos/, and catalog section H.

BEFORE any edit, ask me these with AskUserQuestion (one call), recommended answers in parentheses:
1. Thread scope: one thread per project block, P0 weeks 1-5, P1 weeks 6-8, P2 weeks 9-11, planned one week at a time
   (A24: recommended), one thread per week, or one thread per phase.
2. Demo domain for the first thread (A10): propose three candidates that survive every week of the thread's scope
   (records that live in Python structures, then MySQL, then an ETL job, then go to an LLM), each with one line on where
   it strains; I pick one or name my own.
3. Week 1 start: Tuesday's `team-repo` is rung 0 and Wed-Fri continue in it, every rung ending in a commit whose message
   is the rung name (A7: recommended), or the thread starts in a fresh folder on Wednesday.
4. Enforcement: mechanical carried-lines check in demo_check.py in this stage (recommended), or plan + prompts only now
   and the mechanical check after W1D3 has shipped.

Build a week-level planning stage that runs ONCE per week before the first day-fanout:
- New workflow harness/workflows/week-plan.js (one author agent + one critic, <=4 agents): writes
  harness/plans/week-WW.md with: Weekly Epic (one paragraph: what the learner can do by Friday), what the week assumes
  from the previous week, ordered demo ladder across all days with minutes per demo and dependency guarantees (which
  demo must precede which), per-day shape (AM/PM blocks), stop points if a day runs long, squeeze priorities
  ("cut first" / "never cut"), anti-spoiler ledger (what each day defers to which later day), real-world framing +
  deliberate-deviation ledger (deviation / workplace reality / pedagogical reason), coverage map
  (curriculum subtopic -> day -> demo -> notes step). Template: harness/templates/week-plan.md.
  Model tiers already exist in config.json models.stages (D-0032): `week-plan` (author) and `week-plan-critic`,
  both inherit the session model at high effort. Tiers reach a workflow ONLY through args, so:
  (a) `python harness/args_for.py <week> --plan --today <date>` emits the week-plan args (root, today, week, every
  teaching day with date and subtopics, weekNotes, the previous week's plan path if any, metrics, config, and
  `models` exactly as day args carry it); it is the only source of week-plan args;
  (b) week-plan.js copies day-fanout's tier(stage, pass) and spreads `...tier('week-plan', pass)` on the author call
  and `...tier('week-plan-critic')` on the critic call, with the same escalateOn repass rule; no agent() call in the
  script runs without a tier;
  (c) the script logs the resolved tiers on its first line, as day-fanout does.
- Threads (A7, A10, A12, A23, A24): a thread is one demo codebase that grows rung by rung across days and weeks; a
  rung is one demo; nothing is re-scaffolded. The plan gets a "## Threads" section: thread id, domain, scope, and one
  row per rung (day, demo NN_<slug>, starts from <previous rung's key or "cold">, what it adds, end state, commit
  message). The ladder's dependency guarantees are derived from those rows. A subtopic that fits no thread is a
  standalone demo and the plan says why (A23). The plan for week N+1 reads week N's last rung as its start state.
- Demo contract amendment (new decision that amends D-0030; do NOT pass --supersedes, the rest of D-0030 stands):
  demo-script.md header gains `Thread:` (thread id or "standalone") and `Starts from:` ("cold" or the path of the
  previous rung's key). Each rung's key stays ONE file under that day's key/ and is the full runnable end state of the
  thread at that rung (A12: that file is the canonical copy). Both-ways check becomes: every typed line is in the key;
  every key line is typed in this script OR present in the `Starts from` key; a carried line that this rung deletes or
  rewrites is shown in a ```python replaced block. Transcript keys: the `$` sequence continues the previous rung's
  repo state. demos critic: item 2 replays a rung from its `Starts from` state, item 5 counts earlier rungs of the
  thread as introduced, item 6 keeps tool install/version/config at the thread's first rung only, item 11 unchanged;
  a new item fails a rung that re-types or re-scaffolds what an earlier rung built. metrics.demos: raise or split
  maxLinesPerFile for cumulative keys (propose the number from the week 1 plan) and add a typed-lines-per-rung cap.
  Known limit, write it into the decision: single-file keys only; folder/package keys and publish_demos.py changes
  are a later stage (needed by week 5 at the latest). Exercises are untouched (A10's "learners mirror in their own
  domain" and the learner-repo convention C4 are not part of this stage).
- W1D2 is live and taught Tue 2026-10-13: do NOT re-author it. Its three scripts get the two header bullets by hand
  (metadata only, no step changes) and must still pass demo_check; tests stay green for it at every commit.
- python harness/args_for.py refuses to emit day args when harness/plans/week-WW.md is missing (blocking, like R-013),
  and passes the plan path + the day's rows from the coverage map and the Threads table into args (`weekPlan`,
  `weekPlanRows`, `threadRows` with each rung's `startsFrom` path). Give it an explicit, logged escape
  (`--no-plan`) so a gate bug cannot block a day that must ship; the escape prints a warning and STATUS.md records
  its use.
- day-fanout.js dayHeader includes the day's rows from the plan; the demo author reads the `Starts from` key before
  writing and extends it; the research and notes critics check the day teaches exactly those rows; the runbook critic
  checks minutes against the plan's budgets and that each Demo section's "room state before" names the start rung.
- Run week-plan for week 1 now (W1D2 is already authored and live: the plan records it as-is and plans D3–D5,
  none of which is authored yet). Do not run W1D3 in this stage.
- tests: tests/test_plans.py (every live day's week has a plan; plan lists every subtopic of every teaching day; every
  rung's `Starts from` resolves; `args_for.py <week> --plan` output carries `models.stages` with `week-plan` and
  `week-plan-critic`; week-plan.js contains both tier names and every agent( call in it spreads a tier(...), checked
  statically on the source); tests/test_demos.py self-tests for carried and replaced lines, and a chain test:
  for every live day, each rung's key still contains its `Starts from` key's surviving lines, so re-authoring an
  earlier day fails the later ones loudly instead of silently staling them.
- AGENTS.md: authoring order inside a thread is strictly rung order; re-authoring day N means re-checking every later
  rung; a delivery-day close that changes a key (classroom reality wins) must run before the next rung is authored.
Decision entries (week plan; demo-thread amendment). Exit: plan for week 1 with its Threads section exists and passes
its critic; args_for gated with the escape; demo_check enforces carried lines; W1D2 still live and green; tests green;
pushed. In the report, list every agent the week-plan run launched with its configured tier and the model and effort
it actually ran on, read from the run's agent transcripts and .meta.json files (not from config); a mismatch is a
defect to fix before exit.
```

## Stage 3 — Re-author W1D2 demos under the new contract; promote the page (catalog A1, A21, A22, A29; milestone 6)

```
STAGE 3 — W1D2 demos under the new contract, then promote the page to the template.
Entry: Stage 1 is committed (decision ID in decisions/README.md). Read that decision, harness/critics/demos.md,
harness/templates/demo-script.md, the W1D2 research brief, runbook and notes page.
1. Remove demos/week-01/day-2-orientation-agile-and-git/ (and trainer/<rel>/demos if present); set W1D2 status planned.
2. Re-run ONLY the demos stage and the artifacts that read it: generate args with
   `python harness/args_for.py 1 2 --today 2026-10-13`, then Workflow({ scriptPath: "harness/workflows/day-fanout.js",
   args, resumeFromRunId: "wf_ce312ce5-ce9" }) so research replays from cache. If the demos prompt changed (it did), the
   demos stage and everything after it run live (~16 agents). Report per-artifact status and flagged critiques verbatim.
3. Verify by hand: every script's fenced blocks match the answer key (critic did it; spot-check one); run every answer-key
   file; the runbook demo sections now reference script files; the notes page demo card reflects the visibility decision.
4. Humanizer already runs inside the workflow; confirm the notes-humanize agent ran (journal.jsonl) and the page still
   passes the critic snippet.
5. Promote: set the `template` arg source to docs/weeks/week-01/day-2-orientation-agile-and-git.html for future runs
   (harness/README.md "Changing the bar" and args_for.py default), decision entry; keep day.exemplar.html as fallback.
Exit: W1D2 live again under the new contract, tests green, both repos pushed, STATUS.md milestone 6 first half done.
```

## Week-1 batch run — W1D3 to W1D5 (milestone 6; first use of the week batch, D-0038)

```
WEEK-1 BATCH RUN — author W1D3, W1D4, W1D5 in one invocation.
The trainer approved about 60 agents for this run on 2026-10-12; do not ask again unless it would exceed ~80.
Pre-flight (stop and report if any fails): tests green; `git status` clean in both repos;
`python harness/plan_check.py harness/plans/week-01.md` prints OK; `python harness/demo_check.py
trainer/week-01/day-2-orientation-agile-and-git/demos` prints OK (W1D3's first rung starts from that key).
Run: `python harness/args_for.py 1 3 4 5 --today <today>` and pass its JSON unchanged to
Workflow({ scriptPath: "harness/workflows/day-fanout.js", args }). Research runs for the three days in parallel,
demos one day after the other (a rung needs the previous rung's key on disk), materials in parallel.
Do not edit anything under harness/, tests/ or trainer/ while it runs: agents and the Verify step read the tree.
If a usage limit cuts the run, relaunch with resumeFromRunId in THIS session (it does not work across sessions).
If the report shows a day "blocked by <day> demos": fix that day's demos, then re-run from that day with
`python harness/args_for.py 1 <that day and the later ones> --skip-research --today <today>`.
After the run:
- `python harness/log_run.py amend --last --run-id <wf_...> --minutes M --tokens T --tiers-verified yes|no`
  (verify tiers from the agent transcripts; "inherit" stages run on the session model).
- Per day: `python harness/demo_check.py trainer/<rel>/demos` prints OK; run every .py key; read the notes page,
  the exercise README (it must send trainees to their <FirstnameLastname> repo, D-0037) and the runbook.
- Confirm O-8: each page's window.NEXT points at the next day's file, Friday's at the index.
- Resolve flagged items by hand (max 2 passes each, then report), record `--resolved yes --note "..."`.
- STATUS.md: milestone 6 done, Log line, O-8 closed; strike this row in the order table; rebuild the tracker.
- Delete key/__pycache__ in the trainer repo; commit both repos; push only if tests are green.
Exit: W1D3 to W1D5 are `live`, tests green, both repos pushed, run record complete.
```

## Stage 4 — Daily close audit (loose close done 2026-10-14, D-0050; rung-diff close for thread days: later, week 3) (catalog D16, A15, D19, A26, A28, E6, B8; replaces the 2026-10-11 Stage 4 draft)

```
STAGE 4 — Daily close audit: what actually reached the room, checked against the demo repo.
Decisions already taken by the trainer (2026-10-12), do not re-ask: the truth is the trainer's live classroom
repository (the public demo repo `2494-Gen-AI-CN/demos`, cloned at `demo-repo/`), diffed by script; a step that was not reached goes to the next teaching day's opening
slot; classroom reality wins when the typed code differs from the key; taught days are frozen and fixed forward.
Read catalog rows D16, A15, D19, A26, A28, E6. Read harness/demo_check.py (reuse _header, _steps,
script_commands, transcript_commands, carried_lines), harness/plan_check.py day_rows() (thread rows carry
commitMessage, key, startsFrom), harness/plans/week-01.md line 29 (the stop rule: a cut step's kept lines are
pasted from the key before the rung's commit, so "not reached" never changes a key; only "diverged" does),
harness/publish_demos.py, harness/log_run.py (kind `manual` exists), tests/test_demos.py ThreadChainTests.
Build (stdlib Python, no agents):
- config.json threads.<id>: add `repoDir` and `file`, so a .py key can be compared with the repository file.
  DONE in D-0050.
- harness/close_check.py <week> <day> (read-only; exit 1 on findings; no --classroom path, it reads `demo-repo/`).
  Per demo of the day, in ladder order: find the rung's closing commit in the demo repo by its plan commit message
  (`git log --format=%H%x09%ct%x09%s`). .py key: `git show <sha>:<thread file>` against the key as stripped
  non-blank line sets -> reached | diverged (lines only in class / only in key). Transcript key: every
  `git commit -m` subject from script_commands() must be in the log in order -> reached | stopped after step n
  (step from _steps) | diverged (unexpected subjects). No closing commit -> not reached. Standalone demos leave
  no commit: `assumed reached`, overridable with --not-reached NN_slug. Actual minutes per rung from commit
  timestamps beside the ladder minutes.
- harness/close_day.py <week> <day> [--apply]. `close_day.py` already exists for loose days (D-0050); this stage adds
  the thread mode that reads `demo-repo/<repoDir>/<file>` at each rung's closing commit (found by the plan's
  commit message). Dry run prints the report. --apply:
  (1) writes trainer/<rel>/delivery.json (per demo: status, sha, minutes, unreached steps, diverged lines);
  (2) appends "## Delivery record (<the day's date from build_index.slot_date>)" to the runbook;
  (3) for each diverged .py rung, overwrites the key with the classroom file and prints the script lines that
      must change so demo_check.py passes again;
  (4) sets `taught` in curriculum.json (this script is its only writer) and runs publish_demos.py;
  (5) for each unreached step, prints the block to insert at the top of the next teaching day's runbook
      ("## Carried over from <id> (M min)") with that day's "Cut first" line from the plan, and records it in
      the next day's delivery.json as carriedIn;
  (6) forward re-check: demo_check.check_dir on every later authored day in rung order, next week included;
      lists the rungs that no longer chain;
  (7) adds a `manual` run-log record through log_run.py add, rebuilds the tracker, prints a STATUS.md Log line.
- Repair rule for (6): hand-fix, at most 2 passes; if a rung still fails, re-author that day with
  `args_for.py <week> <day> --skip-research`. Untaught days may be re-authored; taught days never.
- docs/process/delivery-close.md: the checklist, run FIRST in the first session after each teaching day, one
  catch-up close per missed day. harness/templates/runbook.md gains the "## Delivery record" section; runbook
  critic item 1 allows it as a trailing section (critic change: decision entry).
- harness/build_tracker.py: a day with delivery.json shows `closed`; the existing close alarms clear on it.
- tests/test_close.py: build a throwaway git repo in a temp dir (tempfile, not /tmp) and drive close_check
  through reached, diverged, stopped and not reached. ThreadChainTests: every authored day, not only live.
Then run the first thread-day close against `demo-repo/` (week 3).
Exit: tests green; W1D2 closed (taught, published, delivery record); checklist committed; both repos pushed.
```

## Stage 8 — Hidden week, Friday gate, series review, drift check (catalog A13, A14, D9, F5)

Done 2026-10-14 as D-0052 (status `authored`, `releaseOnWire`, `release_week.py`, tracker badge and alarm, `drift_check.py`, `authored_days()`) and D-0053 (series-review critic, authored wording in the week-plan and demos critics). The prompt is kept for the record; the checklist it feeds is `delivery-close.md`.

```
STAGE 8 — Week-ahead visibility and the Friday gate.
Decision already taken by the trainer (2026-10-12): next week's pages stay hidden while they are authored and
the whole week is released at once on Friday. Hidden means unlinked from the index; GitHub Pages still serves
the files at a guessable URL, so this is not access control. Say so in the decision entry.
Build:
- New day status `authored` between `planned` and `live` (all artifacts exist and pass; not linked).
  harness/args_for.py: emit `releaseOnWire` = the week has already started on --today; the forward link also
  accepts an `authored` next day (the next day is same-week only, so a week's last page always points at the
  index). harness/workflows/day-fanout.js Wire step 2 writes `live` or `authored` from releaseOnWire.
  harness/build_index.py line 151 stays as it is (links `live` only): that is what hides the week.
  harness/plan_check.py lines 184, 234, 353: the "recorded as-is" and key-on-disk checks apply to `authored`
  and `live`; same wording in week-plan.js and critics/week-plan.md item at line 14.
  tests/helpers.py: `authored_days()` (authored or live). Artifact-contract tests move to it (test_pages,
  test_trainer, test_exercises, test_demos scripts and chain, test_plans line 32, test_tracker lines 64-70 and
  108-112, test_curriculum lines 181-193). Visibility tests stay on live/taught (index sync, PublishStateTests,
  the demo-card check). test_curriculum line 57 enum gains `authored`; "a taught day must be live" stays.
  harness/templates/tracker.html: `authored` badge; the previous-Friday readiness alarm is satisfied by
  `authored`; new red alarm "authored, not released" from the week's Monday. Extend the alarm tests.
- harness/release_week.py <week> --today <date> [--check]: the Friday gate. Preconditions: the week's plan
  passes plan_check; every teaching day of that week is `authored`; harness/last-tests.json is green; every
  teaching day of the current week dated on or before --today has trainer/<rel>/delivery.json (written by `close_day.py`, D-0050). Then flip
  authored -> live, run build_index.py, print a STATUS.md line.
- Series review: one critic agent at the end of the Demos phase when a run covers more than one day; it reads
  the plan and every script in ladder order and checks that the series tells one story and the last rung
  delivers the Weekly Epic. Flags only; no auto-fix loop yet.
- harness/drift_check.py + tests/test_drift.py (port of catalog F5, read-only, exit 1 on hard findings):
  - also runs `python harness/notes_check.py --all-live --links` (D-0040): dead links and stale stamps on live notes pages
    are findings (network ones soft unless --strict);
  decisions index rows match files and IDs are sequential; stale markers (`TBD`, `OWED`, `pending`, `blocked until`) in
  live docs outside decisions/ and docs/process/*catalog*; untracked files and unstaged deletions in both
  repos; taught days with no Delivery record or no delivery.json; days `taught` but not `live`; a stale tracker.
Decision entries (new status, critic wording). Exit: `release_week.py 2 --check --today 2026-10-16` refuses
while a week-2 day is not `authored`; tests green; pushed.
```

## Stage 5 — Rules registry and OVERRIDE state (catalog D1, D2, D11, D12, D13, D17, D21)

```
STAGE 5 — Rules registry.
Read catalog rows D1, D2, D11, D12, D13, D17, D21. Read AGENTS.md, decisions/README.md, decisions/new.py,
tests/test_decisions.py.
- Create RULES.md at repo root: every standing rule currently stated in prose in AGENTS.md, harness/README.md and the
  critic specs gets a stable ID (R-001 ...), one line, with a Provenance line (which decision created it). Rules are for
  recurring work only (D21); one-time decisions stay in decisions/.
- AGENTS.md cites rule IDs instead of restating; critic specs cite IDs where they enforce one.
- decisions/new.py gains `--status override` (temporary rule break, must name the rule ID and an expiry: the next
  week-plan run) and `--promotes D-00xx` (makes an override permanent) ; tests/test_decisions.py enforces: an override
  older than its expiry with no promote/supersede is a failure; cited R-IDs exist.
- Session read order in AGENTS.md: STATUS.md -> decisions/README.md -> RULES.md -> run harness/drift_check.py.
- Built-in stops list (D17) in AGENTS.md: missing week plan, one-off demo request, 2 failed fix passes, coverage gap,
  critic FAIL after 3 passes, missing delivery close.
Decision entry. Exit: RULES.md exists with >= every rule now in AGENTS.md; tests green; pushed.
```

## Stage 6 — Skills (catalog section I)

```
STAGE 6 — Skills.
Entry: stages 1, 2, 4 done and each process has been run by hand at least once (so the skill encodes what worked).
Create repo-local skills under .claude/skills/<name>/SKILL.md (frontmatter: name, description with trigger phrases):
- demo-script: author one walkthrough script + answer key from a brief, following harness/templates/demo-script.md and
  the demos critic; ends by running the both-ways check and the answer key.
- week-plan: runs harness/workflows/week-plan.js for a given week and reviews the plan against the catalog A27 sections.
- delivery-close: walks docs/process/delivery-close.md interactively (asks for the delivery record facts), runs
  harness/drift_check.py, commits both repos.
- drift-check: runs the script and explains each finding with the rule it violates.
- retrospective-audit: the week-1 retrospective (milestone 7) as a closed check registry (catalog D18/D19): facts phase
  (what shipped, minutes actual vs planned, flags per artifact, tokens per run) locked before judgment; output schema
  DEFECT / STALE / OPEN / OVERHEAD; proposes bar changes as decisions, never edits metrics itself.
- notes-portable (only if Stage 7 chose portable sections): portability grep + section check.
Each skill: < 300 lines, cites rule IDs, no cohort facts inside. Validate with `claude plugin validate .` if applicable.
Exit: skills listed by /skills; one dry run each; pushed.
```

## Stage 7 — Notes depth: interview sections and portability decision (catalog B1, B2, B3, B4, B6, B9)

Done 2026-10-13 as D-0040, wider than the prompt below: day-bound page with portable sections (B1), the depth bar as critic item 12b (B2), "Say it in an interview" per step and a closing "Check yourself" step (B3), adjacent concepts from a new brief section `## Notes depth` (B3/B4), link liveness on every page through `harness/notes_check.py --links` plus WebFetch currency on full-gate and currency-flagged days (B6), 4500–7000 words (B5 raised), delivery phrases banned (`metrics.notes.deliveryPhrases`), every stage tier pinned, and a notes-only workflow mode for the retrofit. The prompt is kept for the record.

```
STAGE 7 — Notes depth.
Read catalog rows B1, B2, B3, B4, B6, B9. Read harness/critics/notes.md, harness/templates/day.exemplar.html (or the
promoted W1D2 page), harness/metrics.json notes.
Ask me first (AskUserQuestion): keep pages day-bound (date, demo links, NEXT) with portable SECTIONS inside, or make
notes fully portable (B1) with the day wrapper generated separately. Recommended: day-bound page, portable sections.
Then: add two mandatory sections to every notes page before Sources: "Say it in an interview" (1–3 sentences per
objective, spoken form) and "Check yourself" (3–5 retrieval questions with answers; may replace or feed the quiz's
open question); depth bar per objective = prose + runnable example + trade-off + recognize-on-sight + spoken answer (B2)
as critic items; notes may teach ahead of demos (B4) written into the notes author prompt; link liveness mandatory
regardless of gate (B6): CHECK_EXTERNAL default on for the notes critic. Update metrics.json (section names, counts),
critic, template, author prompt, tests/test_pages.py; apply to the W1D2 page by hand (then run the humanizer skill on it).
Decision entry. Exit: W1D2 page has both sections and passes; tests green; pushed.
```

## After every stage

- STATUS.md: milestone/open-item row + Log line in the same commit (O-10 tracks this plan).
- Strike the stage's row in the order table above (the tracker reads it), then `python harness/build_tracker.py`;
  finish with `python harness/log_run.py tests` so tracker.html carries the test result (D-0035).
- Decision ID in the commit subject.
- `git status` clean in both repos after push.
