# D-0067 — Week-3 practice tasks are SQL only: the reader writes one SQL statement in the page, run by sqlite3 in memory inside the existing Python task widget (D-0062's documented fallback); no Python-function tasks on a SQL day; a step whose SQL does not run unchanged on SQLite 3.39 stays none until ix-sql lands

- Date: 2026-10-23
- Status: accepted
- Decision: Week-3 practice tasks are SQL only: the reader writes one SQL statement in the page, run by sqlite3 in memory inside the existing Python task widget (D-0062's documented fallback); no Python-function tasks on a SQL day; a step whose SQL does not run unchanged on SQLite 3.39 stays none until ix-sql lands
- Why: The week-3 suitability pass (wf_a45b30b5-d84) proposed three Python helper functions and ruled every SQL step out because harness/critics/practice.md said Pyodide has no sqlite3, a line O-23 measured as stale on 2026-10-17; the ix-sql widget (D-0062 S0-S2, due 2026-10-22) was not built. The trainer's call on 2026-10-23: no Python in these tasks, only SQL, so the critic's runtime section now names sqlite3 as present and defines the SQL task shape (starter = QUERY string, checks seed and read rows), and the three Python proposals were declined.
- Affects: harness/critics/practice.md (runtime, SQL days section), harness/practice/week-03/*.json, STATUS.md O-17 and O-23
- Supersedes: —
- Superseded-by: —
