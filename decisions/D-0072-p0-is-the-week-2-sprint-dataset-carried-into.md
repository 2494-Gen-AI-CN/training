# D-0072 — P0 is the week-2 sprint dataset carried into the week-4 technologies: same pairs, a client and business case the pair invents, a star schema with one SCD type 2 dimension, a Python ETL job into the free BigQuery sandbox, pytest on the transforms, five BigQuery queries and one chart; no Gen AI requirement; official projects hand in under projects/P<n>/ and sprints under week-NN/hackathon/

- Date: 2026-10-28
- Status: accepted
- Decision: P0 is the week-2 sprint dataset carried into the week-4 technologies: same pairs, a client and business case the pair invents, a star schema with one SCD type 2 dimension, a Python ETL job into the free BigQuery sandbox, pytest on the transforms, five BigQuery queries and one chart; no Gen AI requirement; official projects hand in under projects/P<n>/ and sprints under week-NN/hackathon/
- Why: The ticket-desk draft borrowed the demo thread and spread P0 over weeks 1 to 5 with an LLM feature. The trainer wants P0 to be the sprint plus the data week: the pair already owns a 100k-row dataset from the mini-sprint, week 4 teaches cloud concepts, warehousing, BigQuery, dimensional modelling and ETL, and the showcase audience is technical and non-technical managers, so every requirement serves a business question the pair frames. The hand-in path conflict (projects/P0/ in the draft versus week-NN/hackathon/ in D-0051 and D-0068) is settled the same way: official projects own a projects/P<n>/ folder, sprints stay in the week folder.
- Affects: projects/official/P0-dataset-to-warehouse.md (renamed from P0-ticket-desk.md, contents replaced, status draft until the Friday flip), docs/projects/, trainer week-03/day-5 runbook (hand-out bullet and room-work bullet), docs/process/projects-plan.md (filename), STATUS.md O-26
- Supersedes: —
- Superseded-by: —

## Notes

Handed out Fri 2026-10-30 in the W3D5 slot (D-0071); the room still finishes the week-3 SQL work in that slot and P0 work starts Monday 2026-11-02. Showcase W5D5 Fri 2026-11-13, fifteen minutes per pair, both speak. Technologies named in the spec: Python 3, pandas, Matplotlib, pytest, SQL, BigQuery sandbox with google-cloud-bigquery, star schema, SCD type 2, ETL in Python. Dropped on the trainer's call: reconciliation with the sprint numbers, a cloud and big-data write-up, a MySQL stage, an AI-tool rule, a stretch list.
