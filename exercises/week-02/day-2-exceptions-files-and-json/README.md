# Exercise: Ticket store

Week 2 · Day 2 · `w02d2` · ~60–90 min
Notes: [weeks/week-02/day-2-exceptions-files-and-json.html](https://2494-gen-ai-cn.github.io/training/weeks/week-02/day-2-exceptions-files-and-json.html) · Demos: [demos/ticket-desk](https://github.com/2494-Gen-AI-CN/demos/tree/main/ticket-desk)

Both links resolve from the training repo, not from the copy in your own repository. The demo code is the `ticket-desk/` folder of the demo repository; it grows after every class, so reload the page if it looks behind.

## Task

The ticket desk now saves itself to `tickets.json`. Build a small, separate version of that storage layer in `starter/ticketstore.py`, working on plain ticket dicts instead of `Ticket` objects. You save a list of dicts to a JSON file (dates become ISO text on the way out and datetimes again on the way in), load them back, treat a missing file as an empty list, turn a corrupt file into a `ValueError` that keeps the original error as its cause, append one ticket to a file that may not exist yet, and delete a file without crashing when it is already gone. Each docstring states the exact behaviour, so read it before you write the body.

## Acceptance criteria

- [ ] `test_round_trip_restores_the_same_tickets`: what `load_tickets` returns equals what `save_tickets` was given, datetimes included.
- [ ] `test_dates_are_written_as_iso_text_and_none_as_null`: the file holds `"2026-10-20T09:00:00"` and `null`, not Python reprs.
- [ ] `test_save_does_not_change_the_dicts_passed_in`: saving leaves the caller's datetimes as datetimes.
- [ ] `test_save_replaces_an_existing_file`: a second save overwrites the first.
- [ ] `test_missing_file_gives_empty_list_and_is_not_created`: loading never creates the file.
- [ ] `test_corrupt_file_raises_value_error_chained_to_decode_error`: `ValueError` with "is not valid JSON", and `__cause__` is the `JSONDecodeError`.
- [ ] `test_append_creates_the_file_then_adds`: append works on a missing file and keeps order.
- [ ] `test_append_to_corrupt_file_raises_and_leaves_it_alone`: the bad file is not overwritten.
- [ ] `test_delete_file_returns_true_then_false`: `True` when it existed, `False` when not, no exception.
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-02/day-2-exceptions-files-and-json
cp -r exercises/week-02/day-2-exceptions-files-and-json/* ../<FirstnameLastname>/week-02/day-2-exceptions-files-and-json/
cd ../<FirstnameLastname>/week-02/day-2-exceptions-files-and-json
python -m pytest -q          # everything fails until you implement starter/ticketstore.py
```

If the folder already exists (you ran these lines before), skip the `mkdir` line: in Windows PowerShell, `mkdir` stops with an error for a folder that is already there.

Implement the functions in `starter/ticketstore.py` (each has a docstring and currently raises `NotImplementedError`). Start with `save_tickets` and `load_tickets`; `append_ticket` is short once those work.

If you ran pytest inside the training clone before copying, the copy can bring `__pycache__/` and `.pytest_cache/` folders with it, and pytest creates them again in your copy. Do not commit them: check `git status` before your first commit and make sure your `.gitignore` covers both.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-02/day-2-exceptions-files-and-json/` there.

## Hints

- `json.dump` cannot write a `datetime`. Build a new list of copied dicts (`dict(ticket)`) and convert the two date keys in the copies.
- `datetime.isoformat()` makes the text and `datetime.fromisoformat()` reverses it. `None` needs no conversion.
- `open(path)` on a missing file raises `FileNotFoundError`; catch exactly that, not a bare `except:`.
- `json.JSONDecodeError` is a kind of `ValueError`, so a plain `ValueError` check would pass without the chain. Use `raise ValueError(...) from err` to keep the cause.
- `append_ticket` can reuse `load_tickets` and `save_tickets`; the corrupt-file case then needs no extra code, because the error is raised before anything is written.
- `Path(path).unlink()` raises `FileNotFoundError` when the file is gone; catching it is safer than asking `exists()` first.
