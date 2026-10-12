# Exercise: Help desk classes

Week 1 · Day 5 · `w01d5` · ~60–90 min
Notes: [docs/weeks/week-01/day-5-control-flow-functions-and-classes.html](../../../docs/weeks/week-01/day-5-control-flow-functions-and-classes.html) · Demos: [demos/week-01/day-5-control-flow-functions-and-classes](../../../demos/week-01/day-5-control-flow-functions-and-classes)

Both links resolve from the training repo, not from the copy in your own repository. The demos folder is added there after the class, so `git pull` the training repo if a link does not open yet.

## Task

Today's demos turned a ticket dict into a `Ticket` class and wrapped the queue in a `Desk`. Build your own version from the starter in `starter/helpdesk.py`, then take it further than the demo did. The part you have seen: a `Ticket` with a deadline method, an `UrgentTicket` subclass that overrides it, and a `Desk` you can loop over. The part that is new: a `status` function with four outcomes written as guard clauses, a priority sort that leaves the desk's own order alone, an `overdue` list that ignores closed tickets, a `count_by_status` tally, and an `open_ticket` method that numbers new tickets from one counter shared by every desk. Each docstring states the exact behaviour, including the edge cases, so read it before you write the body.

## Acceptance criteria

- [ ] `test_ticket_deadline_uses_priority_sla`: `deadline()` adds the SLA hours for the ticket's priority.
- [ ] `test_ticket_starts_open_and_close_works`: the four constructor arguments are stored as attributes, `is_open` starts True and `close()` sets it False.
- [ ] `test_urgent_ticket_halves_the_time`: `UrgentTicket` is a `Ticket` and its deadline is half the normal window.
- [ ] `test_desk_len_and_for_loop_keep_insertion_order`: `len(desk)` and `for t in desk` work, more than once.
- [ ] `test_desk_supports_manual_iter_and_next`: `iter(desk)` and `next(...)` step through the tickets, and a second iterator starts from the first ticket again.
- [ ] `test_by_priority_sorts_rank_then_opened_at_without_mutating`: a sorted copy made with a lambda key; the desk's own order is unchanged.
- [ ] `test_overdue_skips_closed_and_on_time_tickets`: only open tickets past their deadline, in the order they were added; a ticket exactly at its deadline is not overdue.
- [ ] `test_status_covers_all_four_outcomes`: closed, breached, at risk and on time, including a ticket exactly at its deadline (at risk) and one with exactly 2 hours left (on time).
- [ ] `test_open_ticket_numbers_from_the_shared_class_counter`: `open_ticket` numbers tickets from the class attribute `Desk.next_id`, shared by every desk; `urgent=True` builds an `UrgentTicket`; `add` keeps the counter ahead of the ids it sees.
- [ ] `test_count_by_status_tallies_every_label`: a dict with all four labels as keys, zeros included.
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-01/day-5-control-flow-functions-and-classes
cp -r exercises/week-01/day-5-control-flow-functions-and-classes/* ../<FirstnameLastname>/week-01/day-5-control-flow-functions-and-classes/
cd ../<FirstnameLastname>/week-01/day-5-control-flow-functions-and-classes
python -m pytest -q          # everything fails until you implement starter/helpdesk.py
```

Implement the classes and the function in `starter/helpdesk.py` (each method has a docstring and currently raises `NotImplementedError`). Work top to bottom and run the tests as you go: the `Ticket` tests pass before you touch `Desk`.

If you ran pytest inside the training clone before copying, the copy can bring `__pycache__/` and `.pytest_cache/` folders with it, and pytest creates them again in your copy. Do not commit them: check `git status` before your first commit and make sure your `.gitignore` covers both.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-01/day-5-control-flow-functions-and-classes/` there.

## Hints

- Subtracting one `datetime` from another gives a `timedelta`, and a `timedelta` can be divided by a number.
- A list already knows how to produce an iterator; `Desk` does not need a `__next__` of its own.
- When a sort needs two criteria, the key function can return a tuple. Tuples compare item by item, the way Thursday's queue did.
- A guard clause deals with one case and returns at once, so nothing below it needs indenting for that case. If your `status` has an `else`, it has one more level than it needs.
- If two desks hand out the same id, look at where your assignment to `next_id` lands: compare `vars(desk)` with `vars(Desk)`.
- `count_by_status` must report a label even when no ticket has it, so the keys cannot come from the tickets alone.
