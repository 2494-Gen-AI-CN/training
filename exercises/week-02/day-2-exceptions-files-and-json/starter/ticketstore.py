"""Save and load help-desk tickets as a JSON file.

A ticket is a plain dict such as
{"ticket_id": 1, "title": "Reset password", "priority": "high",
 "opened_at": datetime(2026, 10, 20, 9, 0), "closed_at": None}.
The keys "opened_at" and "closed_at" hold a datetime or None in memory and
ISO 8601 text or null in the file.
"""
# The three imports below are used by your implementation. Until you write
# the bodies, pylint reports them as unused imports (W0611); that is expected.
from datetime import datetime
from pathlib import Path
import json

DATE_KEYS = ("opened_at", "closed_at")


def save_tickets(tickets, path):
    """Write the list of ticket dicts to `path` as JSON, indent=2, UTF-8.

    Every datetime under a key in DATE_KEYS is written as its isoformat()
    text; None stays None (JSON null). The dicts passed in are not changed.
    An existing file is replaced.

    Args:
        tickets (list[dict]): ticket dicts whose DATE_KEYS hold a datetime
            or None.
        path (str | Path): file to write.

    Returns:
        None.
    """
    raise NotImplementedError


def load_tickets(path):
    """Return the list of ticket dicts stored in `path`.

    Text under a key in DATE_KEYS becomes a datetime again; null stays None.
    A missing file gives an empty list (and is not created). A file that is
    not valid JSON raises ValueError(f"{path} is not valid JSON"), chained
    from the original json.JSONDecodeError (use `raise ... from err`).

    Args:
        path (str | Path): file to read.

    Returns:
        list[dict]: the tickets with dates as datetime ([] for a missing
        file).

    Raises:
        ValueError: chained from json.JSONDecodeError when the file is not
            valid JSON.
    """
    raise NotImplementedError


def append_ticket(path, ticket):
    """Add one ticket dict to the tickets stored in `path` and save them all.

    Works when the file does not exist yet (it is created). A corrupt file
    raises the same ValueError as load_tickets and is left untouched.

    Args:
        path (str | Path): file holding the tickets.
        ticket (dict): the ticket to add at the end of the list.

    Returns:
        None.

    Raises:
        ValueError: for a corrupt file, which is left untouched.
    """
    raise NotImplementedError


def delete_file(path):
    """Delete the file at `path`; return True if it existed, False if not.

    Never raises for a missing file. Use pathlib, not a check-then-delete.

    Args:
        path (str | Path): file to delete.

    Returns:
        bool: True if the file existed and was deleted, False if it was
        missing.
    """
    raise NotImplementedError
