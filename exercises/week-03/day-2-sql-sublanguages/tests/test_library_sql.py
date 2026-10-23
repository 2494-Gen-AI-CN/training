"""Tests run each SQL file in the desk-mysql container, in a scratch database."""
import subprocess

import pytest

import library_sql as ls

DB = "library_w3d2"
BASE = ["docker", "exec", "-i", "desk-mysql", "mysql"]
ROOT = BASE + ["-uroot", "-pdesk", "-N", "-B"]

MONDAY = f"""
DROP DATABASE IF EXISTS {DB};
CREATE DATABASE {DB};
USE {DB};
CREATE TABLE books (book_id INT, title VARCHAR(100), author VARCHAR(60), price DECIMAL(6,2));
CREATE TABLE members (member_id INT, name VARCHAR(60), email VARCHAR(100));
CREATE TABLE loans (loan_id INT, book_id INT, member_id INT, loaned_at DATETIME);
"""

ROWS = f"""USE {DB};
INSERT INTO books (book_id, title, author, price) VALUES
  (1, 'Dune', 'Frank Herbert', 12.99), (2, 'Emma', 'Jane Austen', 8.50),
  (3, 'Ulysses', 'James Joyce', 15.00);
INSERT INTO members (member_id, name, email) VALUES
  (1, 'Ana Silva', 'ana@example.com'), (2, 'Ben Okoye', 'ben@example.com');
INSERT INTO loans (loan_id, book_id, member_id, loaned_at) VALUES
  (1, 1, 1, '2026-10-01 10:00:00'), (2, 2, 1, '2026-10-05 14:30:00'),
  (3, 3, 2, '2026-10-06 09:15:00');
"""


def run(sql, cmd=ROOT, check=True):
    """Feed SQL to the client and return the completed process."""
    try:
        proc = subprocess.run(cmd, input=sql, capture_output=True, text=True, timeout=60, check=False)
    except FileNotFoundError:
        pytest.fail("docker is not on PATH")
    if check and proc.returncode != 0:
        pytest.fail(f"mysql refused the file: {proc.stderr.strip()}")
    return proc


def rows(sql):
    """Run one query as root and return its rows as lists of strings."""
    out = run(f"USE {DB};\n{sql}\n").stdout.strip()
    return [line.split("\t") for line in out.splitlines()] if out else []


@pytest.fixture(autouse=True)
def monday():
    """Rebuild a cut-down copy of Monday's three empty tables and drop the reader account around each test."""
    run(MONDAY)
    run("DROP USER IF EXISTS 'library_reader'@'%';")
    yield
    run(f"DROP DATABASE IF EXISTS {DB};")
    run("DROP USER IF EXISTS 'library_reader'@'%';")


def test_alter_adds_shelf_column():
    run(ls.alter_sql(DB))
    found = rows(
        "SELECT column_name, column_type, is_nullable FROM information_schema.columns "
        f"WHERE table_schema = '{DB}' AND table_name = 'books' AND column_name = 'shelf';"
    )
    assert found == [["shelf", "varchar(20)", "YES"]]


def test_seed_loads_every_row():
    run(ls.seed_sql(DB))
    assert rows("SELECT COUNT(*) FROM books;") == [["3"]]
    assert rows("SELECT COUNT(*) FROM members;") == [["2"]]
    assert rows("SELECT COUNT(*) FROM loans;") == [["3"]]
    assert rows("SELECT title, price FROM books WHERE book_id = 3;") == [["Ulysses", "15.00"]]


def test_update_changes_only_book_2():
    run(ROWS)
    run(ls.update_sql(DB))
    assert rows("SELECT book_id, price FROM books ORDER BY book_id;") == [
        ["1", "12.99"], ["2", "9.50"], ["3", "15.00"],
    ]


def test_delete_removes_only_loan_3():
    run(ROWS)
    run(ls.delete_sql(DB))
    assert rows("SELECT loan_id FROM loans ORDER BY loan_id;") == [["1"], ["2"]]
    assert rows("SELECT COUNT(*) FROM books;") == [["3"]]


def test_reader_holds_select_and_nothing_else():
    run(ls.reader_sql(DB))
    grants = run("SHOW GRANTS FOR 'library_reader'@'%';").stdout
    assert f"GRANT SELECT ON `{DB}`.*" in grants
    for word in ("INSERT", "UPDATE", "DELETE", "DROP", "ALL PRIVILEGES"):
        assert word not in grants


def test_reader_can_read_but_not_write():
    run(ROWS)
    run(ls.reader_sql(DB))
    login = BASE + ["-ulibrary_reader", "-preader", "-N", "-B", DB]
    ok = run("SELECT COUNT(*) FROM books;", cmd=login)
    assert ok.stdout.strip() == "3"
    refused = run("DELETE FROM loans;", cmd=login, check=False)
    assert refused.returncode != 0
    assert "1142" in refused.stderr
    assert rows("SELECT COUNT(*) FROM loans;") == [["3"]]


def test_rollback_file_leaves_loans_in_place():
    run(ROWS)
    out = run(ls.rollback_sql(DB)).stdout.strip()
    assert out.splitlines()[-1] == "0"  # inside the transaction the table looked empty
    assert rows("SELECT COUNT(*) FROM loans;") == [["3"]]


def test_rollback_file_is_a_transaction_ending_in_rollback():
    text = ls.rollback_sql(DB).upper()
    statements = [s.strip() for s in text.split(";") if s.strip()]
    assert "START TRANSACTION" in statements
    assert statements[-1] == "ROLLBACK"
    assert "COMMIT" not in statements
