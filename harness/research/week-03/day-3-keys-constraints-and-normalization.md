# w03d3 — Keys, constraints & normalization

gate: light
verified: 2026-10-23
week: 3 · SQL with MySQL
day: 3 · keys-constraints-and-normalization

version-stamps:
  - python: 3.15 (verified 2026-10-23)
  - mysql: 9.7 LTS, image tag mysql:9.7 (verified 2026-10-23)
  - mysql-connector-python: 26.7.0 (verified 2026-10-23) — mysql_connector_python-26.7.0-py2.py3-none-any.whl, pure Python, on 3.15
  - pytest: 9.1.1 (verified 2026-10-23) — pytest-9.1.1-py3-none-any.whl

## Claims

- A PRIMARY KEY column set must be unique and NOT NULL, and a table has at most one primary key — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- A composite primary key lists several columns in one PRIMARY KEY clause; the combination must be unique, not each column — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- InnoDB enforces foreign keys; the referenced columns must be the parent's primary key or a unique key, and the child column must have a compatible type — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- ON DELETE CASCADE deletes child rows when the parent row is deleted; the default (RESTRICT / NO ACTION) refuses the parent delete — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- A foreign key violation on a child insert is error 1452 and on a parent delete is error 1451, both raised as mysql.connector.IntegrityError — [MySQL Connector/Python: errors.IntegrityError](https://dev.mysql.com/doc/connector-python/en/connector-python-api-errors-integrityerror.html)
- A UNIQUE constraint refuses a duplicate value but, for every engine, permits several NULLs in a column that can hold NULL — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- CHECK constraints are enforced (since 8.0.16, so on 9.7); a violating write fails with error 3819 — [MySQL Reference Manual: CHECK Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-check-constraints.html)
- DEFAULT supplies a column value when an INSERT omits the column — [MySQL Reference Manual: Data Type Default Values](https://dev.mysql.com/doc/refman/9.7/en/data-type-defaults.html)
- AUTO_INCREMENT generates the next integer for a key column (normally the primary key) when the INSERT omits it — [MySQL Reference Manual: Using AUTO_INCREMENT](https://dev.mysql.com/doc/refman/9.7/en/example-auto-increment.html)
- InnoDB can hand out an auto-increment value that a failed insert then discards, so ids can have gaps — [MySQL Reference Manual: AUTO_INCREMENT Handling in InnoDB](https://dev.mysql.com/doc/refman/9.7/en/innodb-auto-increment-handling.html)
- BIGINT holds up to 9223372036854775807 signed, against 2147483647 for INT — [MySQL Reference Manual: Integer Types](https://dev.mysql.com/doc/refman/9.7/en/integer-types.html)
- TRUNCATE TABLE empties a table, resets its AUTO_INCREMENT counter, causes an implicit commit and is refused on a table another table's foreign key references — [MySQL Reference Manual: TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
- DROP DATABASE IF EXISTS removes a database and all its tables without an error when it is missing, which makes a rebuild script repeatable — [MySQL Reference Manual: DROP DATABASE](https://dev.mysql.com/doc/refman/9.7/en/drop-database.html)
- An UPDATE or DELETE without WHERE touches every row — [MySQL Reference Manual: UPDATE](https://dev.mysql.com/doc/refman/9.7/en/update.html)
- Connector cursors take values as a tuple with %s placeholders, and conn.commit() ends the transaction — [MySQL Connector/Python: MySQLCursor.execute()](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html)
- A table declared with no PRIMARY KEY and no UNIQUE key accepts two identical rows, which is how Tuesday's second ticket 1 got in — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)

## Notes depth

### Primary key
- Interview questions: What does a primary key guarantee? (qc2.sql.R03); What makes a column set a valid candidate key? (qc2.sql.P01); Natural versus surrogate key, which would you choose for email? (qc2.sql.S02)
- Adjacent concept: Candidate key — every minimal unique, non-null column set is a candidate; one becomes primary and the others become alternate keys.
- Trade-off or limit: A natural primary key that can change (an email) forces every foreign key that references it to change too, so the desk keys customers on a short integer that never changes — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Recognise on sight: `ticket_id INT AUTO_INCREMENT PRIMARY KEY` or `PRIMARY KEY (ticket_id)` at the end of a CREATE TABLE.
- Claims: A table without a PRIMARY KEY accepts duplicate rows, which is how Tuesday's second ticket 1 got into `tickets` — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: A primary key column is implicitly NOT NULL — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: Inserting a duplicate primary key raises error 1062 (Duplicate entry ... for key 'PRIMARY'), which is what refuses Tuesday's second ticket 1 — [MySQL Error Reference: Server Error Message Reference](https://dev.mysql.com/doc/mysql-errors/9.7/en/server-error-reference.html)
- Claims: A table has at most one PRIMARY KEY — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)

### Composite key
- Interview questions: What is a composite key and when do you need one? (qc2.sql.S02); Why is ticket_tags keyed on (ticket_id, tag_id) instead of its own id? (qc2.sql.S04); How would another table reference a row of a table whose primary key is composite?
- Adjacent concept: Bridge table — a composite key of two foreign keys is the standard shape for a many-to-many link.
- Trade-off or limit: A foreign key must name the same columns as the key it references, so a composite primary key makes every foreign key that points at it two columns wide — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Recognise on sight: `PRIMARY KEY (ticket_id, tag_id)` on a table of two foreign keys.
- Claims: Uniqueness applies to the pair, so (1, 2) and (1, 3) can both exist but (1, 2) twice cannot — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: Every column of a composite primary key is NOT NULL — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: A composite key makes a duplicate link row impossible, which a lone generated id column would allow — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)

### Foreign key
- Interview questions: What does a foreign key do? (qc2.sql.R08); What must be true of the parent column? (qc2.sql.R08); Can a foreign key be NULL, and what does that mean?
- Adjacent concept: Referential integrity — the foreign key is the mechanism that enforces it.
- Trade-off or limit: Foreign keys add a check on every write to the child and every delete or key change in the parent, which costs time on heavy writes — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Recognise on sight: `FOREIGN KEY (customer_id) REFERENCES customers (customer_id)`.
- Claims: A NULL foreign key value is allowed unless the column is NOT NULL, and means no parent (a ticket with no agent) — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: The parent table must exist before a child table that references it is created; otherwise CREATE TABLE fails with ERROR 1824 Failed to open the referenced table — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: Foreign keys are enforced by InnoDB, the default engine — [MySQL Reference Manual: The InnoDB Storage Engine](https://dev.mysql.com/doc/refman/9.7/en/innodb-storage-engine.html)

### Referential integrity
- Interview questions: Describe referential integrity (qc2.sql.R16); What happens when you delete a customer who has tickets? (qc2.sql.R16); What are the referential actions?
- Adjacent concept: Orphan row — a child whose parent no longer exists, the failure integrity prevents.
- Trade-off or limit: RESTRICT protects data but forces the caller to delete children first; CASCADE is convenient but can delete far more than intended — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Recognise on sight: ERROR 1452 Cannot add or update a child row; ERROR 1451 Cannot delete or update a parent row.
- Claims: Referential actions are CASCADE, SET NULL, RESTRICT, NO ACTION and SET DEFAULT (the last is rejected by InnoDB) — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: Inserting a child with an unknown parent id fails with 1452 — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: The connector raises mysql.connector.IntegrityError for both 1451 and 1452 — [MySQL Connector/Python: errors.IntegrityError](https://dev.mysql.com/doc/connector-python/en/connector-python-api-errors-integrityerror.html)

### Unique key
- Interview questions: Difference between PRIMARY KEY and UNIQUE? (qc2.sql.R05); Can a UNIQUE column hold NULL? (qc2.sql.R05); Why make email unique?
- Adjacent concept: Natural key versus surrogate key — email is a natural key kept unique beside a generated `customer_id`, and the interviewer asks why it is not the primary key.
- Trade-off or limit: UNIQUE permits several NULLs in a nullable column, so on its own it does not promise every row has a value; pair it with NOT NULL when the column must identify a row — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Recognise on sight: `email VARCHAR(100) NOT NULL UNIQUE` or `UNIQUE KEY uq_email (email)`.
- Claims: A table can have many UNIQUE keys but one PRIMARY KEY — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: For every engine, UNIQUE allows multiple NULLs in a column that can hold NULL — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: A duplicate in a UNIQUE column raises 1062 — [MySQL Error Reference: Server Error Message Reference](https://dev.mysql.com/doc/mysql-errors/9.7/en/server-error-reference.html)

### Secondary alternate key
- Interview questions: What is an alternate key? (qc2.sql.P01); How does it differ from a candidate key? (qc2.sql.S02); When would you choose email over an id as the primary key?
- Adjacent concept: Candidate key — an alternate key is a candidate key that was not chosen as primary, so naming the candidates is the first step to naming the alternates.
- Trade-off or limit: Choosing the alternate key (email) as the primary key instead would copy it into every child row as a foreign key, so a changed email would have to change in each child or be carried by ON UPDATE CASCADE — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Recognise on sight: A `customers` table with `customer_id` as primary key and `email ... NOT NULL UNIQUE` beside it.
- Claims: Every candidate key not chosen as primary is an alternate key; in MySQL it is declared UNIQUE NOT NULL — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: On the desk, `customer_id` and `email` each pick out exactly one customer, so both are candidate keys; `customer_id` is primary and `email` is the alternate key — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: A surrogate id keeps foreign keys short and stable when the natural key (email) changes — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)

### Normalization
- Interview questions: Walk a table from 0NF to 3NF with a reason per step (qc2.sql.R15); What is the benefit and the cost of normalising? (qc2.sql.P08); How do you design a valid schema for a flat data set? (qc2.sql.R09)
- Adjacent concept: Denormalisation — deliberately repeating data to save reads, after measuring; reporting tables do it.
- Trade-off or limit: Normalising stores each fact once in a parent table that children reference by key, which removes update, insert and delete anomalies; the cost (course guidance) is more tables and a join to read one record back whole — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Recognise on sight: a comma-separated column such as `tags = 'login,billing'` (breaks 1NF: every column holds one value and there are no repeating groups, so the tag list becomes one row per tag); a column that depends on only part of a composite key, such as a tag's name in `ticket_tags` (breaks 2NF: a 1NF table whose non-key columns depend on the whole key, so `ticket_tags` keeps only (ticket_id, tag_id) and the name lives in `tags`); `sla_hours` or `customer_email` stored beside `priority` or `customer_id` in tickets (breaks 3NF: a 2NF table where no non-key column depends on another non-key column, so `sla_hours` moves to `priorities` and the name and email to `customers`). These are the course's definitions; no manual page defines the normal forms.
- Claims: A foreign key compares a column's whole value with a parent key, so a comma list such as 'login,billing' can never reference `tags`, while one tag per row can — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: A CHECK or UNIQUE constraint applies to a column's whole value, so a fact repeated across rows (an email on every ticket) can drift out of agreement, which a single parent row prevents — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: A lookup table referenced by a foreign key refuses a value it does not hold (ERROR 1452), so `priorities` replaces the `sla_hours` repeated on every ticket and an unknown priority such as 'urgent' cannot be stored — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: A parent row that child rows still reference cannot be deleted (ERROR 1451) unless the foreign key names an ON DELETE action, so a customer with tickets cannot vanish under them, and because the customer now has its own row, deleting a customer's last ticket no longer erases the customer (the flat sheet's delete anomaly) — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)

### Multiplicity
- Interview questions: Explain one-to-one, one-to-many and many-to-many with examples (qc2.sql.P03); How is each implemented in tables? (qc2.sql.P03); Why does many-to-many need a bridge table? (qc2.sql.S04)
- Adjacent concept: Cardinality in an ERD — Monday's crow's-foot line ends say how many rows sit on each side.
- Trade-off or limit: A foreign key column holds one parent value per row, so it can express one-to-many directly but many-to-many only through a third table — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Recognise on sight: a table of two foreign keys and a composite key over them (bridge); a foreign key that is also UNIQUE (one-to-one).
- Claims: One-to-many puts the foreign key on the many side (tickets.customer_id) — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: Many-to-many needs a bridge table whose composite primary key is its two foreign keys (ticket_tags) — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: Declaring a foreign key column UNIQUE allows each parent at most one child, which makes the relationship one-to-one — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)

### Consistency
- Interview questions: What does consistency mean in a database? (qc2.sql.R05); How do constraints keep data consistent? (qc2.sql.R05); Where else is consistency enforced besides the database?
- Adjacent concept: Strict SQL mode — with STRICT_TRANS_TABLES on (the default) an invalid or missing value is an error instead of a silent adjustment, so constraints and types refuse bad rows rather than bend them.
- Trade-off or limit: Rules in the database hold for every client; rules only in application code can be bypassed by another writer — [MySQL Reference Manual: How MySQL Deals with Constraints](https://dev.mysql.com/doc/refman/9.7/en/constraints.html)
- Recognise on sight: validation repeated in Python that the schema already enforces with NOT NULL or CHECK.
- Claims: The server refuses a statement that violates a constraint and, in InnoDB, rolls back that statement — [MySQL Reference Manual: How MySQL Deals with Constraints](https://dev.mysql.com/doc/refman/9.7/en/constraints.html)
- Claims: In strict SQL mode an invalid value is an error rather than a silent adjustment — [MySQL Reference Manual: Server SQL Modes](https://dev.mysql.com/doc/refman/9.7/en/sql-mode.html)
- Claims: Declared constraints are the schema's statement of which data is valid — [MySQL Reference Manual: How MySQL Deals with Constraints](https://dev.mysql.com/doc/refman/9.7/en/constraints.html)

### CREATE DROP TRUNCATE
- Interview questions: Difference between DROP, DELETE and TRUNCATE?; Why does the rebuild begin with DROP DATABASE IF EXISTS and create parents before children? (qc2.sql.R09); Why can't you TRUNCATE a table a foreign key points to?
- Adjacent concept: Implicit commit — DDL statements commit the current transaction and cannot be rolled back.
- Trade-off or limit: TRUNCATE is fast and resets the counter but cannot be rolled back and takes no WHERE — [MySQL Reference Manual: TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
- Recognise on sight: `DROP DATABASE IF EXISTS ticket_desk;` then `CREATE DATABASE ticket_desk;` at the top of schema.sql.
- Claims: DROP TABLE removes structure and rows — [MySQL Reference Manual: DROP TABLE](https://dev.mysql.com/doc/refman/9.7/en/drop-table.html)
- Claims: TRUNCATE TABLE fails on a table referenced by another table's foreign key — [MySQL Reference Manual: TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
- Claims: CREATE TABLE IF NOT EXISTS skips creation when the table exists, which hides a stale structure; the rebuild drops it — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)

### Constraints
- Interview questions: Name the SQL constraints and what each does (qc2.sql.R05); Which constraints sit on a column and which on a table? (qc2.sql.R05); How do you add a constraint later?
- Adjacent concept: Named constraints — a name makes its error and its removal readable.
- Trade-off or limit: Constraints cost a check per write but move the rule to one place — [MySQL Reference Manual: How MySQL Deals with Constraints](https://dev.mysql.com/doc/refman/9.7/en/constraints.html)
- Recognise on sight: `NOT NULL`, `UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, `DEFAULT` in a column list.
- Claims: NOT NULL refuses NULL, and an INSERT that omits a NOT NULL column with no default fails in strict mode — [MySQL Reference Manual: Data Type Default Values](https://dev.mysql.com/doc/refman/9.7/en/data-type-defaults.html)
- Claims: A column constraint applies to one column; a table constraint can span several — [MySQL Reference Manual: CREATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/create-table.html)
- Claims: Constraints can be named with CONSTRAINT name, and ALTER TABLE adds or drops one later — [MySQL Reference Manual: ALTER TABLE](https://dev.mysql.com/doc/refman/9.7/en/alter-table.html)

### Auto incrementing
- Interview questions: What does AUTO_INCREMENT do? (qc2.sql.R05); Why would you use BIGINT for an event log id? (qc2.sql.S03); Why are there gaps in the ids?
- Adjacent concept: The id counter survives DELETE but not TRUNCATE — deleting every row keeps the next id where it was, while TRUNCATE resets it to the start.
- Trade-off or limit: An INT id overflows at 2147483647 signed; BIGINT delays that for log-like tables such as ticket_events — [MySQL Reference Manual: Integer Types](https://dev.mysql.com/doc/refman/9.7/en/integer-types.html)
- Recognise on sight: `event_id BIGINT AUTO_INCREMENT PRIMARY KEY`.
- Claims: Omitting the id or inserting NULL makes the server generate the next value — [MySQL Reference Manual: Using AUTO_INCREMENT](https://dev.mysql.com/doc/refman/9.7/en/example-auto-increment.html)
- Claims: Gaps appear after failed inserts and rollbacks, because InnoDB hands the value out before the row is checked — [MySQL Reference Manual: AUTO_INCREMENT Handling in InnoDB](https://dev.mysql.com/doc/refman/9.7/en/innodb-auto-increment-handling.html)
- Claims: TRUNCATE TABLE resets the AUTO_INCREMENT counter to its start value — [MySQL Reference Manual: TRUNCATE TABLE](https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html)
- Claims: cursor.lastrowid in the connector returns the id the last INSERT generated — [MySQL Connector/Python: MySQLCursor.lastrowid](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-lastrowid.html)

### CHECK
- Interview questions: What does a CHECK constraint do? (qc2.sql.R05); Give a CHECK for the desk's status column (qc2.sql.R05); What happens on violation?
- Adjacent concept: A lookup table with a foreign key as the alternative to a CHECK list — `priorities` holds the allowed priorities as rows, so adding one is an INSERT, not a schema change, while `status` keeps a CHECK list.
- Trade-off or limit: A CHECK cannot use subqueries or read other tables; use a foreign key to a lookup table for that — [MySQL Reference Manual: CHECK Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-check-constraints.html)
- Recognise on sight: `CHECK (status IN ('open', 'assigned', 'closed'))` or `CHECK (monthly_fee >= 0)`.
- Claims: A violating INSERT or UPDATE fails with error 3819 — [MySQL Reference Manual: CHECK Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-check-constraints.html)
- Claims: The connector raises DatabaseError for 3819, not IntegrityError — [MySQL Connector/Python: errors.DatabaseError](https://dev.mysql.com/doc/connector-python/en/connector-python-api-errors-databaseerror.html)
- Claims: A CHECK that evaluates to NULL passes, so pair it with NOT NULL — [MySQL Reference Manual: CHECK Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-check-constraints.html)

### DEFAULT
- Interview questions: What does DEFAULT do? (qc2.sql.R05); How do you give a status column a starting value? (qc2.sql.R05); Difference between DEFAULT and NOT NULL?
- Adjacent concept: NOT NULL paired with DEFAULT — NOT NULL says a value must be there and DEFAULT says which one the server fills in when the INSERT leaves the column out (`status ... NOT NULL DEFAULT 'open'`).
- Trade-off or limit: A default hides an omitted value instead of flagging it, so choose defaults that are truly sensible — [MySQL Reference Manual: Data Type Default Values](https://dev.mysql.com/doc/refman/9.7/en/data-type-defaults.html)
- Recognise on sight: `status VARCHAR(10) NOT NULL DEFAULT 'open'`, `country CHAR(2) NOT NULL DEFAULT 'CA'`.
- Claims: A default applies only when the column is omitted from the INSERT (or the keyword DEFAULT is written as its value) — [MySQL Reference Manual: Data Type Default Values](https://dev.mysql.com/doc/refman/9.7/en/data-type-defaults.html)
- Claims: An explicit NULL into a NOT NULL DEFAULT column is an error, not the default — [MySQL Reference Manual: Data Type Default Values](https://dev.mysql.com/doc/refman/9.7/en/data-type-defaults.html)
- Claims: A DATETIME column may take a value-of-now default, which `ticket_events.created_at` uses — [MySQL Reference Manual: Automatic Initialization and Updating for TIMESTAMP and DATETIME](https://dev.mysql.com/doc/refman/9.7/en/timestamp-initialization.html)

### CASCADE
- Interview questions: What does ON DELETE CASCADE do? (qc2.sql.P09); When is CASCADE dangerous? (qc2.sql.P09); ON DELETE SET NULL versus CASCADE?
- Adjacent concept: ON UPDATE CASCADE — propagates a changed parent key to the children.
- Trade-off or limit: A cascade can delete a whole tree of child rows in one statement, and the client reports only the parent row as affected — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Recognise on sight: `FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id) ON DELETE CASCADE`.
- Claims: Deleting a ticket removes its ticket_tags and ticket_events rows when both keys cascade — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: Without an ON DELETE action the parent delete is refused with 1451 — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: ON DELETE SET NULL keeps the child and clears its foreign key, which the desk uses for `tickets.agent_id` — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: Cascades run inside the same statement and roll back with it — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)

### INSERT
- Interview questions: Write an INSERT with a column list; Why pass values as %s placeholders instead of an f-string?; How do you insert several rows at once?
- Adjacent concept: SQL injection — what an f-string in a query allows.
- Trade-off or limit: Without a column list, an INSERT breaks when the table gains a column — [MySQL Reference Manual: INSERT](https://dev.mysql.com/doc/refman/9.7/en/insert.html)
- Recognise on sight: `cursor.execute("INSERT INTO tickets (...) VALUES (%s, %s)", (a, b))` then `conn.commit()`.
- Claims: INSERT with several VALUES tuples inserts many rows in one statement — [MySQL Reference Manual: INSERT](https://dev.mysql.com/doc/refman/9.7/en/insert.html)
- Claims: Connector placeholders are %s whatever the value type, and the driver escapes the values — [MySQL Connector/Python: MySQLCursor.execute()](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html)
- Claims: With autocommit off nothing is saved until conn.commit() — [MySQL Connector/Python: MySQLConnection.commit()](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-commit.html)

### UPDATE
- Interview questions: Write an UPDATE that closes one ticket; What happens if you leave out WHERE?; What does rowcount return for an UPDATE to the same value?
- Adjacent concept: Safe-update habit — run the WHERE as a SELECT first.
- Trade-off or limit: An UPDATE with no WHERE rewrites every row — [MySQL Reference Manual: UPDATE](https://dev.mysql.com/doc/refman/9.7/en/update.html)
- Recognise on sight: `UPDATE tickets SET status = %s, closed_at = %s WHERE ticket_id = %s`.
- Claims: UPDATE reports changed rows, so setting a value to itself reports 0 — [MySQL Reference Manual: UPDATE](https://dev.mysql.com/doc/refman/9.7/en/update.html)
- Claims: SET assigns several columns separated by commas — [MySQL Reference Manual: UPDATE](https://dev.mysql.com/doc/refman/9.7/en/update.html)
- Claims: An UPDATE that breaks a CHECK or foreign key fails and changes nothing — [MySQL Reference Manual: CHECK Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-check-constraints.html)

### DELETE
- Interview questions: Write a DELETE for one ticket; DELETE versus TRUNCATE?; What does DELETE do to child rows?
- Adjacent concept: Soft delete — a status flag instead of removing the row, to keep history.
- Trade-off or limit: DELETE removes rows one by one and is slower than TRUNCATE on a big table, but it takes a WHERE and can be rolled back — [MySQL Reference Manual: DELETE](https://dev.mysql.com/doc/refman/9.7/en/delete.html)
- Recognise on sight: `DELETE FROM tickets WHERE ticket_id = %s`.
- Claims: DELETE without WHERE removes every row but keeps the structure and the AUTO_INCREMENT counter — [MySQL Reference Manual: DELETE](https://dev.mysql.com/doc/refman/9.7/en/delete.html)
- Claims: A parent DELETE is refused (1451) or cascades, by the foreign key action — [MySQL Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html)
- Claims: cursor.rowcount after DELETE counts the rows removed — [MySQL Connector/Python: MySQLCursor.rowcount](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-rowcount.html)

## Sources

- MySQL Reference Manual: CREATE TABLE — https://dev.mysql.com/doc/refman/9.7/en/create-table.html
- MySQL Reference Manual: FOREIGN KEY Constraints — https://dev.mysql.com/doc/refman/9.7/en/create-table-foreign-keys.html
- MySQL Reference Manual: CHECK Constraints — https://dev.mysql.com/doc/refman/9.7/en/create-table-check-constraints.html
- MySQL Reference Manual: How MySQL Deals with Constraints — https://dev.mysql.com/doc/refman/9.7/en/constraints.html
- MySQL Reference Manual: Server SQL Modes — https://dev.mysql.com/doc/refman/9.7/en/sql-mode.html
- MySQL Reference Manual: Using AUTO_INCREMENT — https://dev.mysql.com/doc/refman/9.7/en/example-auto-increment.html
- MySQL Reference Manual: AUTO_INCREMENT Handling in InnoDB — https://dev.mysql.com/doc/refman/9.7/en/innodb-auto-increment-handling.html
- MySQL Reference Manual: Data Type Default Values — https://dev.mysql.com/doc/refman/9.7/en/data-type-defaults.html
- MySQL Reference Manual: Integer Types — https://dev.mysql.com/doc/refman/9.7/en/integer-types.html
- MySQL Reference Manual: TRUNCATE TABLE — https://dev.mysql.com/doc/refman/9.7/en/truncate-table.html
- MySQL Reference Manual: DROP DATABASE — https://dev.mysql.com/doc/refman/9.7/en/drop-database.html
- MySQL Reference Manual: INSERT — https://dev.mysql.com/doc/refman/9.7/en/insert.html
- MySQL Reference Manual: UPDATE — https://dev.mysql.com/doc/refman/9.7/en/update.html
- MySQL Reference Manual: DELETE — https://dev.mysql.com/doc/refman/9.7/en/delete.html
- MySQL Error Reference: Server Error Message Reference — https://dev.mysql.com/doc/mysql-errors/9.7/en/server-error-reference.html
- MySQL Connector/Python Developer Guide — https://dev.mysql.com/doc/connector-python/en/
- MySQL Connector/Python: MySQLCursor.execute() — https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html

## Glossary terms

- composite key | A primary key made of two or more columns whose combination, not each column, must be unique. | aka: composite primary key, compound key
- candidate key | A minimal set of columns that could uniquely identify a row, from which one is chosen as the primary key. | aka: candidate keys
- alternate key | A candidate key not chosen as the primary key, declared UNIQUE NOT NULL. | aka: alternate keys, secondary key
- referential integrity | The guarantee that every foreign key value matches an existing parent row or is NULL. | aka: foreign key integrity
- constraint | A rule declared on a table that the database enforces on every write. | aka: integrity constraint
- cascade | A foreign key action that applies a parent's delete or update to its child rows. | aka: ON DELETE CASCADE, cascading delete
- bridge table | A table of two foreign keys that links two tables in a many-to-many relationship. | aka: junction table, link table, association table
- surrogate key | A meaningless generated id used as the primary key instead of a real-world value. | aka: surrogate id

## Common pitfalls

- Making email or another changeable natural value the primary key, then having to update every foreign key that points at it.
- Creating a child table before its parent (ERROR 1824 Failed to open the referenced table) or inserting a child row before its parent row (ERROR 1452); a child column whose type does not match the parent key is a separate refusal at CREATE TABLE.
- Expecting a CHECK to catch NULL, or catching IntegrityError for a CHECK failure when the connector raises DatabaseError.
- Calling TRUNCATE on a table a foreign key references, or using DELETE and expecting AUTO_INCREMENT to restart.
- Forgetting conn.commit() after an INSERT, UPDATE or DELETE in Python, so another session never sees the row.
- Building SQL with an f-string instead of %s placeholders.

## Demo plan hints

- 05-keys-and-constraints: Step 1 retakes the flat ticket sheet from 0NF to 3NF with one reason per form and types four comment lines into `sql/schema.sql`, `-- 1NF` above `tags`, `-- 2NF` above `ticket_tags`, `-- 3NF` above `priorities` and `-- 3NF` above `customers`; then the rebuild (cat schema.sql seed.sql piped to docker exec) runs before any constraint error, and Tuesday's duplicate ticket 1 is now refused by the primary key (ERROR 1062).
- 05-keys-and-constraints: provoke each refusal at the prompt against the known-good rebuild: unknown priority (1452), delete of a parent (1451), duplicate email (1062 on the UNIQUE key), CHECK (3819), NOT NULL, then show CASCADE removing a ticket's ticket_tags rows and TRUNCATE refused on a referenced table; give one-line talking points at first use for IN, IS NULL, OR and the comparison operators in the CHECKs and for CURRENT_TIMESTAMP in the `created_at` DEFAULT, since Thursday teaches them.
- 05-keys-and-constraints: run the succeeding generated-id INSERT (`'high'` gets 7, with DEFAULT filling `status`) before the refused `'urgent'` one (which burns 8), so the id gap is explained, not a surprise; `SELECT LAST_INSERT_ID();` gets a one-line talking point as the function that returns the id this connection just generated.
- 06-desk-on-mysql: `storage.py` gains `insert_ticket`, `close_ticket_db` and `delete_ticket_db`, each passing values as %s placeholders with a tuple and ending with `conn.commit()`; `git status` shows `tickets.json` unchanged after the desk loads from MySQL; the `conn` fixture and its two database tests bring pytest to 21 green (skipped when DESK_DB_PASSWORD is unset); then `feature/desk-mysql` merges into `main` and `git push origin main` runs.
