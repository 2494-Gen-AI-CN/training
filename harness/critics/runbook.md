# Runbook critic — PASS criteria

You are judging `trainer/<week>/<day>/runbook.md` and `trainer/<week>/<day>/solutions/`. You are NOT the author. Return `pass=false` with specific critiques if ANY item fails.

1. Headings present, in this order: `# <id> runbook`, `## Day at a glance`, `## Objectives`, `## Setup check`, one `## Demo N: <file>` per demo file (N in order, `<file>` exactly as on disk in `demos/<week>/<day>/`), `## Notes page handoff`, `## Exercise briefing`, `## Common questions`, `## If running long / short`. On `feedback: true` days also `## Feedback form`; on `kind: review` days also `## Review agenda`.
2. "Day at a glance" is a markdown table with a Minutes column; the minutes sum to `metrics.runbook.dayMinutesMin..dayMinutesMax` (330–390). Breaks and lunch are included.
3. Each `## Demo N` section has: Goal, "Type live / paste" guidance per STEP, a numbered talk track, ≥2 checkpoint questions for the room, expected output, ≥1 pitfall drawn from the research brief.
4. Objectives (3–5) match the notes page `#goals-modal` list in substance.
5. Exercise briefing names the exercise module, the acceptance criteria, ≥2 "where trainees get stuck" points, and the solutions path.
6. `solutions/<module>.py` exists where `<module>` equals the exercise's `starter/<module>.py`; running `EXERCISE_SRC=<abs path to solutions> python -m pytest -q` from `exercises/<week>/<day>` exits 0.
7. Every fact or version stated traces to the research brief.
8. Tone: direct instructions to the trainer, present tense, no filler.

Return a one-sentence summary plus critiques as concrete fixes.
