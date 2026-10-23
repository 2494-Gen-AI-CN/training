"""Tests for library_db: they build a scratch database `library_test` in the desk-mysql container."""
import os

import mysql.connector
import pytest

import library_db

DB = "library_test"


def _connect(database=None):
    return mysql.connector.connect(
        host=os.environ.get("LIBRARY_DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("LIBRARY_DB_PORT", "3306")),
        user=os.environ.get("LIBRARY_DB_USER", "root"),
        password=os.environ.get("LIBRARY_DB_PASSWORD", "desk"),
        database=database,
    )


def _statements(path):
    lines = [ln for ln in path.read_text().splitlines() if not ln.strip().startswith("--")]
    return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


@pytest.fixture(scope="module")
def database():
    """Create an empty library_test database, run schema.sql in it, drop it afterwards."""
    try:
        admin = _connect()
    except mysql.connector.Error as exc:
        pytest.skip(f"desk-mysql container is not reachable: {exc}")
    cur = admin.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DB}")
    cur.execute(f"CREATE DATABASE {DB}")
    cur.execute(f"USE {DB}")
    for statement in _statements(library_db.SCHEMA_PATH):
        cur.execute(statement)
    yield DB
    cur.execute(f"DROP DATABASE IF EXISTS {DB}")
    cur.close()
    admin.close()


@pytest.fixture
def conn(database):
    """A connection to library_test whose changes are rolled back after each test."""
    connection = _connect(database)
    yield connection
    connection.rollback()
    connection.close()


def run(conn, sql, params=()):
    """Execute one statement and return all rows."""
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall() if cur.with_rows else []
    cur.close()
    return rows


def add_book(conn, book_id=1, copies=1):
    """Insert one book row directly."""
    run(conn, "INSERT INTO books (book_id, title, copies) VALUES (%s, 'Dune', %s)", (book_id, copies))


LOAN = "INSERT INTO loans (member_id, book_id, loaned_on) VALUES (%s, 1, '2026-10-01')"


def test_add_member_returns_increasing_generated_ids(conn):
    first = library_db.add_member(conn, "Ada", "ada@example.com")
    second = library_db.add_member(conn, "Bo", "bo@example.com")
    assert isinstance(first, int)
    assert second > first
    rows = run(conn, "SELECT name, email FROM members WHERE member_id = %s", (first,))
    assert rows == [("Ada", "ada@example.com")]


def test_duplicate_email_is_refused(conn):
    library_db.add_member(conn, "Ada", "ada@example.com")
    with pytest.raises(mysql.connector.IntegrityError) as err:
        library_db.add_member(conn, "Other Ada", "ada@example.com")
    assert err.value.errno == 1062


def test_member_name_is_required(conn):
    with pytest.raises(mysql.connector.IntegrityError) as err:
        run(conn, "INSERT INTO members (name, email) VALUES (NULL, 'x@example.com')")
    assert err.value.errno == 1048


def test_negative_copies_fail_the_check(conn):
    with pytest.raises(mysql.connector.DatabaseError) as err:
        add_book(conn, copies=-1)
    assert err.value.errno == 3819


def test_loan_status_defaults_to_out(conn):
    member_id = library_db.add_member(conn, "Ada", "ada@example.com")
    add_book(conn)
    run(conn, LOAN, (member_id,))
    rows = run(conn, "SELECT status, returned_on FROM loans WHERE member_id = %s", (member_id,))
    assert rows == [("out", None)]


def test_loan_pair_is_the_composite_key(conn):
    member_id = library_db.add_member(conn, "Ada", "ada@example.com")
    add_book(conn)
    run(conn, LOAN, (member_id,))
    with pytest.raises(mysql.connector.IntegrityError) as err:
        run(conn, LOAN, (member_id,))
    assert err.value.errno == 1062


def test_loan_needs_existing_member_and_book(conn):
    member_id = library_db.add_member(conn, "Ada", "ada@example.com")
    add_book(conn)
    with pytest.raises(mysql.connector.IntegrityError) as err:
        run(conn, LOAN, (999,))
    assert err.value.errno == 1452
    with pytest.raises(mysql.connector.IntegrityError) as err:
        run(
            conn,
            "INSERT INTO loans (member_id, book_id, loaned_on) VALUES (%s, 999, '2026-10-01')",
            (member_id,),
        )
    assert err.value.errno == 1452


def test_deleting_a_member_or_book_deletes_its_loans(conn):
    ada = library_db.add_member(conn, "Ada", "ada@example.com")
    bo = library_db.add_member(conn, "Bo", "bo@example.com")
    add_book(conn, book_id=1)
    add_book(conn, book_id=2)
    loan = "INSERT INTO loans (member_id, book_id, loaned_on) VALUES (%s, %s, '2026-10-01')"
    run(conn, loan, (ada, 1))
    run(conn, loan, (bo, 2))
    run(conn, "DELETE FROM members WHERE member_id = %s", (ada,))
    assert run(conn, "SELECT member_id, book_id FROM loans") == [(bo, 2)]
    assert run(conn, "SELECT COUNT(*) FROM books") == [(2,)]
    run(conn, "DELETE FROM books WHERE book_id = 2")
    assert run(conn, "SELECT COUNT(*) FROM loans") == [(0,)]
    assert run(conn, "SELECT member_id FROM members") == [(bo,)]


def test_return_book_closes_the_loan_and_restocks(conn):
    member_id = library_db.add_member(conn, "Ada", "ada@example.com")
    add_book(conn, copies=2)
    run(conn, LOAN, (member_id,))
    library_db.return_book(conn, member_id, 1)
    loan = run(conn, "SELECT status, returned_on IS NOT NULL FROM loans WHERE member_id = %s", (member_id,))
    assert loan == [("returned", 1)]
    assert run(conn, "SELECT copies FROM books WHERE book_id = 1") == [(3,)]


def test_return_book_without_an_open_loan_raises(conn):
    member_id = library_db.add_member(conn, "Ada", "ada@example.com")
    add_book(conn, copies=2)
    with pytest.raises(ValueError):
        library_db.return_book(conn, member_id, 1)
    assert run(conn, "SELECT copies FROM books WHERE book_id = 1") == [(2,)]
