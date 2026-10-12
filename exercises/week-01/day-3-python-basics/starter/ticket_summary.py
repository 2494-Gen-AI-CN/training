"""Ticket summary helpers for the ticket desk.

Follow PEP 8: imports first, snake_case names, UPPER_CASE constants,
two blank lines between functions, lines under 79 columns, and comments
that say why. Keep these docstrings; replace only the function bodies.
"""


def age_days(hours_open):
    """Return how many whole days a ticket has been open.

    Args:
        hours_open (float): hours since the ticket was opened.

    Returns:
        float: complete 24-hour days, from floor division; 50 gives 2.
    """
    raise NotImplementedError


def hours_left(sla_hours, hours_open):
    """Return the hours remaining before the ticket breaches its SLA.

    Args:
        sla_hours (int): hours the SLA allows for this priority.
        hours_open (float): hours since the ticket was opened.

    Returns:
        float: sla_hours minus hours_open; below zero once the ticket
            is late.
    """
    raise NotImplementedError


def is_breached(is_open, sla_hours, hours_open):
    """Tell whether an open ticket is past its SLA.

    Args:
        is_open (bool): True while the ticket is still open.
        sla_hours (int): hours the SLA allows for this priority.
        hours_open (float): hours since the ticket was opened.

    Returns:
        bool: True only for an open ticket past its SLA (hours left
            below zero). Exactly zero hours left is not a breach, and
            a closed ticket is never breached.
    """
    raise NotImplementedError


def priority_ok(priority):
    """Tell whether a priority is one of the three the desk accepts.

    Args:
        priority (str): the priority text exactly as typed.

    Returns:
        bool: True when priority equals 'high', 'normal' or 'low';
            False (the bool, not an empty or leftover string) for any
            other text.
    """
    raise NotImplementedError


def is_first_day(hours_open):
    """Tell whether a ticket is still in its first day.

    Args:
        hours_open (float): hours since the ticket was opened.

    Returns:
        bool: True when hours_open is at least 0 and under 24, written
            as one chained comparison.
    """
    raise NotImplementedError


def escalate(ticket_id):
    """Tell whether a ticket is picked for the every-third escalation.

    Args:
        ticket_id (int): the ticket number.

    Returns:
        bool: True when ticket_id divides by 3 with no remainder
            (3, 6, 9, ...).
    """
    raise NotImplementedError


def sla_used_percent(sla_hours, hours_open):
    """Return how much of the SLA a ticket has used, as a percentage.

    Args:
        sla_hours (int): hours the SLA allows; always above zero.
        hours_open (float): hours since the ticket was opened.

    Returns:
        float: hours_open as a percentage of sla_hours, rounded to one
            decimal with the built-in round; 5.5 hours of a 4-hour SLA
            gives 137.5. A number, not text.
    """
    raise NotImplementedError


def summary_line(ticket_id, title, priority, hours_open, reporter):
    """Build one aligned line that describes a ticket.

    Args:
        ticket_id (int): the ticket number.
        title (str): the ticket title.
        priority (str): 'high', 'normal' or 'low'.
        hours_open (float): hours since the ticket was opened.
        reporter (str): who reported the ticket.

    Returns:
        str: '#' and the id, one space, the title left-aligned in 20
            columns, the priority right-aligned in 8, hours_open
            right-aligned in 6 with one decimal, then 'h', one space
            and the reporter. A title longer than 20 characters is
            kept whole. No newline at the end. Example:
            '#7 Login bug               high   5.5h Ada'
    """
    raise NotImplementedError


def print_board(ticket_id, title, priority, hours_open, sla_hours):
    """Print a two-line board, a header and one ticket row, to stdout.

    Every column is joined to the next by ' | ' and every line closes
    with ' |' before its newline; let print's sep and end do that.
    Columns, with the header word and the row value sharing one width:
    'ID' right-aligned in 4, 'Title' left-aligned in 20, 'Priority'
    right-aligned in 8, 'Hours' right-aligned in 6 (the row shows one
    decimal), 'SLA %' right-aligned in 6 (the row shows
    sla_used_percent with one decimal). Example:

      ID | Title                | Priority |  Hours |  SLA % |
     101 | Login bug            |     high |    5.5 |  137.5 |

    Args:
        ticket_id (int): the ticket number.
        title (str): the ticket title.
        priority (str): 'high', 'normal' or 'low'.
        hours_open (float): hours since the ticket was opened.
        sla_hours (int): hours the SLA allows for this priority.

    Returns:
        None: the board is printed, nothing is returned, and nothing
            goes to stderr.
    """
    raise NotImplementedError


def warn_breach(ticket_id, is_open, sla_hours, hours_open):
    """Print one warning line about a ticket to stderr.

    The line reports the breach flag and the hours left with one
    decimal, for example:
    'warning: ticket 101 breached=True hours_left=-1.5'
    The caller decides when to warn, so the line is printed whatever
    the flag is ('breached=False hours_left=1.0' for a ticket with one
    hour to go).

    Args:
        ticket_id (int): the ticket number.
        is_open (bool): True while the ticket is still open.
        sla_hours (int): hours the SLA allows for this priority.
        hours_open (float): hours since the ticket was opened.

    Returns:
        None: the line goes to stderr and nothing goes to stdout.
    """
    raise NotImplementedError
