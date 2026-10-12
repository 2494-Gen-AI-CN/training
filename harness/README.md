# Harness

Agent-driven pipeline that turns one curriculum day into five reviewed artifacts.

```
harness/
  curriculum.json      source of truth: weeks, days, slugs, gate, demoFormat, status
  metrics.json         quality bars (word band, steps, quiz count, test counts, day minutes)
  config.json          site title, repo URL, feedback form, LLM provider defaults
  build_index.py       curriculum.json -> CAL/WEEKS block in docs/index.html (--check in tests); owns all calendar arithmetic
  args_for.py          prints the Workflow args for <week> <day...> (day = weekday slot; holiday slots refused; BLOCKED until the
                       week's plan exists, escape --no-plan) or, with <week> --plan, the args for the week-plan workflow (D-0034)
  plan_check.py        parses + checks one week plan (threads chain, ladder, coverage map, live days as-is); args_for and tests call it
  demo_check.py        format + both-ways check for one day's demo scripts and answer keys (critic and tests call it; D-0030);
                       thread rungs carry lines from their Starts from key, replaced lines go in a python replaced block (D-0033)
  publish_demos.py     copies trainer/<rel>/demos/key/ to demos/<rel>/ and flips the notes demo card once the day is taught (D-0030)
  build_tracker.py     writes ../tracker.html (the work tracker; local, gitignored, D-0036) = templates/tracker.html + a data block
                       read from repo state; --check in tests (D-0035)
  log_run.py           add / amend one record per workflow run in runs.jsonl; `tests` records the suite result in last-tests.json
  runs.jsonl           the run log (committed): agents, passes per artifact, flagged items, tiers, test result per run
  workflows/week-plan.js    once per week, before the first day: author + critic write plans/week-WW.md, then a Record agent (<=5 agents)
  workflows/day-fanout.js   the per-day Workflow-tool script
  plans/week-WW.md     the week plans (committed): Weekly Epic, Threads rung table, demo ladder, per-day shape, ledgers, coverage map
  templates/           tracker.html (work-tracker shell, no data), day.exemplar.html, week-plan.md, research.md, runbook.md, demo-script.md, demo-README.md, exercise-README.md, conftest.py
  critics/             PASS criteria each critic agent reads: week-plan, research, demos, notes, runbook, exercise
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
| Research | `harness/research/<week>/<day>.md` | `critics/research.md` | `full`: URLs fetched; `light`: structure + stamps; covers the plan's rows |
| Demos | `trainer/<week>/<day>/demos/NN_<slug>.md` scripts + `key/` answer keys (skipped on `demoFormat: none`); the plan's thread rows decide the demos, each rung extends its `Starts from` key | `critics/demos.md` | `demo_check.py` OK (format, both-ways with carried lines), every key runs, pre-flight walk, rung matches its plan row |
| Notes ∥ Exercise | `docs/weeks/<week>/<day>.html`, `exercises/<week>/<day>/` + `trainer/.../solutions/` | `critics/notes.md`, `critics/exercise.md` | metrics bands; demo card pending; starter fails / solution passes |
| Runbook | `trainer/<week>/<day>/runbook.md` | `critics/runbook.md` | headings, minutes, one pointer section per script + a Facilitation block per concept subtopic |
| Wire (serial) | glossary.js append, `status: live`, `build_index.py`, NEXT links, `publish_demos.py` (no-op until `taught`), `build_tracker.py` | — | — |
| Record | one line in `runs.jsonl` via `log_run.py add` (agents, passes, flags, tiers); `tracker.html` rebuilt (D-0035) | — | — |
| Verify | test result amended onto the run record | `python -m unittest discover -s tests` (includes the tracker staleness test) | ≤2 fix loops |

Each gated artifact: author → critic → up to 3 repair passes → else **flagged** (reported, never blocks the run).

## Running a day

```
python harness/args_for.py 1 2 --today 2026-10-13      # week 1, weekday slot 2 (Tue Oct 13; slot 1 is Thanksgiving)
```
Paste the JSON as `args`:
```
Workflow({ scriptPath: "harness/workflows/day-fanout.js", args: { ...json... } })
```
Then `python -m unittest discover -s tests -v`, open `docs/weeks/<week>/<day>.html` via `cd docs && python -m http.server 8000`, and rehearse `trainer/<week>/<day>/runbook.md` with the demo scripts in `trainer/<week>/<day>/demos/`. After the session, the delivery-day close sets `taught` on the day and runs `python harness/publish_demos.py <week> <day>` so the answer keys reach `demos/<week>/<day>/` and the notes page links them.

When the run finishes, complete its record with what the script cannot see, then look at the tracker:
```
python harness/log_run.py amend --last --run-id wf_xxxxxxxx-xxx --minutes 38 --tokens 900000 --tiers-verified yes
```
Open `tracker.html` (repo root) from disk for the whole picture: day pipeline, alarms, threads, runs. It is a local file, gitignored so trainees never see it (D-0036), generated by `build_tracker.py` from the committed shell `templates/tracker.html`; a change to `STATUS.md`, the curriculum, a plan, a decision or a trainer file makes it stale until that script runs, and `tests/test_tracker.py` fails meanwhile.

Agent budget: ~13 agents on a clean pass per day, ~28 worst case (one of them the Record agent). Run one day per invocation. To re-run after editing prompts/critics, pass `resumeFromRunId` so finished stages are cached (same session only). From a new session, `python harness/args_for.py <week> <day> --skip-research` reuses the committed brief and runs demos onward live.

## Changing the bar

Edit `metrics.json` (numbers) or `critics/*.md` (PASS rules). The workflow prompts reference both; the tests read `metrics.json`. The notes-page template the authors copy is `config.json` `template` (D-0031: the promoted `docs/weeks/week-01/day-2-orientation-agile-and-git.html`); `args_for.py` passes it as args `template` and falls back to `templates/day.exemplar.html` when the file is missing. To promote a better page, change `template` via a decision entry; the exemplar stays the structure gold standard for `tests/test_pages.py`.
