"""Library reports and a lending transaction through mysql-connector-python."""


def loans_report(conn):
    """Return (member name, book title) for every loan, using a join.

    Order by member name, then title. Return a list of tuples.

    Args:
        conn: an open mysql-connector connection to library_test.

    Returns:
        list of (name, title) tuples ordered by name, then title.
    """
    raise NotImplementedError


def busy_members(conn, minimum):
    """Return (member name, loan count) for members with at least `minimum` loans.

    Use GROUP BY with HAVING, pass `minimum` as a %s placeholder, and order by
    loan count descending, then name. Return a list of tuples.

    Args:
        conn: an open mysql-connector connection to library_test.
        minimum: the smallest loan count to keep (int).

    Returns:
        list of (name, loan_count) tuples, count descending then name.
    """
    raise NotImplementedError


def members_without_loans(conn):
    """Return the names of members who have no loan at all, ordered by name.

    Use a LEFT JOIN and keep the rows where the loan side is NULL. Return a list of strings.

    Args:
        conn: an open mysql-connector connection to library_test.

    Returns:
        list of str: member names ordered by name.
    """
    raise NotImplementedError


def books_never_loaned(conn):
    """Return the titles of books that appear in no loan, ordered by title.

    Use a subquery. Return a list of strings.

    Args:
        conn: an open mysql-connector connection to library_test.

    Returns:
        list of str: book titles ordered by title.
    """
    raise NotImplementedError


def lend_book(conn, book_id, member_id):
    """Lend one copy of a book to a member as one transaction and return the new loan_id.

    Start a transaction, take one off the book's copies (only when copies is above 0),
    then insert the loan with loaned_on set to today. If no copy was available, roll back
    and raise ValueError. If the insert fails (for example an unknown member), roll back so
    the copy count is restored, then re-raise the error. Commit only when both steps worked.

    Args:
        conn: an open mysql-connector connection to library_test.
        book_id: the id of the book to lend (int).
        member_id: the id of the member who borrows it (int).

    Returns:
        the new loan_id (int).

    Raises:
        ValueError: when the book has no copy left.
        mysql.connector.Error: re-raised after rollback when the insert fails.
    """
    raise NotImplementedError
