# Practice tasks — suitability bar and build PASS criteria

Practice tasks are added to a notes page AFTER the day's other content is authored (D-0047), in three steps: a suitability pass proposes tasks, the trainer approves or declines each one, a build writes the approved ones. `harness/practice/<week>/<day>.json` is the one source of a page's tasks; the page's `section.practice` is generated from it by `python harness/practice_tasks.py insert <week> <day>` and never edited by hand. Numbers live in `harness/metrics.json` `practice`.

A task is ungraded practice on one teaching step: the reader types a short solution in the page, runs it, and the page reports each check as passed or failed. It is answerable from the page alone. A task has one of two kinds: a Python task (the default, everything below unless a rule says otherwise) or a choice task (D-0084, its own section below): a multiple-choice question the page checks in JavaScript, with no Python and no Pyodide.

## The runtime (binding for both parts)

Read `docs/assets/js/pyworker.js`; it is the whole contract.

- The code runs in Pyodide (CPython on WebAssembly) in the reader's browser. The version is in your prompt; it can trail the course Python.
- Standard library only. The worker loads no package: nothing from PyPI, and none of the standard-library modules Pyodide ships separately or leaves out (`ssl`, `lzma`, `tkinter`, `curses`, `venv` among them). No `pip`, no `pytest`, no `numpy`, `pandas` or `matplotlib`. Pyodide's core DOES ship `sqlite3` (SQLite 3.39.0 in Pyodide 314.0.7, measured 2026-10-17, STATUS.md O-23): an in-memory database is part of the runtime.
- SQL runs in the page through `sqlite3` (D-0067, the fallback of D-0062 until the `ix-sql` widget lands). The checking side under CPython 3.15 (`tests/test_assets.py`, `practice_tasks.py verify`) runs SQLite 3.53.4, newer than the browser's 3.39.0, so a statement CPython accepts can fail in the reader's browser: use nothing 3.39.0 lacks (no `CONCAT()`; `RIGHT`/`FULL OUTER JOIN`, window functions and `WITH` are present). The browser pass is the proof.
- No terminal. `input()` meets end-of-file. No subprocess, no threads or processes, no sockets, no network, no API key, no database server.
- Files exist only in an in-memory file system that lasts as long as the worker. A task that reads or writes files takes the path as an argument, and its checks create what they need under `tempfile.mkdtemp()` in their own setup lines.
- A check sees the namespace the reader's code left behind: names, functions, classes and what calling them returns or raises. It does not see what was printed.
- One file. A task cannot span modules.
- Output is cut at 200 lines; nothing should loop or wait. A model answer runs in well under a second.

When you are not sure a standard-library module is present in Pyodide, say so in the step's reason (suitability) or avoid it (build). The browser pass is the proof, and it runs after the build.

## SQL days (D-0067, binding for both parts)

On a day whose steps teach SQL (week 3), a task is SQL only. The reader writes ONE SQL statement and no Python: no function, no loop, no string building. The page's existing Python widget carries it:

- `starter` is `QUERY = """` on the first line, a one-line SQL comment saying what to write (`-- the open tickets, newest first`), and `"""` on the last; the reader types inside the quotes. A fix-it task holds the broken statement instead. Nothing else.
- `tests` begin with setup lines that build the desk from the page, with the walkthroughs' table and column names (`priorities`, `customers`, `agents`, `tickets`, `ticket_events` as the page has them): `import sqlite3`, `conn = sqlite3.connect(":memory:")`, `conn.execute("PRAGMA foreign_keys = ON")`, one `conn.executescript("""...""")` with the CREATE TABLE statements and three to six rows per table (small: the seed is the longest part of the task), then `cur = conn.execute(QUERY)` and `rows = cur.fetchall()`. The asserts read `rows` (a list of tuples), `[c[0] for c in cur.description]` for the columns, `conn.total_changes` or a second SELECT for an INSERT, UPDATE or DELETE, and `raises(sqlite3.IntegrityError, conn.execute, "...")` for a refused row. Compare `rows` as the task text orders them; when the text sets no order, compare `sorted(rows)`.
- `q` names the tables and columns, says what the statement returns (which columns, in which order, which rows) or changes, and asks for SQL in words the page uses. It never asks for a Python name.
- `practice.py` holds one `QUERY = """..."""` per task with SQL only inside; `practice_cases.py` has `accept` statements written another way (a subquery for a join, `NOT EXISTS` for `NOT IN`) and `reject` statements that make the mistakes the page names (`= NULL`, an alias in `WHERE`, `COUNT(col)` for `COUNT(*)`, a join without its `ON`, a missing `WHERE` on a `DELETE`), each labelled with the check that catches it; a statement sqlite3 refuses outright has the label `None`.
- A step fits when its SQL text runs unchanged on SQLite 3.39.0 and MySQL 9.7: `SELECT` with `WHERE`, `IS NULL`, `ORDER BY`, `LIMIT`, `GROUP BY`, `HAVING`, aliases, `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `COALESCE`, scalar and `IN`/`NOT IN`/`EXISTS` subqueries, derived tables, `WITH`, `CROSS`/`INNER`/`LEFT`/`RIGHT`/`FULL OUTER JOIN`, `UNION`, window functions; `INSERT`, `UPDATE`, `DELETE` whose effect a `SELECT` reads back; `CREATE TABLE` with `INT`, `BIGINT`, `VARCHAR(n)`, `CHAR(n)`, `DECIMAL(p,s)`, `DATETIME`, `NOT NULL`, `DEFAULT`, `UNIQUE`, `CHECK`, `PRIMARY KEY`, `FOREIGN KEY ... REFERENCES`, `ON DELETE CASCADE`; `CREATE VIEW`.
- A step does not fit, and stays `none` until `ix-sql` (D-0062) lands, when its point is what SQLite does not have or does differently: `AUTO_INCREMENT` and its gaps, `DESCRIBE`, `SHOW ...`, `CREATE USER`, `GRANT`, `REVOKE`, `START TRANSACTION`/`COMMIT`/`ROLLBACK` typed at the client, autocommit, isolation levels, `TRUNCATE`, `ALTER TABLE ... MODIFY`/`CHANGE`, `CONCAT()`, `TIMESTAMPDIFF`, triggers, stored procedures and functions, `DELIMITER`, `EXPLAIN`, MySQL error numbers (a refusal is checked as `sqlite3.IntegrityError`, and the task text names the rule, never the number), the mysql client itself, and anything reached through mysql-connector-python.
- Read every Suitability and Build item above with this shape: "function" reads as "statement", "signature" as "tables, columns and result", "namespace" as `QUERY` plus what the setup lines built.

## Choice tasks (D-0084, binding for both parts)

A choice task is a multiple-choice question among the practice tasks: radio buttons in the page, checked by `docs/assets/js/widgets.js` in JavaScript, with no Python and no Pyodide. The reader picks one option and presses Check; the page marks the pick right or wrong, shows `explain`, and offers Try again. "The runtime" above does not apply to it. The browser pass (`harness/practice_browser.py`) picks every option in turn and holds the page to the file.

Suitability. A step fits a choice task when it has no behaviour a Python check can see but teaches a judgement the reader can get wrong, and the page names the wrong ways: when to paste what into an assistant and what never to paste, which of two prompts is better, which piece of generated code has the planted flaw, which step comes first. A step that is pure vocabulary recall (what an acronym stands for, which word a definition names) does not fit; that belongs in the quiz. Where a Python task fits, propose the Python task: the choice kind is for steps a Python task cannot serve. Write `"kind": "choice"` on the proposal, the scenario and the right answer in `idea`, and in `checks` one sentence per wrong option: the misconception it catches, as the page names it.

Build. For each approved choice task the author fills `q`, `options`, `answer` and `explain` and leaves `starter` and `tests` as `""`. Nothing goes to `trainer/<rel>/solutions/` for it; a day whose built tasks are all choice tasks has neither `practice.py` nor `practice_cases.py`.

- Exactly one option is right, and a reader who has read the step can tell which without doubt. No wrong option is right under a reading the step leaves open.
- `choiceOptionsMin`..`choiceOptionsMax` options, distinct, each a whole answer of similar length and form, so length or wording gives nothing away. `<code>` is the only markup.
- Every wrong option is a mistake the page names (its pitfalls, its "recognise on sight" lines, the brief's Pitfalls), the one its `checks` sentence names. No joke option, no option that is wrong only because it is absurd.
- No "all of the above", "none of the above", "both" or "neither" option. No trick wording: no double negatives, no "which is NOT", no option that turns on a single word.
- `q` is a short scenario in the page's words, one to three sentences ending in the question, `<code>` only. No reference to the classroom or the trainer (`metrics.notes.deliveryPhrases`). It reads like a person wrote it (the wording rules of `harness/critics/notes.md` item 18).
- `answer` is the 0-based index of the right option. Vary its position across the day's choice tasks.
- `explain` is one or two sentences: why the right option is right, citing the step's idea in the page's words, and where it helps what the most tempting wrong option misses. It never says "correct answer", never names an option by letter or number (the page shows neither), and holds `<code>` as its only markup.

Verify items for a choice task. They replace Build items 3 to 8 and 10, which are for Python tasks; items 1, 2 and 9 apply as written.

- C1. `python harness/practice_tasks.py verify <week> <day>` prints OK. For a choice task that is the validation: the option count within the bounds, options distinct and non-empty, `answer` in range, `explain` non-empty, `<code>` the only markup, no "of the above" option, and the page in sync with the file.
- C2. Answer each question yourself from `q` and the options alone before you read `answer`. If you picked another option, or two options seemed right, that is a critique.
- C3. Each wrong option is a mistake the page or the brief names and matches its `checks` sentence in the proposal; none is a joke, a giveaway or a trick.
- C4. `explain` states the step's idea in one or two sentences, is true of the right option only, and never says "correct answer".

## Suitability (the proposal)

The assessor reads the authored page and decides, for EVERY teaching step (each `section.step` but the last), whether one task fits. The trainer reads the result and decides what gets built, so a reason must stand on its own.

A step fits when ALL of these hold:

1. What it teaches shows up as behaviour: a function's return value, an object's state, a name's value, an exception raised, or, on a SQL day, the rows a statement returns or leaves in a table. A step that teaches a convention, a tool or a concept (PEP 8 layout, comments, pip, pylint, Git, Scrum) does not fit a Python task; say so in one sentence. Such a step may still be `suitable` with a choice task when it teaches a judgement the reader can get wrong (see "Choice tasks (D-0084)"); items 2 to 6 below are for Python tasks.
2. The task runs inside the runtime above with nothing faked. A step whose point is typed input, an installed package, several files, a network call or a MySQL server does not fit, even when a neighbouring idea would; `sqlite3` in memory is the runtime, not a server, and a SQL statement that runs on it unchanged is not faked.
3. The page alone is enough to solve it: every name, method and idiom the model answer needs is taught on this page or listed as known in the audience line. Nothing the week plan's anti-spoiler rows defer from this day to a later one.
4. It is small: a model answer of at most `modelLinesMax` lines, one function, class or short script.
5. Each proposed check proves ONE behaviour, and a mistake the page names (its pitfalls, its "recognise on sight" lines, the brief's Pitfalls) fails it. A task whose only wrong answer is "did not write it" is not worth a slot.
6. It does not hand over the day's demo rungs: the task is a sibling in the same domain, never the rung itself.

Shape of a proposal: at most ONE task per teaching step, ids `t1`, `t2`, ... in step order, `kind` (`"python"` or `"choice"`) on every proposal, `title` the short name of the section it practises (as the exemplar does), `idea` in two or three sentences (what the reader writes, the signature, one example of input and result; for a choice task, the scenario and the right answer), `checks` a list of `checksPerTaskMin`..`checksPerTaskMax` plain sentences, each the behaviour one check will prove (for a choice task, one sentence per wrong option: the misconception it catches). Keep to the demo thread's domain where the page does (the exemplar's tasks are all about tickets). `q`, `starter` and `tests` stay empty and `approved` stays null: the trainer has not answered.

Verdict: `full` when every teaching step carries a task, `partial` when some do, `none` when none does. `none` and `partial` are honest outcomes, not failures. `summary` says in one sentence what the day lends itself to and what it does not.

Mechanical check: `python harness/practice_tasks.py validate <week> <day>` prints OK.

## Build (PASS criteria for the critic)

You are judging the built tasks of one day. You are NOT the author. Read the day's file under `harness/practice/`, the page, `trainer/<rel>/solutions/practice.py` and `practice_cases.py`, and the exemplar named in your prompt (the accepted shape, D-0046). Run the commands and quote their output; return `pass=false` with specific critiques if ANY item fails.

1. `python harness/practice_tasks.py verify <week> <day>` prints OK: the file is valid and the page's section is what the file renders; for Python tasks, every starter fails, every model answer passes, every other right answer passes, every wrong answer is caught by the check named for it, and every check is failed by at least one wrong answer.
2. Exactly the approved tasks were built, with the ids, titles and steps of the proposal. A declined task has no `q`, `starter` or `tests`. Nothing else in the file moved: the steps, the reasons, the ideas and the trainer's answers are as they were.
3. `q` (the task text) names the function, class or names to write with the exact signature, says what comes back (returned, never "printed", unless the task is a script), and gives one example. It is solvable from the page alone and uses nothing a later day teaches. Markup is `<code>` only. No reference to the classroom or the trainer (`metrics.notes.deliveryPhrases`). It reads like a person wrote it (the wording rules of `harness/critics/notes.md` item 18).
4. `starter` is the signature with `...` for a body, or for a fix-it task the broken script as the reader meets it. At most `starterLinesMax` lines. It gives away no part of the answer.
5. `tests`: `checksPerTaskMin`..`checksPerTaskMax` top-level asserts, each with a message that names the behaviour in words a reader can act on without being told the answer ("leaves the caller's list as it was"). Prefer `left == right`, so the page can show expected and got. Lines that are not asserts are setup. `raises(ExcType, fn, *args)` is available for a check that expects an exception. Deterministic: no clock, no randomness, no reliance on set or dict order beyond what Python guarantees. No check depends on printed output.
6. The checks hold the task text and nothing more: every sentence of `q` that states a requirement has a check, and no check asks for something `q` does not say.
7. For Python tasks: `practice.py` holds one model answer per built Python task, in page order, each under a `# Task N: <title>` comment with N the number the page shows (choice tasks count in that numbering and get no answer here), in one file whose names do not collide. Each answer is at most `modelLinesMax` lines and uses only what the page teaches. A day whose built tasks are all choice tasks has no `practice.py`.
8. For Python tasks: `practice_cases.py` has an entry per built Python task and no other (a day of choice tasks only has no `practice_cases.py`): `accept` with at least `acceptMin` right answers written a different way from the model (a different idiom, not a renamed variable), `reject` with (code, label) pairs where each wrong answer is a mistake a learner of this page would plausibly make, most of them the pitfalls the page names. A `None` label marks code that stops with an error before the checks. No case, right or wrong, recurses without end: under CPython that is a RecursionError the check catches, but in the browser it overflows the stack and kills Pyodide, so the page restarts it and the case behaves differently from CPython (a `__repr__` that formats a bound method, as in `f"{self.load}"`, is the usual way in).
9. The page changed only inside `section.practice`: `git diff --stat -- <page>` and the diff itself show no other hunk, and `python harness/notes_check.py <page> --counts` passes as it did before.
10. Runtime: every import is standard library present in Pyodide, nothing reads `input()`, file tasks work on a path they are given, nothing sleeps or loops without end.

Not yours to judge: whether the day should have tasks at all (the trainer decided), and the browser pass (the session runs `harness/practice_browser.py` after the build; the stage is not done until it reports `ok: true`).

Return a one-sentence summary plus critiques as concrete fixes, each naming the task id.
