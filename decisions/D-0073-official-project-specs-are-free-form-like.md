# D-0073 — Official project specs are free-form like sprint sheets: no required sections, R-nn numbering only when a spec has a Requirements section, checkpoints rendered in the At a glance table; the seven-section rule of D-0065 is withdrawn and P0 becomes a two-week mini-sprint page

- Date: 2026-10-28
- Status: accepted
- Decision: Official project specs are free-form like sprint sheets: no required sections, R-nn numbering only when a spec has a Requirements section, checkpoints rendered in the At a glance table; the seven-section rule of D-0065 is withdrawn and P0 becomes a two-week mini-sprint page
- Why: Thirteen numbered requirements, a nine-row rubric and seven mandatory sections made P0 read as a specification. The trainer wants it to read like the week-2 mini-sprint sheet: one page, short bullets, a two-week sprint feel. The weight came from build_projects.py forcing the seven sections and R-nn bullets on kind: official while sprints were free-form, so the harness rule goes rather than the content. kind: official stays for the projects/P<n>/ hand-in, the checkpoint calendar mark and the draft to published flip.
- Affects: harness/build_projects.py (validator, renderer, CSS), tests/test_projects.py, projects/README.md, projects/official/P0-dataset-to-warehouse.md, docs/projects/, docs/process/projects-plan.md, trainer week-03/day-5 runbook, decisions/D-0072 notes, STATUS.md O-26
- Supersedes: —
- Superseded-by: —

## Notes

P0 body: lead paragraph, Dataset, Build (ingest, warehouse, analyse and tell), Rules, Presentation, Hand-in, What we look for; about sixty lines; pytest on the transforms with no coverage figure; silent on AI tools; all D-0072 content and dates unchanged (showcase Fri 13 Nov 2026, fifteen minutes per pair, findings first, flip to published Fri 30 Oct).
