# Exercise — Ticket summary helpers

Week 1 · Day 3 · `w01d3` · ~60–90 min
Notes: [docs/weeks/week-01/day-3-python-basics.html](../../../docs/weeks/week-01/day-3-python-basics.html) · Demos: [demos/week-01/day-3-python-basics](../../../demos/week-01/day-3-python-basics)

## Task

The ticket desk from today's demos keeps its rules inline in one script, where nobody can test them. A team would pull them into small helpers with a test beside each one, and that is the job here: implement the ten functions in `starter/ticket_summary.py`. Six of them are the day's operators (`//`, `-`, `and`, `or`, `==`, `%`, a chained comparison), one rounds a percentage with `/`, `*` and `round`, one returns an aligned f-string, and two print: a board on stdout built with `print`'s `sep` and `end`, and a warning on stderr. The tests compare output character for character, so the column widths in the docstrings are the specification. Write it the way the team's contract says: PEP 8 throughout, and comments that earn their place, which means at least one comment that gives a reason the code cannot show and none that restates the line under it. Stay inside today's material: no `input()`, no lists or dicts, no string methods, no loops.

Suggested time-box: 10 min set-up and reading the docstrings · 20 min the six operator helpers · 10 min `sla_used_percent` and `summary_line` · 25 min `print_board` and `warn_breach` · 15 min PEP 8 pass, comments, commits and push.

## Acceptance criteria

Checked by pytest, one line per test:

- [ ] `test_age_days_is_floor_division`: `age_days` returns whole days
- [ ] `test_hours_left_goes_negative_when_late`: `hours_left` returns SLA hours minus hours open
- [ ] `test_is_breached_open_and_late`: `is_breached` is `True` only for an open ticket with hours left below zero; exactly zero left, or a closed ticket, gives `False`
- [ ] `test_priority_ok_accepts_three_values_and_rejects_other_text`: `high`, `normal`, `low` give `True`; anything else gives exactly `False`
- [ ] `test_is_first_day_bounds`: `0 <= hours_open < 24` as one chained comparison
- [ ] `test_escalate_every_third_id`: ids divisible by 3 escalate
- [ ] `test_sla_used_percent_rounds_to_one_decimal`: `sla_used_percent` returns a float rounded to one decimal with `round`
- [ ] `test_summary_line_alignment_and_long_title`: title `<20`, priority `>8`, hours `>6.1f`; a long title is kept whole
- [ ] `test_print_board_header_and_row_on_stdout`: `print_board` prints the header and the row to stdout, columns joined by ` | `, each line closed by ` |`, and returns `None`
- [ ] `test_warn_breach_writes_one_line_to_stderr_only`: `warn_breach` prints its one line to stderr and nothing to stdout
- [ ] All tests pass: `python -m pytest -q`

Read by the trainer in your repository (pytest cannot check these):

- [ ] Comments: at least one comment says why, none restates the code, and the starter's docstrings are still there
- [ ] PEP 8: `import sys` sits right under the module docstring, `24` is named once as an UPPER_CASE constant, names are snake_case, functions are two blank lines apart, no line is over 79 columns
- [ ] `print_board` uses `sep` and `end` instead of typing the separators into the strings
- [ ] History: at least three commits, each with an imperative subject line that says what changed

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-01/day-3-python-basics
cp -r exercises/week-01/day-3-python-basics/* ../<FirstnameLastname>/week-01/day-3-python-basics/
cd ../<FirstnameLastname>/week-01/day-3-python-basics
python -m pytest -q          # everything fails until you implement starter/ticket_summary.py
```

Implement the functions in `starter/ticket_summary.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-01/day-3-python-basics/` there.

## Hints

- `is_breached` can call `hours_left` instead of repeating the subtraction, and `warn_breach` can call both.
- Write `priority_ok` with three full `==` comparisons joined by `or`. `or` returns one of its operands, so `priority == "high" or "normal"` hands back the string `"normal"` for any other text, and the test asks for the bool `False`.
- In an f-string the format spec follows a colon: `{title:<20}` pads on the right, `{hours_open:>6.1f}` right-aligns with one decimal. A literal takes a spec too: `{'Title':<20}`.
- `print` puts `sep` between its arguments and `end` after the last one, so pass each column as its own argument. An `end` of your own replaces the newline; it has to bring its own `\n`.
- `print(..., file=sys.stderr)` needs `import sys`, and PEP 8 puts imports at the top of the file, under the module docstring.
- A failing string comparison shows both strings one above the other; count the spaces against the widths in the docstring.
- Done early? See the two streams split. From the `starter` folder run the line below: the board appears on screen and only the warning lands in `err.txt` (Windows PowerShell wraps it in a few lines of its own). Delete `err.txt` afterwards; it is not part of the hand-in.

```
python -c "import ticket_summary as ts; ts.print_board(101, 'Login bug', 'high', 5.5, 4); ts.warn_breach(101, True, 4, 5.5)" 2> err.txt
```
