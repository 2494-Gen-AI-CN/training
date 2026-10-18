# SQL in the page: a MySQL-shaped practice terminal for week 3 (D-0062, O-23)

Companion to `codify-plan.md`. Same shape: one stage per clean session, each stage's exit criteria are the next
stage's entry conditions, the kickoff prompt from `codify-plan.md` applies, then the stage block below. Written
2026-10-17, for the week-3 practice stage (SQL with MySQL, Mon 2026-10-26 to Fri 2026-10-30).

## The decision in one paragraph

Learners never need a MySQL server to practise in the page. The engine is sql.js (SQLite compiled to wasm),
vendored into the site so it is a first-party file and the two pinned external origins stay as they are
(`tests/test_assets.py`). JavaScript dresses it as the mysql client the room uses (D-0059): a `mysql>` prompt,
MySQL result boxes, MySQL error codes and wording, `SHOW` and `DESCRIBE`, a short list of dialect rewrites, and
stored procedures with IN parameters. Checks are declarative JSON, not Python, and the identical wasm runs them
under node for the contract tests, so there is no engine skew between the test and the browser. The Pyodide
practice task (`ix-task`, D-0043) stays for the Wed–Fri Python-desk steps; the new `ix-sql` kind covers every
SQL-in-the-client step. What the costume cannot fake stays with predict and spot widgets and an honest `partial`.

## Facts established on 2026-10-17 (do not re-derive)

| Fact | Measured how |
|---|---|
| Pyodide 314.0.7 core ships `sqlite3`, SQLite 3.39.0 | `loadPyodide()` under node 22, `import sqlite3` |
| `harness/critics/practice.md` runtime section says sqlite3 is absent | stale; correct it in Stage S1 |
| CPython 3.15.0 on the trainer machine bundles SQLite 3.53.4 (has `CONCAT`) | `sqlite3.sqlite_version` |
| Pyodide's 3.39.0 lacks `CONCAT`, `NOW`, `YEAR`; a CPython-passing check can fail in the browser | probe under node |
| sql.js 1.15.0 (npm, 2026-10-14) bundles SQLite 3.54.0: `CONCAT` and `RIGHT JOIN` native, `create_function` works | `sql-wasm.js` under node |
| sql.js footprint: `sql-wasm.wasm` 684,897 bytes, `sql-wasm.js` 46,635 bytes, MIT | npm tarball |
| CodeMirror 5.65.21 ships `mode/sql/sql.js` on the pinned origin (HTTP 200) | curl |
| SQLite cannot run: `TRUNCATE`, `ALTER ... MODIFY`, `ENUM`, `GRANT`, `CREATE PROCEDURE`, SQL UDFs, `CREATE SEQUENCE`, `SET TRANSACTION ISOLATION LEVEL`, `ON DUPLICATE KEY` | probe under node |
| SQLite traps: FKs off unless `PRAGMA foreign_keys=ON`; `INT AUTO_INCREMENT` parses and does nothing; `VARCHAR(n)` unenforced; `DECIMAL` is REAL; text compare is case-sensitive | probe under node |

## Recommended order and sizing

| Order | Stage | When | Size |
|---|---|---|---|
| 1 | S0 Ground truth from MySQL 9.7 | as soon as `desk-mysql` runs on the trainer machine (O-21 rehearsal), target Tue 2026-10-20 | half a session, no agents, Docker up |
| 2 | S1 Engine, costume, terminal widget | Tue–Wed 2026-10-20/21, after the W2D1/W2D2 closes | 1 session, no agents; flips D-0062 to accepted |
| 3 | S2 Task kind, checks, node parity, critic | Thu 2026-10-22 | 1 session, no agents |
| 4 | S3 Week-3 practice stage with both kinds | after the week-3 batch (Fri 2026-10-23), by Mon 2026-10-26 | 1 session, ~20 agents (suitability 5, build up to 15) + browser pass |

Fallback (named in D-0062): if S1 and S2 are not green when the week-3 batch finishes, run the practice stage
as it is today with SQL as Python strings against Pyodide's `sqlite3` (checks seed an in-memory database in
their setup lines, `PRAGMA foreign_keys=ON`, `con.create_function` shims for `CONCAT`/`NOW`, `?` placeholders
not `%s`) plus predict and spot widgets for the rest. That path needs only the critic's runtime line corrected.
Do not build S1 after week 3 is taught: week 4 is BigQuery and week 5 onward is LLMs, so a late `ix-sql` has no
second customer.

---

## Stage S0 — Ground truth from MySQL 9.7 (no decision needed)

```
STAGE S0 — Record what the mysql client really prints, so the costume copies it instead of guessing.
Prerequisite: the desk-mysql container from D-0059 is up on this machine (docker ps shows it).
1. Write harness/sqlfake/record.py (stdlib only): takes a .sql file of statements, runs each through
   `docker exec -i desk-mysql mysql -uroot -p<env MYSQL_ROOT_PASSWORD> --table --comments` one at a time,
   and writes harness/sqlfake/recorded/<name>.txt as pairs of "mysql> <statement>" and the verbatim reply.
   Never store the password in the repo; read it from the environment and fail with a clear line if unset.
2. Record, in a scratch database the script creates and drops (desk_fake):
   a. SHOW DATABASES; CREATE DATABASE; USE; SHOW TABLES on an empty and a filled database.
   b. CREATE TABLE for agents, customers, tickets with INT AUTO_INCREMENT PRIMARY KEY, VARCHAR(n), ENUM,
      DECIMAL(5,2), DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY ... ON DELETE CASCADE, CHECK, UNIQUE.
   c. DESCRIBE each table; SHOW CREATE TABLE tickets; SHOW INDEX FROM tickets.
   d. INSERT (one row, many rows), UPDATE, DELETE, TRUNCATE: the exact "Query OK, N rows affected (0.00 sec)"
      and "Records: N  Duplicates: 0  Warnings: 0" lines.
   e. SELECT with 0 rows ("Empty set"), 1 row, many rows, NULLs, a column alias, a long value, numbers right-
      aligned; the box format with its column widths.
   f. Every error the week will meet, each as the real "ERROR nnnn (SQLSTATE): text" line:
      1064 syntax, 1146 unknown table, 1054 unknown column, 1062 duplicate entry, 1452 FK child row,
      1451 FK parent row, 3819 CHECK failed, 1406 data too long, 1265/1366 bad ENUM value, 1048 NOT NULL,
      1050 table exists, 1051 unknown table on DROP, 1305 procedure does not exist, 1318 wrong arg count.
   g. DELIMITER //, CREATE PROCEDURE with IN params, CALL, DROP PROCEDURE; CREATE FUNCTION ... RETURNS ...
      DETERMINISTIC RETURN expr; CREATE TRIGGER; CREATE VIEW; CREATE INDEX; EXPLAIN SELECT.
   h. START TRANSACTION / COMMIT / ROLLBACK / SAVEPOINT; SET TRANSACTION ISOLATION LEVEL ...; SHOW VARIABLES
      LIKE 'transaction_isolation'.
   i. GRANT / REVOKE / SHOW GRANTS on a scratch user, then DROP USER.
3. Commit harness/sqlfake/recorded/*.txt and record.py. These files are the spec for S1; nothing else is.
Exit: every item a–i has a recorded file; MySQL version line ("Server version: 9.7.2 MySQL Community Server")
captured at the top of the first file; STATUS.md O-23 notes the commit.
```

## Stage S1 — Engine, costume, terminal widget (flips D-0062 to accepted)

```
STAGE S1 — Vendor sql.js, write the MySQL costume, add the ix-sql widget and data-run="sql" prose blocks.
Read first: docs/process/sql-in-page-plan.md, harness/sqlfake/recorded/*.txt (S0), docs/assets/js/widgets.js,
docs/assets/js/pyworker.js (the shape the Python runner has; the SQL path does not use it), tests/test_assets.py,
tests/helpers.py.
1. Vendor: docs/assets/vendor/sqljs/sql-wasm.js, sql-wasm.wasm and LICENSE from the sql.js 1.15.0 npm tarball
   (sha256 of each file in docs/assets/vendor/sqljs/README.md with the version and date). Nothing else from
   the package. tests/test_assets.py: the vendored files are the only allowed content of docs/assets/vendor/,
   their sha256 is pinned, and the pinned-origin test still lists exactly pyodide and codemirror.
2. docs/assets/js/sqlfake.js: a module worker (like pyworker.js) that loads the vendored engine once and runs a
   job { id, seed, sql, checks } on a FRESH database per job. It owns the costume:
   a. Statement split on ";" with DELIMITER handling; strings and comments respected.
   b. Rewrites before execution, each one a named rule in a table at the top of the file:
      INT AUTO_INCREMENT PRIMARY KEY -> INTEGER PRIMARY KEY AUTOINCREMENT;
      ENUM('a','b') -> TEXT CHECK(col IN ('a','b'));
      VARCHAR(n) / CHAR(n) -> TEXT CHECK(length(col) <= n) COLLATE NOCASE (MySQL's default collation is
      case-insensitive, SQLite's is not);
      DECIMAL(p,s) -> NUMERIC; DATETIME / TIMESTAMP / DATE -> TEXT; BOOLEAN -> INTEGER;
      TRUNCATE TABLE t -> DELETE FROM t; DELETE FROM sqlite_sequence WHERE name='t';
      INSERT ... ON DUPLICATE KEY UPDATE c=VALUES(c) -> ON CONFLICT DO UPDATE SET c=excluded.c;
      START TRANSACTION -> BEGIN; SET autocommit / SET TRANSACTION ISOLATION LEVEL / GRANT / REVOKE ->
      accepted no-ops that print "Query OK, 0 rows affected" (grants recorded in a side table __grants so
      SHOW GRANTS answers); SHOW VARIABLES LIKE 'transaction_isolation' answers REPEATABLE-READ or the level
      last SET, from a side variable.
   c. Synthesised statements, printed in the recorded MySQL layout: SHOW DATABASES, CREATE DATABASE, USE,
      SHOW TABLES, DESCRIBE / DESC / EXPLAIN t, SHOW CREATE TABLE, SHOW INDEX FROM, SHOW GRANTS, SHOW
      PROCEDURE STATUS. Built from sqlite_master and pragma table_info / foreign_key_list / index_list.
   d. Procedures and functions: CREATE PROCEDURE p(IN a INT, IN b VARCHAR(10)) BEGIN ...; END stored in a JS
      map; CALL p(1,'x') binds the params by name and runs the body statement by statement (IN params and
      plain statements only; DECLARE, IF, loops and OUT params print ERROR 1064 with a one-line note that the
      page engine does not run control flow). CREATE FUNCTION f(x INT) RETURNS INT DETERMINISTIC RETURN expr
      registers db.create_function(f, ...) that evaluates expr through SELECT with the params bound.
      DROP PROCEDURE / FUNCTION remove them; 1305 when missing.
   e. MySQL functions SQLite lacks, registered with create_function: NOW, CURDATE, CURTIME, YEAR, MONTH, DAY,
      DATE_FORMAT (the %Y %m %d %H %i %s subset), IF, DATEDIFF, CONCAT_WS. CONCAT, IFNULL, COALESCE, SUBSTRING,
      LENGTH, UPPER, LOWER, ROUND, ABS are native in 3.54. Nothing else: list the set in metrics.json.
   f. Error map: SQLite error text patterns -> the recorded MySQL line (1064, 1146, 1054, 1062, 1452, 1451,
      3819, 1406, 1048, 1050, 1051, 1305, 1318). An unmapped SQLite error prints as "ERROR (engine): <text>"
      so a leak is visible, never silent.
   g. Output: result sets in the recorded box layout (widths from the data, numbers right-aligned, NULL as
      NULL), "N rows in set (0.00 sec)", "Empty set (0.00 sec)", "Query OK, N rows affected (0.00 sec)" from
      getRowsModified(), the Records/Duplicates/Warnings line after multi-row INSERT. Output cut at 200 lines
      like the Python runner.
   h. After the reader's statements, the checks (S2 defines them; S1 ships rows / affected / error / count
      / schema so the smoke task works) are evaluated on the same database and returned as
      [{ ok, label, detail }], the same shape widgets.js already draws.
3. widgets.js: ix-sql widget. Markup: <div class="ix-sql" data-id data-title data-q><pre class="sql-seed"
   hidden>…</pre><pre class="sql-starter">…</pre><pre class="sql-tests" hidden>{json}</pre></div>. CodeMirror
   in mode text/x-mysql (load mode/sql/sql.js beside the python mode, same pinned package). Buttons Run, Check,
   Reset; output panel styled as a terminal with the mysql> echo of each statement before its reply. Saved work
   and solved state in localStorage under the same key scheme as ix-task. Prose blocks: <pre data-run="sql"
   data-seed="#id"> runs on the seed block it names; data-continues chains on the block above's database.
   The practice intro sentence gains, once per page that has an ix-sql: "SQL tasks run on a MySQL-compatible
   engine in your browser, not on the desk-mysql server; a few server-only features are listed on the page."
4. style.css: the terminal panel (monospace, the page's code colours, no new palette); docs/bump-css.sh gains
   sqlfake.js in --all and the vendored files are versioned by their sha in the README, not by ?v=.
5. tests/helpers.py ALLOWED_JS gains sqlfake.js; test_pages.py script order unchanged (sqlfake.js is a worker
   started by widgets.js, no script tag on any page, like pyworker.js).
6. harness/sqlfake/run_cases.cjs: node runner that loads sqlfake.js's costume and the vendored wasm (the
   costume is written so the same source runs in a worker and under node: no DOM, postMessage behind one
   function) and takes a JSON job list on stdin, prints results on stdout. tests/test_sqlfake.py drives it
   against harness/sqlfake/cases/*.json: every recorded S0 transcript replayed through the costume must print
   the recorded reply byte for byte, except the "(0.00 sec)" timing which is normalised. Skips when node is
   absent (the existing precedent).
7. Smoke test: one hand-written ix-sql on a local copy of the W2D2 page (not committed) with seed, starter
   and two checks; run it in the browser; fix until green.
8. Decision: flip D-0062 to accepted in the same commit (edit its Status line; no new entry). In
   harness/critics/practice.md rewrite "The runtime" as two runtimes: Python (Pyodide 314.0.7, sqlite3 present
   at SQLite 3.39.0, the CPython-skew warning) and SQL (sql.js 1.15.0, SQLite 3.54.0, the rewrite list, the
   not-supported list). Mention D-0062 in the commit subject.
Exit: suite green including test_sqlfake.py; browser smoke green; vendored files pinned by sha; D-0062
accepted; STATUS.md O-23 and Log updated; python harness/build_tracker.py run. Push.
```

## Stage S2 — Task kind, declarative checks, node parity, critic and prompts

```
STAGE S2 — Teach the practice stage the second kind.
Read first: harness/practice_tasks.py, harness/critics/practice.md, harness/workflows/practice-tasks.js,
harness/args_for.py (practice args, the runtime block), harness/practice_browser.py and .js,
tests/test_assets.py PracticeTaskTests, harness/practice/week-02/day-2-exceptions-files-and-json.json (exemplar).
1. File shape (harness/practice/<week>/<day>.json): a task gains "lang": "python" | "sql" (python when
   absent, so every existing file is unchanged) and, for sql, "seed" (the schema and rows the task starts
   from, MySQL dialect, run through the costume) and "tests" as a JSON list of checks instead of Python:
     { "label": "keeps Bo, who has no ticket", "rows": [["Ana","Login 500"],["Bo",null]], "ordered": false }
     { "label": "selects name then title", "cols": ["name","title"] }
     { "label": "one SELECT does it", "statements": 1 }
     { "label": "two rows changed", "affected": 2 }
     { "label": "the second insert is refused", "error": 1452 }
     { "label": "tickets has an agent_id column", "schema": { "tickets": ["id","title","agent_id"] } }
     { "label": "three open tickets remain", "query": "SELECT COUNT(*) FROM tickets WHERE status='open'", "rows": [[3]] }
   rows / cols / statements read the LAST statement the reader ran; query runs its own SELECT after the
   reader's statements, for DDL and DML tasks. "error" means the last statement must have printed that code.
   Bounds in metrics.json practice.sql: seedLinesMax, statementsMax, checksPerTaskMin/Max (reuse the Python
   numbers), the shim function list and the rewrite names (for the lint below).
2. practice_tasks.py: render() emits div.ix-sql for sql tasks (seed, starter, tests JSON escaped like the
   Python ones); TASK_RE / page_tasks / in_sync read both kinds; _built_problems for sql: seed and starter
   split into complete statements, checks list valid with known keys only, starter does not solve; a lint
   that rejects any token from metrics.json practice.sql.unsupported (ISOLATION in a task statement, DECLARE,
   OUT params, CREATE SEQUENCE, ...) in seed, starter or model answers. verify runs the sql tasks through
   harness/sqlfake/run_cases.cjs (the same engine the browser gets): starter fails, model answer passes,
   accept cases pass, each reject case is caught by its named check, every check is failed by some reject.
3. Trainer files: sql model answers in trainer/<rel>/solutions/practice.sql under "-- task tN" headers;
   practice_cases.py keeps one dict for both kinds (SQL strings for sql tasks). tests/test_assets.py
   PracticeTaskTests cover sql tasks through the node runner and skip them (not fail) when node is absent.
4. practice_browser.js: types each case into an ix-sql editor (CodeMirror setValue works the same), clicks
   Check, compares the rows the page drew with the node outcome. practice_browser.py builds the cases for
   both kinds.
5. harness/critics/practice.md: suitability item 2 gains the SQL runtime (a step that teaches SQL in the
   client fits when its statements run through the costume; a step whose point is a server-only feature
   does not, name it); the proposal carries "lang" per task; build items 4–8 get their sql wording (starter
   is SQL ending in ";", checks are the JSON list, model answers in practice.sql). practice-tasks.js: the
   runtime line names both engines and both contracts (sqlfake.js, pyworker.js); args_for.py runtime block
   adds sqlfake and the sql.js version read from the vendored README.
6. Decision entry (critic + metrics change): "practice tasks have two kinds, python and sql" with the file
   shape above; ID in the commit subject.
7. Re-run the S1 smoke task through insert / verify / browser pass on the local page copy; discard the copy.
Exit: suite green; python harness/practice_tasks.py check OK on every existing day (nothing moved);
verify on the smoke day OK; STATUS.md O-23 and Log; tracker rebuilt. Push.
```

## Stage S3 — Week-3 practice stage with both kinds

```
STAGE S3 — The three steps of D-0047 on week 3, with ix-sql live.
Entry: week 3 authored (the batch of Fri 2026-10-23), S1 and S2 green, O-21's trainer rehearsal done.
1. python harness/args_for.py 3 --practice --today <date> -> practice-tasks.js (suitability, 5 agents).
   Expect: W3D1 and W3D2 mostly sql tasks (DDL, DML, DQL, TCL), W3D3 sql for keys and constraints, W3D4 sql
   for joins and aggregates and python for the desk's transaction, W3D5 sql for views, triggers and indexes.
   Expect partial on: ERD, DCL beyond SHOW GRANTS, isolation levels, procedures with control flow, UDFs
   beyond RETURN expr, Sequence, Review.
2. python harness/practice_tasks.py show 3; the trainer answers per task (approve ...); never on their behalf.
3. python harness/args_for.py 3 --practice-build --today <date> -> practice-tasks.js (build + critic, up to
   3 passes per day); python harness/practice_tasks.py verify 3 <day> per day.
4. Browser pass per day (practice_browser.py, Claude in Chrome), recorded in the STATUS.md Log with runs,
   seconds, browser and both runtimes.
5. Pages already live: insert writes the section; commit and push the same day; bump-css.sh --all if
   widgets.js changed since the release.
Exit: every week-3 day either carries its approved tasks browser-green or has an honest none/partial;
O-17 and O-23 updated; run records amended (log_run.py amend).
```

## Not in this plan

- A second connection or two "sessions" side by side to show isolation levels and locking: predict/spot only.
- MySQL's EXPLAIN format, query cost or the optimizer: EXPLAIN prints SQLite's plan under an "(engine)" note.
- Python-desk tasks that drive mysql-connector against a server: the Pyodide ix-task with an open sqlite3
  connection handed in by the checks (the fallback path), never a faked connector.
- Running any of this against the week's demo repo or the desk-mysql container.

## After every stage

- STATUS.md: O-23 row and a Log line in the same commit; `python harness/build_tracker.py`; finish with
  `python harness/log_run.py tests`.
- Decision ID in the commit subject (D-0062 for S1, the new entry for S2).
- `python harness/drift_check.py` before the push; `git status` clean in both repos after it.
