# w03d2 — SQL sublanguages

gate: light
verified: 2026-10-23
week: 3 · SQL with MySQL
day: 2 · sql-sublanguages

version-stamps:
  - python: 3.15 (verified 2026-10-23)
  - mysql: 9.7 (LTS line, image tag mysql:9.7; patch floats with the tag; no Python library is imported on this day, the work is in the mysql client) (verified 2026-10-23)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- CREATE TABLE defines a table's columns and data types, and CREATE TABLE IF NOT EXISTS skips the statement without error when the table exists — [MySQL 9.7 CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- ALTER TABLE changes a table after creation: ADD COLUMN, DROP COLUMN, MODIFY COLUMN, CHANGE COLUMN and RENAME COLUMN — [MySQL 9.7 ALTER TABLE](https://dev.mysql.com/doc/refman/9.7/en/alter-table.html)
- DROP TABLE removes the table definition, its data and its indexes, and cannot be rolled back — [MySQL 9.7 DROP TABLE](https://dev.mysql.com/doc/refman/9.7/en/drop-table.html)
- TRUNCATE TABLE empties a table by dropping and recreating it, resets AUTO_INCREMENT to its start value and is DDL, so it cannot be rolled back — [MySQL 9.7 TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
- DELETE without WHERE removes every row but keeps the table and does not reset AUTO_INCREMENT; with InnoDB it can be rolled back — [MySQL 9.7 DELETE](https://dev.mysql.com/doc/refman/9.7/en/delete.html)
- INSERT ... VALUES adds one or more rows, and naming the column list makes the statement survive later column additions — [MySQL 9.7 INSERT](https://dev.mysql.com/doc/refman/9.7/en/insert.html)
- UPDATE without a WHERE clause changes every row in the table — [MySQL 9.7 UPDATE](https://dev.mysql.com/doc/refman/9.7/en/update.html)
- SELECT reads rows without changing them; the course teaches it as DQL, its own sublanguage — [MySQL 9.7 SELECT](https://dev.mysql.com/doc/refman/9.7/en/select.html)
- CREATE USER makes an account named user@host, and the host part is part of the identity: 'desk_app'@'%' matches any host — [MySQL 9.7 CREATE USER](https://dev.mysql.com/doc/refman/9.7/en/create-user.html)
- GRANT gives privileges at a level (global, database, table), and `ON ticket_desk.*` covers every table of one database — [MySQL 9.7 GRANT](https://dev.mysql.com/doc/refman/9.7/en/grant.html)
- REVOKE removes privileges previously granted, and SHOW GRANTS FOR an account lists what it holds — [MySQL 9.7 REVOKE](https://dev.mysql.com/doc/refman/9.7/en/revoke.html)
- START TRANSACTION, COMMIT and ROLLBACK group statements so they apply or vanish together; autocommit is on by default, so each statement outside START TRANSACTION commits itself — [MySQL 9.7 START TRANSACTION, COMMIT, and ROLLBACK](https://dev.mysql.com/doc/refman/9.7/en/commit.html)
- Statements that cause an implicit commit include most DDL (CREATE, ALTER, DROP, TRUNCATE) and account statements such as CREATE USER and GRANT — [MySQL 9.7 Statements That Cause an Implicit Commit](https://dev.mysql.com/doc/refman/9.7/en/implicit-commit.html)
- SAVEPOINT names a point inside a transaction, and ROLLBACK TO SAVEPOINT undoes only the work after it — [MySQL 9.7 SAVEPOINT](https://dev.mysql.com/doc/refman/9.7/en/savepoint.html)
- InnoDB is the default storage engine and the one that supports transactions — [MySQL 9.7 The InnoDB Storage Engine](https://dev.mysql.com/doc/refman/9.7/en/innodb-storage-engine.html)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### DDL
- Interview questions: What does DDL stand for and which statements belong to it?; Write the statements that create a scratch table, empty it and remove it. (qc2.sql.R04); How do you add a column to an existing table, and how do you change a column's data type? (qc2.sql.S01); Why can you not roll back a DROP TABLE?
- Adjacent concept: DDL against DML — structure against rows — the split that sets up the DROP, DELETE and TRUNCATE comparison in the next step.
- Trade-off or limit: DDL statements commit implicitly in MySQL, so a ROLLBACK afterwards undoes nothing — [MySQL 9.7 Statements That Cause an Implicit Commit](https://dev.mysql.com/doc/refman/9.7/en/implicit-commit.html)
- Recognise on sight: `ALTER TABLE scratch_notes ADD COLUMN author VARCHAR(50);` and `DROP TABLE scratch_notes;`
- Claims:
  - MySQL files CREATE TABLE, ALTER TABLE, DROP TABLE and TRUNCATE TABLE under Data Definition Statements — [MySQL 9.7 Data Definition Statements](https://dev.mysql.com/doc/refman/9.7/en/sql-data-definition-statements.html)
  - ALTER TABLE ... ADD COLUMN appends the column at the end by default; FIRST and AFTER col place it elsewhere — [MySQL 9.7 ALTER TABLE](https://dev.mysql.com/doc/refman/9.7/en/alter-table.html)
  - MODIFY changes a column's definition and keeps its name; CHANGE also renames, and RENAME COLUMN renames only — [MySQL 9.7 ALTER TABLE](https://dev.mysql.com/doc/refman/9.7/en/alter-table.html)
  - Narrowing a column type can fail or truncate data, so a MODIFY on a populated table needs a check first — [MySQL 9.7 ALTER TABLE](https://dev.mysql.com/doc/refman/9.7/en/alter-table.html)
  - DROP TABLE IF EXISTS suppresses the error for a missing table and gives a note instead — [MySQL 9.7 DROP TABLE](https://dev.mysql.com/doc/refman/9.7/en/drop-table.html)

### DML
- Interview questions: Write an INSERT that adds two rows with the column list spelled out. (qc2.sql.R06); Write an UPDATE that retitles ticket 6 and a DELETE that removes one ticket by id. (qc2.sql.R06); What happens if you run UPDATE or DELETE without WHERE?; Explain DROP against DELETE against TRUNCATE, and say which of the three can be rolled back. (qc2.sql.R07)
- Adjacent concept: Rows affected — what the client's `Query OK, n rows affected` line reports after an INSERT, UPDATE or DELETE, the first check that a write touched the rows it meant to.
- Trade-off or limit: DELETE removes rows one at a time and is slower on large tables than TRUNCATE, which is why TRUNCATE exists for emptying a table — [MySQL 9.7 TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
- Recognise on sight: `DELETE FROM tickets;` and `UPDATE tickets SET status = 'closed';` with no WHERE; a second `(1, 'Login page returns 500', ...)` row that loads because nothing stops a repeated id yet (named as a problem, solved on a later day).
- Claims:
  - INSERT with an explicit column list is safer than one that relies on column order — [MySQL 9.7 INSERT](https://dev.mysql.com/doc/refman/9.7/en/insert.html)
  - A multi-row INSERT uses one VALUES list with comma-separated row tuples — [MySQL 9.7 INSERT](https://dev.mysql.com/doc/refman/9.7/en/insert.html)
  - UPDATE reports "Rows matched" and "Changed"; an UPDATE to the same value matches a row but changes none — [MySQL 9.7 UPDATE](https://dev.mysql.com/doc/refman/9.7/en/update.html)
  - DELETE removes rows and leaves the AUTO_INCREMENT counter where it was; TRUNCATE resets it — [MySQL 9.7 TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
  - TRUNCATE is DDL, DELETE is DML, DROP removes the table itself; only DELETE rolls back — [MySQL 9.7 TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)

### DQL
- Interview questions: Is SELECT DML or DQL?; How do you select only some columns?; How do you read one ticket by its id?; What does SELECT * return and why avoid it in application code?
- Adjacent concept: Column aliases with AS — renaming a result column for the reader without touching the table, the first way a query shapes its own output.
- Trade-off or limit: SELECT * returns every column, so a later ALTER TABLE changes what the caller receives — [MySQL 9.7 SELECT](https://dev.mysql.com/doc/refman/9.7/en/select.html)
- Recognise on sight: `SELECT title, priority, status FROM tickets;` and `SELECT title FROM tickets WHERE ticket_id = 2;`
- Claims:
  - MySQL's manual files SELECT among its Data Manipulation Statements; the course splits it out as DQL because it reads and never writes — [MySQL 9.7 Data Manipulation Statements](https://dev.mysql.com/doc/refman/9.7/en/sql-data-manipulation-statements.html)
  - A SELECT names its columns in a comma-separated list, and the result shows them in that order — [MySQL 9.7 SELECT](https://dev.mysql.com/doc/refman/9.7/en/select.html)
  - SELECT without FROM can evaluate expressions, such as `SELECT VERSION();` — [MySQL 9.7 SELECT](https://dev.mysql.com/doc/refman/9.7/en/select.html)
  - A column alias with AS renames a result column and does not change the table — [MySQL 9.7 SELECT](https://dev.mysql.com/doc/refman/9.7/en/select.html)

### DCL
- Interview questions: What do GRANT and REVOKE do?; Why create an application account instead of using root?; How do you see what an account may do?; What does 'desk_app'@'%' mean?
- Adjacent concept: Least privilege — giving an account only the statements it needs — which is why the desk's app account cannot DROP.
- Trade-off or limit: A grant on `ticket_desk.*` survives DROP DATABASE and re-creation of the tables, and privileges are checked at statement time, so a refused statement shows ERROR 1142 — [MySQL 9.7 GRANT](https://dev.mysql.com/doc/refman/9.7/en/grant.html)
- Recognise on sight: `GRANT SELECT, INSERT, UPDATE, DELETE ON ticket_desk.* TO 'desk_app'@'%';`
- Claims:
  - An account is the pair user@host, and two accounts with the same user and different hosts are distinct — [MySQL 9.7 Specifying Account Names](https://dev.mysql.com/doc/refman/9.7/en/account-names.html)
  - CREATE USER ... IDENTIFIED BY sets the password; since MySQL 8 GRANT no longer creates accounts — [MySQL 9.7 CREATE USER](https://dev.mysql.com/doc/refman/9.7/en/create-user.html)
  - Privileges can be granted at global, database, table, column and routine levels — [MySQL 9.7 GRANT](https://dev.mysql.com/doc/refman/9.7/en/grant.html)
  - SHOW GRANTS FOR 'desk_app'@'%' lists the privileges of one account — [MySQL 9.7 SHOW GRANTS](https://dev.mysql.com/doc/refman/9.7/en/show-grants.html)
  - A statement without the privilege fails with "command denied to user" (ERROR 1142) — [MySQL 9.7 Privileges Provided by MySQL](https://dev.mysql.com/doc/refman/9.7/en/privileges-provided.html)

### TCL
- Interview questions: What do COMMIT and ROLLBACK do?; What is autocommit?; What does a SAVEPOINT add?; Can you roll back a DROP TABLE?
- Adjacent concept: Autocommit — why a DELETE you did not wrap in START TRANSACTION is already permanent; the guarantees a transaction makes are a later day's subject.
- Trade-off or limit: Only InnoDB tables take part in a transaction, and a DDL or account statement inside one commits it implicitly, so a ROLLBACK after it restores nothing (a talking point on this page, not a demo step) — [MySQL 9.7 Statements That Cause an Implicit Commit](https://dev.mysql.com/doc/refman/9.7/en/implicit-commit.html)
- Recognise on sight: `START TRANSACTION; DELETE FROM tickets; ROLLBACK;`
- Claims:
  - autocommit defaults to 1 (on); START TRANSACTION turns it off until COMMIT or ROLLBACK — [MySQL 9.7 START TRANSACTION, COMMIT, and ROLLBACK](https://dev.mysql.com/doc/refman/9.7/en/commit.html)
  - ROLLBACK after a DELETE restores the deleted rows, and SELECT shows them again — [MySQL 9.7 START TRANSACTION, COMMIT, and ROLLBACK](https://dev.mysql.com/doc/refman/9.7/en/commit.html)
  - ROLLBACK TO SAVEPOINT name keeps the transaction open and the earlier work intact — [MySQL 9.7 SAVEPOINT](https://dev.mysql.com/doc/refman/9.7/en/savepoint.html)
  - Closing the client mid-transaction rolls the transaction back — [MySQL 9.7 START TRANSACTION, COMMIT, and ROLLBACK](https://dev.mysql.com/doc/refman/9.7/en/commit.html)

### Overview of sublanguages
- Interview questions: Name the sublanguages of SQL and one statement for each. (qc2.sql.R02); Which statements can ROLLBACK undo? (qc2.sql.R02); Where does SELECT sit?
- Adjacent concept: Sorting the week's statements by what they act on (structure, rows, reads, permissions, transactions) — a classification habit that carries to any database.
- Trade-off or limit: The grouping is a teaching convention, and the MySQL manual files statements by function rather than by DDL/DML labels — [MySQL 9.7 SQL Statements](https://dev.mysql.com/doc/refman/9.7/en/sql-statements.html)
- Recognise on sight: A question that lists CREATE, GRANT, SELECT, INSERT, COMMIT and asks which sublanguage each belongs to.
- Claims:
  - DDL: CREATE, ALTER, DROP, TRUNCATE — [MySQL 9.7 Data Definition Statements](https://dev.mysql.com/doc/refman/9.7/en/sql-data-definition-statements.html)
  - DML: INSERT, UPDATE, DELETE — [MySQL 9.7 Data Manipulation Statements](https://dev.mysql.com/doc/refman/9.7/en/sql-data-manipulation-statements.html)
  - DCL: GRANT, REVOKE (account statements) — [MySQL 9.7 Account Management Statements](https://dev.mysql.com/doc/refman/9.7/en/account-management-statements.html)
  - TCL: START TRANSACTION, COMMIT, ROLLBACK, SAVEPOINT — [MySQL 9.7 Transactional and Locking Statements](https://dev.mysql.com/doc/refman/9.7/en/sql-transactional-statements.html)

### Getting ready for your interview - 2nd part
- Interview questions: Explain DROP against DELETE against TRUNCATE. (qc2.sql.R07); What does a GRANT do? (qc2.sql.R02); What does ROLLBACK undo and what can it not undo? (qc2.sql.R02)
- Adjacent concept: Answer shape — one-sentence definition, one example statement, one limit — because spoken answers are scored on structure.
- Trade-off or limit: An answer that says "TRUNCATE is just a fast DELETE" misses that it is DDL, resets AUTO_INCREMENT and cannot roll back — [MySQL 9.7 TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
- Recognise on sight: A comparison table with columns Statement, Sublanguage, Removes, WHERE allowed, Rolls back, AUTO_INCREMENT.
- Claims:
  - DROP removes structure and data, DELETE removes rows with WHERE, TRUNCATE removes all rows and keeps structure — [MySQL 9.7 DROP TABLE](https://dev.mysql.com/doc/refman/9.7/en/drop-table.html)
  - TRUNCATE takes no WHERE clause — [MySQL 9.7 TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
  - DELETE can take WHERE and so removes a chosen subset — [MySQL 9.7 DELETE](https://dev.mysql.com/doc/refman/9.7/en/delete.html)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- MySQL 9.7 CREATE TABLE — https://dev.mysql.com/doc/refman/9.7/en/create-table.html
- MySQL 9.7 ALTER TABLE — https://dev.mysql.com/doc/refman/9.7/en/alter-table.html
- MySQL 9.7 DROP TABLE — https://dev.mysql.com/doc/refman/9.7/en/drop-table.html
- MySQL 9.7 TRUNCATE TABLE — https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html
- MySQL 9.7 DELETE — https://dev.mysql.com/doc/refman/9.7/en/delete.html
- MySQL 9.7 INSERT — https://dev.mysql.com/doc/refman/9.7/en/insert.html
- MySQL 9.7 UPDATE — https://dev.mysql.com/doc/refman/9.7/en/update.html
- MySQL 9.7 SELECT — https://dev.mysql.com/doc/refman/9.7/en/select.html
- MySQL 9.7 CREATE USER — https://dev.mysql.com/doc/refman/9.7/en/create-user.html
- MySQL 9.7 GRANT — https://dev.mysql.com/doc/refman/9.7/en/grant.html
- MySQL 9.7 REVOKE — https://dev.mysql.com/doc/refman/9.7/en/revoke.html
- MySQL 9.7 SHOW GRANTS — https://dev.mysql.com/doc/refman/9.7/en/show-grants.html
- MySQL 9.7 START TRANSACTION, COMMIT, and ROLLBACK — https://dev.mysql.com/doc/refman/9.7/en/commit.html
- MySQL 9.7 Statements That Cause an Implicit Commit — https://dev.mysql.com/doc/refman/9.7/en/implicit-commit.html
- MySQL 9.7 SAVEPOINT — https://dev.mysql.com/doc/refman/9.7/en/savepoint.html
- MySQL 9.7 SQL Statements — https://dev.mysql.com/doc/refman/9.7/en/sql-statements.html
- MySQL 9.7 Data Definition Statements — https://dev.mysql.com/doc/refman/9.7/en/sql-data-definition-statements.html
- MySQL 9.7 Data Manipulation Statements — https://dev.mysql.com/doc/refman/9.7/en/sql-data-manipulation-statements.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- DDL | Data Definition Language: the SQL statements (CREATE, ALTER, DROP, TRUNCATE) that define or change the structure of tables and databases. | aka: data definition language
- DML | Data Manipulation Language: the SQL statements (INSERT, UPDATE, DELETE) that add, change or remove the rows inside tables. | aka: data manipulation language
- DQL | Data Query Language: the SQL statement SELECT, which reads rows without changing them. | aka: data query language
- DCL | Data Control Language: the SQL statements (GRANT, REVOKE) that give or take away what an account may do. | aka: data control language, GRANT, REVOKE
- TCL | Transaction Control Language: the SQL statements (START TRANSACTION, COMMIT, ROLLBACK, SAVEPOINT) that group changes so they apply or vanish together. | aka: transaction control language, rollback, savepoint
- autocommit | The MySQL default in which every statement outside a transaction is saved the moment it runs. | aka: auto-commit
- least privilege | Giving an account only the permissions its job needs, so a mistake or a leaked password does less damage. | aka: principle of least privilege

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Running UPDATE or DELETE without WHERE, which changes or removes every row, and assuming ROLLBACK will help when autocommit already saved it.
- Calling TRUNCATE "a fast DELETE" and expecting to roll it back: it is DDL, commits implicitly and resets AUTO_INCREMENT.
- Expecting ROLLBACK to undo a DROP TABLE, ALTER TABLE or GRANT, because DDL and account statements commit implicitly.
- Writing the account as 'desk_app' without the host part, or granting on `ticket_desk` instead of `ticket_desk.*`, so the login or the privilege does not match.
- Forgetting the semicolon at the mysql> prompt (the `->` continuation prompt waits) and typing a string with double quotes or a missing closing quote.
- Trusting SELECT * in application code, so a later ALTER TABLE silently changes the columns the code receives.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- `03-ddl-and-dml` (AM, 85 min, opens `feature/desk-sql`), DDL steps: at `mysql>` on the throwaway `scratch_notes` only, CREATE TABLE, ALTER TABLE ADD COLUMN and DROP COLUMN (MODIFY and RENAME COLUMN are cut-first), DESCRIBE after the changes, an INSERT of two rows, TRUNCATE with `SELECT * FROM scratch_notes;` showing the empty table kept, then DROP and `SHOW TABLES;` showing it gone; the break (15) falls here, before `seed.sql`.
- `03-ddl-and-dml`, DML step: the new file `sql/seed.sql` (`USE ticket_desk;` and three column-listed multi-row INSERTs with every id written out) loads four customers, four agents and the six week-2 tickets through `docker exec -i desk-mysql mysql -uroot -pdesk < sql/seed.sql`, and the block commits "Seed the desk tables with INSERT statements" at `SELECT * FROM tickets;` showing six rows; the DROP-DELETE-TRUNCATE comparison is not run here, it opens Facilitation: Getting ready for your interview - 2nd part as its first question.
- `04-dql-dcl-tcl` (PM, 70 min): Step 1 is the prompt DML moved from 03 (`UPDATE tickets SET title = 'Add a dark mode' WHERE ticket_id = 6;`, a second ticket 1 that loads and `SELECT * FROM tickets WHERE ticket_id = 1;` showing two rows, `DELETE FROM tickets WHERE ticket_id = 1 AND status = 'open';`); then DQL with column lists and `WHERE ... = ...`; `sql/users.sql` creating `'desk_app'@'%'` IDENTIFIED BY 'deskapp' with SELECT, INSERT, UPDATE, DELETE on `ticket_desk.*`, SHOW GRANTS, the login `docker exec -it desk-mysql mysql -udesk_app -p ticket_desk`, an allowed SELECT and the refused `DROP TABLE tickets;` (ERROR 1142), and the commit "Add a desk_app account with limited grants" (the REVOKE round trip is cut-first).
- `04-dql-dcl-tcl`, after the break: `SELECT @@autocommit;`, START TRANSACTION, `DELETE FROM tickets;`, SELECT showing no rows, ROLLBACK, SELECT showing the rows back (the SAVEPOINT pair is cut-first and named; the notes carry it); then `git switch main`, `git merge feature/desk-sql`, `git push origin main` (may slide to 05-keys-and-constraints Step 1).
