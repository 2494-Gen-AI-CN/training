# D-0069 — Demo repo tracks its PNGs: the ticket-desk ERD lives at ticket-desk/sql/Ticket_Desk_ERD.png and the Matplotlib charts move to ticket-desk/plots/

- Date: 2026-10-26
- Status: accepted
- Decision: Demo repo tracks its PNGs: the ticket-desk ERD lives at ticket-desk/sql/Ticket_Desk_ERD.png and the Matplotlib charts move to ticket-desk/plots/
- Why: Trainer decision after W3D1 (2026-10-26). The ERD the room whiteboarded in 02-desk-schema is now a file the learners can open next to schema.sql, and the week-2 charts (status.png, hours.png) are worth keeping in the public demo repo as the thread's visible output rather than regenerating them. ticket-desk/.gitignore drops the '*.png' line that 09-status-charts added; .venv/, __pycache__/ and board.txt stay ignored.
- Affects: demo-repo ticket-desk/.gitignore, ticket-desk/sql/Ticket_Desk_ERD.png (new), ticket-desk/plots/ (new, holds status.png and hours.png); harness untouched
- Supersedes: —
- Superseded-by: —

## Notes

Classroom-reality change on demo-repo main only; prep/week-03 keeps its own .gitignore with *.png and is not re-authored (D-0055 close rule). Known follow-up for the trainer: ticket_desk.py still writes status.png and hours.png to ticket-desk/ (lines 99-100), so the next run of the script recreates them at the root, now untracked but no longer ignored; point those two calls at plots/ when the chart code is next touched.
