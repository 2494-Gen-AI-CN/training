# D-0021 — W1D2 exercise shape: a tiny Python-orientation exercise (variables, arithmetic, strings, simple functions; stdlib only, no git); git practice happens live in the demos; pytest contract kept

- Date: 2026-10-11
- Status: superseded
- Decision: W1D2 exercise shape: a tiny Python-orientation exercise (variables, arithmetic, strings, simple functions; stdlib only, no git); git practice happens live in the demos; pytest contract kept
- Why: O-1: a pytest exercise on an orientation/git day is awkward. Options weighed: parse a git-log fixture, subprocess real git, tiny Python-basics, skip the exercise. Chose tiny Python-basics so the exercise contract (starter fails / solution passes) holds from day one and trainees meet the pytest loop before Wednesday; the cost is a small pre-teach of day 3 content, limited to what the 'Python orientation' and 'REPL and Jupyter' subtopics already imply. Carried as a day-level notes field in curriculum.json; args_for.py passes day notes and day-fanout.js prints them in every author/critic prompt as 'Day note'.
- Affects: harness/curriculum.json week 1 day 2 (notes), harness/args_for.py (day notes passthrough), harness/workflows/day-fanout.js dayHeader, exercises/week-01/day-2-orientation-agile-and-git, trainer/week-01/day-2-orientation-agile-and-git/solutions
- Supersedes: —
- Superseded-by: D-0025

## Notes

Critic rule 8 in harness/critics/exercise.md ('exercises THIS day's subtopics') is satisfied via the Python orientation subtopic; critics read the day note and must not demand a git-based exercise. Rejected: git-log fixture (teaches parsing, not git), subprocess git (needs git on PATH, slower), skipping (breaks the five-artifact contract on the pilot day).
