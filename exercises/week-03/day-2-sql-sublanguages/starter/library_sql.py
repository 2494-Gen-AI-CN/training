"""SQL for the library database: one function per sublanguage statement file.

Each function returns the text of a SQL file as a string. `db` is the database name
the tests create for you; start every file with a USE line that names it.
"""


def alter_sql(db):
    """DDL: add a nullable `shelf` column, VARCHAR(20), to `books`.

    Args:
        db: name of the scratch database the tests create (put it in the USE line).

    Returns:
        str: the SQL file text, every statement ending with `;`.
    """
    raise NotImplementedError


def seed_sql(db):
    """DML: INSERT the three books, two members and three loans listed in the README.

    Args:
        db: name of the scratch database the tests create (put it in the USE line).

    Returns:
        str: the SQL file text, one INSERT per table with its column list and every id written
        out, every statement ending with `;`.
    """
    raise NotImplementedError


def update_sql(db):
    """DML: set the price of book 2 to 9.50, touching no other row.

    Args:
        db: name of the scratch database the tests create (put it in the USE line).

    Returns:
        str: the SQL file text, every statement ending with `;`.
    """
    raise NotImplementedError


def delete_sql(db):
    """DML: delete loan 3 only.

    Args:
        db: name of the scratch database the tests create (put it in the USE line).

    Returns:
        str: the SQL file text, every statement ending with `;`.
    """
    raise NotImplementedError


def reader_sql(db):
    """DCL: create 'library_reader'@'%' (password reader) with SELECT only on every table of `db`.

    Args:
        db: name of the scratch database the tests create; used only in the
            `GRANT ... ON <db>.*` line (this file needs no USE line).

    Returns:
        str: the SQL file text (a CREATE USER and a GRANT), every statement ending with `;`.
    """
    raise NotImplementedError


def rollback_sql(db):
    """TCL: START TRANSACTION, delete every loan, SELECT the count, then end with ROLLBACK.

    Args:
        db: name of the scratch database the tests create (put it in the USE line).

    Returns:
        str: the SQL file text, every statement ending with `;`, the last one `ROLLBACK;`
        and no COMMIT anywhere.
    """
    raise NotImplementedError
