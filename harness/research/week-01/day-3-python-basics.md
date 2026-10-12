# w01d3 — Python basics

gate: light
verified: 2026-10-12
week: 1 · Agile for developers, Git & Python fundamentals
day: 3 · python-basics

version-stamps:
  - python: 3.12 (verified 2026-10-12)
  - sys (standard library): 3.12 (verified 2026-10-12)

## Claims (each MUST carry a source on a full gate; light gate: source optional but recommended)

- PEP 8 sets the style conventions: snake_case for functions and variables, UPPER_CASE for constants, four-space indents, lines of at most 79 characters, two blank lines around top-level definitions, imports at the top of the file. — [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- PEP 8 states that comments that contradict the code are worse than no comments, and that inline comments are unnecessary and distracting if they state the obvious; "a comment says why, not what" is the team convention this course draws from those two statements, not a PEP 8 quotation. — [PEP 8 – Comments](https://peps.python.org/pep-0008/#comments)
- A module docstring is a string literal that is the first statement of the module; PEP 257 defines the conventions. — [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- Python variables are names bound to objects and are not declared with a type; `type()` reports the type of the object currently bound. — [Python tutorial: An Informal Introduction to Python](https://docs.python.org/3/tutorial/introduction.html)
- `/` is true division and always returns a float, `//` is floor division, `%` is the remainder, and `**` binds tighter than a unary minus on its left, so `-2 ** 2` is `-4`. — [Python tutorial: Numbers](https://docs.python.org/3/tutorial/introduction.html#numbers)
- Comparisons can be chained (`0 <= x < 24`), and `and` / `or` short-circuit and return one of their operands; `not` always returns `True` or `False`. — [Python reference: Comparisons and Boolean operations](https://docs.python.org/3/reference/expressions.html#comparisons)
- `x == "a" or "b"` parses as `(x == "a") or "b"`; when the comparison is false the expression evaluates to the string `"b"`, which is truthy because it is non-empty, so the check never fails. — [Python reference: Boolean operations](https://docs.python.org/3/reference/expressions.html#boolean-operations)
- `in` and `not in` test membership and return a bool; for two strings, `x in y` is true when `x` is a substring of `y`. An augmented assignment such as `hours_open += 0.5` evaluates the target once, applies the operator and rebinds the name. — [Python reference: Membership test operations](https://docs.python.org/3/reference/expressions.html#membership-test-operations) and [Augmented assignment statements](https://docs.python.org/3/reference/simple_stmts.html#augmented-assignment-statements)
- `round()` rounds a tie to the nearest even choice, so `round(2.5)` is `2` and `round(3.5)` is `4`; 2.5 is exactly representable as a float, so this result is the tie rule alone. — [Built-in functions: round](https://docs.python.org/3/library/functions.html#round)
- `round(2.675, 2)` is `2.67`, not `2.68`, for a separate reason: most decimal fractions cannot be represented exactly as a binary float, and the stored value is slightly below 2.675. — [Built-in functions: round](https://docs.python.org/3/library/functions.html#round)
- f-strings accept a format spec after a colon: `<` left, `>` right, width and `.1f` precision. — [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#format-specification-mini-language)
- `print()` takes `sep`, `end`, `file` and `flush` keyword arguments; `file=sys.stderr` sends output to the error stream. — [Built-in functions: print](https://docs.python.org/3/library/functions.html#print)
- `input(prompt)` writes the prompt, reads one line from standard input, strips the trailing newline and always returns `str`; it raises `EOFError` when standard input is at end of file. — [Built-in functions: input](https://docs.python.org/3/library/functions.html#input)
- `sys.stdin.isatty()` is true when standard input is a character device such as an interactive terminal, false when it is a pipe or a regular file; on Windows the NUL device also reports true, so unattended runs should pipe input rather than redirect from NUL. — [sys.stdin](https://docs.python.org/3/library/sys.html#sys.stdin) and [io.IOBase.isatty](https://docs.python.org/3/library/io.html#io.IOBase.isatty)

## Sources (official / primary docs preferred; ≥3; full gate: every URL fetched and confirmed)

- PEP 8 – Style Guide for Python Code — https://peps.python.org/pep-0008/
- PEP 257 – Docstring Conventions — https://peps.python.org/pep-0257/
- The Python Tutorial: An Informal Introduction to Python — https://docs.python.org/3/tutorial/introduction.html
- Python reference: Expressions — https://docs.python.org/3/reference/expressions.html
- Python reference: Simple statements, Augmented assignment statements — https://docs.python.org/3/reference/simple_stmts.html#augmented-assignment-statements
- Python library: Built-in functions — https://docs.python.org/3/library/functions.html
- Python library: string, Format Specification Mini-Language — https://docs.python.org/3/library/string.html#format-specification-mini-language
- Python library: sys — https://docs.python.org/3/library/sys.html
- Python library: io — https://docs.python.org/3/library/io.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- PEP 8 | The official Python style guide that a team adopts as its shared contract for names, layout and comments. | aka: PEP8, Python style guide
- snake_case | A naming style that writes identifiers in lowercase words joined by underscores, used for Python variables and functions. | aka: snake case, lower_case_with_underscores
- docstring | A string literal placed first in a module, function or class that documents what it is for and is readable at runtime. | aka: docstrings, module docstring
- f-string | A string literal prefixed with f whose braces hold expressions and optional format specs that are evaluated when the line runs. | aka: f-strings, formatted string literal, formatted string literals
- operator precedence | The fixed ranking that decides which operator in an expression is applied first when there are no parentheses. | aka: precedence, order of operations
- short-circuit evaluation | The rule that and/or stop evaluating as soon as the result is known and return one of their operands rather than a pure True or False. | aka: short-circuit, short circuit, short-circuiting
- standard streams | The three channels every process gets, stdin for input, stdout for normal output and stderr for warnings and errors. | aka: stdin, stdout, stderr

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Writing `priority == "high" or "normal"` and believing it checks two values; with `priority = "low"` it evaluates to the string `normal` (not `True`, not `False`), which is truthy, so every ticket passes the check.
- Using `=` where `==` is meant, or mixing up `is` with `==` for comparing values.
- Expecting `/` to return an int (it always returns float) or `-2 ** 2` to be `4` (it is `-4`). Separately, expecting `round(2.5)` to be `3`: it is `2` because ties go to the even neighbour; and blaming that same tie rule for `round(2.675, 2) == 2.67`, which is float representation error instead.
- Comments that restate the code (`# add one to x`) or go stale after an edit, versus comments that record the reason for a rule such as an SLA threshold; PEP 8 calls obvious inline comments distracting and contradicting comments worse than none.
- Lowercase constants or camelCase names from other languages, lines over 79 columns, and imports placed mid-file; the room should learn to read them as review comments, not taste.
- Calling `input()` unconditionally: under pytest's default capture it raises `OSError: pytest: reading from stdin while output is captured`, and with an empty standard input it raises `EOFError: EOF when reading a line`; the `sys.stdin.isatty()` guard avoids both. The guard is false for a pipe or a regular file, but on Windows the NUL device (the null device in every shell there, Git Bash included) also reports true, so a run redirected from it enters the guard and crashes on `input()`; test the unattended path with a pipe, `echo "" | python ticket_desk.py`. Typed text is always `str`, and casting is Thursday's topic.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Demo 1 (01_ticket_record): start with `git switch -c feature/ticket-record`, then type `ticket_desk.py` in PEP 8 shape from the first line (module docstring, `SLA_HOURS_*` constants, the flat ticket variables); paste a restating comment next to a why-comment and delete the restating one live, so the comment rule is a visible edit; finish with `python ticket_desk.py` and `type()` on two variables.
- Demo 2 (02_ticket_rules): run the `priority == "high" or "normal"` pitfall with `priority = "low"` and have the room predict the output before it prints the string `normal` (not `True`), which is short-circuit evaluation made visible; delete it and write the three `==` version. Type `/` beside `//`, `%` for the every-third escalation, `-2 ** 2`, `round(2.5)`, `hours_open += 0.5`, `is_breached = is_open and hours_left < 0`, a `not` on a bool, the chained comparison `0 <= hours_open < 24` and one `in` test, each with the output predicted aloud first. Keep `in` to a substring of `title` (string against string), since lists, tuples and sets are deferred to w01d4.
- Demo 3 (03_desk_intake): run the script at a terminal (prompts appear), then unattended with a pipe, `echo "" | python ticket_desk.py`, which works in PowerShell, cmd and Git Bash and gives `isatty() == False`, to show the guard keeps the sample values; do not redirect from the null device, which reports a terminal on Windows and crashes on `input()` (in cmd or Git Bash a redirect from a real file, `python ticket_desk.py < sample.txt`, is the only safe redirect). Show `sep`, `end`, the aligned board and a `file=sys.stderr` line (`2> err.txt` splits the streams). Close the thread inside this demo: `git switch main`, `git merge feature/ticket-record`, then `git log --oneline` to show the day's three commits on `main`.
