"""Ticket reports with the collections module and pandas."""
from collections import Counter, OrderedDict, defaultdict, namedtuple

import pandas as pd

# One ticket as a named row: ticket_id (int), priority, status, assignee (None if unassigned).
TicketRow = namedtuple("TicketRow", ["ticket_id", "priority", "status", "assignee"])


def status_counts(tickets):
    """Count how many tickets have each status.

    Args:
        tickets (list[dict]): ticket dicts, each with a "status" key.

    Returns:
        Counter: status -> number of tickets. A status no ticket has counts 0.
    """
    raise NotImplementedError


def to_rows(tickets):
    """Turn ticket dicts into named rows, in the same order.

    Args:
        tickets (list[dict]): ticket dicts with "ticket_id", "priority" and
            "status" keys, and an optional "assignee" key.

    Returns:
        list[TicketRow]: one row per ticket; a dict with no "assignee" key
        gets assignee None.
    """
    raise NotImplementedError


def work_queue(rows):
    """Build the work queue of rows whose status is "open" or "assigned".

    Order: priority "high" first, then "normal", then "low"; within one
    priority, lower ticket_id first. Closed rows are left out.

    Args:
        rows (list[TicketRow]): the rows to queue.

    Returns:
        OrderedDict[int, TicketRow]: ticket_id -> row, in queue order.
    """
    raise NotImplementedError


def ids_by_agent(rows):
    """Group ticket ids per assignee, using a defaultdict(list) inside.

    Args:
        rows (list[TicketRow]): the rows to group.

    Returns:
        dict[str, list[int]]: assignee -> ticket ids, ids in the order of
        `rows`. Rows with assignee None are left out. A plain dict, not the
        defaultdict.
    """
    raise NotImplementedError


def load_frame(path):
    """Read the tickets from a JSON file into a pandas DataFrame.

    Args:
        path (str | pathlib.Path): a JSON file holding a list of ticket dicts.

    Returns:
        pandas.DataFrame: one row per ticket, columns are the JSON keys.
    """
    raise NotImplementedError


def status_table(df):
    """Count tickets per status from the DataFrame's "status" column.

    Args:
        df (pandas.DataFrame): tickets, with a "status" column.

    Returns:
        dict[str, int]: status -> number of tickets, as a plain dict.
    """
    raise NotImplementedError
