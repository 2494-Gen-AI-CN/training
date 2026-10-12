# Project agent memory

Committed home for project-intrinsic knowledge: build, test, authoring rules and sharp edges that should travel with the code. `CLAUDE.md` points here.

## What this repo is

Prep repo for the 11-week **2494 Gen-AI Python** training. Two deliverables per day: live code-along demos (`demos/`) and a GitHub Pages site (`docs/`) with notes, quizzes and exercises. `harness/` is the agent-driven pipeline that produces them. Trainer-only runbooks and solutions live in a separate private repo cloned at `trainer/` (gitignored).

## Status and decision log (read first)

- `STATUS.md` is the single "what's next" surface: phase, milestones, open items. **Read it at session start** and update it in the same commit as any milestone or open-item change.
- `decisions/README.md` is the newest-first index of every on-the-fly decision (schedule, scope, API currency, naming). **Read it at session start.** Never redo or undo a logged decision; supersede it with a new entry.
- Any change to `harness/curriculum.json`, `harness/metrics.json`, `harness/config.json`, `harness/critics/*.md`, or the calendar (dates, holidays) requires an entry: `python decisions/new.py "Decision" --why "..." --affects "..."` and the printed ID (`D-NNNN`) goes in the commit message. `tests/test_decisions.py` enforces the format.

## Rules

- `harness/curriculum.json` is the single source of truth for weeks, days, slugs and status. Never hand-edit the WEEKS block in `docs/index.html`; run `python harness/build_index.py`.
- Calendar dates derive from `startDate` + week index + weekday slot, with `holidays` turning slots into `kind: "holiday"` (D-0013, D-0014). Never hand-type a date into a page, prompt or template; use `build_index.slot_date` / `args_for.py`. `day` is the weekday slot (1=Mon … 5=Fri); the feedback form is the last teaching day of each week, derived, never a JSON flag.
- Paths are always `{week.dir}/{day.slug}` (e.g. `week-01/day-2-orientation-agile-and-git`) across `demos/`, `exercises/`, `trainer/`, `docs/weeks/`, `harness/research/`. The short `id` (`w01d2`) is only for `<meta name="tc-day">`, localStorage keys and test keys.
- Week plan first (D-0034): no day of a week is authored before `harness/plans/week-WW.md` exists and passes `python harness/plan_check.py <plan>`. It is written once per week by `harness/workflows/week-plan.js` from `python harness/args_for.py <week> --plan --today <date>` (the only source of its args; tiers `week-plan` / `week-plan-critic`, D-0032) and holds the Weekly Epic, the Threads rung table, the demo ladder, per-day shape, the anti-spoiler and deviation ledgers and the coverage map. `args_for.py <week> <day>` is BLOCKED without it and passes the day's rows (`weekPlanRows`, `threadRows` with `startsFrom`, `ladderRows`, `dayShape`) into the day workflow; `--no-plan` is the logged escape (warning on stderr; record every use in STATUS.md with the reason). A live day's rows are recorded as-is; week N+1's plan starts from week N's last rung.
- Authoring is research-first: no notes page, demo or runbook is written before `harness/research/<week>/<day>.md` exists. Gate level (`full` | `light`) is per day in the curriculum. Full-gate briefs verify every URL; light-gate briefs still need version stamps and 3 official-doc URLs.
- Demos (D-0030): a demo IS the walkthrough script the trainer types live, `trainer/<rel>/demos/NN_<slug>.md` (template `harness/templates/demo-script.md`); the committed code is its answer key under `trainer/<rel>/demos/key/` (`NN_<slug>.py` runnable, or `.md` transcript for terminal demos). `python harness/demo_check.py <that dir>` enforces the format and the both-ways check (every typed line is in the key, every key line was typed). Nobody writes to the public `demos/<rel>/` by hand: `harness/publish_demos.py <week> <day>` copies `key/` there and flips the notes demo card only once the day carries `taught: "YYYY-MM-DD"` in `curriculum.json` (set by the delivery-day close). Concept subtopics get a timed `## Facilitation` block in the runbook, not code; `demoFormat: none` marks a day with no code demo at all (no demos stage, no demo card).
- Demo threads (D-0033): most demos are RUNGS of one demo codebase that grows across days and weeks (thread `p0-ticket-desk` for weeks 1–5, one per project block). Every script header carries `Thread:` and `Starts from:` (`cold` or the previous rung's key path); a rung's `.py` key is the thread's whole runnable end state (the one canonical copy) and the script types only what the rung adds; `demo_check.py` accepts carried lines and requires a dropped or rewritten carried line to appear in a ```python replaced block. Authoring order inside a thread is strictly rung order (the `Starts from` key must exist on disk). Re-authoring day N means re-checking every later rung (`tests/test_demos.py` ThreadChainTests fails them loudly). A delivery-day close that changes a key (classroom reality wins) runs BEFORE the next rung is authored. Single-file keys only until a later stage adds folder keys.
- Demos are authored before notes/runbook/exercise; those three refer to demos by objective and to answer-key files only where the contract allows (code popups, runbook pointers).
- `harness/config.json` `audience` is the learner persona (recent CS grads, no industry experience; D-0023). It reaches every author/critic prompt as "Audience". Week-level `notes` carry the week arc (what each day assumes from the previous one); day-level `notes` carry a day's shape. Change any of them via a decision entry.
- `harness/config.json` `models` maps each workflow stage to a model/effort tier (D-0026); `null` inherits the session model. A repass numbered ≥ `escalateOn` runs on the `escalate` tier. Tune it from the flag counts at retrospectives, via a decision entry.
- `exerciseKind` per day: `pytest` (default: starter fails, solution passes) or `rubric` (D-0025: hands-on deliverable, acceptance checklist and rubric in `exercises/<rel>/README.md`, trainer marking guide at `trainer/<rel>/solutions/RUBRIC.md`, no starter/ or tests/).
- Every notes page gets a `humanizer` pass (plugin skill `humanizer:humanizer`, file mode) after the author and before the critic (D-0029); critic item 18 in `harness/critics/notes.md` fails AI-sounding prose. Hand-edited notes prose gets the same pass before commit.
- Quality bars live in `harness/metrics.json`; critic PASS criteria live in `harness/critics/*.md`. Change those files, not the prompts, when the bar moves.
- Workflow scripts cannot read files or call `Date()`. Generate args with `python harness/args_for.py <week> <day...>` and pass them to `Workflow({ scriptPath: "harness/workflows/day-fanout.js", args })`. Run one day per invocation. The week plan runs once per week before its first day: `python harness/args_for.py <week> --plan --today <date>` then `Workflow({ scriptPath: "harness/workflows/week-plan.js", args })` (≤4 agents).
- No backend. Quiz, survey and theme state are localStorage only. Any `FDE_`, `workers.dev` or `2463` string in `docs/` is a leak from the reference site and fails `tests/test_assets.py`.
- `Reference-Example/` is read-only inspiration (nested git clones). Never `git add` it.

## Commands

- Contract tests: `python -m unittest discover -s tests -v`
- Index sync check: `python harness/build_index.py --check`
- Exercise contract: `cd exercises/<week>/<day> && python -m pytest -q` must fail; with `EXERCISE_SRC=../../../trainer/<week>/<day>/solutions` must pass.
- Preview site: `cd docs && python -m http.server 8000`
- Cache-bust after CSS/JS edits: `docs/bump-css.sh [--all]`

## Sharp edges

- Node is at `C:\Program Files\nodejs\node.exe`; the nvm shell hook may fail in some shells. Tests that need node skip when it is absent.
- Week 7 curriculum names TFLearn (unmaintained). Research must map each topic to a Keras/TF2 equivalent.
- Weeks 9–10 curriculum names pre-1.0 LangChain/LangGraph APIs (LLMChain, *SequentialChain, RouterChain, ConversationBuffer*Memory, AgentExecutor). Teach the LangChain/LangGraph 1.x equivalents; keep topic names in titles only. `notes` on those weeks in curriculum.json flow into every author/critic prompt.
- Key-gated demos (Anthropic wk 5, Pinecone wk 8, Bedrock wk 9, SageMaker wk 11) are compile-checked only by critics; rehearse them manually.

## Maintaining this file

Keep entries useful to almost every future agent session. Point to the authoritative file rather than repeating it. Prefer rewriting over appending.
