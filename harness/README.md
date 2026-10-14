# Harness

Agent-driven pipeline that turns one curriculum day into five reviewed artifacts.

```
harness/
  curriculum.json      source of truth: weeks, days, slugs, gate, demoFormat, status (planned -> authored -> live; taught implies live, D-0052)
  metrics.json         quality bars (word band, steps, quiz count, test counts, day minutes)
  config.json          site title, repo URL, feedback form, LLM provider defaults, learner repo convention (public, D-0051) and demo repo (D-0050)
  build_index.py       curriculum.json -> CAL/WEEKS block in docs/index.html (--check in tests); owns all calendar arithmetic
  args_for.py          prints the Workflow args for <week> <day...> (day = weekday slot; holiday slots refused; BLOCKED until the
                       week's plan exists, escape --no-plan) or, with <week> --plan, the args for the week-plan workflow (D-0034)
  plan_check.py        parses + checks one week plan (threads chain, ladder, coverage map, live days as-is); args_for and tests call it
  demo_check.py        format + both-ways check for one day's demo scripts and answer keys (critic and tests call it; D-0030);
                       thread rungs carry lines from their Starts from key, replaced lines go in a python replaced block (D-0033);
                       "What we did NOT cover" bullets take one format (D-0039)
  prose_guard.py       prose-only guard for a humanizer pass on demo scripts and runbooks (D-0039) and, in html mode, on notes
                       pages (D-0040): compares a file with a snapshot or with HEAD and fails when code, headings, header
                       bullets, tables, labels, the HTML tag skeleton, attributes, citations or quiz answers moved
  notes_check.py       the one mechanical checker for a notes page (D-0040): --counts (steps, words, h3, interview callouts,
                       Check yourself, code blocks, citations, quiz, minutes), --phrases (classroom references), --stamps
                       (Sources checked vs the brief), --citations (sup.cite -> li#src-N, URLs in the brief), --links
                       (liveness); --all-live covers every live page, --all-authored every authored or live page (drift_check uses it, D-0052); author, humanizer, verify agent, critic and tests call it
  publish_demos.py     copies trainer/<rel>/demos/key/ to demos/<rel>/ and flips the notes demo card once the day is taught (D-0030); loose days are published by close_day.py
  close_day.py         closes a loose demo day (D-0050): `<week> <day> [--date YYYY-MM-DD] [--files ...] [--notes "..."] [--no-pull] [--apply]`; the only writer
                       of `taught`; pulls demo-repo/, copies the day's committed files to demos/<rel>/ with a README, writes trainer/<rel>/delivery.json,
                       flips the demo card, appends the runbook Delivery record, logs a manual run, rebuilds index and tracker; dry run without --apply
  release_week.py      the Friday gate (D-0052): `<week> --today <date> [--check]`; refuses unless the plan passes plan_check, every teaching day is authored (or live),
                       pages and exercise READMEs exist, last-tests.json is green and the current week's past teaching days have delivery.json; then flips
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
  workflows/week-plan.js    once per week, before the first day: author + critic write plans/week-WW.md, then a Record agent (<=5 agents)
  workflows/day-fanout.js   the per-day Workflow-tool script
  workflows/practice-tasks.js   after a week is authored: suitability pass (one assessor per page), then, once the trainer approved, the build (author + critic per day)
  plans/week-WW.md     the week plans (committed): Weekly Epic, Threads rung table, demo ladder, per-day shape, ledgers, coverage map
  templates/           tracker.html (work-tracker shell, no data), day.exemplar.html, week-plan.md, research.md, runbook.md, demo-script.md, demo-README.md, exercise-README.md, conftest.py
  critics/             PASS criteria each critic agent reads: week-plan, research, demos, series-review (D-0053), notes, runbook, exercise, practice
  research/<week>/<day>.md   research briefs (committed; the audit trail for every claim)
```

## Per-week stage (runs once, before the week's first day)

```
python harness/args_for.py 1 --plan --today 2026-10-12      # week-plan args: every teaching day, threads in scope, previous plan
Workflow({ scriptPath: "harness/workflows/week-plan.js", args: { ...json... } })
python harness/plan_check.py harness/plans/week-01.md       # the critic ran it; run it again before committing
```

The plan's `## Threads` table makes most demos rungs of one growing codebase (D-0033): each row says which demo, which key, what it starts from, what it adds and the commit that ends it. `args_for.py <week> <day>` then passes that day's coverage rows, thread rows (with `startsFrom`), ladder rows and day shape into `day-fanout.js`, where the demo author extends the `Starts from` key and the critics check the day teaches exactly those rows. A day cannot be authored without its plan; `--no-plan` is the logged escape for a gate bug.

Decisions that shaped any of this (and every later schedule/scope change) are logged in `decisions/README.md` (newest first; see `AGENTS.md` for the rule, D-0001).

## Per-day pipeline

| Stage | Author writes | Critic checks (spec) | Gate |
|---|---|---|---|
| Research | `harness/research/<week>/<day>.md` (Claims, a `## Notes depth` block per subtopic, Sources, Glossary, Pitfalls, Demo hints) | `critics/research.md` | `full`: URLs fetched; `light`: structure + stamps; covers the plan's rows; Notes depth per subtopic (D-0040) |
| Demos | `trainer/<week>/<day>/demos/NN_<slug>.md` scripts + `key/` answer keys (skipped on `none`; optional fallback on `loose`); the plan's thread rows decide the demos, each rung extends its `Starts from` key | `critics/demos.md` | `demo_check.py` OK (format, both-ways with carried lines), every key runs, pre-flight walk, rung matches its plan row; a multi-day run ends the phase with one series-review critic (`critics/series-review.md`, D-0053: one story, each rung starts where the previous ended, ledger respected, last rung delivers the Weekly Epic; flags only, no fix loop) |
| Notes ∥ Exercise | `docs/weeks/<week>/<day>.html` (reference/study material, D-0040: 4500–7000 words, h3 subsections, an interview callout per step, a Check-yourself step, inline citations, a Sources-checked stamp, no classroom references), `exercises/<week>/<day>/` + `trainer/.../solutions/` | `critics/notes.md` (+ a notes-verify agent: `notes_check.py` every day, WebFetch currency on full-gate and currency-flagged days; its findings bind the critic), `critics/exercise.md` | metrics bands via `notes_check.py`; demo card pending; starter fails / solution passes |
| Runbook | `trainer/<week>/<day>/runbook.md` | `critics/runbook.md` | headings, minutes, one pointer section per script + a Facilitation block per concept subtopic |
| Wire (serial) | glossary.js append, `status: live|authored` (`releaseOnWire`; a live day is never downgraded), `build_index.py`, NEXT links, `publish_demos.py` (no-op until `taught`; loose days: `close_day.py`), `build_tracker.py` | — | — |
| Record | one line in `runs.jsonl` via `log_run.py add` (agents, passes, flags, tiers); `tracker.html` rebuilt (D-0035) | — | — |
| Verify | test result amended onto the run record | `python -m unittest discover -s tests` (includes the tracker staleness test) | ≤2 fix loops |

Each gated artifact: author → critic → up to 3 repair passes → else **flagged** (reported, never blocks the run).

A humanizer agent (`humanizer:humanizer`, file mode, tier `humanize`) runs between author and critic on three artifacts: the notes page (D-0029) and the trainer's delivery wording, which is the day's demo scripts and the runbook (D-0039). On every one of them it changes prose only and proves it: `python harness/prose_guard.py snapshot <files>` before, `python harness/prose_guard.py check <snapshot dir> <files>` after (html mode for a page, D-0040). No critic item judges the wording of trainer files, so the pass adds agents (two per day, more on a repass) without moving the bar. For a hand pass on committed files use `python harness/prose_guard.py git <files>`.

Notes-only mode (D-0040): `python harness/args_for.py <week> <day...> --notes-only` runs a research DEPTH pass (a research agent extends the committed brief's `## Notes depth` section, judged by the research critic), then the notes page on top of the demo scripts and keys already on disk; exercise and runbook are untouched. `--template <path>` points the authors at another page shape (used to pilot a new template). Every stage tier in `config.json` `models` is pinned to opus, sonnet or haiku; none inherits the session model.

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
Then `python -m unittest discover -s tests -v`, open `docs/weeks/<week>/<day>.html` via `cd docs && python -m http.server 8000`, and rehearse `trainer/<week>/<day>/runbook.md` with the demo scripts in `trainer/<week>/<day>/demos/`. After the session, the delivery-day close sets `taught`: `python harness/close_day.py <week> <day> --apply` for a loose day (the files typed in class reach `demos/<week>/<day>/` and the notes page links them), `python harness/publish_demos.py <week> <day>` for a py/nb day.

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

Agent budget: ~13 agents on a clean pass per day, ~28 worst case (one of them the Record agent). A week is one batch (D-0038): pass its teaching days in one invocation; demos are authored in day order, everything else in parallel, and a day with no demo keys blocks the later days of the run. A single day stays valid. To re-run after editing prompts/critics, pass `resumeFromRunId` so finished stages are cached (same session only). From a new session, `python harness/args_for.py <week> <day> --skip-research` reuses the committed brief and runs demos onward live.

## Changing the bar

Edit `metrics.json` (numbers) or `critics/*.md` (PASS rules). The workflow prompts reference both; the tests and `notes_check.py` read `metrics.json`. The notes-page template the authors copy is `config.json` `template` (D-0031: the promoted `docs/weeks/week-01/day-2-orientation-agile-and-git.html`); `args_for.py` passes it as args `template` and falls back to `templates/day.exemplar.html` when the file is missing. To promote a better page, change `template` via a decision entry; the exemplar stays the structure gold standard for `tests/test_pages.py`.
