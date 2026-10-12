# D-0036 — The work tracker is local-only (amends D-0035, the rest stands): tracker.html at the repo root is gitignored and no longer tracked, so trainees browsing the public repo do not see it; its hand-written, data-free shell is the committed template harness/templates/tracker.html and harness/build_tracker.py generates tracker.html from that shell plus the data block; the staleness test compares the local file when it exists and skips on a machine that has not built it

- Date: 2026-10-12
- Status: accepted
- Decision: The work tracker is local-only (amends D-0035, the rest stands): tracker.html at the repo root is gitignored and no longer tracked, so trainees browsing the public repo do not see it; its hand-written, data-free shell is the committed template harness/templates/tracker.html and harness/build_tracker.py generates tracker.html from that shell plus the data block; the staleness test compares the local file when it exists and skips on a machine that has not built it
- Why: The repository is public and trainees read it; the tracker shows authoring progress, alarms and run quality the trainer wants to keep to themselves. The page is only ever opened from the trainer's disk, so nothing needs it in git. A committed template keeps the page reproducible on any machine with trainer/ cloned, without committing data
- Affects: .gitignore (/tracker.html), tracker.html (untracked going forward), harness/templates/tracker.html (new, the shell), harness/build_tracker.py (TEMPLATE, expected(), build creates the file), decisions/new.py (rebuild guard), tests/test_tracker.py (local-only test, staleness test skips when the file is absent, page tests read the template), tests/test_decisions.py (citation scope), AGENTS.md, harness/README.md, docs/process/codify-plan.md, STATUS.md
- Supersedes: —
- Superseded-by: —

## Notes

History is not rewritten: tracker.html was pushed once in commit d8c7bcd (D-0035) and stays readable there; this applies going forward, by the trainer's choice. Still public and unchanged: STATUS.md, harness/runs.jsonl, harness/last-tests.json, harness/plans/ and decisions/, which carry the same facts in raw form; hiding those would be a separate decision (moving them to the private trainer repo). tests/test_tracker.py asserts .gitignore keeps /tracker.html, git does not track it, and the template's data block is empty.
