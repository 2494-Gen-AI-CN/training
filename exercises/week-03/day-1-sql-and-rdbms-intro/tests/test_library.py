"""Checks library.sql by running it in your desk-mysql container (no network needed)."""
import pytest

from mysql_helpers import (SQL_FILE, TABLES, column_types, key_columns,
                           opening_statements, reset_database, row_count,
                           run_sql_file)


@pytest.fixture(scope="module", autouse=True)
def built():
    """Run library.sql once before the tests in this module."""
    assert SQL_FILE.exists(), f"write {SQL_FILE} first"
    reset_database()
    run_sql_file(SQL_FILE)


def test_opens_with_drop_create_use():
    """The file's first three statements drop, create and select the city_library database."""
    assert opening_statements(SQL_FILE) == [
        "DROP DATABASE IF EXISTS city_library", "CREATE DATABASE city_library", "USE city_library"]


def test_books_columns():
    """books has book_id, title, isbn and price with the described types."""
    assert column_types("books") == {
        "book_id": "int", "title": "varchar(200)", "isbn": "char(13)", "price": "decimal(6,2)"}


def test_members_columns():
    """members has member_id, name, email, country and joined_at with the described types."""
    assert column_types("members") == {
        "member_id": "int", "name": "varchar(100)", "email": "varchar(100)",
        "country": "char(2)", "joined_at": "datetime"}


def test_loans_columns():
    """loans has six columns with the described types."""
    assert column_types("loans") == {
        "loan_id": "int", "book_id": "int", "member_id": "int", "loaned_at": "datetime",
        "due_at": "datetime", "late_fee": "decimal(5,2)"}


def test_no_keys_yet():
    """The three tables exist and no column carries a key: keys arrive on Wednesday."""
    for table in TABLES:
        assert column_types(table), f"table {table} is missing"
        assert key_columns(table) == []


def test_tables_are_empty():
    """The file creates tables only and inserts no rows."""
    for table in TABLES:
        assert row_count(table) == 0


def test_file_can_run_twice():
    """A second run succeeds and leaves the same three tables."""
    before = {table: column_types(table) for table in TABLES}
    run_sql_file(SQL_FILE)
    after = {table: column_types(table) for table in TABLES}
    assert all(before.values()) and after == before
