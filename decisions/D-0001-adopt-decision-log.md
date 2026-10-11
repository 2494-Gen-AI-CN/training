# D-0001 — Adopt an append-only decision log in decisions/

- Date: 2026-10-11
- Status: accepted
- Decision: Adopt an append-only decision log in decisions/
- Why: No changelog/ADR existed; only git history, AGENTS.md rules and harness-walkthrough.html (a snapshot). Later sessions and agents need to trace why things are the way they are and never redo or undo prior work.
- Affects: decisions/, AGENTS.md, harness/README.md, harness-walkthrough.html, tests/test_decisions.py
- Supersedes: —
- Superseded-by: —

## Notes

One Markdown file per entry, newest-first index in decisions/README.md, stable IDs D-NNNN, statuses proposed | accepted | superseded. Minted with decisions/new.py. Contract-tested by tests/test_decisions.py. Rule in AGENTS.md: read the index at session start; any change to curriculum.json, metrics.json, config.json, critic specs or the calendar needs an entry whose ID goes in the commit message.
