# w03d5 — Advanced SQL: triggers, views, procedures & indexes

gate: light
verified: 2026-10-23
week: 3 · SQL with MySQL
day: 5 · views-procedures-and-indexes

version-stamps:
  - python: 3.15 (verified 2026-10-23)
  - mysql: 9.7 (image tag mysql:9.7, LTS line; patch floats with the tag) (verified 2026-10-23)
  - mysql-connector-python: 26.7.0 (verified 2026-10-23)   # pure-Python wheel pip picks on 3.15: mysql_connector_python-26.7.0-py2.py3-none-any.whl
  - pytest: 9.0 (verified 2026-10-23)   # pure-Python wheel: pytest-9.0.x-py3-none-any.whl

## Claims

- A trigger is a named database object tied to a table that activates when INSERT, UPDATE or DELETE happens on it, BEFORE or AFTER the row change. — [CREATE TRIGGER statement](https://dev.mysql.com/doc/refman/9.7/en/create-trigger.html)
- Inside a trigger, OLD.col is the row before the change and NEW.col the row after; OLD does not exist for INSERT and NEW does not exist for DELETE. — [Trigger syntax and examples](https://dev.mysql.com/doc/refman/9.7/en/trigger-syntax.html)
- A trigger body with several statements is a BEGIN ... END block, which needs the client's DELIMITER changed so the semicolons inside do not end the CREATE statement. — [Defining stored programs](https://dev.mysql.com/doc/refman/9.7/en/stored-programs-defining.html)
- MySQL fires triggers only for changes made by SQL statements, not for cascaded foreign-key actions. — [CREATE TRIGGER statement](https://dev.mysql.com/doc/refman/9.7/en/create-trigger.html)
- A view is a stored SELECT with a name; it holds no rows of its own and runs its query each time it is read. — [CREATE VIEW statement](https://dev.mysql.com/doc/refman/9.7/en/create-view.html)
- A view that uses aggregates, GROUP BY, DISTINCT or UNION is not updatable; a plain one-table view generally is. — [Updatable and insertable views](https://dev.mysql.com/doc/refman/9.7/en/view-updatability.html)
- CREATE PROCEDURE defines routine code run with CALL; IN, OUT and INOUT parameters pass values in and out. — [CREATE PROCEDURE and CREATE FUNCTION statements](https://dev.mysql.com/doc/refman/9.7/en/create-procedure.html)
- A stored function returns one value and is used inside an expression such as SELECT or WHERE; a procedure is run on its own with CALL. — [CREATE PROCEDURE and CREATE FUNCTION statements](https://dev.mysql.com/doc/refman/9.7/en/create-procedure.html)
- With binary logging on, creating a function that is not declared DETERMINISTIC, NO SQL or READS SQL DATA fails with error 1418. — [Stored program binary logging](https://dev.mysql.com/doc/refman/9.7/en/stored-programs-logging.html)
- GRANT EXECUTE on a database lets an account CALL its procedures and use its functions. — [GRANT statement](https://dev.mysql.com/doc/refman/9.7/en/grant.html)
- A routine runs with the privileges of its DEFINER by default (`SQL SECURITY DEFINER`), so an account holding only EXECUTE can still change the tables the routine touches; with `SQL SECURITY INVOKER` the caller would need those table privileges itself. — [CREATE PROCEDURE and CREATE FUNCTION statements](https://dev.mysql.com/doc/refman/9.7/en/create-procedure.html)
- An index is a separate sorted structure (a B-tree in InnoDB) that lets the server find matching rows without reading the whole table. — [How MySQL uses indexes](https://dev.mysql.com/doc/refman/9.7/en/mysql-indexes.html)
- Every index speeds some reads but costs disk space and extra work on each INSERT, UPDATE and DELETE. — [Optimization and indexes](https://dev.mysql.com/doc/refman/9.7/en/optimization-indexes.html)
- EXPLAIN shows the plan for a statement; in 9.7 the default output format is a tree, naming a table scan or an index lookup. — [EXPLAIN statement](https://dev.mysql.com/doc/refman/9.7/en/explain.html)
- Connector/Python's cursor.callproc(name, args) calls a stored procedure from Python. — [MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/)

## Notes depth

### Trigger
- Interview questions: What is a trigger and what tasks would you automate with one, such as writing an audit row on every status change? (qc2.sql.P12); What do OLD and NEW mean in a trigger?; Why can a trigger make a system hard to debug?
- Adjacent concept: BEFORE versus AFTER triggers — an interviewer asks which can change the incoming row and which suits writing an audit row.
- Trade-off or limit: A trigger runs invisibly on every matching change, so it adds hidden cost and logic that application code cannot see — [CREATE TRIGGER statement](https://dev.mysql.com/doc/refman/9.7/en/create-trigger.html)
- Recognise on sight: `CREATE TRIGGER tickets_status_change AFTER UPDATE ON tickets FOR EACH ROW BEGIN ... END //`
- Claims:
  - A trigger is bound to one table and one event and time (BEFORE or AFTER INSERT, UPDATE, DELETE). — [CREATE TRIGGER statement](https://dev.mysql.com/doc/refman/9.7/en/create-trigger.html)
  - Typical automated tasks are audit or history rows, derived values kept in step, and rule checks that refuse a bad row before it is written. — [Trigger syntax and examples](https://dev.mysql.com/doc/refman/9.7/en/trigger-syntax.html)
  - `NOT (OLD.agent_id <=> NEW.agent_id)` is the NULL-safe way to detect a change; plain `<>` yields NULL when either side is NULL. — [Comparison operators](https://dev.mysql.com/doc/refman/9.7/en/comparison-operators.html)
  - A trigger fires inside the transaction of the statement that caused it, so a rollback undoes its writes too. — [Trigger syntax and examples](https://dev.mysql.com/doc/refman/9.7/en/trigger-syntax.html)
  - Triggers are removed with DROP TRIGGER and listed with SHOW TRIGGERS. — [DROP TRIGGER statement](https://dev.mysql.com/doc/refman/9.7/en/drop-trigger.html)

### Views
- Interview questions: How do you create a view over a query and read from it? (qc2.sql.R14); Does a view store data?; Can you update through a view?
- Adjacent concept: Security through views — exposing only chosen columns and rows to an account, one reason teams create them.
- Trade-off or limit: A view re-runs its query on every read, so it saves typing, not computation — [CREATE VIEW statement](https://dev.mysql.com/doc/refman/9.7/en/create-view.html)
- Recognise on sight: `CREATE VIEW open_board AS SELECT ... FROM tickets AS t JOIN ... WHERE t.status <> 'closed' ORDER BY t.ticket_id;` then `SELECT * FROM open_board;`
- Claims:
  - A view is queried exactly like a table in FROM. — [CREATE VIEW statement](https://dev.mysql.com/doc/refman/9.7/en/create-view.html)
  - Column names of a view come from the SELECT's names or aliases, so aliasing keeps the names stable for callers. — [CREATE VIEW statement](https://dev.mysql.com/doc/refman/9.7/en/create-view.html)
  - Python reads a view with an ordinary SELECT through cursor.execute, and `conn.cursor(dictionary=True)` returns each row as a dict keyed by the view's column names. — [MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/)
  - DROP VIEW removes the definition and no data. — [DROP VIEW statement](https://dev.mysql.com/doc/refman/9.7/en/drop-view.html)

### What is a stored procedure
- Interview questions: What is a stored procedure and how do you create and call it? (qc2.sql.R13); What are IN and OUT parameters?; How does a trigger call a procedure? (qc2.sql.P10)
- Adjacent concept: Security and round trips — a procedure keeps logic next to the data and a grant of EXECUTE can replace table grants.
- Trade-off or limit: Logic in procedures is versioned apart from application code and is harder to test and review — [Stored objects](https://dev.mysql.com/doc/refman/9.7/en/stored-objects.html)
- Recognise on sight: `DELIMITER //` / `CREATE PROCEDURE close_ticket(IN p_ticket_id INT, IN p_closed_at DATETIME) BEGIN ... END //` / `CALL close_ticket(4, '2026-10-19 15:00:00');`
- Claims:
  - CALL runs a procedure; a procedure may return result sets, change rows, or set OUT parameters. — [CALL statement](https://dev.mysql.com/doc/refman/9.7/en/call.html)
  - A trigger body may CALL a procedure, so shared logic is written once. — [Trigger syntax and examples](https://dev.mysql.com/doc/refman/9.7/en/trigger-syntax.html)
  - A procedure that returns a result set to the client cannot be called from a trigger. — [Restrictions on stored programs](https://dev.mysql.com/doc/refman/9.7/en/stored-program-restrictions.html)
  - From Python, `cursor.callproc("close_ticket", (ticket_id, at))` calls a procedure that returns no rows. — [MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/)
  - DECLARE variables and IF/WHILE control flow are available inside BEGIN ... END. — [Compound statements](https://dev.mysql.com/doc/refman/9.7/en/sql-compound-statements.html)

### What is a user defined function
- Interview questions: How do you create a user-defined function in MySQL and call it in a query? (qc2.sql.R12); Why must it say DETERMINISTIC?; Function versus procedure?
- Adjacent concept: Built-in functions (Thursday) as the model a UDF extends, and why a function in WHERE can defeat an index.
- Trade-off or limit: A function called per row in WHERE or SELECT runs once for every row, which is slow on big tables — [CREATE PROCEDURE and CREATE FUNCTION statements](https://dev.mysql.com/doc/refman/9.7/en/create-procedure.html)
- Recognise on sight: `CREATE FUNCTION hours_open(p_opened DATETIME, p_closed DATETIME) RETURNS DECIMAL(8,2) DETERMINISTIC RETURN ROUND(TIMESTAMPDIFF(MINUTE, p_opened, p_closed) / 60, 2);`
- Claims:
  - A function has only IN parameters and must RETURN exactly one value of the declared type. — [CREATE PROCEDURE and CREATE FUNCTION statements](https://dev.mysql.com/doc/refman/9.7/en/create-procedure.html)
  - DETERMINISTIC promises the same inputs always give the same output; a body that reads NOW() is strictly not deterministic, so a teaching example should take both times as parameters. — [CREATE PROCEDURE and CREATE FUNCTION statements](https://dev.mysql.com/doc/refman/9.7/en/create-procedure.html)
  - A function cannot run COMMIT or ROLLBACK or return a result set. — [Restrictions on stored programs](https://dev.mysql.com/doc/refman/9.7/en/stored-program-restrictions.html)
  - A function is used inside a query, as in `SELECT ticket_id, hours_open(opened_at, closed_at) AS hours FROM tickets;`, and TIMESTAMPDIFF returns NULL when either time is NULL, so an open ticket shows NULL hours. — [Date and time functions](https://dev.mysql.com/doc/refman/9.7/en/date-and-time-functions.html)

### Indexes
- Interview questions: What is an index and why use one? (qc2.sql.P11); What does an index cost?; How do you check a query uses one?
- Adjacent concept: Composite indexes and the leftmost-prefix rule — an interviewer asks how column order matters.
- Trade-off or limit: Indexes slow writes and use disk, and a low-selectivity column such as a three-value status may gain little — [Optimization and indexes](https://dev.mysql.com/doc/refman/9.7/en/optimization-indexes.html)
- Recognise on sight: `CREATE INDEX idx_tickets_status ON tickets (status);` then `EXPLAIN SELECT * FROM tickets WHERE status = 'open';`
- Claims:
  - InnoDB indexes the primary key automatically, and a foreign-key column gets an index if none exists. — [Foreign key constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
  - A secondary index in InnoDB is a B-tree whose entries point to the primary key. — [Clustered and secondary indexes](https://dev.mysql.com/doc/refman/9.7/en/innodb-index-types.html)
  - EXPLAIN output reading `Table scan on tickets` means every row is read; `Index lookup on tickets using idx_tickets_status` means the index is used. — [EXPLAIN output format](https://dev.mysql.com/doc/refman/9.7/en/explain-output.html)
  - On a six-row table the optimizer may still choose a scan, so the demo must show the plan, not time it. — [EXPLAIN output format](https://dev.mysql.com/doc/refman/9.7/en/explain-output.html)
  - SHOW INDEX FROM tickets lists indexes; DROP INDEX removes one. — [SHOW INDEX statement](https://dev.mysql.com/doc/refman/9.7/en/show-index.html)

### Review
- Interview questions: Walk me through how you would model and secure a small ticket system in MySQL; When do you pick a view, a procedure or a function?; What would you check first on a slow query?
- Adjacent concept: Choosing the tool — trigger for automatic side effects, view for a reusable read, procedure for a unit of work, function for a computed value, index for read speed.
- Trade-off or limit: Every automatic mechanism (trigger, procedure) moves behaviour out of the application, which trades visibility for consistency — [Stored objects](https://dev.mysql.com/doc/refman/9.7/en/stored-objects.html)
- Recognise on sight: a `sql/` folder holding schema.sql, seed.sql, users.sql, reports.sql and routines.sql rebuilt in order.
- Claims:
  - ACID transactions (atomicity, consistency, isolation, durability) are how InnoDB keeps multi-statement changes safe. — [InnoDB and the ACID model](https://dev.mysql.com/doc/refman/9.7/en/mysql-acid.html)
  - Foreign keys and CHECK constraints enforce rules inside the database regardless of which program writes. — [CREATE TABLE statement](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
  - Placeholders (`%s` with a tuple) keep values out of the SQL text and prevent injection. — [MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/)
  - `pytest.skip` inside a fixture skips every test that uses it, which keeps the suite green when the database is not reachable (pytest's own documentation; its fixtures page shows the yield-then-clean-up shape the `conn` fixture follows). — [pytest: skipping tests](https://docs.pytest.org/en/stable/how-to/skipping.html)

## Sources

- MySQL 9.7 Reference Manual: CREATE TRIGGER — https://dev.mysql.com/doc/refman/9.7/en/create-trigger.html
- MySQL 9.7: Trigger syntax and examples — https://dev.mysql.com/doc/refman/9.7/en/trigger-syntax.html
- MySQL 9.7: CREATE VIEW — https://dev.mysql.com/doc/refman/9.7/en/create-view.html
- MySQL 9.7: Updatable and insertable views — https://dev.mysql.com/doc/refman/9.7/en/view-updatability.html
- MySQL 9.7: CREATE PROCEDURE and CREATE FUNCTION — https://dev.mysql.com/doc/refman/9.7/en/create-procedure.html
- MySQL 9.7: Stored program binary logging — https://dev.mysql.com/doc/refman/9.7/en/stored-programs-logging.html
- MySQL 9.7: Restrictions on stored programs — https://dev.mysql.com/doc/refman/9.7/en/stored-program-restrictions.html
- MySQL 9.7: How MySQL uses indexes — https://dev.mysql.com/doc/refman/9.7/en/mysql-indexes.html
- MySQL 9.7: EXPLAIN statement — https://dev.mysql.com/doc/refman/9.7/en/explain.html
- MySQL 9.7: GRANT statement — https://dev.mysql.com/doc/refman/9.7/en/grant.html
- MySQL 9.7: Date and time functions — https://dev.mysql.com/doc/refman/9.7/en/date-and-time-functions.html
- MySQL Connector/Python Developer Guide — https://dev.mysql.com/doc/connector-python/en/
- pytest: skipping tests — https://docs.pytest.org/en/stable/how-to/skipping.html
- pytest: how to use fixtures — https://docs.pytest.org/en/stable/how-to/fixtures.html

## Glossary terms

- trigger | A routine stored with a table that the server runs automatically when a row is inserted, updated or deleted. | aka: triggers, database trigger
- view | A named, stored SELECT that is read like a table but holds no rows of its own. | aka: views
- stored procedure | A named block of SQL kept in the database and run on demand with CALL. | aka: stored procedures, procedure
- user-defined function | A named routine kept in the database that takes inputs and returns one value, usable inside a query. | aka: UDF, stored function
- index | A separate sorted structure on one or more columns that lets the server find rows without reading the whole table. | aka: indexes, B-tree index
- EXPLAIN | A statement that prints how the server plans to run a query, such as a table scan or an index lookup. | aka: query plan, execution plan

## Common pitfalls

- Forgetting `DELIMITER //`, so the first semicolon inside a trigger or procedure body ends the CREATE statement and the client reports a syntax error.
- Declaring a function without DETERMINISTIC and hitting ERROR 1418 with binary logging on; or writing DETERMINISTIC on a body that calls NOW().
- Comparing OLD and NEW with `<>` on a nullable column such as agent_id, so a change from NULL to a value never fires; the NULL-safe `<=>` is needed.
- Writing history both in a trigger and in the application, so each event is stored twice; and expecting `execute("CALL ...")` from Python to return rows instead of using the prompt for result-set procedures.
- Expecting a view to store or cache results, or an index to help a query that wraps the indexed column in a function; judging an index by timing a six-row table instead of reading EXPLAIN.

## Demo plan hints

- 09-routines-and-indexes (AM), trigger: once `tickets_status_change` exists, run `UPDATE tickets SET status = 'closed', closed_at = '2026-10-19 14:00:00' WHERE ticket_id = 5;` at the prompt and read the `ticket_events` row the trigger writes (kind `closed`, note `was assigned, agent 2`); after `log_event` is created and the trigger's INSERT is rewritten to `CALL log_event(...)`, the next change writes its row through the procedure.
- 09-routines-and-indexes (AM), views then procedures, all before the function and the index: paste the `-- board` and `-- agent load` queries of `reports.sql` into `open_board` (with `WHERE t.status <> 'closed'` typed before its ORDER BY) and `agent_load` and read both with `SELECT *`; after the break, `CALL close_ticket(4, '2026-10-19 15:00:00');` then `SELECT * FROM ticket_events;` (the row written by the trigger through `log_event`), `CALL tickets_for_customer('dana@example.com');`, and `GRANT EXECUTE ON ticket_desk.* TO 'desk_app'@'%';` added to `users.sql` and rerun (the block's stop point: when time runs short the commit is made here).
- 09-routines-and-indexes (AM, last; moved to the first 15 minutes of Facilitation: Review when the block stops early): `hours_open` declared DETERMINISTIC and called as `SELECT ticket_id, hours_open(opened_at, closed_at) AS hours FROM tickets;`, then `EXPLAIN SELECT * FROM tickets WHERE status = 'open';` before and after `idx_tickets_status`, reading `Table scan on tickets` against `Index lookup on tickets using idx_tickets_status`.
- 10-desk-views (PM): `close_ticket_db` reduced to `cursor.callproc("close_ticket", (ticket_id, at))`, `assign_ticket` with its own `ticket_events` INSERT deleted so the trigger owns history, `open_board(conn)` reading the view through `conn.cursor(dictionary=True)` so `python ticket_desk.py` prints `row["ref"]`, `row["customer"]`, `row["agent"]` and `row["deadline"]`, `pytest` at 25 passed, then `git switch main`, `git merge feature/desk-routines` and `git push origin main`.
