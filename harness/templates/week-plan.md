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

## Conventions

<!-- D-0057. Every rule a day author or a demo author could NOT infer from the block table, written BEFORE the block
     table is sized (the rows change what counts as a typed line). Kind is one of:
       tally          how typed lines are counted (editor, REPL, shell; what is not counted)
       lint           linter rules and what they force into the typed lines (docstrings, encoding=, pins)
       schema         the record keys / columns / file names later blocks select by name
       git            branch, merge and push cadence, incl. what to do when a merge slid to the next morning
       config         ordering rules (a basicConfig before the first log call, an import before its first use)
       tooling        container, venv, CLI and client conventions (image tag, container name, port, env names)
       carried-lines  which earlier lines a rewriting block replaces, line by line
     Applies from = all, or the walkthrough the rule starts at. Cells may not contain a pipe character.
     plan_check.py requires at least one tally and one git row. The critic reports a line-level gap as a missing or
     wrong row here, never as a per-block critique; the rows reach every day and demo author and the trainer README. -->

| Convention | Kind | Applies from | Rule | Why |
|---|---|---|---|---|
| typed-line tally | tally | all | every non-blank line the room types counts: editor lines, REPL lines and shell commands; lines moved by cut and paste or re-indented in place do not | the Adds budgets (metrics.demos.maxTypedLinesPerBlock at 1.5 per minute) are checked against it |
| branch per day | git | all | each day's AM block opens `feature/<slug>`; the PM block merges it into `main` and pushes; a merge that slid is made first thing in the next AM block before any new line | the Weekly Epic needs `main` on GitHub to hold the week's work; the demos critic runs each block's commit |
| pylint docstrings | lint | 02-pip-and-module-split | every new module, class, function and test function gets a one-line docstring; every `open()` passes `encoding="utf-8"` | C0114/C0115/C0116/W1514 fire otherwise and the later "only W0621 remains" claim must hold; both count in each block's typed lines |

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
     lunch, notes handoff, sprint / project work, wrap-up. Stop points and cut lists live in the
     week-level sections below. -->

### w02d1 — {{title}} ({{dateLabel}})

- AM: setup check (10), framing (5), Walkthrough 01-desk-modules (105; a 15-minute break inside it after Step 4), lunch (60).
- PM: Walkthrough 02-pip-and-module-split (75), break (10), notes page handoff (15), sprint / project work (70), wrap-up (10). Total 375.
- Demo minutes: 180.

## Stop points

<!-- One row per walkthrough: the clean step boundary to halt at if the block runs long (the repo is runnable and
     the commit can be made there), and where the remainder resumes (the next block's first step, the PM, the
     notes handoff). -->

| Walkthrough | Clean stop point | Resume at |
|---|---|---|
| 01-desk-modules | after Step 5 (logging wired; commit `Log desk events with the logging module` made) | 02-pip-and-module-split Step 1 opens with the regex step |

## Squeeze priorities

<!-- Over budget: cut in this order. Then what is never cut: the steps a later block starts from and the wrap-up
     questions. -->

**Cut first** (lowest cost to the through-line):
1. 01-desk-modules Step 6 (the `re.sub` redaction): name it, the pattern stays in the commit.
2. ...

**Never cut** (the lesson dies without these):
- 01-desk-modules Steps 2–4 (the module imports every later block reads).
- The wrap-up questions of every block.

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

## Exit criteria map

<!-- D-0063. Every criterion of this week's exit-criteria group (args exitGroup; `python harness/exit_criteria.py show <group>`
     prints the ids and the exact text) EXACTLY ONCE, in one of three Day forms:
       w03d2     mapped to a day of this week: Where = the walkthrough of that day that covers it, or facilitation, or
                 notes-only; Notes step = the page step that teaches it, 1-based, required on every Required row
       week 04   a LATER week of the group = deferred (Where and Notes step —); the last week of a group may defer nothing
       week 02   an EARLIER week of the group = taught earlier (Where and Notes step —); that week's plan maps it in-week,
                 so nothing is re-mapped twice
     The Coverage map's Demo column uses `notes`; this table's Where column uses `notes-only`; do not cross them.
     Required rows first within each section. -->

| ID | Tier | Criterion | Day | Where | Notes step |
|---|---|---|---|---|---|
| qc2.sql.R01 | Required | Articulate the reasons for using a Relational Database Model to represent data. | w03d1 | 01-desk-schema | 2 |
| qc2.sql.S05 | Stretch | Understand and know how to utilize Window Functions | w03d4 | notes-only | 6 |
| qc3.data.P03 | Preferred | (a row the next week of the group carries) | week 05 | — | — |
| qc3.data.R02 | Required | (a row the previous week of the group mapped in-week) | week 04 | — | — |
