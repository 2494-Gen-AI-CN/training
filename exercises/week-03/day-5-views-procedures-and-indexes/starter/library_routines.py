"""The Python side of the library's view, procedure, function and index.

The five objects themselves are created in library_routines.sql, through the client.
"""


def overdue_loans(conn):
    """Return the rows of the overdue_loans view as dicts keyed by column name.

    Read the view with a dictionary cursor (conn.cursor(dictionary=True)), then commit.

    Args:
        conn: an open mysql.connector connection to library_routines_test.

    Returns:
        list of dicts with keys loan_id, member, title, due_on, ordered by due_on
        then loan_id; due_on is a datetime.date.
    """
    raise NotImplementedError


def return_loan(conn, loan_id, returned_on):
    """Call the close_loan procedure for one loan with cursor.callproc, then commit.

    Args:
        conn: an open mysql.connector connection to library_routines_test.
        loan_id: int, the loan to close, for example 1.
        returned_on: str in the form "YYYY-MM-DD" (or a datetime.date), the return date.

    Returns:
        None. The trigger, not this function, writes the loan_events row.
    """
    raise NotImplementedError


def fee_for(conn, due_on, returned_on):
    """Return late_fee(due_on, returned_on) as read from the database (values as %s).

    Args:
        conn: an open mysql.connector connection to library_routines_test.
        due_on: str "YYYY-MM-DD" (or a datetime.date), the day the book was due.
        returned_on: str "YYYY-MM-DD" (or a datetime.date), the day it came back.

    Returns:
        Decimal, for example Decimal("0.75") for three days late, Decimal("0.00") when
        on time or early.
    """
    raise NotImplementedError


def due_lookup_plan(conn, due_on):
    """Return the EXPLAIN text for selecting the loans with exactly this due date.

    Run EXPLAIN SELECT * FROM loans WHERE due_on = %s and join the plan lines with newlines.

    Args:
        conn: an open mysql.connector connection to library_routines_test.
        due_on: str "YYYY-MM-DD" (or a datetime.date), the due date to look up.

    Returns:
        str, the EXPLAIN tree lines joined by newlines.
    """
    raise NotImplementedError
