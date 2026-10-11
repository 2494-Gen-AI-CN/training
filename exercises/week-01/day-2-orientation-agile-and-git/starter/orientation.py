"""orientation.py - six tiny functions that prove the script / REPL / pytest loop.

Every function below is one to three lines of plain Python: a variable or two,
some arithmetic, some string work, and a `return`. No imports are needed.

Work in a loop:
  1. implement one function here,
  2. run `python -m pytest -q` from the exercise folder,
  3. (optional) run `python -i starter/orientation.py` and call the function at `>>>`.
"""

# The planning-poker scale from demo 03. Relative effort, NOT hours.
STORY_POINT_SCALE = [1, 2, 3, 5, 8, 13]

# Ontario HST, used as the default tax rate (same as demo 01's add_tax).
HST_RATE = 0.13


def greet(name):
    """Build the welcome sentence printed at the top of every cohort script.

    Args:
        name: the person's first name, e.g. "Ana".

    Returns:
        The exact string "Hello, Ana! Welcome to the Gen AI cohort." with the
        given name in place of Ana.
    """
    raise NotImplementedError


def add_tax(price, rate=HST_RATE):
    """Return the price with tax added, rounded to two decimal places.

    Args:
        price: the pre-tax amount as a number, e.g. 100 or 19.99.
        rate: the tax rate as a fraction; defaults to HST_RATE (0.13).

    Returns:
        price * (1 + rate), rounded to 2 decimals, e.g. add_tax(100) -> 113.0.
    """
    raise NotImplementedError


def sprint_window(sprint_number, sprint_weeks=2):
    """Work out which calendar weeks a Sprint covers (demo 02, STEP 3).

    Sprint 1 of a two-week cadence covers weeks 1-2, Sprint 2 covers 3-4, and so on.

    Args:
        sprint_number: 1-based Sprint number, e.g. 3.
        sprint_weeks: length of one Sprint in weeks; defaults to 2.

    Returns:
        A tuple (first_week, last_week), e.g. sprint_window(3) -> (5, 6).
    """
    raise NotImplementedError


def is_story_point(value):
    """Say whether a planning-poker vote is on the team's scale.

    Args:
        value: the number someone voted, e.g. 5 or 4.

    Returns:
        True when value is one of STORY_POINT_SCALE, otherwise False.
    """
    raise NotImplementedError


def branch_name(ticket_id, title):
    """Turn a backlog item into a git branch name like "feature/42-add-hello-script".

    Args:
        ticket_id: the backlog item number, e.g. 42.
        title: the item's title as typed by a human, e.g. "  Add Hello Script ".

    Returns:
        "feature/<ticket_id>-<slug>" where slug is the title with surrounding
        whitespace removed, lower-cased, and every space replaced by a hyphen.
    """
    raise NotImplementedError


def commit_line(full_hash, message):
    """Format one line the way `git log --oneline` prints it.

    Args:
        full_hash: the 40-character commit hash.
        message: the commit message, e.g. "add hello script".

    Returns:
        The first seven characters of the hash, one space, then the message,
        e.g. "a1b2c3d add hello script".
    """
    raise NotImplementedError
