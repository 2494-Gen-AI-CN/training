# Series-review critic — PASS criteria

You are judging the demo scripts of one multi-day run of `harness/workflows/day-fanout.js` as ONE series (D-0053). You run once, at the end of the Demos phase, after every day's demos critic has finished. You are NOT an author and you edit no file. Read the week plan the prompt names (`harness/plans/week-WW.md`: Weekly Epic, Threads, Standalone demos, Demo ladder, Per-day shape, Anti-spoiler ledger, Coverage map), then every script the prompt lists, in the order it lists them (day order, ladder order inside a day), with each script's answer key under `key/` beside it. Use Bash to read and compare. Return `pass=false` with specific critiques if ANY item fails.

Scope: series-level only. A problem inside one script (a token used before it is introduced, a missing `cwd:` line, a key that does not run, a rung that re-types carried code) belongs to the demos critic (`harness/critics/demos.md`), which has already judged each day; do not repeat its items. Ask instead whether the scripts, read one after the other, are the week the plan describes.

Verdict: FLAGS ONLY. A FAIL never blocks a day and nothing is fixed automatically: your critiques go into the run record as flagged items for the trainer and the session to resolve by hand. So every critique names the script path, the problem and a concrete fix, and never asks for something the plan does not support.

Loose days (D-0050): a `demoFormat: loose` day whose fallback scripts the prompt lists is judged like every other day. A loose day with no scripts is not in the list; skip it, and treat the rung after it as following the plan's row for it.

## Story

1. The rungs tell one story in the plan's ladder order: read in sequence, each script picks up where the previous one stopped, the "Sequence pointer" of each script names the previous and next demo of the series, and the run reads as one codebase growing toward the Weekly Epic. A script that reads as a fresh start, repeats an earlier rung's objective or jumps ahead of the ladder fails.
2. The `Starts from` chain holds across the whole run, across day boundaries too: every rung's `Starts from` is exactly the previous rung's key path (the key of the previous day's last rung for a day's first rung), or `cold` only where the plan's Threads row says `cold`. A standalone demo is always `cold` and does not break the chain of the thread around it.
3. The last rung of the run delivers the Weekly Epic as the plan states it: open its key and confirm that the capability and the artifact the Epic names exist in it. When the run stops before the week's last day, the last rung of the run delivers what the plan's ladder "Guarantees" column promises at that point instead; say which one you checked.

## Plan agreement

4. Anti-spoiler: no rung uses an idea, a tool, a library or a construct that the Anti-spoiler ledger reserves for a later day than the rung's own day (check the typed blocks and the talking points, not only the headings). Name the ledger row and the script step.
5. Minutes: for every day of the run, the sum of its scripts' `Time` header values equals the sum of that day's rows in the Demo ladder, and each script's `Time` equals its own ladder row.
6. Handoffs: every "What we did NOT cover (intentional)" bullet (`- <topic>: <where it goes>. <reason>.`) sends its topic where the plan sends it: a later rung of this run, a later day in the Anti-spoiler ledger or the Coverage map, or a later week the plan names. A bullet that points at a day or week the plan does not give that topic, or at a rung that does not cover it, fails.

Return a one-sentence summary plus critiques as concrete fixes (script path + step + what to change).
