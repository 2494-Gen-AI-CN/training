# Exercise — Ticket data helpers

Week 1 · Day 4 · `w01d4` · ~60–90 min
Notes: [docs/weeks/week-01/day-4-python-data-types.html](../../../docs/weeks/week-01/day-4-python-data-types.html) · Demos: [demos/week-01/day-4-python-data-types](../../../demos/week-01/day-4-python-data-types)

Both links resolve from the training repo, not from the copy in your own repository. The demos folder is added there after the class, so `git pull` the training repo if a link does not open yet.

## Task

Today's demos grew the ticket desk from text cleanup to a tuple queue, an SLA lookup table and a datetime clock. Here you package those ideas as small, tested functions in `starter/ticket_data.py`: normalise a ticket title, turn typed text into an `int`, build the queue as tuples without touching the caller's list, collect reporters in a set, look up SLA hours from a dict, and compute a deadline with `timedelta`. Each function is a few lines; the point is choosing the right type and avoiding the pitfalls from the demos.

## Acceptance criteria

- [ ] `test_normalise_title_strips_whitespace`: surrounding whitespace is removed
- [ ] `test_normalise_title_cuts_to_limit`: the result is at most `limit` characters, stripped before cutting
- [ ] `test_parse_ticket_id_returns_int`: `" 101 "` becomes the `int` 101
- [ ] `test_parse_ticket_id_rejects_non_integers`: `"3.5"`, `"abc"` and `""` raise `ValueError`
- [ ] `test_build_queue_sorts_by_rank_then_id`: the queue sorts by tuple order
- [ ] `test_build_queue_returns_new_list_and_keeps_input`: the input list is not modified
- [ ] `test_unique_reporters_is_a_normalised_set`: a set of stripped, lower-cased names
- [ ] `test_sla_hours_lookup_and_fallback`: dict lookup, case-insensitive, unknown falls back to `normal`
- [ ] `test_deadline_for_adds_sla_hours`: `opened_at` plus a `timedelta` of the SLA hours
- [ ] `test_is_breached_is_strictly_after_deadline`: `True` only when `now` is after the deadline
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-01/day-4-python-data-types
cp -r exercises/week-01/day-4-python-data-types/* ../<FirstnameLastname>/week-01/day-4-python-data-types/
cd ../<FirstnameLastname>/week-01/day-4-python-data-types
python -m pytest -q          # everything fails until you implement starter/ticket_data.py
```

Implement the functions in `starter/ticket_data.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go.

If you ran pytest inside the training clone before copying, the copy can bring `__pycache__/` and `.pytest_cache/` folders with it, and pytest creates them again in your copy. Do not commit them. The `.gitignore` you wrote on Tuesday already covers `__pycache__/` and `*.pyc`; check `git status` before your first commit and add `.pytest_cache/` to that `.gitignore` if the folder shows up.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-01/day-4-python-data-types/` there.

## Hints

- Strings are immutable: `strip()` and slicing return new strings, so use the returned value.
- `int()` already raises `ValueError` for `"3.5"`; you do not need to check the text yourself.
- `sorted()` returns a new list and leaves its argument alone; `list.sort()` does the opposite and returns `None`.
- Today's demos built a set with a literal and `.add`. A set comprehension builds it in one line: `{w.lower() for w in words}` computes the expression before `for` once per item and keeps the distinct results.
- `dict.get(key, default)` gives you the fallback without a `KeyError`.
- Adding a `timedelta(hours=n)` to a `datetime` gives a later `datetime`.
