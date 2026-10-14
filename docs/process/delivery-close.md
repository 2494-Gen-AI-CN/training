# Delivery close checklist

Run in the first session after a teaching day, on the Friday before a week starts, and before every push. Decisions behind it: D-0050 (loose close), D-0052 (authored status, release gate, drift check). Scripts and flags are documented in `harness/README.md`; this page is the order of operations.

## Every teaching morning

Close yesterday's day, one catch-up close per missed day.

1. Dry run: `python harness/close_day.py <week> <day>`. Read the file list and the date it picked; override with `--date YYYY-MM-DD`, `--files ...` or `--notes "..."` if the demo repo's commits do not match what happened.
2. Apply: `python harness/close_day.py <week> <day> --apply`.

What `--apply` writes: `taught` in `curriculum.json` (this script is its only writer), `demos/<rel>/` with a generated README.md, `trainer/<rel>/delivery.json`, the notes demo card, `## Delivery record (<date>)` in the runbook, a `manual` run in `runs.jsonl`, and a rebuilt index and tracker. Add the printed Log line to `STATUS.md`.

Python and notebook days (`demoFormat` not `loose`) are not closed by this script: `python harness/publish_demos.py <week> <day>` publishes them. Thread days that need the rung-diff close wait for week 3 (STATUS O-18).

## Friday

Release next week.

1. `python harness/release_week.py <week+1> --today <date> --check`. It never writes. Read every reason it prints.
2. Fix what it names, then run it again until it is clean.
3. `python harness/release_week.py <week+1> --today <date>`. Add the printed Log line to `STATUS.md`.

What refuses it, and the fix:

- A teaching day is still `planned`: author it (`python harness/args_for.py <week> <day> --today <date>`, then the day workflow).
- The week plan fails `plan_check`: `python harness/plan_check.py harness/plans/week-WW.md` and repair the plan.
- A page or exercise README is missing for an authored day: re-author that day.
- `harness/last-tests.json` is red or missing: run the tests, then `python harness/log_run.py tests`.
- A teaching day of the current week before `--today` has no `trainer/<rel>/delivery.json`: close it with `close_day.py` (section above).

## Before every push

1. `python harness/drift_check.py` (add `--strict` to make dead links hard). Exit 1 means fix first.
2. `python harness/build_tracker.py --check`
3. `python harness/build_index.py --check`
4. `python harness/log_run.py tests`

## What hidden means

An `authored` page is written but not linked from `docs/index.html`; `build_index.py` links `live` days only. GitHub Pages still serves the file at its URL, so anyone with the address can open it. This keeps a week out of the learners' way. It is not access control.
