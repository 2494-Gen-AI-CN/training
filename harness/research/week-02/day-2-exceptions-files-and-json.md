# w02d2 — Exceptions, files & JSON

gate: light
verified: 2026-10-15
week: 2 · Python advanced
day: 2 · day-2-exceptions-files-and-json

version-stamps:
  - python: 3.15 (verified 2026-10-15)
  - json: stdlib, Python 3.15 (verified 2026-10-15)   # json.dump, json.load, json.JSONDecodeError
  - pathlib: stdlib, Python 3.15 (verified 2026-10-15)   # Path.unlink
  - datetime: stdlib, Python 3.15 (verified 2026-10-15)   # isoformat, fromisoformat
  - logging: stdlib, Python 3.15 (verified 2026-10-15)   # log.error in the intake except branch

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- A traceback lists the call stack with the most recent call last, so the exception type and message on the final line are read first — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- A SyntaxError is raised while the file is being parsed, before any line runs, so it cannot be caught by a try statement in the same file — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- In a try statement the except clause runs only if the try body raised a matching exception — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- The else clause runs only when the try body raised nothing, and the finally clause runs on every path — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- A bare except: also catches KeyboardInterrupt and SystemExit, so name the exception type you expect — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- The raise statement raises a given exception, and raise ... from err records err as the direct cause shown in the traceback — [The raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement)
- KeyError, ValueError and TypeError are built-in exceptions with distinct meanings: missing key, right type but unacceptable value, wrong type — [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- FileNotFoundError and FileExistsError are subclasses of OSError — [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- open() takes a mode: "r" reads (default), "w" truncates or creates, "a" appends, "x" creates and fails if the file exists — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)
- When encoding is omitted, text mode uses a platform-dependent default, so pass encoding="utf-8" explicitly — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)
- Using open() in a with statement closes the file even if an exception occurs inside the block — [Reading and Writing Files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- str.splitlines() splits on line boundaries and drops the line endings, unlike readlines() — [Built-in Types: str.splitlines](https://docs.python.org/3/library/stdtypes.html#str.splitlines)
- Path.unlink() removes a file and raises FileNotFoundError if it is missing (unless missing_ok=True) — [pathlib](https://docs.python.org/3/library/pathlib.html#pathlib.Path.unlink)
- json.dump writes JSON to a file object and json.load reads it back; dumps and loads work on strings — [json](https://docs.python.org/3/library/json.html)
- json.dumps raises TypeError for objects JSON has no type for, such as datetime — [json](https://docs.python.org/3/library/json.html)
- Python None is written as JSON null, and tuples come back as lists — [json](https://docs.python.org/3/library/json.html)
- Invalid JSON text makes json.load raise json.JSONDecodeError, a subclass of ValueError — [json](https://docs.python.org/3/library/json.html#json.JSONDecodeError)
- datetime.isoformat() and datetime.fromisoformat() round-trip a datetime through ISO 8601 text — [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Errors
- Interview questions: How do you read a traceback?; What do KeyError, ValueError and TypeError each mean?; Follow-up: how does a SyntaxError differ from an exception raised while the program runs, and why can a try in the same file not catch it?
- Adjacent concept: Exception hierarchy (BaseException, Exception, OSError) — a handler for a parent type catches its children, which decides what an except clause matches.
- Trade-off or limit: A SyntaxError is found before the program runs, so it cannot be handled in the same file — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- Recognise on sight: `Traceback (most recent call last):` then `File "desk.py", line 12, in <module>` and a last line such as `KeyError: 'urgent'`
- Claims:
  - The last traceback line holds the exception type and message — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
  - KeyError is raised for a missing mapping key — [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
  - ValueError is raised when an argument has the right type but an unacceptable value, as in int("TD-7") — [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
  - TypeError is raised when an operation is applied to the wrong type, as in len(5) — [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
  - A missing colon is a SyntaxError reported with the line and a caret — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)

### Exception handling
- Interview questions: When would you raise an exception yourself?; What does finally guarantee?; Follow-up: what does `__cause__` hold after `raise ... from err`, and how does that differ from `__context__`?
- Adjacent concept: Validating inputs at the boundary — raising at the top of __init__ stops an invalid object from ever existing.
- Trade-off or limit: Catching too wide hides real bugs, so catch the narrowest type the code can recover from — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- Recognise on sight: `raise ValueError(f"unknown priority: {priority!r}")` guarded by an `if` at the top of a constructor
- Claims:
  - raise with an exception instance stops the current function and unwinds to the nearest matching handler — [The raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement)
  - raise ... from err sets the cause shown as "The above exception was the direct cause" — [The raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement)
  - An exception raised inside an except clause without from is chained implicitly: the handled exception is stored in the new exception's __context__ and the traceback reads "During handling of the above exception, another exception occurred"; from sets __cause__ (and suppresses the context display) — [The raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement)
  - A raised, uncaught exception exits the program with a non-zero status — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
  - logging.Logger.error records an ERROR-level message without stopping the program — [logging](https://docs.python.org/3/library/logging.html#logging.Logger.error)

### try-except
- Interview questions: What order do try, except, else and finally run in?; Can one try have several except clauses?; Follow-up: why is a bare except a code smell, and what does it catch that `except Exception` does not?
- Adjacent concept: Putting only the risky line in try and the follow-up work in else — keeps the handler from masking errors raised by unrelated code.
- Trade-off or limit: A bare except: also traps KeyboardInterrupt, so Ctrl+C stops working — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- Recognise on sight: `try: ... except ValueError as err: ... else: ... finally: ...`
- Claims:
  - The first matching except clause runs and the rest are skipped — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
  - except X as err binds the exception to err only inside that clause — [The try statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
  - else runs only when no exception occurred in the try body — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
  - finally runs whether or not an exception occurred, even if the handler itself raises — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
  - except (A, B): with a tuple catches either type — [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)

### File handling
- Interview questions: Why use a with statement for files?; What is the difference between text and binary mode?; Follow-up: why pass encoding="utf-8" when the code already runs on your own machine?
- Adjacent concept: Relative paths resolve against the current working directory, not the script's folder — explains "file not found" for a file that exists.
- Trade-off or limit: Without encoding="utf-8" the default depends on the operating system, so the same code can read a file differently on two machines — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)
- Recognise on sight: `with open(path, encoding="utf-8") as f:`
- Claims:
  - open() returns a file object, and text mode converts bytes to str using an encoding — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)
  - A with block calls close() on exit, even after an exception — [Reading and Writing Files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
  - A missing file raises FileNotFoundError, an OSError subclass — [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
  - pathlib.Path wraps a filesystem path as an object with methods such as unlink — [pathlib](https://docs.python.org/3/library/pathlib.html)

### Read files
- Interview questions: What is the difference between read(), readline() and readlines()?; What does splitlines() do that split("\n") does not?; Follow-up: how do you read a very large file without loading it all into memory?
- Adjacent concept: Iterating a file object line by line — reads one line at a time, so memory stays flat.
- Trade-off or limit: read() loads the whole file into memory, which is fine for small files and wrong for very large ones — [Reading and Writing Files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- Recognise on sight: `return f.read().splitlines()`
- Claims:
  - f.read() returns the whole content as one string — [Reading and Writing Files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
  - Looping over a file object yields one line at a time, each ending in a newline — [Reading and Writing Files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
  - splitlines() removes the line endings and gives no empty last item for a trailing newline — [Built-in Types: str.splitlines](https://docs.python.org/3/library/stdtypes.html#str.splitlines)
  - Default mode is "r", so open(path) reads text — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)

### Write and create files
- Interview questions: What is the difference between "w", "a" and "x"?; Does write() add a newline?; Follow-up: when exactly is existing content lost with "w", and how does "x" guard against it?
- Adjacent concept: Buffering and flush — written text may sit in a buffer until the file closes, which is another reason for with.
- Trade-off or limit: Mode "w" truncates an existing file the moment it is opened, before anything is written — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)
- Recognise on sight: `with open(path, "a", encoding="utf-8") as f: f.write(text + "\n")`
- Claims:
  - "w" creates the file if absent and empties it if present — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)
  - "a" creates the file if absent and writes at the end — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)
  - "x" raises FileExistsError if the file already exists — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)
  - f.write() writes exactly the string given and returns the number of characters written — [Reading and Writing Files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
  - "\t".join(fields) builds a tab-separated line from strings — [Built-in Types: str.join](https://docs.python.org/3/library/stdtypes.html#str.join)

### Delete files
- Interview questions: How do you delete a file in Python?; What happens if the file does not exist?; Follow-up: why not check that the file exists first and then delete it (EAFP versus LBYL)?
- Adjacent concept: EAFP versus LBYL — Python style tries the operation and handles the failure, since a file can vanish between a check and the delete.
- Trade-off or limit: Path.unlink() removes only a file or symbolic link; a directory needs Path.rmdir() instead — [pathlib](https://docs.python.org/3/library/pathlib.html#pathlib.Path.unlink)
- Recognise on sight: `try: Path(path).unlink() except FileNotFoundError: return False`
- Claims:
  - Path.unlink() deletes a file or symbolic link, not a directory — [pathlib](https://docs.python.org/3/library/pathlib.html#pathlib.Path.unlink)
  - Path.unlink(missing_ok=True) ignores a missing file — [pathlib](https://docs.python.org/3/library/pathlib.html#pathlib.Path.unlink)
  - os.remove() does the same job as unlink on a string path — [os](https://docs.python.org/3/library/os.html#os.remove)
  - os.remove() raises FileNotFoundError for a missing path and IsADirectoryError when the path is a directory — [os](https://docs.python.org/3/library/os.html#os.remove)

### JSON
- Interview questions: What is the difference between json.dump and json.dumps?; Which Python values cannot be written as JSON directly?; Follow-up: how do you store a date in JSON and get a datetime back on load?
- Adjacent concept: Serialization and round trips — save then load must give back an equal object, which is how a storage layer is checked.
- Trade-off or limit: JSON has no date type and no tuples, so dates travel as ISO 8601 text and tuples return as lists — [json](https://docs.python.org/3/library/json.html)
- Recognise on sight: `json.dump(records, f, indent=2)` and `"closed_at": null`
- Claims:
  - json.dump(obj, f) writes to a file object, json.dumps(obj) returns a string — [json](https://docs.python.org/3/library/json.html)
  - indent=2 pretty-prints, which makes a committed file readable in a diff — [json](https://docs.python.org/3/library/json.html)
  - A dict maps to a JSON object, a list to an array, None to null, True to true — [json](https://docs.python.org/3/library/json.html)
  - datetime.isoformat() gives text and datetime.fromisoformat() reads it back — [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)
  - json.JSONDecodeError is a ValueError subclass carrying the message, line and column — [json](https://docs.python.org/3/library/json.html#json.JSONDecodeError)
  - Saving through open(path, "w") truncates the old file the moment it is opened, so every save rewrites the whole file — [Built-in Functions: open](https://docs.python.org/3/library/functions.html#open)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Errors and Exceptions — https://docs.python.org/3/tutorial/errors.html
- Built-in Exceptions — https://docs.python.org/3/library/exceptions.html
- The raise statement — https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement
- The try statement — https://docs.python.org/3/reference/compound_stmts.html#the-try-statement
- Reading and Writing Files — https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
- Built-in Functions: open — https://docs.python.org/3/library/functions.html#open
- Built-in Types: str.splitlines — https://docs.python.org/3/library/stdtypes.html#str.splitlines
- Built-in Types: str.join — https://docs.python.org/3/library/stdtypes.html#str.join
- pathlib — https://docs.python.org/3/library/pathlib.html
- os — https://docs.python.org/3/library/os.html#os.remove
- json — https://docs.python.org/3/library/json.html
- datetime — https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
- logging — https://docs.python.org/3/library/logging.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- traceback | The report Python prints when an exception is not handled, listing the chain of calls with the most recent last and the error on the final line. | aka: stack trace, backtrace
- try-except | A statement that runs a block of code and, if a named exception is raised in it, runs a handler instead of ending the program. | aka: try/except, exception handler, exception handling
- context manager | An object used with a with statement that sets something up on entry and always cleans it up on exit, such as closing a file. | aka: with statement, with block
- file mode | The string passed to open() that says whether a file is read, written, appended to or exclusively created, and whether as text or bytes. | aka: open mode
- serialization | Converting an in-memory object into text or bytes that can be stored or sent, so it can be rebuilt later. | aka: serialize, serialise, deserialization, round trip
- ISO 8601 | The international standard text format for dates and times, such as 2026-10-20T09:00:00, which sorts correctly and is how dates are stored in JSON. | aka: ISO date, isoformat
- exception chaining | Raising a new exception with raise ... from err so the traceback keeps the original error as its direct cause. | aka: raise from, direct cause

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Writing a bare `except:` or `except Exception: pass`, which hides real bugs and traps Ctrl+C; the handler should name the type it can recover from.
- Opening a file with mode "w" to add to it, which wipes existing content; "a" appends and "w" truncates at open.
- Forgetting encoding="utf-8", or forgetting that write() does not add a newline, so lines run together.
- Relative paths resolve from the folder the command is run in, so `python ticket_desk.py` from another directory reports FileNotFoundError for a file that exists.
- Passing a datetime (or any custom object) to json.dump and getting TypeError, instead of converting to a dict of plain values and ISO text first.
- Confusing json.load/json.dump (file objects) with json.loads/json.dumps (strings), and swallowing JSONDecodeError instead of raising a clearer error with `from err`.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- `01_ticket_errors`: run the three one-line tracebacks (`SLA_HOURS['urgent']` KeyError, `int('TD-7')` ValueError, `len(5)` TypeError) and read each bottom-up, run the missing-colon SyntaxError once and fix it, add `raise ValueError(f"unknown priority: {priority!r}")` at the top of `Ticket.__init__`, wrap the intake in `try`/`except ValueError as err`/`else`/`finally` so `rejected ticket` and `intake done` both log, and show a bare `except:` before narrowing it.
- `02_board_file`: run `read_lines` on `requirements.txt`, read the transient FileNotFoundError from `read_lines("missing.txt")`, write `export_board` with mode "w" and `append_line` with mode "a", show the transient "x" FileExistsError on a second run, `cat board.txt`, and call `delete_file` twice so it prints `True False`.
- `03_desk_json`: show the transient `json.dumps` TypeError on a datetime, write `to_record`/`from_record` with ISO text through `isoformat`/`fromisoformat`, write `save_desk` and `load_desk` with a missing file giving an empty `Desk`, run `python ticket_desk.py` twice so the second run loads instead of seeding, and `cat tickets.json`.
- `04_json_errors`: delete a `]` from `tickets.json` by hand, read the raw JSONDecodeError traceback, add the `raise ValueError(...) from err` branch and read its "direct cause" traceback, reseed with `delete_file` and a run, check that `git status` shows only `storage.py` changed, then merge `feature/desk-storage` into `main` and push.
