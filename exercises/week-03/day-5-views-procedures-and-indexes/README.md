# Exercise — A library with a trigger, a view, a procedure, a function and an index

Week 3 · Day 5 · `w03d5` · Fri 2026-10-30 · ~60–90 min
Notes: [weeks/week-03/day-5-views-procedures-and-indexes.html](https://2494-gen-ai-cn.github.io/training/weeks/week-03/day-5-views-procedures-and-indexes.html) · Demos: [2494-Gen-AI-CN/demos](https://github.com/2494-Gen-AI-CN/demos)

## Task

Give a small library database the same five objects the ticket desk got today. Two files share the work. `starter/library_routines.sql` holds the five objects, written the way the desk's `sql/routines.sql` is: a trigger `loans_returned` that logs each returned loan, a view `overdue_loans`, a procedure `close_loan` that closes a loan, a `late_fee` function declared `DETERMINISTIC` and an index `idx_loans_due_on` on the loans' due date. `starter/library_routines.py` holds the Python side, in four functions: one reads the view, one calls the procedure with `callproc`, one calls the function and one returns the `EXPLAIN` plan for a lookup by due date. Routines are created only through the client, never from Python, so the `.py` file creates nothing.

The tests build a scratch database called `library_routines_test` inside your `desk-mysql` container, a cut-down rebuild of the `members`, `books` and `loans` tables of the library you have worked on since Monday, plus an empty `loan_events` table. For every test they rebuild it with fixed rows, pipe your `.sql` file into the client with `docker exec -i desk-mysql mysql -uroot -pdesk library_routines_test`, call your Python, and drop the database at the end. Your `ticket_desk` database is never touched.

The tables and rows:

- `members`: `member_id`, `name`. Rows: 1 Ada, 2 Bo, 3 Cy.
- `books`: `book_id`, `title`. Rows: 1 Dune, 2 Emma, 3 Hamlet.
- `loans`: `loan_id`, `member_id`, `book_id`, `loaned_on`, `due_on`, `returned_on` (`NULL` while the book is out). Four loans; loans 1 and 4 are out and past due, loan 3 is out and due in 2099, loan 2 is returned.
- `loan_events`: `event_id` (generated), `loan_id`, `kind`. Empty at the start.

## Acceptance criteria

- [ ] `test_trigger_logs_a_return`: `return_loan` on an open loan leaves one `loan_events` row with that `loan_id` and kind `returned`
- [ ] `test_trigger_ignores_other_updates`: setting `returned_on` writes one event, and changing a loan's `due_on` writes none
- [ ] `test_view_lists_only_unreturned_past_due_loans`: `overdue_loans` returns the view's rows as dicts with the keys `loan_id`, `member`, `title`, `due_on`, ordered by `due_on` then `loan_id`
- [ ] `test_overdue_is_a_view_that_follows_the_loans_table`: `overdue_loans` is a real view, and a loan drops out of it once it is returned
- [ ] `test_procedure_closes_a_loan_once`: calling `close_loan` twice keeps the first `returned_on` and writes one event
- [ ] `test_late_fee_charges_a_quarter_per_late_day`: three days late costs `0.75`; on time or early costs `0.00`
- [ ] `test_late_fee_is_declared_deterministic`: the database records `late_fee` as deterministic
- [ ] `test_index_exists_on_due_on`: `idx_loans_due_on` exists on `loans (due_on)`
- [ ] `test_explain_names_the_index`: the plan from `due_lookup_plan` names `idx_loans_due_on`
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/week-03/day-5-views-procedures-and-indexes
cp -r exercises/week-03/day-5-views-procedures-and-indexes/* ../<FirstnameLastname>/week-03/day-5-views-procedures-and-indexes/
cd ../<FirstnameLastname>/week-03/day-5-views-procedures-and-indexes
docker start desk-mysql      # only if the container is stopped
python -m pip install mysql-connector-python==26.7.0 pytest==9.1.1
python -m pytest -q          # everything fails until you write starter/library_routines.sql and starter/library_routines.py
```

Write the five objects in `starter/library_routines.sql` (its comments list each one), then implement the functions in `starter/library_routines.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go. If the client refuses your `.sql` file, the failing test prints the client's `ERROR` line with the line number it stopped at.

The tests connect to `127.0.0.1:3306` as `root` with the password `desk`, and pipe the file into the container `desk-mysql`. If yours differ, set `LIBRARY_DB_HOST`, `LIBRARY_DB_PORT`, `LIBRARY_DB_USER`, `LIBRARY_DB_PASSWORD` and `LIBRARY_DB_CONTAINER` before running pytest. If the container is not running, the tests are skipped with a message instead of passing, so a skip is not a pass.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `week-03/day-5-views-procedures-and-indexes/` there.

## Hints

- The client ends a statement at the first `;`, and a trigger or procedure body has `;` inside it. Wrap each of those two in `DELIMITER //` and `DELIMITER ;` and end the body with `END //`, as the desk's `routines.sql` does:

  ```sql
  DELIMITER //
  CREATE TRIGGER loans_returned
  AFTER UPDATE ON loans
  FOR EACH ROW
  BEGIN
    -- the IF ... THEN ... END IF; block goes here
  END //
  DELIMITER ;
  ```

  The view, the function (one `RETURN` line, no `BEGIN`) and the index are single statements that end with `;` and need no `DELIMITER`. The file runs from top to bottom right after the tables are built, so it needs no `USE` line and no `DROP ... IF EXISTS`.
- Inside the trigger, `OLD.returned_on` is the value before the update and `NEW.returned_on` the value after. Fire only when the old one is `NULL` and the new one is not.
- The procedure's `UPDATE` should only touch a loan whose `returned_on IS NULL`; then a second call changes no row, so the trigger does not fire twice.
- The function must say `DETERMINISTIC` (without it the server answers ERROR 1418) and must take both dates as parameters instead of reading `NOW()`. `DATEDIFF(p_returned, p_due)` is negative for an early return; `GREATEST(..., 0)` clamps it.
- Call the procedure with `cursor.callproc("close_loan", (loan_id, returned_on))`, then `conn.commit()`; the connector has autocommit off, so a write that is not committed is lost. Read the view through `conn.cursor(dictionary=True)`.
- `EXPLAIN` prints a tree in MySQL 9.7, one row per line. A plan that says `Table scan on loans` means no index was used; one that says `Index lookup on loans using idx_loans_due_on` means yours was.
