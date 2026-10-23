# Exercise — Library reports with joins, GROUP BY and a lending transaction

Week 3 · Day 4 · `w03d4` · Thu 2026-10-29 · ~60–90 min
Notes: [weeks/week-03/day-4-joins-subqueries-and-transactions.html](https://2494-gen-ai-cn.github.io/training/weeks/week-03/day-4-joins-subqueries-and-transactions.html) · Demos: [2494-Gen-AI-CN/demos](https://github.com/2494-Gen-AI-CN/demos)

## Task

Write the reports a library would run, then the one write it must get right. In `starter/library_reports.py` implement four functions that each run one query (a join, a `GROUP BY` with `HAVING`, a `LEFT JOIN` that keeps the unmatched side, and a subquery) and `lend_book(conn, book_id, member_id)`, a transaction that takes a copy off a book and records the loan together or not at all, as the ticket desk's `assign_ticket` did.

The tests build a scratch database called `library_test` inside your `desk-mysql` container with three tables and fixed rows, and drop it at the end. Your `ticket_desk` database is never touched.

The tables and rows:

- `members`: `member_id`, `name`. Rows: 1 Ada, 2 Bo, 3 Cy.
- `books`: `book_id`, `title`, `copies` (copies on the shelf, never negative). Rows: 1 Dune (0), 2 Emma (1), 3 Ulysses (2), 4 Hamlet (1).
- `loans`: `loan_id` (generated), `member_id`, `book_id`, `loaned_on`. Rows: Ada has Dune and Emma, Bo has Emma. Cy has none.

## Acceptance criteria

- [ ] `test_loans_report_joins_members_and_books`: `loans_report` returns `(member name, title)` pairs for every loan, ordered by name then title
- [ ] `test_busy_members_applies_having`: `busy_members(conn, 2)` returns only members with at least two loans, with their counts
- [ ] `test_busy_members_orders_by_count_then_name`: `busy_members(conn, 1)` lists the larger count first
- [ ] `test_members_without_loans_uses_the_missing_side`: `members_without_loans` returns the names of members with no loan
- [ ] `test_books_never_loaned_uses_a_subquery`: `books_never_loaned` returns the titles that appear in no loan
- [ ] `test_lend_book_takes_a_copy_and_records_the_loan`: `lend_book` lowers `copies` by one, inserts the loan and returns its generated `loan_id`
- [ ] `test_lend_book_with_no_copy_left_raises_and_changes_nothing`: with `copies` at 0 it raises `ValueError` and leaves books and loans as they were
- [ ] `test_lend_book_rolls_back_the_copy_when_the_loan_fails`: for an unknown member the insert fails with `IntegrityError` and the copy taken is given back by the rollback
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-03/day-4-joins-subqueries-and-transactions
cp -r exercises/week-03/day-4-joins-subqueries-and-transactions/* ../<FirstnameLastname>/week-03/day-4-joins-subqueries-and-transactions/
cd ../<FirstnameLastname>/week-03/day-4-joins-subqueries-and-transactions
docker start desk-mysql      # only if the container is stopped
python -m pip install mysql-connector-python==26.7.0 pytest==9.1.1
python -m pytest -q          # everything fails until you implement starter/library_reports.py
```

Implement the functions in `starter/library_reports.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go.

The tests connect to `127.0.0.1:3306` as `root` with the password `desk`. If yours differ, set `LIBRARY_DB_HOST`, `LIBRARY_DB_PORT`, `LIBRARY_DB_USER` and `LIBRARY_DB_PASSWORD` before running pytest. If the container is not running, the tests are skipped with a message instead of passing, so a skip is not a pass.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-03/day-4-joins-subqueries-and-transactions/` there.

## Hints

- Join through the middle table: `FROM loans AS l JOIN members AS m ON m.member_id = l.member_id JOIN books AS b ON b.book_id = l.book_id`.
- `WHERE` runs before grouping, so a condition on `COUNT(*)` belongs in `HAVING`. Pass the minimum as `%s`, never an f-string.
- For members with no loan, `LEFT JOIN loans` from `members` and keep the rows where a loan column is `NULL`. For books never loaned, `WHERE book_id NOT IN (SELECT book_id FROM loans)` works.
- Connector/Python has autocommit off. A read leaves a transaction open, and `conn.start_transaction()` raises `Transaction already in progress` on a connection that ran any statement since its last commit. Call `conn.commit()` after your reads so the next call starts clean.
- In `lend_book`, run the `UPDATE books SET copies = copies - 1 ... AND copies > 0` first and check `cursor.rowcount`: `0` means no copy was available. Then `INSERT` the loan and read `cursor.lastrowid`. Wrap both in `try`, call `conn.rollback()` in the `except` and re-raise, and `conn.commit()` only after both succeeded.
