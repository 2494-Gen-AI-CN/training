"""Test-side helpers: run library.sql in the desk-mysql container and read column facts back."""
import os
import pathlib
import subprocess

SRC = pathlib.Path(
    os.environ.get("EXERCISE_SRC") or pathlib.Path(__file__).resolve().parents[1] / "starter"
)
SQL_FILE = SRC / "library.sql"
TABLES = ("books", "members", "loans")
BASE = ["docker", "exec", "-i", "desk-mysql", "mysql", "-uroot", "-pdesk"]


def run_sql_file(path):
    """Feed the SQL file at `path` to the mysql client inside desk-mysql; raise on failure."""
    with open(path, "rb") as handle:
        result = subprocess.run(BASE, stdin=handle, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace"))


def reset_database():
    """Drop the city_library database so each test run starts from what library.sql alone builds."""
    _query("DROP DATABASE IF EXISTS city_library;")


def _query(sql):
    """Run one statement in the client and return its rows as lists of strings."""
    result = subprocess.run(BASE + ["-N", "-B", "-e", sql], capture_output=True,
                            text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return [line.split("\t") for line in result.stdout.splitlines() if line]


def _checked(table):
    """Return `table` if it is one of the three exercise tables, else raise ValueError."""
    # Only a fixed, known name is ever pasted into the SQL text below, so nothing
    # from outside can change the statement (Wednesday's %s placeholders do this for values).
    if table not in TABLES:
        raise ValueError(f"unknown table {table!r}")
    return table


def column_types(table):
    """Return {column_name: column_type} for `table` in the city_library database, in column order."""
    rows = _query("SELECT column_name, column_type FROM information_schema.columns "
                  "WHERE table_schema = 'city_library' AND table_name = '" + _checked(table) + "' "
                  "ORDER BY ordinal_position;")
    return {name: ctype for name, ctype in rows}


def key_columns(table):
    """Return the names of columns in `table` whose column_key is not empty."""
    rows = _query("SELECT column_name FROM information_schema.columns "
                  "WHERE table_schema = 'city_library' AND table_name = '" + _checked(table) + "' "
                  "AND column_key <> '';")
    return [row[0] for row in rows]


def row_count(table):
    """Return how many rows `table` in the city_library database holds."""
    return int(_query("SELECT COUNT(*) FROM city_library." + _checked(table) + ";")[0][0])


def opening_statements(path, count=3):
    """Return the first `count` statements of the file, comment lines removed, spaces collapsed."""
    lines = [line for line in path.read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.strip().startswith("--")]
    statements = [" ".join(part.split()) for part in "\n".join(lines).split(";")]
    return [s for s in statements if s][:count]
