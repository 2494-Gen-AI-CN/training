"""Small helpers for the ticket desk: days open, SLA checks and ticket references."""
import logging
import math
import re
from datetime import timedelta

SLA_HOURS = {"high": 4, "normal": 24, "low": 72}

# TODO: compile TICKET_REF and EMAIL here with re.compile (patterns are in the docstrings below).

# TODO: create the module-level logger `log` with logging.getLogger(__name__).


def days_open(opened_at, now):
    """Return the whole days a ticket has been open, rounded up with math.ceil.

    Exactly 24 hours is 1 day; 24 hours and one minute is 2; zero hours is 0.

    Args:
        opened_at (datetime): When the ticket was opened.
        now (datetime): The moment to measure up to.

    Returns:
        int: The days open, rounded up to a whole number.
    """
    raise NotImplementedError


def is_past_sla(priority, opened_at, now):
    """Return True when `now` is strictly after opened_at plus the SLA hours.

    Exactly at the deadline is not past it. SLA_HOURS maps priority to hours.

    Args:
        priority (str): A key of SLA_HOURS: "high", "normal" or "low".
        opened_at (datetime): When the ticket was opened.
        now (datetime): The moment to check.

    Returns:
        bool: True when the deadline has passed, else False.
    """
    raise NotImplementedError


def check_sla(ticket_id, priority, opened_at, now):
    """Return True when the ticket is past its SLA, else False.

    When it is late, emit one WARNING on this module's logger with the
    message "TD-<id> is past its SLA" (use %s-style arguments, not an f-string).
    When it is on time, log nothing.

    Args:
        ticket_id (int): The ticket's number, as in TD-7.
        priority (str): A key of SLA_HOURS: "high", "normal" or "low".
        opened_at (datetime): When the ticket was opened.
        now (datetime): The moment to check.

    Returns:
        bool: True when the ticket is past its SLA, else False.
    """
    raise NotImplementedError


def ticket_refs(text):
    """Return the ticket numbers mentioned in `text` as ints, in order.

    "TD-2" and "TD-15" count; "XTD-3", "TD-" and "TD-x" do not.
    Use a compiled pattern kept at module level: r"\\bTD-(\\d+)\\b".

    Args:
        text (str): Free text, such as a customer note.

    Returns:
        list[int]: The ticket numbers in the order they appear, repeats kept.
    """
    raise NotImplementedError


def redact(text):
    """Return `text` with every email address replaced by "[email]".

    Use a compiled pattern kept at module level: r"[\\w.+-]+@[\\w-]+\\.[\\w.]+".

    Args:
        text (str): Free text that may contain email addresses.

    Returns:
        str: The same text with each address replaced by "[email]".
    """
    raise NotImplementedError


def main():
    """Print a short demo line; runs only when the file is executed directly.

    Print ticket_refs("See TD-2 and TD-5").

    Returns:
        None
    """
    raise NotImplementedError


# TODO: guard the call to main() so importing this module prints nothing.
