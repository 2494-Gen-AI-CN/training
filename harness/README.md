# Harness

Agent-driven pipeline that turns one curriculum day into five reviewed artifacts.

```
harness/
  curriculum.json      source of truth: weeks, days, slugs, gate, demoFormat, status
  metrics.json         quality bars (word band, steps, quiz count, test counts, day minutes)
  config.json          site title, repo URL, feedback form, LLM provider defaults, learner repo convention (D-0037)
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
                       (liveness); --all-live covers every live page; author, humanizer, verify agent, critic and tests call it
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
| Research | `harness/research/<week>/<day>.md` (Claims, a `## Notes depth` block per subtopic, Sources, Glossary, Pitfalls, Demo hints) | `critics/research.md` | `full`: URLs fetched; `light`: structure + stamps; covers the plan's rows; Notes depth per subtopic (D-0040) |
| Demos | `trainer/<week>/<day>/demos/NN_<slug>.md` scripts + `key/` answer keys (skipped on `demoFormat: none`); the plan's thread rows decide the demos, each rung extends its `Starts from` key | `critics/demos.md` | `demo_check.py` OK (format, both-ways with carried lines), every key runs, pre-flight walk, rung matches its plan row |
| Notes ∥ Exercise | `docs/weeks/<week>/<day>.html` (reference/study material, D-0040: 4500–7000 words, h3 subsections, an interview callout per step, a Check-yourself step, inline citations, a Sources-checked stamp, no classroom references), `exercises/<week>/<day>/` + `trainer/.../solutions/` | `critics/notes.md` (+ a notes-verify agent: `notes_check.py` every day, WebFetch currency on full-gate and currency-flagged days; its findings bind the critic), `critics/exercise.md` | metrics bands via `notes_check.py`; demo card pending; starter fails / solution passes |
| Runbook | `trainer/<week>/<day>/runbook.md` | `critics/runbook.md` | headings, minutes, one pointer section per script + a Facilitation block per concept subtopic |
| Wire (serial) | glossary.js append, `status: live`, `build_index.py`, NEXT links, `publish_demos.py` (no-op until `taught`), `build_tracker.py` | — | — |
| Record | one line in `runs.jsonl` via `log_run.py add` (agents, passes, flags, tiers); `tracker.html` rebuilt (D-0035) | — | — |
| Verify | test result amended onto the run record | `python -m unittest discover -s tests` (includes the tracker staleness test) | ≤2 fix loops |

Each gated artifact: author → critic → up to 3 repair passes → else **flagged** (reported, never blocks the run).

A humanizer agent (`humanizer:humanizer`, file mode, tier `humanize`) runs between author and critic on three artifacts: the notes page (D-0029) and the trainer's delivery wording, which is the day's demo scripts and the runbook (D-0039). On every one of them it changes prose only and proves it: `python harness/prose_guard.py snapshot <files>` before, `python harness/prose_guard.py check <snapshot dir> <files>` after (html mode for a page, D-0040). No critic item judges the wording of trainer files, so the pass adds agents (two per day, more on a repass) without moving the bar. For a hand pass on committed files use `python harness/prose_guard.py git <files>`.

Notes-only mode (D-0040): `python harness/args_for.py <week> <day...> --notes-only` runs a research DEPTH pass (a research agent extends the committed brief's `## Notes depth` section, judged by the research critic), then the notes page on top of the demo scripts and keys already on disk; exercise and runbook are untouched. `--template <path>` points the authors at another page shape (used to pilot a new template). Every stage tier in `config.json` `models` is pinned to opus, sonnet or haiku; none inherits the session model.

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

Agent budget: ~13 agents on a clean pass per day, ~28 worst case (one of them the Record agent). A week is one batch (D-0038): pass its teaching days in one invocation; demos are authored in day order, everything else in parallel, and a day with no demo keys blocks the later days of the run. A single day stays valid. To re-run after editing prompts/critics, pass `resumeFromRunId` so finished stages are cached (same session only). From a new session, `python harness/args_for.py <week> <day> --skip-research` reuses the committed brief and runs demos onward live.

## Changing the bar

Edit `metrics.json` (numbers) or `critics/*.md` (PASS rules). The workflow prompts reference both; the tests and `notes_check.py` read `metrics.json`. The notes-page template the authors copy is `config.json` `template` (D-0031: the promoted `docs/weeks/week-01/day-2-orientation-agile-and-git.html`); `args_for.py` passes it as args `template` and falls back to `templates/day.exemplar.html` when the file is missing. To promote a better page, change `template` via a decision entry; the exemplar stays the structure gold standard for `tests/test_pages.py`.
