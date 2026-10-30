# D-0077 — Week-3 hand-over confirmed after W3D5 closed (06, 08, 10 untaught; 05, 07, 09 taught): no re-plan, the W4D3 week-3 catch-up fetches the untaught blocks' files from 61d70bf and also always fetches 09's sql/routines.sql, replacing the room's taught copy

- Date: 2026-10-30
- Status: superseded
- Decision: Week-3 hand-over confirmed after W3D5 closed (06, 08, 10 untaught; 05, 07, 09 taught): no re-plan, the W4D3 week-3 catch-up fetches the untaught blocks' files from 61d70bf and also always fetches 09's sql/routines.sql, replacing the room's taught copy
- Why: W3D5 closed 2026-10-30 with 06 untaught (week 3 stayed pure SQL), which the week-4 plan's catch-up row says triggers a counts re-check and a decision either way. The room's schema.sql matches 61d70bf apart from comments and its seed.sql holds the same six tickets and tags (names and three agents already handled), so the hand-over stands. But 01's rebuild pipes sql/routines.sql, and the room typed it as a working file (no USE, demo SELECTs and EXPLAINs, SHOW TRIGGERS, an UPDATE of ticket 5, CALLs of log_event and close_ticket) that would shift the event rows and ticket states 01's Checks expect; fetching the plan's version (trainer chose this over skipping the file in the rebuild) keeps the rebuild clean, and the room's copy stays in demo-repo history at 849382b.
- Affects: harness/plans/week-04.md (Assumes bullet, 01-desk-extract Step 1, Conventions row week-3 catch-up, risk line, deviation row), STATUS.md (O-28, Phase line)
- Supersedes: —
- Superseded-by: D-0078
