# Harness

Agent-driven pipeline that turns one curriculum day into five reviewed artifacts.

```
harness/
  curriculum.json      source of truth: weeks, days, slugs, gate, demoFormat, status
  metrics.json         quality bars (word band, steps, quiz count, test counts, day minutes)
  config.json          site title, repo URL, feedback form, LLM provider defaults
  build_index.py       curriculum.json -> CAL/WEEKS block in docs/index.html (--check in tests); owns all calendar arithmetic
  args_for.py          prints the Workflow args for <week> <day...> (day = weekday slot; holiday slots refused)
  demo_check.py        format + both-ways check for one day's demo scripts and answer keys (critic and tests call it; D-0030);
                       thread rungs carry lines from their Starts from key, replaced lines go in a python replaced block (D-0033)
  publish_demos.py     copies trainer/<rel>/demos/key/ to demos/<rel>/ and flips the notes demo card once the day is taught (D-0030)
  workflows/day-fanout.js   the Workflow-tool script
  templates/           day.exemplar.html, research.md, runbook.md, demo-script.md, demo-README.md, exercise-README.md, conftest.py
  critics/             PASS criteria each critic agent reads: research, demos, notes, runbook, exercise
  research/<week>/<day>.md   research briefs (committed; the audit trail for every claim)
```

Decisions that shaped any of this (and every later schedule/scope change) are logged in `decisions/README.md` (newest first; see `AGENTS.md` for the rule, D-0001).

## Per-day pipeline

| Stage | Author writes | Critic checks (spec) | Gate |
|---|---|---|---|
| Research | `harness/research/<week>/<day>.md` | `critics/research.md` | `full`: URLs fetched; `light`: structure + stamps |
| Demos | `trainer/<week>/<day>/demos/NN_<slug>.md` scripts + `key/` answer keys (skipped on `demoFormat: none`) | `critics/demos.md` | `demo_check.py` OK (format, both-ways), every key runs, pre-flight walk |
| Notes ∥ Exercise | `docs/weeks/<week>/<day>.html`, `exercises/<week>/<day>/` + `trainer/.../solutions/` | `critics/notes.md`, `critics/exercise.md` | metrics bands; demo card pending; starter fails / solution passes |
| Runbook | `trainer/<week>/<day>/runbook.md` | `critics/runbook.md` | headings, minutes, one pointer section per script + a Facilitation block per concept subtopic |
| Wire (serial) | glossary.js append, `status: live`, `build_index.py`, NEXT links, `publish_demos.py` (no-op until `taught`) | — | — |
| Verify | — | `python -m unittest discover -s tests` | ≤2 fix loops |

Each gated artifact: author → critic → up to 3 repair passes → else **flagged** (reported, never blocks the run).

## Running a day

```
python harness/args_for.py 1 2 --today 2026-10-13      # week 1, weekday slot 2 (Tue Oct 13; slot 1 is Thanksgiving)
```
Paste the JSON as `args`:
```
Workflow({ scriptPath: "harness/workflows/day-fanout.js", args: { ...json... } })
```
Then `python -m unittest discover -s tests -v`, open `docs/weeks/<week>/<day>.html` via `cd docs && python -m http.server 8000`, and rehearse `trainer/<week>/<day>/runbook.md` with the demo scripts in `trainer/<week>/<day>/demos/`. After the session, the delivery-day close sets `taught` on the day and runs `python harness/publish_demos.py <week> <day>` so the answer keys reach `demos/<week>/<day>/` and the notes page links them.

Agent budget: ~12 agents on a clean pass per day, ~27 worst case. Run one day per invocation. To re-run after editing prompts/critics, pass `resumeFromRunId` so finished stages are cached (same session only). From a new session, `python harness/args_for.py <week> <day> --skip-research` reuses the committed brief and runs demos onward live.

## Changing the bar

Edit `metrics.json` (numbers) or `critics/*.md` (PASS rules). The workflow prompts reference both; the tests read `metrics.json`. The notes-page template the authors copy is `config.json` `template` (D-0031: the promoted `docs/weeks/week-01/day-2-orientation-agile-and-git.html`); `args_for.py` passes it as args `template` and falls back to `templates/day.exemplar.html` when the file is missing. To promote a better page, change `template` via a decision entry; the exemplar stays the structure gold standard for `tests/test_pages.py`.
