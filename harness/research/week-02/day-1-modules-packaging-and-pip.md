# w02d1 — Modules, packaging & pip

gate: light
verified: 2026-10-15
week: 2 · Python advanced
day: 1 · modules-packaging-and-pip

version-stamps:
  - python: 3.15 (verified 2026-10-15)
  - math: stdlib, Python 3.15 (verified 2026-10-15)
  - logging: stdlib, Python 3.15 (verified 2026-10-15)
  - re: stdlib, Python 3.15 (verified 2026-10-15)
  - venv: stdlib, Python 3.15 (verified 2026-10-15)
  - pip: 26 (major line bundled with Python 3.15 via ensurepip; the exact version is whatever `python -m pip --version` prints inside the venv) (verified 2026-10-15)
  - pylint: 4.0.0 (known-stable 4.x major; light gate, not web-checked). The 3.14 fallback in rung 4 applies: this brief cannot confirm a pylint release that declares Python 3.15 support, and 4.0.0 is the 4.x release known to declare 3.14. Demo 4 creates the venv with `py -3.14 -m venv .venv` (Windows) or `python3.14 -m venv .venv` (macOS), types `python -m pip install pylint==4.0.0`, and `requirements.txt` holds `pylint==4.0.0`. Transcript reason line: "pylint has no release yet that declares Python 3.15, so this venv uses 3.14; the desk code runs the same on both." The setup check must confirm a 3.14 interpreter is installed alongside 3.15.

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- `import math` binds the module object to the name `math`; `from math import ceil` binds only the name `ceil` in the importing namespace — [The import system](https://docs.python.org/3/reference/import.html)
- `math.ceil(x)` returns the smallest integer greater than or equal to x, and `math.floor(x)` the largest integer less than or equal to x — [math module](https://docs.python.org/3/library/math.html)
- `math.isclose(a, b)` compares floats with a relative tolerance (default 1e-09), so `math.isclose(0.1 + 0.2, 0.3)` is True while `0.1 + 0.2 == 0.3` is False — [math module](https://docs.python.org/3/library/math.html)
- `math.sqrt` of a negative number raises ValueError; `math.pi` is a constant, not a function — [math module](https://docs.python.org/3/library/math.html)
- `logging.getLogger(__name__)` returns a named logger; the standard levels in ascending order are DEBUG (10), INFO (20), WARNING (30), ERROR (40), CRITICAL (50) — [logging module](https://docs.python.org/3/library/logging.html)
- With no configuration, the root logger's effective level is WARNING, so `log.info(...)` prints nothing until `logging.basicConfig(level=logging.INFO)` runs — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- Logging output from the default handler goes to stderr, not stdout — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- Passing `log.info("added %s", ticket)` defers string formatting until a handler actually emits the record; an f-string is built every time even when the level filters the message out — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- `%(levelname)s`, `%(name)s`, `%(message)s` and `%(asctime)s` are LogRecord attributes usable in a `basicConfig` format string — [logging module](https://docs.python.org/3/library/logging.html)
- `basicConfig` does nothing if the root logger already has handlers (unless `force=True`), so it belongs once, at the program's entry point — [logging module](https://docs.python.org/3/library/logging.html)
- `re.compile(pattern)` returns a pattern object reusable for `finditer`, `search`, `match` and `sub`; `re.match` anchors at the start of the string, `re.search` scans the whole string — [re module](https://docs.python.org/3/library/re.html)
- Raw string literals (`r"\bTD-(\d+)\b"`) keep backslashes literal; in a normal string `"\b"` is a backspace character — [re module](https://docs.python.org/3/library/re.html)
- `match.group(1)` returns the text captured by the first parenthesised group as a str, or None when that group did not take part in the match; in `TD-(\d+)` the group always takes part, so `ticket_refs` always gets a str to pass to `int()` — [re module](https://docs.python.org/3/library/re.html)
- `pattern.sub(repl, text)` returns a new string; strings are immutable so the original is untouched — [re module](https://docs.python.org/3/library/re.html)
- `python -m venv .venv` creates an isolated environment; after activation, `pip` installs into that environment's own site-packages — [venv module](https://docs.python.org/3/library/venv.html)
- Since Python 3.13, `venv` writes a `.gitignore` inside the new environment directory whose only rule is `*`, so Git skips the environment even before the project ignores `.venv/` (proven in the W2D1 rung 4 transcript: `cat .venv/.gitignore` prints `*` under a "Created by venv" comment) — [venv module](https://docs.python.org/3/library/venv.html)
- Running `python -m pip` guarantees pip belongs to the same interpreter as `python`, which a bare `pip` command does not — [Installing Python Modules](https://docs.python.org/3/installing/index.html)
- `pip install name==X.Y.Z` pins an exact version; `requirements.txt` lists such pins one per line and `pip install -r requirements.txt` recreates them — [pip requirements file format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)
- Pylint prints messages as `file:line:column: ID: text (symbol)` followed by a score out of 10, and message ids start with C (convention), R (refactor), W (warning), E (error) or F (fatal) — [Pylint user guide](https://pylint.readthedocs.io/en/stable/)
- A file's `__name__` is `"__main__"` when run as a script and the module's name when imported, so `if __name__ == "__main__":` keeps import free of side effects — [__main__ module](https://docs.python.org/3/library/__main__.html)
- Python caches compiled bytecode of imported modules in `__pycache__/`, which belongs in `.gitignore` — [Modules tutorial](https://docs.python.org/3/tutorial/modules.html)
- A module is searched for in the script's directory first, then the rest of `sys.path`; a local file named `math.py` or `logging.py` shadows the standard library — [Modules tutorial](https://docs.python.org/3/tutorial/modules.html)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Math module
- Interview questions: What is the difference between `import math` and `from math import ceil`?; Why does `0.1 + 0.2 == 0.3` give False and what do you use instead?; What do `math.floor`, `math.ceil` and `round` each do with 2.5 and -2.5?
- Adjacent concept: Python's `round` uses banker's rounding (ties to even) — it is the first thing asked after `ceil` and `floor`, and explains why `round(2.5)` is 2.
- Trade-off or limit: `math` works on real numbers and raises ValueError outside a function's domain (`math.sqrt(-1)`); complex numbers live in `cmath` — [math module](https://docs.python.org/3/library/math.html)
- Recognise on sight: `import math as m` then `m.floor(x)`; `math.ceil(hours / 24)` to count whole days.
- Claims:
  - `math.ceil` and `math.floor` return int in Python 3 — [math module](https://docs.python.org/3/library/math.html)
  - `math.isclose` takes `rel_tol` and `abs_tol` keyword arguments; `abs_tol` matters when comparing to 0 — [math module](https://docs.python.org/3/library/math.html)
  - `import x as y` only renames the binding in the importing namespace; the module is still loaded once — [The import system](https://docs.python.org/3/reference/import.html)
  - `from math import *` is discouraged because it hides where names came from; PEP 8 asks for explicit imports — [PEP 8](https://peps.python.org/pep-0008/)
  - A module is loaded once per interpreter and cached in `sys.modules`; a second `import` reuses it — [The import system](https://docs.python.org/3/reference/import.html)

### Logging
- Interview questions: Why use `logging` instead of `print`?; What are the five levels and which shows by default?; Why `getLogger(__name__)` and not a single shared logger?
- Adjacent concept: handlers and formatters (where records go and how they look) — the follow-up to `basicConfig`, which is shorthand for attaching one StreamHandler to the root logger.
- Trade-off or limit: `basicConfig` is a one-shot convenience; libraries should never call it, only applications at their entry point — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- Recognise on sight: `log = logging.getLogger(__name__)` near the top of a module; `log.warning("%s is past its SLA", t)`.
- Claims:
  - Logger names are dotted and form a hierarchy; `desk.sub` is a child of `desk` and inherits its level — [logging module](https://docs.python.org/3/library/logging.html)
  - A named logger has no handler of its own in the desk; its records propagate up to the root logger, so the one StreamHandler `basicConfig` attaches to the root prints `log.info` from `getLogger(__name__)` — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
  - `log.error(...)` and `log.critical(...)` record at ERROR (40) and CRITICAL (50), above WARNING, so they show under the default threshold too — [logging module](https://docs.python.org/3/library/logging.html)
  - Lazy `%s` arguments avoid formatting cost for filtered records — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
  - `level=logging.DEBUG` on `basicConfig` makes debug records visible; the level is a threshold, records below it are dropped — [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
  - Adding `%(asctime)s` to the format adds a timestamp, which is why the demo omits it for stable output — [logging module](https://docs.python.org/3/library/logging.html)

### Regex
- Interview questions: What is the difference between `re.match`, `re.search` and `re.findall`?; Why do regex patterns use raw strings?; What does `\d+` match and what does a group do?
- Adjacent concept: greedy versus lazy quantifiers (`.*` versus `.*?`) — the standard follow-up once `+` and `*` are on the table.
- Trade-off or limit: a regex is the wrong tool for a fixed string; `in` or `str.replace` is simpler and faster when no pattern is needed — [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html). Design note (unsourced): the `EMAIL` pattern only approximates the address grammar, so it suits redacting likely addresses, not proving an address can receive mail.
- Recognise on sight: `re.compile(r"\bTD-(\d+)\b")` at module level; `pattern.sub("[email]", text)`.
- Claims:
  - `\b` is a word boundary, `\d` a digit, `\w` a word character, `+` one or more, `*` zero or more, `( )` a capturing group — [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html)
  - `re.match("TD-", "see TD-2")` returns None while `re.search` finds it — [re module](https://docs.python.org/3/library/re.html)
  - `finditer` yields match objects lazily; `findall` returns a list of strings (or tuples when there are groups) — [re module](https://docs.python.org/3/library/re.html)
  - Module-level `re.search(p, s)` caches compiled patterns internally, but a named compiled pattern documents intent — [re module](https://docs.python.org/3/library/re.html)
  - Inside `[ ]`, `.` and `+` are literal, so `[\w.+-]+` matches letters, digits, underscore, dot, plus and hyphen — [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html)

### pip and installing packages
- Interview questions: What does pip do and where does it get packages?; Why create a virtual environment?; What is `requirements.txt` for and why pin versions?
- Adjacent concept: PyPI, the public index pip downloads from — asked right after "where do packages come from".
- Trade-off or limit: pinning gives reproducible installs but freezes security fixes until someone bumps the pin; `pip install` runs with whatever the active environment is, so an unactivated shell installs into the wrong place — [venv module](https://docs.python.org/3/library/venv.html)
- Recognise on sight: `python -m pip install -r requirements.txt`; `.venv/` in `.gitignore`; a prompt prefixed `(.venv)`.
- Claims:
  - Activation scripts live in `.venv/Scripts/` on Windows and `.venv/bin/` on macOS and Linux — [venv module](https://docs.python.org/3/library/venv.html)
  - `pip list` shows installed packages and their versions; `pip --version` shows which Python the pip belongs to — [pip user guide](https://pip.pypa.io/en/stable/user_guide/)
  - A virtual environment is disposable: it is recreated from `requirements.txt`, so it is not committed — [venv module](https://docs.python.org/3/library/venv.html)
  - Installing a package also installs its dependencies, which `pip list` then shows — [pip user guide](https://pip.pypa.io/en/stable/user_guide/)
  - On Windows the `py` launcher selects an interpreter version (`py -3.15`) — [Python on Windows](https://docs.python.org/3/using/windows.html)

### pylint
- Interview questions: What is a linter and what does pylint check?; What is the difference between pylint and a test?; How do you silence one message and when is that acceptable?
- Adjacent concept: formatters versus linters (a formatter rewrites layout, a linter reports problems) — brought up with any style tool; name only, no formatter is taught.
- Trade-off or limit: the score is a heuristic; chasing 10/10 can push people to add noise comments, and pylint cannot prove behaviour is right — [Pylint user guide](https://pylint.readthedocs.io/en/stable/)
- Recognise on sight: `ticket_desk.py:12:0: C0115: Missing class docstring (missing-class-docstring)`; `# pylint: disable=...` comment.
- Claims:
  - Message ids: C convention, R refactor, W warning, E error, F fatal — [Pylint user guide](https://pylint.readthedocs.io/en/stable/)
  - `missing-module-docstring` (C0114), `missing-class-docstring` (C0115) and `missing-function-docstring` (C0116) are the usual first messages on new code — [Pylint messages](https://pylint.readthedocs.io/en/stable/user_guide/messages/messages_overview.html)
  - Pylint exits with a non-zero status when messages are found, which is how CI uses it — [Pylint user guide](https://pylint.readthedocs.io/en/stable/)
  - PEP 8 names `snake_case` for functions and `CapWords` for classes, which pylint's naming checks enforce — [PEP 8](https://peps.python.org/pep-0008/)
  - PEP 257 defines docstring conventions the missing-docstring checks point at — [PEP 257](https://peps.python.org/pep-0257/)

### Writing your own module
- Interview questions: What is a module versus a package?; What does `if __name__ == "__main__":` do?; Why does importing a module sometimes run code?
- Adjacent concept: circular imports (a imports b and b imports a) — the classic failure once code is split across files; named only.
- Trade-off or limit: splitting too early scatters small code across files; a module earns its own file by being imported by more than one caller or by having one clear job — [Modules tutorial](https://docs.python.org/3/tutorial/modules.html)
- Recognise on sight: `from desk import Desk, Ticket`; a `main()` function followed by the `__name__` guard.
- Claims:
  - Importing a module executes its top-level statements once; function and class bodies only define, they do not run — [Modules tutorial](https://docs.python.org/3/tutorial/modules.html)
  - A module's `__name__` is its file name without `.py` when imported — [__main__ module](https://docs.python.org/3/library/__main__.html)
  - `import desk` followed by `desk = Desk()` rebinds `desk` from module to instance; the earlier module reference is lost — [The import system](https://docs.python.org/3/reference/import.html)
  - Inside a function, assigning to a name makes it local for the whole function, so using it earlier raises UnboundLocalError — [Python FAQ: local and global variables](https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value)
  - `git merge` of a feature branch into `main` followed by `git push origin main` publishes the work; git was taught W1D2 — [git merge](https://git-scm.com/docs/git-merge)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- The Python math module — https://docs.python.org/3/library/math.html
- The Python logging module — https://docs.python.org/3/library/logging.html
- Logging HOWTO — https://docs.python.org/3/howto/logging.html
- The Python re module — https://docs.python.org/3/library/re.html
- Regular Expression HOWTO — https://docs.python.org/3/howto/regex.html
- The Python venv module — https://docs.python.org/3/library/venv.html
- Installing Python Modules — https://docs.python.org/3/installing/index.html
- Modules tutorial — https://docs.python.org/3/tutorial/modules.html
- The import system — https://docs.python.org/3/reference/import.html
- __main__ module — https://docs.python.org/3/library/__main__.html
- Python on Windows — https://docs.python.org/3/using/windows.html
- PEP 8 — https://peps.python.org/pep-0008/
- PEP 257 — https://peps.python.org/pep-0257/
- pip requirements file format — https://pip.pypa.io/en/stable/reference/requirements-file-format/
- pip user guide — https://pip.pypa.io/en/stable/user_guide/
- Pylint user guide — https://pylint.readthedocs.io/en/stable/
- git merge — https://git-scm.com/docs/git-merge

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- logging level | A label (DEBUG, INFO, WARNING, ERROR, CRITICAL) on each log message, plus a threshold below which messages are dropped. | aka: log level, log levels, severity level
- logger | A named object that code calls to record events, which the logging system routes to handlers such as the console. | aka: loggers, getLogger
- regular expression | A compact pattern language for finding or replacing text that follows a shape, such as a ticket reference or an email address. | aka: regex, regexes, regexp, regular expressions
- pip | The tool that downloads and installs Python packages from an index into the active environment. | aka: pip install
- PyPI | The public online index that pip downloads packages from. | aka: Python Package Index
- requirements file | A text file listing the packages and versions a project needs so another machine can install the same set. | aka: requirements.txt, pinned dependencies, pinning
- linter | A tool that reads source code without running it and reports style problems and likely mistakes. | aka: linters, linting, pylint
- __name__ guard | The `if __name__ == "__main__":` test that runs code only when a file is run directly, not when it is imported. | aka: main guard, name guard, __main__

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Calling `log.info(...)` with no `basicConfig` and seeing nothing, because the default threshold is WARNING; or calling the module-level function `logging.info()` or `logging.warning()` before `basicConfig`, which configures the root logger implicitly so the later `basicConfig` is silently ignored (a named logger's `log.info()` configures nothing, so it does not cause this).
- Writing `"\bTD-"` without the `r` prefix: `\b` becomes a backspace character and the pattern silently matches nothing; also confusing `re.match` (start only) with `re.search`.
- Running a bare `pip install` or `pylint` in a shell where the venv is not activated (prompt lacks `(.venv)`), so the package lands in, or is missing from, the wrong Python; on Windows `python` may not be 3.15.
- Committing `.venv/` or `__pycache__/` because `.gitignore` was created after `git add .`.
- Naming a file `math.py`, `logging.py` or `re.py` so it shadows the standard library, or writing `import desk` then `desk = Desk()` which rebinds the module name to the instance.
- Putting script code at the top level of a module with no `__name__` guard, so importing it prints the board or reconfigures logging.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- 01_desk_math then 02_desk_logging: in 01_desk_math type `import math` beside `from datetime import datetime, timedelta` and use the REPL lines (`import math as m`, `m.floor(2.7)`, `math.sqrt(16)`, `math.pi`, `math.isclose(0.1 + 0.2, 0.3)`) to show that `import` binds the module name while `from ... import` binds single names, then run `python ticket_desk.py` so `math.ceil` in `days_open` visibly rounds part-days up; in 02_desk_logging run the script three times so the room sees the INFO lines appear once `basicConfig(level=logging.INFO)` is the first line, the `log.debug` line stay hidden at INFO and appear at `level=logging.DEBUG` before the level is set back, and the f-string log call rewritten with `%s`; that log lines go to stderr while the board goes to stdout is a talking point.
- 03_ticket_patterns: compile `TICKET_REF` and `EMAIL` with the constants and print `ticket_refs(note)` as `[2, 5]` and `redact(note)` with `[email]` in place of the address; the transient lines are `re.match` against `re.search` on the same note (None against a match) and a `"\b"` pattern without the `r` prefix shown then deleted, so both classic regex failures are seen before trainees meet them.
- 04_pip_and_pylint: show `python --version`, create the venv with the 3.14 fallback and say the one-line reason, activate it until the prompt shows `(.venv)`, run `python -m pip --version` so the venv path proves which Python pip belongs to, install `pylint==4.0.0` and read `python -m pip list` (pylint's dependencies arrive with it), then read pylint's score and each message id aloud before fixing it; write `.gitignore` before `git add` and add files by name; an unactivated shell installing into the wrong Python is a talking point, not a typed step.
- 05_desk_module: move the model into `desk.py` by cut and paste from a ```text listing, run `python ticket_desk.py` to show the same board with log lines now reading `INFO desk: ...`, then `python -c "import desk; print(desk.__name__, desk.Ticket)"` and `ls __pycache__` to show that importing runs no `main()` and leaves cached bytecode; finish with `pylint desk.py ticket_desk.py`, the merge into `main` and `git push origin main`; the `import desk` then `desk = Desk()` rebinding pitfall is named as a talking point, never typed.
