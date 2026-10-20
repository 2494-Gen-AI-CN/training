# Delivery close checklist

Run in the first session after a teaching day, on the Friday before a week starts, and before every push. Decisions behind it: D-0050 (the close), D-0052 (authored status, release gate, drift check), D-0055 (walkthrough blocks, the prep branch as the answer key). Scripts and flags are documented in `harness/README.md`; this page is the order of operations.

## Every teaching morning

Close yesterday's day, one catch-up close per missed day.

1. Dry run: `python harness/close_day.py <week> <day>`. Read the block list: each block of the day is `reached` (the room's commit matches the prep commit), `diverged` (it differs; the diffstat is printed) or `not reached` (no live commit with that message on that date). Override with `--date YYYY-MM-DD`, `--match NN-slug=<sha>` (when the room's commit message was not typed verbatim) or `--notes "..."` if the demo repo's commits do not match what happened.
2. Apply: `python harness/close_day.py <week> <day> --apply`.
3. Fold back by hand what diverged: edit the walkthrough so it says what the room really typed, and rebase or amend the block's commit on `prep/week-WW` so the prep branch equals the room's reality; run `python harness/demo_check.py trainer/week-WW/demos` and `prose_guard.py git` on the edited file. The steps a `not reached` block left over open the next block (its first step), as the plan's Stop points row says; put a line about it in the next day's runbook.

What `--apply` writes: `taught` in `curriculum.json` (this script is its only writer), `trainer/<rel>/delivery.json` (per block: prep sha, live sha, state, diffstat), a `> **DELIVERY RECORD (<date>)**` blockquote under each block's walkthrough header, `## Delivery record (<date>)` in the runbook, the re-rendered `trainer/week-WW/demos/README.md`, a `manual` run in `runs.jsonl`, and a rebuilt index and tracker. Add the printed Log line to `STATUS.md`. A `demoFormat: none` day has nothing to close.

## Friday

Release next week.

1. `python harness/release_week.py <week+1> --today <date> --check`. It never writes. Read every reason it prints.
2. Fix what it names, then run it again until it is clean.
3. `python harness/release_week.py <week+1> --today <date>`. Add the printed Log line to `STATUS.md`. The release also rebuilds `docs/exit-criteria/` (the "Covered on" links to the week's pages appear when its days go live, D-0063).
4. Push the week's prep branch so the trainer can rehearse from it and the close can diff against it: `git -C demo-repo push -u origin prep/week-WW`.

What refuses it, and the fix:

- A teaching day is still `planned`: author it (`python harness/args_for.py <week> <day> --today <date>`, then the day workflow).
- The week plan fails `plan_check`: `python harness/plan_check.py harness/plans/week-WW.md` and repair the plan.
- A page or exercise README is missing for an authored day: re-author that day.
- `harness/last-tests.json` is red or missing: run the tests, then `python harness/log_run.py tests`.
- A teaching day before `--today` has no `trainer/<rel>/delivery.json`: close it with `close_day.py` (section above).
- A walkthrough fails `demo_check` or the series README is stale: fix the walkthrough, or `python harness/series_readme.py <week>`.

## Before every push

1. `python harness/drift_check.py` (add `--strict` to make dead links hard). Exit 1 means fix first.
2. `python harness/build_tracker.py --check`
3. `python harness/build_index.py --check` (covers `docs/exit-criteria/` too, D-0063; `python harness/build_exit_pages.py` rebuilds those pages when a week plan's exit map or a day's status changed)
4. `python harness/log_run.py tests`

## What hidden means

An `authored` page is written but not linked from `docs/index.html`; `build_index.py` links `live` days only. GitHub Pages still serves the file at its URL, so anyone with the address can open it. This keeps a week out of the learners' way. It is not access control. The walkthroughs are trainer-only (the private repo); the prep branch of the public demo repo holds their end state and is visible to anyone who looks (D-0055).
