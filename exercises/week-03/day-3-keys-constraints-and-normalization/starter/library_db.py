"""Library database helpers: add a member and return a book through mysql-connector-python."""
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def add_member(conn, name, email):
    """Insert a member with %s placeholders and return the generated member_id.

    The function does not commit; the caller owns the transaction.

    Args:
        conn (mysql.connector.connection.MySQLConnection): An open connection
            to the library database.
        name (str): The member's name.
        email (str): The member's email; no two members may share one.

    Returns:
        int: The member_id the server generated for the new row.

    Raises:
        mysql.connector.IntegrityError: When another member already has this email.
    """
    raise NotImplementedError


def return_book(conn, member_id, book_id):
    """Mark the outstanding loan of the book by the member as returned and put the copy back.

    Set status to 'returned' and returned_on to today on the loan whose status is 'out',
    then add one to the book's copies. The function does not commit.

    Args:
        conn (mysql.connector.connection.MySQLConnection): An open connection
            to the library database.
        member_id (int): The member who has the book.
        book_id (int): The book being returned.

    Returns:
        None

    Raises:
        ValueError: When the member has no loan of this book with status 'out';
            nothing is changed.
    """
    raise NotImplementedError
