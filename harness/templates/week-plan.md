# Week {{WW}} plan — {{theme}}

Week {{W}} · {{weekStart}} to {{weekEnd}} · phase {{phase}} · project {{project}} · plan written {{today}}

<!--
Week plan (D-0034). Written ONCE per week by harness/workflows/week-plan.js before the first day of the week is
authored; harness/args_for.py refuses to emit day args until harness/plans/week-WW.md exists and passes
harness/plan_check.py. Keep every heading below, in this order; the tables are parsed mechanically (column names
exact, one row per line, no merged cells). Day ids are the curriculum ids (w01d3). Demo names are NN_<slug> with NN
counting 01.. within the day in ladder order. Keys are NN_<slug>.py (runnable end state) or NN_<slug>.md (transcript).
-->

## Weekly Epic

One paragraph, written as what the learner can DO by Friday afternoon (not what they will have seen), in the demo
domain of the thread. Name the artifact they will have built along the trainer.

## Assumes from the previous week

- What this week takes as given (week 1: the audience persona from config.json; later weeks: the previous plan's
  Weekly Epic, and the thread's end state at that week's last rung: `trainer/<rel>/demos/key/NN_<slug>.py`).
- What this week does NOT assume (so the first day re-checks it in its first demo).

## Threads

<!-- One "### <thread-id>" per thread touched this week. Thread ids are kebab-case and stable across weeks. -->

### {{thread-id}}

- Domain: one line (the records the thread manages and why that domain survives every week of the scope).
- Scope: weeks {{a}}–{{b}} (project {{P}}); this week plans rungs {{r1}}–{{r2}}.
- Start state this week: cold | `trainer/<rel>/demos/key/NN_<slug>.py` (the previous week's last rung).
- End state this week: `trainer/<rel>/demos/key/NN_<slug>.py` (the last rung below), about N lines.

| Rung | Day | Demo | Key | Starts from | Adds | End state | Commit message |
|---|---|---|---|---|---|---|---|
| 1 | w01d2 | 02_local_git_loop | 02_local_git_loop.md | cold | what the trainer types in this rung (a line per function/class/file added) | what runs at the end of the rung | the commit that ends the rung (imperative, 50 chars) |
| 2 | w01d2 | 03_remote_round_trip | 03_remote_round_trip.md | trainer/week-01/day-2-orientation-agile-and-git/demos/key/02_local_git_loop.md | ... | ... | ... |

<!--
Rung rules (checked by plan_check.py): rungs numbered 1..n in teaching order; Starts from is "cold" on the first
rung of the thread's whole scope, otherwise EXACTLY the previous rung's key path trainer/<weekDir>/<slug>/demos/key/<Key>
(the previous week's last rung for the first rung of a later week); Key is Demo + .py|.md|.ipynb; a .py key is the
thread's whole end state at that rung and fits metrics.demos.maxLinesPerThreadKey; Adds fits
metrics.demos.maxTypedLinesPerRung typed lines. An authored or live day's rows are recorded as-is from its scripts on
disk (D-0052).
-->

## Standalone demos

<!-- Subtopics that fit no thread (A23). Each says why. "none this week" if empty. -->

| Day | Demo | Key | Minutes | Why it fits no thread |
|---|---|---|---|---|
| w01d2 | 01_tooling_check | 01_tooling_check.py | 15 | on-ramp tooling check; no codebase exists yet |

## Demo ladder

<!-- Every demo of the week (thread rungs + standalone), in teaching order. Must follow = ladder numbers this demo
     depends on (the previous rung of its thread at least), "—" if none. Guarantees = what a later demo may assume
     exists because this one ran. Minutes within metrics.demos.minutesPerScriptMin..Max; scripts per day within
     scriptsMin..Max. -->

| # | Day | Demo | Minutes | Must follow | Guarantees |
|---|---|---|---|---|---|
| 1 | w01d2 | 01_tooling_check | 15 | — | python 3.15 answers on every machine; hello.py exists |
| 2 | w01d2 | 02_local_git_loop | 40 | 1 | the Tuesday scratch repo with hello.py, .gitignore, a merged feature branch and a resolved conflict |

## Per-day shape

<!-- One "### <id> — <title> (<dateLabel>)" per teaching day of the week, in order. -->

### w01d3 — {{title}} ({{dateLabel}})

- AM: setup check, framing, Demo 1 (NN_<slug>, M min), Facilitation blocks named by subtopic, break.
- PM: Demo 2 (NN_<slug>, M min), notes page handoff, exercise briefing, exercise, wrap-up.
- Demo minutes: N (the scripts of this day, from the ladder).
- Stop points: if the day runs long after Demo 1 Step n → what moves to the PM; after Demo 2 Step n → what moves to tomorrow's first demo (and tomorrow's plan row absorbs it).
- Cut first: the block that can go without breaking a later rung.
- Never cut: the rungs a later day starts from; the exercise briefing.

## Anti-spoiler ledger

<!-- What each day deliberately defers, to which later day (an id in this week or "week WW"), and why. -->

| Day | Defers | To | Why |
|---|---|---|---|
| w01d3 | functions (the ticket stays a flat set of variables) | w01d5 | functions are Friday's design choice; Wednesday is conventions |

## Real-world framing and deliberate deviations

One paragraph: how the thread's domain maps to a workplace (who files a ticket, who triages, what "done" means) and
what a professional team would build instead of what the demos build.

| Deviation | Workplace reality | Pedagogical reason |
|---|---|---|
| one `.py` file holds the whole ticket desk | a package with modules and tests | single-file keys keep the typed-live contract checkable; the package split is week 2 |

## Coverage map

<!-- Every curriculum subtopic of every teaching day of the week, exactly as spelled in curriculum.json, once.
     Demo = NN_<slug> of that day, or "facilitation" (a timed runbook block, D-0030), or "notes" (notes page only;
     say why in the Per-day shape). Notes step = the step number on the notes page that teaches it (1-based). -->

| Subtopic | Day | Demo | Notes step |
|---|---|---|---|
| Python syntax | w01d3 | 01_<slug> | 1 |
