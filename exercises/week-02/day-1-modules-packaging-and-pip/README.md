# Exercise: The desk toolkit module

Week 2 · Day 1 · `w02d1` · ~60–90 min
Notes: [weeks/week-02/day-1-modules-packaging-and-pip.html](https://2494-gen-ai-cn.github.io/training/weeks/week-02/day-1-modules-packaging-and-pip.html) · Demos: [demos/ticket-desk](https://github.com/2494-Gen-AI-CN/demos/tree/main/ticket-desk)

Both links resolve from the training repo, not from the copy in your own repository. The demo code is the `ticket-desk/` folder of the demo repository; it grows after every class, so reload the page if it looks behind.

## Task

The ticket desk went from one file to a module you import. Write a small module of your own, `deskkit.py`, that holds the desk's helper functions: `days_open` rounds the time a ticket has been open up to whole days with `math.ceil`; `is_past_sla` and `check_sla` apply the SLA table and report late tickets through a module-level logger instead of `print`; `ticket_refs` and `redact` use patterns compiled once at module level. Importing the module must print nothing, and running the file directly must print one line, which is what the `__name__` guard is for. Each docstring states the exact behaviour, including the edge cases, so read it before you write the body.

## Acceptance criteria

- [ ] `test_days_open_rounds_up_to_whole_days`: `math.ceil` of the hours open divided by 24; zero hours is 0, exactly 24 hours is 1, one minute more is 2.
- [ ] `test_is_past_sla_is_strict_at_the_deadline`: late only when `now` is after the deadline; exactly on it is not late.
- [ ] `test_module_level_logger_is_named_after_the_module`: `log` is a `logging.Logger` made with `logging.getLogger(__name__)`.
- [ ] `test_check_sla_warns_once_for_a_late_ticket`: one WARNING record, message `TD-7 is past its SLA`, built from a `%s` argument.
- [ ] `test_check_sla_is_silent_when_on_time`: no log record and a return value of `False`.
- [ ] `test_ticket_refs_finds_numbers_in_order`: ints in the order they appear, repeats kept, an empty list when none.
- [ ] `test_ticket_refs_ignores_near_misses`: `XTD-3`, `TD-`, `TD-x` and `TD-4x` do not match; a reference inside brackets does.
- [ ] `test_patterns_are_compiled_at_module_level`: `TICKET_REF` and `EMAIL` are compiled patterns.
- [ ] `test_redact_replaces_every_email`: every address becomes `[email]`.
- [ ] `test_importing_prints_nothing_but_running_the_file_does`: `import deskkit` prints nothing; `python deskkit.py` prints `[2, 5]`.
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-02/day-1-modules-packaging-and-pip
cp -r exercises/week-02/day-1-modules-packaging-and-pip/* ../<FirstnameLastname>/week-02/day-1-modules-packaging-and-pip/
cd ../<FirstnameLastname>/week-02/day-1-modules-packaging-and-pip
python -m pytest -q          # everything fails until you implement starter/deskkit.py
```

Implement the functions in `starter/deskkit.py` (each has a docstring and currently raises `NotImplementedError`). Work top to bottom and run the tests as you go.

Your own repository has no virtual environment yet. If `python -m pytest` reports that pytest is missing, make one in this folder, activate it, and install pytest into it:

```
python -m venv .venv
.venv\Scripts\Activate.ps1        # PowerShell on Windows
source .venv/Scripts/activate     # Git Bash on Windows
source .venv/bin/activate         # macOS
python -m pip install pytest
```

Run only the activate line for your shell. Once it is active, your prompt starts with `(.venv)`.

If you ran pytest inside the training clone before copying, the copy can bring `__pycache__/` and `.pytest_cache/` folders with it, and pytest creates them again in your copy. Do not commit them or the virtual environment: check `git status` before your first commit and make sure your `.gitignore` covers `.venv/`, `__pycache__/` and `.pytest_cache/`.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-02/day-1-modules-packaging-and-pip/` there.

## Hints

- Subtracting one `datetime` from another gives a `timedelta`; its `.total_seconds()` method gives a number you can divide by 3600 for hours.
- `math.ceil(0.0)` is 0 and `math.ceil(1.0)` is 1, so exact multiples need no special case.
- A logging call takes the message and its values separately: `log.warning("... %s ...", value)`. The logger name comes from `__name__`, which is `"deskkit"` when the file is imported.
- `pattern.finditer(text)` yields match objects; `match.group(1)` is the text inside the first parentheses, still a string until you pass it to `int`.
- `\b` inside a normal string is a backspace character. Put an `r` before the opening quote so the regex engine sees the backslash.
- The guard is `if __name__ == "__main__":` followed by a call to `main()`. Without it, importing the file would run `main`.
