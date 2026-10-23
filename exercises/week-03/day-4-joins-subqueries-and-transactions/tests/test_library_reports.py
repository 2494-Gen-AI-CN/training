"""Tests for library_reports: they build a scratch database `library_test` in desk-mysql."""
import os

import mysql.connector
import pytest

import library_reports

DB = "library_test"

SCHEMA = [
    """CREATE TABLE members (
        member_id INT PRIMARY KEY,
        name VARCHAR(60) NOT NULL
    )""",
    """CREATE TABLE books (
        book_id INT PRIMARY KEY,
        title VARCHAR(80) NOT NULL,
        copies INT NOT NULL CHECK (copies >= 0)
    )""",
    """CREATE TABLE loans (
        loan_id INT AUTO_INCREMENT PRIMARY KEY,
        member_id INT NOT NULL,
        book_id INT NOT NULL,
        loaned_on DATE NOT NULL,
        FOREIGN KEY (member_id) REFERENCES members (member_id),
        FOREIGN KEY (book_id) REFERENCES books (book_id)
    )""",
]

SEED = [
    "INSERT INTO members (member_id, name) VALUES (1, 'Ada'), (2, 'Bo'), (3, 'Cy')",
    "INSERT INTO books (book_id, title, copies) VALUES "
    "(1, 'Dune', 0), (2, 'Emma', 1), (3, 'Ulysses', 2), (4, 'Hamlet', 1)",
    "INSERT INTO loans (loan_id, member_id, book_id, loaned_on) VALUES "
    "(1, 1, 1, '2026-10-01'), (2, 1, 2, '2026-10-02'), (3, 2, 2, '2026-10-03')",
]


def _connect(database=None):
    """Open a connection to desk-mysql, optionally to one database."""
    return mysql.connector.connect(
        host=os.environ.get("LIBRARY_DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("LIBRARY_DB_PORT", "3306")),
        user=os.environ.get("LIBRARY_DB_USER", "root"),
        password=os.environ.get("LIBRARY_DB_PASSWORD", "desk"),
        database=database,
    )


@pytest.fixture(scope="module")
def database():
    """Create library_test with its three tables, drop it afterwards."""
    try:
        admin = _connect()
    except mysql.connector.Error as exc:
        pytest.skip(f"desk-mysql container is not reachable: {exc}")
    cur = admin.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DB}")
    cur.execute(f"CREATE DATABASE {DB}")
    cur.execute(f"USE {DB}")
    for statement in SCHEMA:
        cur.execute(statement)
    yield DB
    cur.execute(f"DROP DATABASE IF EXISTS {DB}")
    cur.close()
    admin.close()


@pytest.fixture
def conn(database):
    """A connection to library_test holding the same committed seed rows for every test."""
    connection = _connect(database)
    cur = connection.cursor()
    cur.execute("DELETE FROM loans")
    cur.execute("DELETE FROM books")
    cur.execute("DELETE FROM members")
    for statement in SEED:
        cur.execute(statement)
    cur.execute("ALTER TABLE loans AUTO_INCREMENT = 10")
    connection.commit()
    cur.close()
    yield connection
    connection.rollback()
    connection.close()


def read(conn, sql, params=()):
    """Run a read and commit, so the connection is clean for the next call."""
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.commit()
    return rows


def test_loans_report_joins_members_and_books(conn):
    """The loans report joins each loan to its member and book."""
    assert library_reports.loans_report(conn) == [
        ("Ada", "Dune"),
        ("Ada", "Emma"),
        ("Bo", "Emma"),
    ]


def test_busy_members_applies_having(conn):
    """HAVING keeps only members with at least the minimum loan count."""
    assert library_reports.busy_members(conn, 2) == [("Ada", 2)]


def test_busy_members_orders_by_count_then_name(conn):
    """Busy members come back by loan count descending, then name."""
    assert library_reports.busy_members(conn, 1) == [("Ada", 2), ("Bo", 1)]


def test_members_without_loans_uses_the_missing_side(conn):
    """A member with no loan is found on the NULL side of a LEFT JOIN."""
    assert library_reports.members_without_loans(conn) == ["Cy"]


def test_books_never_loaned_uses_a_subquery(conn):
    """Books that appear in no loan are listed by title."""
    assert library_reports.books_never_loaned(conn) == ["Hamlet", "Ulysses"]


def test_lend_book_takes_a_copy_and_records_the_loan(conn):
    """A loan takes one copy and records the loan in one transaction."""
    loan_id = library_reports.lend_book(conn, 3, 3)
    assert loan_id == 10
    assert read(conn, "SELECT copies FROM books WHERE book_id = 3") == [(1,)]
    assert read(conn, "SELECT member_id, book_id FROM loans WHERE loan_id = %s", (loan_id,)) == [(3, 3)]


def test_lend_book_with_no_copy_left_raises_and_changes_nothing(conn):
    """Lending a book with no copy left raises ValueError and changes nothing."""
    with pytest.raises(ValueError):
        library_reports.lend_book(conn, 1, 3)
    assert read(conn, "SELECT copies FROM books WHERE book_id = 1") == [(0,)]
    assert read(conn, "SELECT COUNT(*) FROM loans") == [(3,)]


def test_lend_book_rolls_back_the_copy_when_the_loan_fails(conn):
    """A failed loan insert rolls back the copy that was taken."""
    with pytest.raises(mysql.connector.IntegrityError):
        library_reports.lend_book(conn, 3, 99)
    assert read(conn, "SELECT copies FROM books WHERE book_id = 3") == [(2,)]
    assert read(conn, "SELECT COUNT(*) FROM loans") == [(3,)]
