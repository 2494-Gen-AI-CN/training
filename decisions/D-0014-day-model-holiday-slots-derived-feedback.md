# D-0014 — Day model: day = weekday slot (1=Mon..5=Fri); a slot on a holiday is kind holiday with no slug or artifacts; the weekly feedback form moves to the last teaching day of the week and is derived, not hand-set

- Date: 2026-10-11
- Status: accepted
- Decision: Day model: day = weekday slot (1=Mon..5=Fri); a slot on a holiday is kind holiday with no slug or artifacts; the weekly feedback form moves to the last teaching day of the week and is derived, not hand-set
- Why: Keeps the Mon-Fri grid and the week-WW/day-N-slug naming (D-0007) stable while holidays become data. A derived feedback flag cannot drift from the holiday list; week 7's feedback day is therefore Wed 11-25.
- Affects: harness/curriculum.json (holiday slots, feedback key removed), harness/build_index.py, harness/args_for.py, harness/workflows/day-fanout.js, harness/templates/runbook.md, tests/test_curriculum.py, tests/test_pages.py
- Supersedes: —
- Superseded-by: —

## Notes

Holiday slot shape: {"day": N, "kind": "holiday"}; the label is looked up from the top-level holidays list so it is stored once. Review days (kind: review) move with the content. Tests assert 5 slots per week, each teaching or holiday, holiday slots exactly match holiday dates, derived dates strictly increase, week 1 starts on startDate and the last teaching day is endDate.
