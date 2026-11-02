# D-0081 — 06-etl-job's report reads hours to close from dim_ticket's close times, not the fact's event-stamped rate: the trigger stamps ticket 5's close event when changes.sql runs, so the fact's hours_since_open for it is the log time, not the close; report.sql computes AVG(DATETIME_DIFF(closed_at, opened_at)) per priority (two rows, no low ticket has closed), the chart title states that finding, and the late stamp is one data-quality talking point; load_log is 'one row per run'

- Date: 2026-11-02
- Status: accepted
- Decision: 06-etl-job's report reads hours to close from dim_ticket's close times, not the fact's event-stamped rate: the trigger stamps ticket 5's close event when changes.sql runs, so the fact's hours_since_open for it is the log time, not the close; report.sql computes AVG(DATETIME_DIFF(closed_at, opened_at)) per priority (two rows, no low ticket has closed), the chart title states that finding, and the late stamp is one data-quality talking point; load_log is 'one row per run'
- Why: The D-0080 re-author's critic found the committed chart title false on the demo's own numbers (normal 134.74 h came from one 364 h late-stamped event; by close times normal averages 22.7 h inside its 24 h SLA). Close times are the same on every laptop and keep every Check reproducible; changing changes.sql or the hand-out would re-plan blocks 01 to 06. With two priorities closed any two points give a correlation of exactly 1 or -1, which the talking point says; a pair's 100,000 rows give the number its meaning.
- Affects: harness/plans/week-04.md block row 6 and conventions row 'report from the star'; trainer/week-04/demos/06-etl-job.md Step 11; demo-repo prep/week-04 06 commit
- Supersedes: —
- Superseded-by: —
