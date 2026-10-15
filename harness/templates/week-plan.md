# Week {{WW}} plan — {{theme}}

Week {{W}} · {{weekStart}} to {{weekEnd}} · phase {{phase}} · project {{project}} · plan written {{today}}

<!--
Week plan (D-0034, D-0055). Written ONCE per week by harness/workflows/week-plan.js before the first day of the week
is authored; harness/args_for.py refuses day args until harness/plans/week-WW.md exists and passes
harness/plan_check.py. The plan is also the source of the week's demo series README: harness/series_readme.py renders
trainer/week-WW/demos/README.md from it. Keep every heading below, in this order; the tables are parsed
mechanically (column names exact, one row per line, no merged cells). Day ids are the curriculum ids (w02d3).
A walkthrough is one demo BLOCK (an AM or PM demo slot, 45–180 min) that ends in ONE commit on the demo repo's prep
branch; walkthrough names are NN-<slug> with NN counting 01.. ACROSS THE WEEK in ladder order.
-->

## Weekly Epic

One paragraph, written as what the learner can DO by Friday afternoon (not what they will have seen), in the demo
domain of the thread. Name the artifact they will have built along the trainer.

## Assumes from the previous week

- What this week takes as given (week 1: the audience persona from config.json; later weeks: the previous plan's
  Weekly Epic, and the thread's end state at that week's last walkthrough, i.e. its commit on the demo repo).
- What this week does NOT assume (so the first block re-checks it in its first step).

## Threads

<!-- One "### <thread-id>" per thread touched this week. Thread ids are kebab-case and stable across weeks. -->

### {{thread-id}}

- Domain: one line (the records the thread manages and why that domain survives every week of the scope).
- Scope: weeks {{a}}–{{b}} (project {{P}}); this week plans blocks {{b1}}–{{b2}}.
- Start state this week: cold | `NN-<slug>` (the previous week's last walkthrough, i.e. its commit on the prep branch).
- End state this week: the commit of `NN-<slug>` (the last block below): what the repo holds then, about N lines.

| Block | Day | Slot | Walkthrough | Starts from | Adds | End state | Commit message |
|---|---|---|---|---|---|---|---|
| 1 | w02d1 | AM | 01-desk-modules | cold | what the trainer types in this block (a line per function/class/file added) | what runs at the end of the block | the commit that ends the block (imperative, <= 50 chars) |
| 2 | w02d1 | PM | 02-pip-and-module-split | 01-desk-modules | ... | ... | ... |

<!--
Block rules (checked by plan_check.py): blocks numbered 1..n in teaching order; Slot is AM or PM and a day has at
most one block per slot; Starts from is "cold" on the first block of the thread's whole scope, the previous week's
last walkthrough name on the first block of a later week, otherwise EXACTLY the previous block's Walkthrough; the
block's commit on the prep branch (config.json demoRepo.prepBranch) is its answer key; Adds fits about
metrics.demos.maxTypedLinesPerBlock typed lines (1.5 per minute). An authored or live day's rows are recorded
as-is from its walkthroughs on disk (D-0052).
-->

## Standalone demos

<!-- Blocks that fit no thread (A23). Each says why. Leave the table empty if there is none. -->

| Day | Slot | Walkthrough | Minutes | Why it fits no thread |
|---|---|---|---|---|

## Demo ladder

<!-- Every walkthrough of the week (thread blocks + standalone), in teaching order. Must follow = ladder numbers
     this one depends on (the previous block of its thread at least), "—" if none. Guarantees = what a later
     block may assume exists because this one ran. Minutes within metrics.demos.minutesPerBlockMin..Max; blocks
     per day within blocksPerDayMin..Max; NN of the name equals the ladder number. -->

| # | Day | Walkthrough | Minutes | Must follow | Guarantees |
|---|---|---|---|---|---|
| 1 | w02d1 | 01-desk-modules | 105 | — | `ticket-desk/ticket_desk.py` imports math, logging and re; branch `feature/desk-modules` has three commits |
| 2 | w02d1 | 02-pip-and-module-split | 75 | 1 | a `.venv` with pylint pinned; `desk.py` split out; `main` merged and pushed |

## Per-day shape

<!-- One "### <id> — <title> (<dateLabel>)" per teaching day of the week, in order. AM and PM list every block of
     the day: setup check, framing, the walkthrough (name, minutes), facilitation blocks by subtopic, breaks,
     lunch, notes handoff, exercise briefing, exercise, wrap-up. Stop points and cut lists live in the
     week-level sections below. -->

### w02d1 — {{title}} ({{dateLabel}})

- AM: setup check (10), framing (5), Walkthrough 01-desk-modules (105; a 15-minute break inside it after Step 4), lunch (60).
- PM: Walkthrough 02-pip-and-module-split (75), break (10), notes page handoff (15), exercise briefing (10), exercise (60), wrap-up (10). Total 375.
- Demo minutes: 180.

## Stop points

<!-- One row per walkthrough: the clean step boundary to halt at if the block runs long (the repo is runnable and
     the commit can be made there), and where the remainder resumes (the next block's first step, the PM, the
     notes handoff). -->

| Walkthrough | Clean stop point | Resume at |
|---|---|---|
| 01-desk-modules | after Step 5 (logging wired; commit `Log desk events with the logging module` made) | 02-pip-and-module-split Step 1 opens with the regex step |

## Squeeze priorities

<!-- Over budget: cut in this order. Then what is never cut: the steps a later block starts from, the exercise
     briefing, the wrap-up questions. -->

**Cut first** (lowest cost to the through-line):
1. 01-desk-modules Step 6 (the `re.sub` redaction): name it, the pattern stays in the commit.
2. ...

**Never cut** (the lesson dies without these):
- 01-desk-modules Steps 2–4 (the module imports every later block reads).
- The exercise briefing and the wrap-up questions of every block.

## Hard-stop rule

If a walkthrough hits 80% of its slot with 50% of its steps left, stop at the nearest clean stop point above, make the
block's commit from the script's kept lines, and resume at the named step next slot. Never double-speed a
code-along: a lost trainee cannot catch up, and every later block depends on this one being understood, not just
present.

## Scaffold bundle

<!-- "Scaffold the rote, hand-type the lesson." Hand-outs are files on main of the demo repo, run by path, never a
     branch switch. First-contact blocks pre-provide nothing. -->

| Day | Hand-out | Pre-provided | Why rote |
|---|---|---|---|
| w02d1 | — | none | first-contact modules; the typing is the lesson |

| Never pre-provide | Walkthrough |
|---|---|
| the module imports, the logging config, the regex patterns | 01-desk-modules |

## Run prerequisites

- The demo repo clone at `demo-repo/` on branch `main` with the previous week's commits; `prep/week-WW` pushed before Monday.
- Python 3.15; no container, no key this week.

## Anti-spoiler ledger

<!-- What each day deliberately defers, to which later day (an id in this week or "week WW"), and why. -->

| Day | Defers | To | Why |
|---|---|---|---|
| w02d1 | exceptions (`ValueError` is named, never raised) | w02d2 | exceptions are Tuesday's topic |

## Real-world framing and deliberate deviations

One paragraph: how the thread's domain maps to a workplace (who files a ticket, who triages, what "done" means) and
what a professional team would build instead of what the demos build.

| Deviation | Workplace reality | Pedagogical reason |
|---|---|---|
| one `.py` file holds the whole ticket desk | a package with modules and tests | the package split is this week's first PM block |

## Coverage map

<!-- Every curriculum subtopic of every teaching day of the week, exactly as spelled in curriculum.json, once.
     Demo = the NN-<slug> walkthrough of that day that teaches it, or "facilitation" (a timed runbook block), or
     "notes" (notes page only; say why in the Per-day shape). Notes step = the step number on the notes page that
     teaches it (1-based). -->

| Subtopic | Day | Demo | Notes step |
|---|---|---|---|
| Math module | w02d1 | 01-desk-modules | 1 |
