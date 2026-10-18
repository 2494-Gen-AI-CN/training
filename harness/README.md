# Harness

Agent-driven pipeline that turns one curriculum day into five reviewed artifacts.

```
harness/
  curriculum.json      source of truth: weeks, days, slugs, gate, demoFormat (walkthrough | none, D-0055), status (planned -> authored -> live; taught implies live, D-0052)
  metrics.json         quality bars (word band, steps, quiz count, test counts, day minutes)
  config.json          site title, repo URL, feedback form, LLM provider defaults, learner repo convention (public, D-0051) and demo repo (D-0050)
  build_index.py       curriculum.json -> CAL/WEEKS block in docs/index.html (--check in tests); owns all calendar arithmetic
  args_for.py          prints the Workflow args for <week> <day...> (day = weekday slot; holiday slots refused; BLOCKED until the
                       week's plan exists, escape --no-plan; --notes-only / --runbook-only re-author one artifact), with <week> --plan
                       the args for the week-plan workflow (D-0034), with <week> --demos the week's walkthrough blocks for demo-series.js (D-0055)
  plan_check.py        parses + checks one week plan (block chain, conventions table, ladder, series sections, coverage map, authored days as-is); args_for and tests call it
  demo_check.py        FORMAT check for one walkthrough or a week's folder (D-0055): title, the five header fields, Time = sum of step
                       minutes within metrics.demos, cheat-sheet rows = steps, cwd lines, closing sections, the last step's commit,
                       typed-line cap; "What we did NOT cover" bullets take one format (D-0039). The answer key is the demo repo commit.
  series_readme.py     renders trainer/week-WW/demos/README.md (the series index: ordered table, dependency graph, stop points, squeeze
                       priorities, hard-stop rule, scaffold bundle, run prerequisites, ledgers) from the plan and the delivery records; --check
  prose_guard.py       prose-only guard for a humanizer pass on walkthroughs and runbooks (D-0039) and, in html mode, on notes
                       pages (D-0040): compares a file with a snapshot or with HEAD and fails when code, headings, the header
                       block, tables, labels, the HTML tag skeleton, attributes, citations or quiz answers moved
  notes_check.py       the one mechanical checker for a notes page (D-0040): --counts (steps, words, h3, interview callouts,
                       Check yourself, code blocks, citations, quiz, minutes), --phrases (classroom references), --stamps
                       (Sources checked vs the brief), --citations (sup.cite -> li#src-N, URLs in the brief), --links
                       (liveness); --all-live covers every live page, --all-authored every authored or live page (drift_check uses it, D-0052); author, humanizer, verify agent, critic and tests call it
  close_day.py         closes a taught day (D-0050, D-0055): `<week> <day> [--date YYYY-MM-DD] [--match NN-slug=<sha> ...] [--notes "..."] [--no-pull] [--apply]`;
                       the only writer of `taught`; pulls demo-repo/, matches the day's live commits to the plan's blocks and diffs them against the
                       prep commits (reached / diverged / not reached), writes trainer/<rel>/delivery.json, appends a DELIVERY RECORD blockquote to
                       each walkthrough and the runbook Delivery record, re-renders the series README, logs a manual run, rebuilds index and tracker
  release_week.py      the Friday gate (D-0052): `<week> --today <date> [--check]`; refuses unless the plan passes plan_check, every teaching day is authored (or live),
                       pages and exercise READMEs exist, last-tests.json is green, the past teaching days have delivery.json and, when the week's
                       walkthrough folder exists, demo_check passes and the series README is fresh (D-0055); then flips
                       authored -> live, rebuilds index and tracker, logs a manual run, prints a STATUS.md line; `--check` never writes
  drift_check.py       read-only repo audit (D-0052), exit 1 on hard findings: decisions index vs files, stale markers, untracked files, taught days without a
                       delivery record, taught-but-not-live days, a stale tracker, notes links; flags `--strict --no-git --no-links --no-notes --no-markers --no-tracker --json --root`
  practice_browser.py  browser pass for a page's practice tasks (D-0043): re-checks every case under CPython, then serves docs/ with the cases and
                       practice_browser.js so an agent with browser tools can drive the real page through them (AGENTS.md has the five steps)
  practice_tasks.py    practice tasks as a stage after authoring (D-0047): show / approve the proposals in practice/<week>/<day>.json, insert the page's
                       section.practice from that file (generated, never hand-edited), check page and file agree, verify one day under CPython
  practice/<week>/<day>.json   per day: which teaching steps take a task and why, the proposed tasks, the trainer's answer, and the built task text,
                       starter and checks (committed; the model answers and cases are in the trainer repo)
  build_tracker.py     writes ../tracker.html (the work tracker; local, gitignored, D-0036) = templates/tracker.html + a data block
                       read from repo state; --check in tests (D-0035)
  log_run.py           add / amend one record per workflow run in runs.jsonl; `tests` records the suite result in last-tests.json
  runs.jsonl           the run log (committed): agents, passes per artifact, flagged items, tiers, test result per run
  workflows/week-plan.js    once per week, before the first day: author + critic write plans/week-WW.md (up to two repasses, D-0057), then a Record agent (<=7 agents)
  workflows/demo-series.js  once per week, after the plan and the briefs: per block author -> humanize -> critic in ladder order, each block
                       one commit on the demo repo's prep branch; then one series-review critic, the series README, Record, Verify (D-0055)
  workflows/day-fanout.js   the per-day Workflow-tool script (research -> notes ∥ exercise -> runbook -> wire; no demos stage)
  workflows/practice-tasks.js   after a week is authored: suitability pass (one assessor per page), then, once the trainer approved, the build (author + critic per day)
  plans/week-WW.md     the week plans (committed): Weekly Epic, Threads block table, demo ladder, per-day shape, stop points, squeeze priorities, hard-stop rule, scaffold bundle, run prerequisites, ledgers, coverage map
  templates/           tracker.html (work-tracker shell, no data), day.exemplar.html, week-plan.md, research.md, runbook.md, demo-script.md, exercise-README.md, conftest.py
  critics/             PASS criteria each critic agent reads: week-plan, research, demos, series-review (D-0053), notes, runbook, exercise, practice
  research/<week>/<day>.md   research briefs (committed; the audit trail for every claim)
```

## Per-week stage (runs once, before the week's first day)

```
python harness/args_for.py 1 --plan --today 2026-10-12      # week-plan args: every teaching day, threads in scope, previous plan
Workflow({ scriptPath: "harness/workflows/week-plan.js", args: { ...json... } })
python harness/plan_check.py harness/plans/week-01.md       # the critic ran it; run it again before committing
```

The plan's `## Threads` table makes most demo blocks rungs of one growing codebase (D-0033, D-0055): each row is one walkthrough (an AM or PM slot) and says which day and slot, what it starts from, what it adds and the ONE commit that ends it on the demo repo's prep branch. `args_for.py <week> --demos` passes the blocks into `demo-series.js`; `args_for.py <week> <day>` passes that day's coverage rows, block rows, ladder rows and day shape into `day-fanout.js`, where the runbook points at the blocks and the critics check the day teaches exactly those rows. A day cannot be authored without its plan; `--no-plan` is the logged escape for a gate bug.

## Per-week demo series (after the plan and the research briefs, D-0055)

```
python harness/args_for.py 2 --demos --today 2026-10-15        # the week's blocks in ladder order (plan must pass; a brief per day)
Workflow({ scriptPath: "harness/workflows/demo-series.js", args: { ...json... } })
python harness/demo_check.py trainer/week-02/demos             # the critic ran it per block; run it again before committing
python harness/series_readme.py 2 --check                       # the generated README is fresh
git -C demo-repo push -u origin prep/week-02                    # the answer key, one commit per block; never pushed by an agent
```

Each block: author (tier `demos`, reads the brief, the template, the plan rows and the previous block's commit; writes `trainer/week-WW/demos/NN-<slug>.md` and commits the block's code on `prep/week-WW`) → humanizer (prose only, `prose_guard.py`) → critic (tier `demos-critic`, `critics/demos.md`: `demo_check` OK, the commit runs in a scratch worktree and matches the Check fences, the diff against the previous block is exactly what the script types, learner walk, teaching, plan row) → up to 3 passes, then flagged; a block that leaves no commit blocks the later blocks of its thread. Then one series-review critic (`critics/series-review.md`, flags only), the series README, Record (`kind: demo-series`) and Verify. About 3 agents per block on a clean pass.

Decisions that shaped any of this (and every later schedule/scope change) are logged in `decisions/README.md` (newest first; see `AGENTS.md` for the rule, D-0001).

## Per-day pipeline

| Stage | Author writes | Critic checks (spec) | Gate |
|---|---|---|---|
| Research | `harness/research/<week>/<day>.md` (Claims, a `## Notes depth` block per subtopic, Sources, Glossary, Pitfalls, Demo hints) | `critics/research.md` | `full`: URLs fetched; `light`: structure + stamps; covers the plan's rows; Notes depth per subtopic (D-0040) |
| Notes ∥ Exercise | `docs/weeks/<week>/<day>.html` (reference/study material, D-0040: 4500–7000 words, h3 subsections, an interview callout per step, a Check-yourself step, inline citations, a Sources-checked stamp, no classroom references), `exercises/<week>/<day>/` + `trainer/.../solutions/` | `critics/notes.md` (+ a notes-verify agent: `notes_check.py` every day, WebFetch currency on full-gate and currency-flagged days; its findings bind the critic), `critics/exercise.md` | metrics bands via `notes_check.py`; no demo card, list or popup (D-0055); starter fails / solution passes |
| Runbook | `trainer/<week>/<day>/runbook.md` | `critics/runbook.md` | headings, minutes, one `## Demo:` pointer section per walkthrough block of the day + a Facilitation block per concept subtopic |
| Wire (serial) | glossary.js append, `status: live|authored` (`releaseOnWire`; a live day is never downgraded), `build_index.py`, NEXT links, `practice_tasks.py insert`, `build_tracker.py` | — | — |
| Record | one line in `runs.jsonl` via `log_run.py add` (agents, passes, flags, tiers); `tracker.html` rebuilt (D-0035) | — | — |
| Verify | test result amended onto the run record | `python -m unittest discover -s tests` (includes the tracker staleness test) | ≤2 fix loops |

Each gated artifact: author → critic → up to 3 repair passes → else **flagged** (reported, never blocks the run).

A humanizer agent (`humanizer:humanizer`, file mode, tier `humanize`) runs between author and critic on three artifacts: the notes page (D-0029) and the trainer's delivery wording, which is the runbook here and each walkthrough in `demo-series.js` (D-0039, D-0055). On every one of them it changes prose only and proves it: `python harness/prose_guard.py snapshot <files>` before, `python harness/prose_guard.py check <snapshot dir> <files>` after (html mode for a page, D-0040). No critic item judges the wording of trainer files, so the pass adds agents (one per runbook, one per block, more on a repass) without moving the bar. For a hand pass on committed files use `python harness/prose_guard.py git <files>`.

Notes-only mode (D-0040): `python harness/args_for.py <week> <day...> --notes-only` runs a research DEPTH pass (a research agent extends the committed brief's `## Notes depth` section, judged by the research critic), then the notes page; exercise and runbook are untouched. `--runbook-only` re-authors the runbooks alone (author, humanize, critic), for instance after the week's blocks were regrouped (D-0055). `--template <path>` points the authors at another page shape (used to pilot a new template). Every stage tier in `config.json` `models` is pinned to opus, sonnet or haiku; none inherits the session model.

Readability bar (D-0060): `metrics.json` `notes.prose` caps paragraphs (80 prose words), sentences (40 words, 5 inline code spans; interview callouts and check answers exempt), asks for 3+ lists or tables inside the teaching steps, a `div.recap` ("Takeaways", 2–4 one-line items) immediately before each interview callout, and output directly under every code block (`pre.out`, or one sentence). `notes_check.py --style` counts it (a default phase; every `style:` line is hard and binds the notes critic through notes-verify), `critics/notes.md` items 5d, 5e and 10b judge it, `glossary.js` underlines a term once per step. Pages written before the bar get the restructure pass: `python harness/args_for.py [week [day...]] --restructure` → `Workflow({ scriptPath: "harness/workflows/notes-restructure.js", args })`. Per page: an author (tier `restructure`, sonnet first, escalate from pass 2) changes only the containers of the prose (splits paragraphs, listifies enumerations, adds the recap, moves the output sentence under its block; no rewording, no new fact, no `pre.out`), proven by `prose_guard.py check --restructure` (code, headings, citations, numbers, scripts, callouts, details, widgets, the Check-yourself step and `section.practice` frozen; per-step words within −8%..+15%/+90; page inside the word band) and gated by `notes_check.py --style`; a gate agent (tier `verify`) re-runs both and reads `git status`; up to 3 passes, then flagged. Record writes `kind: notes-restructure`. The in-page survey is gone (D-0061): no `survey.js`, the MS Forms link stays in the index rail and the runbook.

## Practice tasks (after the week's days are authored, D-0047)

```
python harness/args_for.py 1 --practice --today 2026-10-13        # suitability args: the week's authored pages that carry no built task
Workflow({ scriptPath: "harness/workflows/practice-tasks.js", args: { ...json... } })
python harness/practice_tasks.py show 1                           # the proposals, to put in front of the trainer
python harness/practice_tasks.py approve 1 5 t1 t3 t4             # the trainer's answer, per day (--all, --none)
python harness/args_for.py 1 --practice-build --today 2026-10-13  # build args; refused while a proposed task has no answer
Workflow({ scriptPath: "harness/workflows/practice-tasks.js", args: { ...json... } })
python harness/practice_browser.py 1 5                            # then the browser pass, per built day (AGENTS.md)
```

The suitability pass reads each page against `critics/practice.md`: what the browser runtime can run (standard library, no typed input, no packages, one file) and what a check can see (names and return values). It proposes at most one task per teaching step and says why a step takes none. Nothing reaches a page without the trainer's answer. The build writes the task text, starter and checks into `practice/<week>/<day>.json`, the model answers and cases into the trainer repo, and the page's section through `practice_tasks.py insert`; the section is generated, so a re-authored page gets it back from the same command (the Wire step runs it). Agents: one per day plus two for the suitability pass; two to six per day plus two for the build.

## Running a day

```
python harness/args_for.py 1 2 --today 2026-10-13      # week 1, weekday slot 2 (Tue Oct 13; slot 1 is Thanksgiving)
```
Paste the JSON as `args`:
```
Workflow({ scriptPath: "harness/workflows/day-fanout.js", args: { ...json... } })
```
Then `python -m unittest discover -s tests -v`, open `docs/weeks/<week>/<day>.html` via `cd docs && python -m http.server 8000`, and rehearse `trainer/<week>/<day>/runbook.md` with the walkthroughs in `trainer/<week>/demos/` and the prep branch checked out in `demo-repo/`. After the session, the delivery-day close sets `taught`: `python harness/close_day.py <week> <day> --apply` (it diffs the room's commits against the prep commits and records reached / diverged / not reached per block; folding the room's reality back into a walkthrough and the prep branch is a hand step).

A week authored before its Monday lands as `authored`: written, tested, but not linked from `docs/index.html` (`args_for.py` emits `releaseOnWire`, true when `--today` is on or after the week's Monday). On the Friday before, release it (D-0052):
```
python harness/release_week.py 2 --today 2026-10-16 --check   # reads the reasons; never writes
python harness/release_week.py 2 --today 2026-10-16           # authored -> live, index and tracker rebuilt
```
Before every push: `python harness/drift_check.py`. The checklist for all three moments is `docs/process/delivery-close.md`.

When the run finishes, complete its record with what the script cannot see, then look at the tracker:
```
python harness/log_run.py amend --last --run-id wf_xxxxxxxx-xxx --minutes 38 --tokens 900000 --tiers-verified yes
```
Open `tracker.html` (repo root) from disk for the whole picture: day pipeline, alarms, threads, runs. It is a local file, gitignored so trainees never see it (D-0036), generated by `build_tracker.py` from the committed shell `templates/tracker.html`; a change to `STATUS.md`, the curriculum, a plan, a decision or a trainer file makes it stale until that script runs, and `tests/test_tracker.py` fails meanwhile.

Agent budget: ~10 agents on a clean pass per day, ~22 worst case (one of them the Record agent), plus ~3 per walkthrough block in the separate demo-series run. A week is one batch (D-0038): pass its teaching days in one invocation; every day runs in parallel. A single day stays valid. To re-run after editing prompts/critics, pass `resumeFromRunId` so finished stages are cached (same session only). From a new session, `python harness/args_for.py <week> <day> --skip-research` reuses the committed brief and runs demos onward live.

## Changing the bar

Edit `metrics.json` (numbers) or `critics/*.md` (PASS rules). The workflow prompts reference both; the tests and `notes_check.py` read `metrics.json`. The notes-page template the authors copy is `config.json` `template` (D-0031: the promoted `docs/weeks/week-01/day-2-orientation-agile-and-git.html`); `args_for.py` passes it as args `template` and falls back to `templates/day.exemplar.html` when the file is missing. To promote a better page, change `template` via a decision entry; the exemplar stays the structure gold standard for `tests/test_pages.py`.
