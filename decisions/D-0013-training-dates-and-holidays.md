# D-0013 — Training runs Tue 2026-10-13 to Thu 2026-12-24 (America/Toronto); blocked days are 10-12 Thanksgiving CA, 11-26 and 11-27 US Thanksgiving, 12-25 Christmas; 11-11 Remembrance Day is NOT blocked

- Date: 2026-10-11
- Status: accepted
- Decision: Training runs Tue 2026-10-13 to Thu 2026-12-24 (America/Toronto); blocked days are 10-12 Thanksgiving CA, 11-26 and 11-27 US Thanksgiving, 12-25 Christmas; 11-11 Remembrance Day is NOT blocked
- Why: Trainer wrote the end date as 10/24/26, a typo for 12/24/26 (11 weeks from Oct 13 lands on the week of Dec 21-25); confirmed with the trainer. Delivered in Canada by a US-based trainer, so both countries' Thanksgivings block. Remembrance Day is a normal teaching day; Christmas Day is blocked by default.
- Affects: harness/curriculum.json (startDate, endDate, timezone, holidays), harness/build_index.py, docs/index.html, harness/args_for.py, README.md, weeks 1, 7, 11
- Supersedes: —
- Superseded-by: —

## Notes

Every calendar date is derived from startDate + week index + weekday slot in harness/build_index.py. Never hand-type a date into a page, prompt or template; change startDate or holidays and rebuild. Teaching days: week 1 = 4 (Tue-Fri), week 7 = 3 (Mon-Wed), week 11 = 4 (Mon-Thu), all others 5; 51 days total.
