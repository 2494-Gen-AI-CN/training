# Exercise — Orientation, Agile & Git fundamentals

Week 1 · Day 2 · `w01d2` · Tue 2026-10-13 · ~60–90 min
Notes: [docs/weeks/week-01/day-2-orientation-agile-and-git.html](../../../docs/weeks/week-01/day-2-orientation-agile-and-git.html) · Demos: [demos/week-01/day-2-orientation-agile-and-git](../../../demos/week-01/day-2-orientation-agile-and-git)

## Task

Today's goal is the **workflow**, not the code: edit a script, run it, poke at it in the REPL, and let pytest tell you what is still missing. `starter/orientation.py` holds six tiny functions, each one to three lines of plain Python (a variable, some arithmetic, some string work, a `return`). They reuse the day's own vocabulary — the welcome line and `add_tax` from demo 01, Sprint weeks from demo 02, the planning-poker scale from demo 03, and a git branch name and a `git log --oneline` line from demo 04 — so nothing here is new; you are just writing it yourself. The git commands themselves are practised live after demos 04 and 05 in PowerShell; this exercise is standard library only, no git, no files, no classes.

## Acceptance criteria

- [ ] `test_greet_builds_welcome_sentence` — `greet("Ana")` returns exactly `Hello, Ana! Welcome to the Gen AI cohort.`
- [ ] `test_add_tax_uses_hst_by_default` — `add_tax(100)` is `113.0` (13% HST, rounded to 2 decimals)
- [ ] `test_add_tax_accepts_a_custom_rate` — `add_tax(200, 0.05)` is `210.0`
- [ ] `test_sprint_window_returns_first_and_last_week` — `sprint_window(3)` is `(5, 6)`; `sprint_window(2, sprint_weeks=3)` is `(4, 6)`
- [ ] `test_is_story_point_accepts_only_scale_values` — `True` for 1, 2, 3, 5, 8, 13 and `False` for anything else (4, 0, ...)
- [ ] `test_branch_name_slugs_title_for_git` — `branch_name(42, "Add hello script")` is `feature/42-add-hello-script`; extra spaces around the title are trimmed
- [ ] `test_commit_line_shortens_hash_to_seven_chars` — first seven characters of the hash, one space, then the message
- [ ] All tests pass: `python -m pytest -q`

## Getting started

```
cd exercises/week-01/day-2-orientation-agile-and-git
python -m pytest -q          # everything fails until you implement starter/orientation.py
```

Implement the functions in `starter/orientation.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go: implement `greet`, run pytest, watch one test turn green, move on.

Between runs, try the REPL loop from demo 01:

```
python -i starter/orientation.py
>>> greet("Ana")
>>> add_tax(100)
>>> exit()
```

`python -i` runs the file and then leaves you at the `>>>` prompt with every function defined, so you can call them by hand before pytest does. (Shell commands such as `python -m pytest` do not work at `>>>` — type `exit()` first.)

## Hints

- `greet`: an f-string puts a variable inside text: `f"Hello, {name}!"`. The test compares the whole sentence, so copy the punctuation from the docstring exactly.
- `add_tax`: `round(x, 2)` keeps two decimals. `rate` already has a default value in the signature, so you do not need an `if`.
- `sprint_window`: the last week is `sprint_number * sprint_weeks`; the first week is `sprint_weeks - 1` before that. Return both with `return first, last` — Python packs them into a tuple for you.
- `is_story_point`: `value in STORY_POINT_SCALE` is already `True` or `False`; return it directly.
- `branch_name`: chain string methods — `.strip()` removes the surrounding spaces, `.lower()` lower-cases, `.replace(" ", "-")` swaps every space for a hyphen.
- `commit_line`: slicing `full_hash[:7]` takes the first seven characters; join pieces with `+` or an f-string.
- Reading a failure: pytest prints `assert 'what you returned' == 'what was expected'` — the difference between the two sides is the bug.
