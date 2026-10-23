"""Tests for library_routines: they build a scratch database `library_routines_test` in desk-mysql.

For every test the tables and rows are rebuilt, then library_routines.sql is piped into the
mysql client inside the container (the way the desk's sql/routines.sql is run), and only then
does the Python in library_routines.py get called.
"""
import datetime
import os
import pathlib
import subprocess
from decimal import Decimal

import mysql.connector
import pytest

import library_routines

DB = "library_routines_test"
SRC = pathlib.Path(
    os.environ.get("EXERCISE_SRC") or pathlib.Path(__file__).resolve().parents[1] / "starter"
)
SQL_FILE = SRC / "library_routines.sql"
CONTAINER = os.environ.get("LIBRARY_DB_CONTAINER", "desk-mysql")

SCHEMA = [
    """CREATE TABLE members (
        member_id INT PRIMARY KEY,
        name VARCHAR(60) NOT NULL
    )""",
    """CREATE TABLE books (
        book_id INT PRIMARY KEY,
        title VARCHAR(80) NOT NULL
    )""",
    """CREATE TABLE loans (
        loan_id INT PRIMARY KEY,
        member_id INT NOT NULL,
        book_id INT NOT NULL,
        loaned_on DATE NOT NULL,
        due_on DATE NOT NULL,
        returned_on DATE NULL,
        FOREIGN KEY (member_id) REFERENCES members (member_id),
        FOREIGN KEY (book_id) REFERENCES books (book_id)
    )""",
    """CREATE TABLE loan_events (
        event_id INT AUTO_INCREMENT PRIMARY KEY,
        loan_id INT NOT NULL,
        kind VARCHAR(20) NOT NULL,
        FOREIGN KEY (loan_id) REFERENCES loans (loan_id)
    )""",
]

SEED = [
    "INSERT INTO members (member_id, name) VALUES (1, 'Ada'), (2, 'Bo'), (3, 'Cy')",
    "INSERT INTO books (book_id, title) VALUES (1, 'Dune'), (2, 'Emma'), (3, 'Hamlet')",
    "INSERT INTO loans (loan_id, member_id, book_id, loaned_on, due_on, returned_on) VALUES "
    "(1, 1, 1, '2026-09-20', '2026-10-08', NULL), "
    "(2, 1, 2, '2026-09-21', '2026-10-09', '2026-10-08'), "
    "(3, 2, 2, '2026-09-22', '2099-01-01', NULL), "
    "(4, 3, 3, '2026-09-15', '2026-10-05', NULL)",
]


def _connect(database=None):
    """Open a connector connection as root (the same login the client uses)."""
    return mysql.connector.connect(
        host=os.environ.get("LIBRARY_DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("LIBRARY_DB_PORT", "3306")),
        user=os.environ.get("LIBRARY_DB_USER", "root"),
        password=os.environ.get("LIBRARY_DB_PASSWORD", "desk"),
        database=database,
    )


def run_sql_file(path):
    """Pipe the SQL file into the mysql client inside the container; fail the test if it refuses."""
    password = os.environ.get("LIBRARY_DB_PASSWORD", "desk")
    command = ["docker", "exec", "-i", CONTAINER, "mysql", "-uroot", f"-p{password}", DB]
    try:
        with open(path, "rb") as handle:
            result = subprocess.run(command, stdin=handle, capture_output=True, timeout=60,
                                    check=False)
    except FileNotFoundError:
        pytest.fail("docker is not on PATH")
    if result.returncode != 0:
        errors = [line for line in result.stderr.decode(errors="replace").splitlines()
                  if "Using a password" not in line]
        pytest.fail(f"mysql refused {path.name}: " + " ".join(errors))


@pytest.fixture(scope="module")
def admin():
    """A root connection that drops the scratch database at the end of the module."""
    try:
        connection = _connect()
    except mysql.connector.Error as exc:
        pytest.skip(f"desk-mysql container is not reachable: {exc}")
    yield connection
    cur = connection.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DB}")
    cur.close()
    connection.close()


@pytest.fixture
def installed(admin):
    """A connection to a freshly built library_routines_test after library_routines.sql has run."""
    cur = admin.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DB}")
    cur.execute(f"CREATE DATABASE {DB}")
    cur.execute(f"USE {DB}")
    for statement in SCHEMA + SEED:
        cur.execute(statement)
    admin.commit()
    cur.close()
    run_sql_file(SQL_FILE)
    connection = _connect(DB)
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


def test_trigger_logs_a_return(installed):
    """Returning an open loan writes exactly one 'returned' event for it."""
    library_routines.return_loan(installed, 1, "2026-10-12")
    assert read(installed, "SELECT loan_id, kind FROM loan_events") == [(1, "returned")]


def test_trigger_ignores_other_updates(installed):
    """Only the return writes an event; updates that leave returned_on alone write none."""
    cur = installed.cursor()
    cur.execute("UPDATE loans SET returned_on = '2026-10-12' WHERE loan_id = 1")
    cur.execute("UPDATE loans SET due_on = '2026-11-01' WHERE loan_id = 1")
    cur.execute("UPDATE loans SET due_on = '2099-02-01' WHERE loan_id = 3")
    installed.commit()
    cur.close()
    assert read(installed, "SELECT loan_id, kind FROM loan_events") == [(1, "returned")]


def test_view_lists_only_unreturned_past_due_loans(installed):
    """overdue_loans returns the two late loans as dicts, earliest due date first."""
    assert library_routines.overdue_loans(installed) == [
        {"loan_id": 4, "member": "Cy", "title": "Hamlet", "due_on": datetime.date(2026, 10, 5)},
        {"loan_id": 1, "member": "Ada", "title": "Dune", "due_on": datetime.date(2026, 10, 8)},
    ]


def test_overdue_is_a_view_that_follows_the_loans_table(installed):
    """overdue_loans is a VIEW, and a returned loan drops out of it."""
    kind = read(
        installed,
        "SELECT table_type FROM information_schema.tables "
        "WHERE table_schema = %s AND table_name = 'overdue_loans'",
        (DB,),
    )
    assert kind == [("VIEW",)]
    library_routines.return_loan(installed, 4, "2026-10-12")
    assert [row["loan_id"] for row in library_routines.overdue_loans(installed)] == [1]


def test_procedure_closes_a_loan_once(installed):
    """A second close_loan call keeps the first return date and writes no second event."""
    library_routines.return_loan(installed, 3, "2026-10-12")
    library_routines.return_loan(installed, 3, "2026-10-20")
    assert read(installed, "SELECT returned_on FROM loans WHERE loan_id = 3") == [
        (datetime.date(2026, 10, 12),)
    ]
    assert read(installed, "SELECT COUNT(*) FROM loan_events WHERE loan_id = 3") == [(1,)]


def test_late_fee_charges_a_quarter_per_late_day(installed):
    """late_fee is 0.25 a day late and never negative."""
    assert library_routines.fee_for(installed, "2026-10-08", "2026-10-11") == Decimal("0.75")
    assert library_routines.fee_for(installed, "2026-10-08", "2026-10-08") == Decimal("0.00")
    assert library_routines.fee_for(installed, "2026-10-08", "2026-10-01") == Decimal("0.00")


def test_late_fee_is_declared_deterministic(installed):
    """The server records late_fee as DETERMINISTIC."""
    rows = read(
        installed,
        "SELECT is_deterministic FROM information_schema.routines "
        "WHERE routine_schema = %s AND routine_name = 'late_fee'",
        (DB,),
    )
    assert rows == [("YES",)]


def test_index_exists_on_due_on(installed):
    """idx_loans_due_on exists and covers loans.due_on only."""
    rows = read(installed, "SHOW INDEX FROM loans WHERE Key_name = 'idx_loans_due_on'")
    assert [row[4] for row in rows] == ["due_on"]


def test_explain_names_the_index(installed):
    """The plan for a lookup by due date uses idx_loans_due_on."""
    plan = library_routines.due_lookup_plan(installed, "2026-10-08")
    assert "idx_loans_due_on" in plan
