# Harness

Agent-driven pipeline that turns one curriculum day into five reviewed artifacts.

```
harness/
  curriculum.json      source of truth: weeks, days, slugs, gate, demoFormat, status
  metrics.json         quality bars (word band, steps, quiz count, test counts, day minutes)
  config.json          site title, repo URL, feedback form, LLM provider defaults
  build_index.py       curriculum.json -> WEEKS block in docs/index.html   (--check in tests)
  args_for.py          prints the Workflow args for <week> <day...>
  workflows/day-fanout.js   the Workflow-tool script
  templates/           day.exemplar.html, research.md, runbook.md, demo-README.md, exercise-README.md, conftest.py
  critics/             PASS criteria each critic agent reads: research, demos, notes, runbook, exercise
  research/<week>/<day>.md   research briefs (committed; the audit trail for every claim)
```

Decisions that shaped any of this (and every later schedule/scope change) are logged in `decisions/README.md` (newest first; see `AGENTS.md` for the rule, D-0001).

## Per-day pipeline

| Stage | Author writes | Critic checks (spec) | Gate |
|---|---|---|---|
| Research | `harness/research/<week>/<day>.md` | `critics/research.md` | `full`: URLs fetched; `light`: structure + stamps |
| Demos | `demos/<week>/<day>/` | `critics/demos.md` | compiles, runs, README order, STEP markers |
| Notes ∥ Exercise | `docs/weeks/<week>/<day>.html`, `exercises/<week>/<day>/` + `trainer/.../solutions/` | `critics/notes.md`, `critics/exercise.md` | metrics bands; starter fails / solution passes |
| Runbook | `trainer/<week>/<day>/runbook.md` | `critics/runbook.md` | headings, minutes, one section per demo |
| Wire (serial) | glossary.js append, `status: live`, `build_index.py`, NEXT links | — | — |
| Verify | — | `python -m unittest discover -s tests` | ≤2 fix loops |

Each gated artifact: author → critic → up to 3 repair passes → else **flagged** (reported, never blocks the run).

## Running a day

```
python harness/args_for.py 1 1 --today 2026-10-13
```
Paste the JSON as `args`:
```
Workflow({ scriptPath: "harness/workflows/day-fanout.js", args: { ...json... } })
```
Then `python -m unittest discover -s tests -v`, open `docs/weeks/<week>/<day>.html` via `cd docs && python -m http.server 8000`, and rehearse `trainer/<week>/<day>/runbook.md` against the demo files.

Agent budget: ~12 agents on a clean pass per day, ~27 worst case. Run one day per invocation. To re-run after editing prompts/critics, pass `resumeFromRunId` so finished stages are cached.

## Changing the bar

Edit `metrics.json` (numbers) or `critics/*.md` (PASS rules). The workflow prompts reference both; the tests read `metrics.json`. After the week-1 pilot, point `TEMPLATE` (args `template`) at the real `docs/weeks/week-01/day-1-*.html` instead of the exemplar.
