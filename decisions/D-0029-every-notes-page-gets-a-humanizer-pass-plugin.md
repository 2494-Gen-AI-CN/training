# D-0029 — Every notes page gets a humanizer pass (plugin skill humanizer:humanizer, file mode, prose only) after the notes author and before the notes critic; notes critic item 18 fails AI-sounding prose; hand-edited notes prose gets the same pass before commit

- Date: 2026-10-11
- Status: accepted
- Decision: Every notes page gets a humanizer pass (plugin skill humanizer:humanizer, file mode, prose only) after the notes author and before the notes critic; notes critic item 18 fails AI-sounding prose; hand-edited notes prose gets the same pass before commit
- Why: Trainer installed the Humanizer skill (github.com/blader/humanizer) and wants every notes page to read as written by a person: no not-X-but-Y contrasts, one-line closers, forced triads, dash-joined sentences, bold labels or stock AI words. The pass is placed before the critic so the critic re-verifies facts, word band and counts after the rewrite.
- Affects: harness/workflows/day-fanout.js (humanize() after notes author), harness/config.json models.stages.humanize, harness/critics/notes.md item 18, AGENTS.md, docs/weeks/week-01/day-2-orientation-agile-and-git.html (retro pass)
- Supersedes: —
- Superseded-by: —

## Notes

The skill's file mode keeps code blocks, inline code, paths, numbers and link targets unchanged; the humanize agent is told to re-run the notes critic word-count snippet and restore cut sentences rather than invent if the band is broken.
