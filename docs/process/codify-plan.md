# Codify plan: turning the mined rules into this harness, one stage per clean session

Companion to `mined-rules-catalog.md` (D-0028). Row IDs below (A1, D16, F5 ...) point at that catalog.
Each stage is sized for one Claude Code session. Run them in the recommended order; each stage's exit criteria
are the next stage's entry conditions. Training starts Tue 2026-10-13, so stages 1 and 3 came first; Stage 2 (week
plan) now runs before W1D3 so the three unauthored days of week 1 are written against a plan (reordered 2026-10-12).

## Kickoff prompt (paste at the top of every clean session, then the stage block)

```
You are working in C:\Users\JonathanDeLaCruz\Documents\Revature\CGZT-Canada\2494-Gen-AI-CN (public repo 2494-Gen-AI-CN/training;
trainer/ is a separate private repo, gitignored). Read, in this order: STATUS.md, decisions/README.md, AGENTS.md,
docs/process/codify-plan.md, then only the catalog rows the stage names in docs/process/mined-rules-catalog.md.
Run `python -m unittest discover -s tests -v` before and after every change; keep it green.

Facts already established (do not re-derive): dates derive from curriculum.json startDate + holidays (D-0013, D-0014);
one Workflow invocation per training day, args only from `python harness/args_for.py <week> <day> --today <date>` (D-0008);
learner persona lives in config.json audience (D-0023); exerciseKind pytest|rubric (D-0025); per-stage model tiers in
config.json models (D-0026); every notes page gets a humanizer pass before its critic (D-0029).

Rules for this session: use Edit/Write for code (no sed, no heredocs with escapes). Any change to curriculum.json,
metrics.json, config.json, critics/*.md, templates or the calendar needs `python decisions/new.py ...` and the ID in
the commit message. Update STATUS.md in the same commit. Ask before any action that costs more than ~30 agents.
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
| 4 | Run W1D3 (milestone 6, not a stage here) | Wed 2026-10-14; after Stage 2 `args_for.py` needs `harness/plans/week-01.md` to emit its args | 1 session, ~20 agents |
| 5 | Stage 4 Delivery-day close + drift check | Needed Tue evening after the first delivery; independent of Stage 2 and W1D3, so run it Tue evening wherever they stand | 1 session, no agents |
| 6 | Stage 7 Notes depth (interview sections) | Fits the persona; touches critic + template | 1 session |
| 7 | Stage 5 Rules registry + OVERRIDE state | Governance; no delivery dependency | 1 session |
| 8 | Stage 6 Skills | After the processes have run at least once by hand | 1–2 sessions |

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

## Stage 4 — Delivery-day close and drift check (catalog D6, D15, D16, D20, F5, A15, A26, E6)

```
STAGE 4 — Delivery-day close + drift check.
Read catalog rows D6, D15, D16, D20, F5, A15, A26, E6, and section G. Read STATUS.md, tests/test_decisions.py,
harness/templates/runbook.md, trainer/week-01/day-2-orientation-agile-and-git/runbook.md.
Build:
- docs/process/delivery-close.md: the checklist run in the FIRST session after each training day, before any other work:
  (1) record what was actually taught vs the runbook (minutes per block, demos reached, where it ran long/short) as a
  dated "## Delivery record" appended to that day's runbook (template section added to harness/templates/runbook.md);
  (2) fold classroom reality back: if the trainer's live code diverged from the answer key, the answer key is updated to
  the taught shape (classroom reality wins, A15) with a maintenance commit; taught artifacts are then FROZEN
  (curriculum.json day gains `taught: "YYYY-MM-DD"`); later defects are fixed forward, never rewritten;
  (3) every untracked file gets a disposition (commit / ignore / delete / defer with reason);
  (4) run the drift check; every WARN gets a disposition; (5) STATUS.md Log line; (6) commit both repos.
  Catch-up clause: one close per missed day.
- harness/drift_check.py (port of F5, read-only, exit 1 on hard findings): decisions index rows match files and IDs are
  sequential (reuse tests/test_decisions.py logic); stale markers in live docs (TBD, OWED, pending, blocked until)
  outside decisions/ and docs/process/*catalog*; untracked files and unstaged deletions in both repos; live days
  whose `taught` date has passed with no Delivery record in the runbook; curriculum days `taught` but status != live.
  Wire into tests as tests/test_drift.py (skips the git checks when not in a repo).
- A `delivery-close` slash-command skill is Stage 6; here only the checklist + script.
Decision entry (curriculum.json gains `taught`). Exit: script runs clean on the current tree; checklist committed; pushed.
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
- Decision ID in the commit subject.
- `git status` clean in both repos after push.
