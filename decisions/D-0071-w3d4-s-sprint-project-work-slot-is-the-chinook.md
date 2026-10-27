# D-0071 — W3D4's Sprint / project work slot is the Chinook query activity: the demo repo's activities/week-03-chinook/ carries Chinook v1.4.5 (MIT, unchanged MySQL script) and 26 questions in chinook-questions.sql (one table, aggregates, joins over two to four tables, LEFT JOIN, subqueries, two stretch items) with expected row counts; no sprint runs in week 3 and P0 is handed out in W3D5's slot

- Date: 2026-10-27
- Status: accepted
- Decision: W3D4's Sprint / project work slot is the Chinook query activity: the demo repo's activities/week-03-chinook/ carries Chinook v1.4.5 (MIT, unchanged MySQL script) and 26 questions in chinook-questions.sql (one table, aggregates, joins over two to four tables, LEFT JOIN, subqueries, two stretch items) with expected row counts; no sprint runs in week 3 and P0 is handed out in W3D5's slot
- Why: 07 teaches every clause, function, aggregate, subquery and join on six seeded tickets whose answers the room can count by eye; a never-seen eleven-table data set makes a query right by its shape, using only the syntax 07 typed. The trainer assigns no sprint this week and gives P0's requirements on Friday, so Thursday's slot (which D-0070 had earmarked for P0 R-05 carry-over) is free.
- Affects: demo-repo activities/week-03-chinook/ (README.md, chinook-questions.sql, Chinook_MySql.sql, Chinook-LICENSE.md), demo-repo README.md activities bullet, trainer week-03/day-4 runbook (glance row, sprint slot, long/short lines, 08 pitfall line) and activities/ (chinook-key.sql, chinook-key.md, chinook-key-output.txt, check_key.py), trainer week-03/day-3 runbook (carry-over line), trainer week-03/day-5 runbook (P0 hand-out opens the slot), STATUS.md
- Supersedes: —
- Superseded-by: —

## Notes

Questions and key verified against MySQL 9.7.4 in the desk-mysql container on 2026-10-27 (check_key.py); the learner file is generated from the key with check_key.py --starter. Table names are case sensitive in the Linux container (lower_case_table_names=0); the README and key both say so.
