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
- Authoring is research-first: no notes page, demo or runbook is written before `harness/research/<week>/<day>.md` exists. Gate level (`full` | `light`) is per day in the curriculum. Full-gate briefs verify every URL; light-gate briefs still need version stamps and 3 official-doc URLs.
- Demos are authored before notes/runbook/exercise; those three only link to demo files that exist.
- Quality bars live in `harness/metrics.json`; critic PASS criteria live in `harness/critics/*.md`. Change those files, not the prompts, when the bar moves.
- Workflow scripts cannot read files or call `Date()`. Generate args with `python harness/args_for.py <week> <day...>` and pass them to `Workflow({ scriptPath: "harness/workflows/day-fanout.js", args })`. Run one day per invocation.
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
