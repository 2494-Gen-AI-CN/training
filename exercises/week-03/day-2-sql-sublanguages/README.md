# Exercise — SQL sublanguages

Week 3 · Day 2 · `w03d2` · ~60–90 min
Notes: [weeks/week-03/day-2-sql-sublanguages.html](https://2494-gen-ai-cn.github.io/training/weeks/week-03/day-2-sql-sublanguages.html) · Demos: [2494-Gen-AI-CN/demos](https://github.com/2494-Gen-AI-CN/demos)

## Task

Monday's exercise built a `city_library` database with three empty tables: `books`, `members` and `loans`. Today you write one file for each sublanguage against a cut-down copy of those three tables. In `starter/library_sql.py` each function returns the text of a SQL file as a string: an ALTER (DDL), a seed of INSERTs, an UPDATE and a DELETE (DML), a read-only account (DCL) and a transaction that ends in ROLLBACK (TCL).

The tests never touch your own `city_library` database. They need your `desk-mysql` container running (`docker start desk-mysql` if the laptop rebooted). For each test they build the cut-down copy, three empty tables, in a scratch database called `library_w3d2`, run your file there through `docker exec -i desk-mysql mysql -uroot -pdesk`, and read the rows and grants back. The `db` argument of each function is that database name: begin every file with `USE <db>;` (the account file needs none).

The tables the tests build (not Monday's exact columns: this `books` has an `author` and no `isbn`, and the other two are shorter):

- `books` (`book_id`, `title`, `author`, `price`)
- `members` (`member_id`, `name`, `email`)
- `loans` (`loan_id`, `book_id`, `member_id`, `loaned_at`)

The rows your seed file inserts, with every id written out and the column list spelled out:

| Table | Rows |
| --- | --- |
| `books` | (1, 'Dune', 'Frank Herbert', 12.99), (2, 'Emma', 'Jane Austen', 8.50), (3, 'Ulysses', 'James Joyce', 15.00) |
| `members` | (1, 'Ana Silva', 'ana@example.com'), (2, 'Ben Okoye', 'ben@example.com') |
| `loans` | (1, 1, 1, '2026-10-01 10:00:00'), (2, 2, 1, '2026-10-05 14:30:00'), (3, 3, 2, '2026-10-06 09:15:00') |

## Acceptance criteria

- [ ] `alter_sql` adds a nullable `shelf VARCHAR(20)` column to `books` — `test_alter_adds_shelf_column`
- [ ] `seed_sql` loads 3 books, 2 members and 3 loans — `test_seed_loads_every_row`
- [ ] `update_sql` sets book 2's price to 9.50 and changes no other row — `test_update_changes_only_book_2`
- [ ] `delete_sql` removes loan 3 and nothing else — `test_delete_removes_only_loan_3`
- [ ] `reader_sql` creates `'library_reader'@'%'` (password `reader`) holding SELECT on the database and no other privilege — `test_reader_holds_select_and_nothing_else`
- [ ] `library_reader` can read a table and is refused a write with error 1142 — `test_reader_can_read_but_not_write`
- [ ] `rollback_sql` deletes every loan inside a transaction and the loans are back afterwards — `test_rollback_file_leaves_loans_in_place`
- [ ] `rollback_sql` is START TRANSACTION ... ROLLBACK with no COMMIT — `test_rollback_file_is_a_transaction_ending_in_rollback`
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-03/day-2-sql-sublanguages
cp -r exercises/week-03/day-2-sql-sublanguages/* ../<FirstnameLastname>/week-03/day-2-sql-sublanguages/
cd ../<FirstnameLastname>/week-03/day-2-sql-sublanguages
docker ps                    # desk-mysql must be listed; if not: docker start desk-mysql
python -m pytest -q          # everything fails until you implement starter/library_sql.py
```

Implement the functions in `starter/library_sql.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-03/day-2-sql-sublanguages/` there.

## Hints

- Return an f-string such as `f"USE {db};\nALTER TABLE ..."`, or a triple-quoted f-string for a longer file. Every statement ends with `;`.
- If a test says `mysql refused the file`, the message after it is the server's own error text. Try the statement by hand first: `docker exec -it desk-mysql mysql -uroot -p`.
- A statement with no WHERE changes every row. Name the row by its id in the UPDATE and the DELETE.
- Account names carry a host part: `'library_reader'@'%'`. A privilege is granted on `database.*`, not on the bare database name.
- Run `SHOW GRANTS FOR 'library_reader'@'%';` to see exactly what an account holds. Anything beyond SELECT fails the test.
- The transaction file needs the `SELECT COUNT(*) FROM loans;` before the ROLLBACK so the rows inside the transaction are visible in the output.
