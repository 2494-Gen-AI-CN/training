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

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Python syntax
- Interview questions: How does Python mark a block of code, and what happens if the indentation is inconsistent?; What does PEP 8 say about line length, blank lines and where imports go?; Follow-up: how does a long expression continue across lines, and which way does PEP 8 prefer?
- Adjacent concept: Naming conventions (snake_case, UPPER_CASE, CapWords) — the next question after layout is always how identifiers are named, and a reviewer reads both in the same pass.
- Trade-off or limit: Significant indentation removes brace noise but makes whitespace part of the program, so a block that mixes tabs and spaces in a way that makes its meaning depend on how many spaces a tab is worth is rejected with a TabError, and PEP 8 asks for four spaces per level. — [Python reference: Indentation](https://docs.python.org/3/reference/lexical_analysis.html#indentation)
- Recognise on sight: `import os, sys` on one line, a `def` with one blank line above it, or `Total_Count = 3` at module level, each of which a PEP 8 reviewer flags.
- Claims:
  - A logical line ends at a NEWLINE token unless it sits inside brackets or ends in a backslash; PEP 8 prefers continuing inside parentheses over using a backslash. — [Python reference: Explicit line joining](https://docs.python.org/3/reference/lexical_analysis.html#explicit-line-joining) and [PEP 8 – Maximum Line Length](https://peps.python.org/pep-0008/#maximum-line-length)
  - Statements in a block are grouped by indentation, and a block with inconsistent dedent raises IndentationError. — [Python reference: Indentation](https://docs.python.org/3/reference/lexical_analysis.html#indentation)
  - PEP 8 asks for two blank lines around top-level function and class definitions. — [PEP 8 – Blank Lines](https://peps.python.org/pep-0008/#blank-lines)
  - PEP 8 asks for imports at the top of the file, after the module docstring and before module globals, with standard-library imports first. — [PEP 8 – Imports](https://peps.python.org/pep-0008/#imports)
  - PEP 8 recommends limiting lines to 79 characters and says individual teams may agree on a longer limit. — [PEP 8 – Maximum Line Length](https://peps.python.org/pep-0008/#maximum-line-length)
  - PEP 8 says a project's own style guide takes precedence over PEP 8 itself, and that consistency within a project matters more than consistency with the guide, and consistency within one module or function matters most. — [PEP 8 – Introduction](https://peps.python.org/pep-0008/#introduction) and [PEP 8 – A Foolish Consistency](https://peps.python.org/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds)

### Comments
- Interview questions: What is the difference between a comment and a docstring?; When is a comment a bad comment?; Follow-up: how does a comment go stale, and what in a code review catches it?
- Adjacent concept: Docstrings and self-documenting names — an interviewer asks what you do before reaching for a comment, and the answer is a clearer name or a docstring.
- Trade-off or limit: A comment is never checked by the interpreter or by tests, so unlike code it can silently drift from the behaviour, which is why PEP 8 says comments that contradict the code are worse than none. — [PEP 8 – Comments](https://peps.python.org/pep-0008/#comments)
- Recognise on sight: `x = x + 1  # add one to x` (restates the code) against `SLA_HOURS_HIGH = 4  # contract with the customer, see policy` (records a reason).
- Claims:
  - A comment starts with `#` (outside a string literal) and runs to the end of the physical line, and the tokenizer ignores it; the one exception is an encoding declaration in the first or second line. A `#!` first line is read by the OS, not by Python. — [Python reference: Comments](https://docs.python.org/3/reference/lexical_analysis.html#comments)
  - A `#` inside a string literal is part of the string, not a comment. — [Python reference: Comments](https://docs.python.org/3/reference/lexical_analysis.html#comments)
  - PEP 8 says inline comments should be separated from the statement by at least two spaces and start with `# `. — [PEP 8 – Inline Comments](https://peps.python.org/pep-0008/#inline-comments)
  - A docstring is available at runtime as the `__doc__` attribute, a comment is not. — [PEP 257 – What is a Docstring?](https://peps.python.org/pep-0257/#what-is-a-docstring)
  - PEP 8 asks that comments be complete sentences and be kept up to date when the code changes. — [PEP 8 – Comments](https://peps.python.org/pep-0008/#comments)

### Variables and datatypes
- Interview questions: Is Python statically or dynamically typed, and what does `type(x)` tell you?; What does `a = b` do when `b` holds a number or a string?; Follow-up: what is the difference between a name being rebound and an object being changed?
- Adjacent concept: Identity versus equality (`is` against `==`) — it comes up as soon as you say a variable is a name for an object rather than a box that holds a value.
- Trade-off or limit: Dynamic typing lets one name hold a str now and an int later, so a type mistake surfaces only when that line runs, and nothing in the language marks a name as a constant. — [Python reference: Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
- Recognise on sight: `count = "3"` later used as `count + 1` (a TypeError at run time), or `MAX_RETRIES = 3` reassigned further down the file.
- Claims:
  - Assignment binds a name to an object; it does not copy a value into a typed slot. — [Python reference: Assignment statements](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements)
  - The built-in scalar types for today are int (unbounded precision), float (a C double), str and bool; bool is a subclass of int, so `True + 1` is `2`. — [Library: Built-in types](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)
  - `0.1 + 0.2 == 0.3` is False because binary floats cannot store most decimal fractions exactly. — [Tutorial: Floating-point arithmetic](https://docs.python.org/3/tutorial/floatingpoint.html)
  - Identifiers are case-sensitive and may contain letters, digits and underscores but cannot start with a digit or be a keyword. — [Python reference: Identifiers and keywords](https://docs.python.org/3/reference/lexical_analysis.html#identifiers)
  - PEP 8 names constants in UPPER_CASE with underscores, and variables and functions in lowercase_with_underscores. — [PEP 8 – Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions)
  - An f-string evaluates its braces at run time, so `f"{hours_open}"` shows the current binding of the name. — [Reference: Formatted string literals](https://docs.python.org/3/reference/lexical_analysis.html#f-strings)

### Operators
- Interview questions: What is the difference between `/` and `//`, and what does `%` return for a negative number?; Why does `x == "a" or "b"` always pass?; Follow-up: what do `and` and `or` return, and how does that differ from `not`?
- Adjacent concept: Operator precedence and parentheses — the next question after any operator list is which one binds first, and the readable answer is to add parentheses.
- Trade-off or limit: `and` / `or` return an operand rather than a bool, which enables the `value or default` idiom but also hides bugs when a falsy value such as `0` or `""` is a legitimate input. — [Python reference: Boolean operations](https://docs.python.org/3/reference/expressions.html#boolean-operations)
- Recognise on sight: `if status == "open" or "new":` (always true), `a < b < c` (chained comparison), or `n % 3 == 0` (every third).
- Claims:
  - `//` floors toward negative infinity, so `-7 // 2` is `-4`, and `%` takes the sign of the right operand, keeping `a == (a // b) * b + a % b`. — [Python reference: Binary arithmetic operations](https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations)
  - `a < b < c` is evaluated as `a < b and b < c` with `b` evaluated once. — [Python reference: Comparisons](https://docs.python.org/3/reference/expressions.html#comparisons)
  - `not` binds looser than comparison operators, so `not a == b` means `not (a == b)`. — [Python reference: Operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence)
  - `and` binds tighter than `or`, so `a or b and c` is `a or (b and c)`. — [Python reference: Operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence)
  - `==` compares values and `is` compares object identity; since Python 3.8, `is` or `is not` with a literal such as `x is "high"` emits a SyntaxWarning at compile time. — [Python reference: Identity comparisons](https://docs.python.org/3/reference/expressions.html#identity-comparisons) and [What's New In Python 3.8](https://docs.python.org/3/whatsnew/3.8.html)
  - Integer division or modulo by zero raises ZeroDivisionError. — [Library: Built-in Exceptions, ZeroDivisionError](https://docs.python.org/3/library/exceptions.html#ZeroDivisionError)

### User input and output
- Interview questions: What type does `input()` return?; What is the difference between stdout and stderr, and why print a warning to stderr?; Follow-up: how does a script behave when its standard input is a pipe instead of a terminal?
- Adjacent concept: Standard streams and redirection (`>`, `2>`, `|`) — the next question about print is where the output goes when the program runs under a shell, a scheduler or a test runner.
- Trade-off or limit: `input()` blocks waiting for a line, so a script that calls it unconditionally hangs or raises EOFError when run unattended or under a test runner; the usual guard is checking `sys.stdin.isatty()`. — [Built-in functions: input](https://docs.python.org/3/library/functions.html#input)
- Recognise on sight: `print(..., file=sys.stderr)`, `print(a, b, sep=", ", end="")` and `f"{name:<30}{n:>6.1f}"` for aligned columns.
- Claims:
  - `print` joins its arguments with `sep` (default a space) and ends with `end` (default a newline). — [Built-in functions: print](https://docs.python.org/3/library/functions.html#print)
  - `sys.stdout` and `sys.stderr` are separate text streams, so a shell can redirect them to different places. — [Library: sys.stdout, sys.stderr](https://docs.python.org/3/library/sys.html#sys.stdout)
  - In a format spec, `<` and `>` align within a minimum width, and `.1f` fixes one digit after the decimal point. — [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#format-specification-mini-language)
  - `print` converts each non-string argument with `str()`, so `print(1.0)` shows `1.0`; an f-string field without a spec calls `format(value, "")`, which for these types gives the same text as `str()`. — [Built-in functions: print](https://docs.python.org/3/library/functions.html#print) and [Reference: Formatted string literals](https://docs.python.org/3/reference/lexical_analysis.html#f-strings)
  - Standard output is line-buffered when attached to a terminal and block-buffered otherwise, so `flush=True` matters when output is piped. — [Library: sys.stdout](https://docs.python.org/3/library/sys.html#sys.stdout)

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
- Python reference: Lexical analysis — https://docs.python.org/3/reference/lexical_analysis.html
- Python reference: Execution model, Naming and binding — https://docs.python.org/3/reference/executionmodel.html#naming-and-binding
- Python library: Built-in types — https://docs.python.org/3/library/stdtypes.html
- Python library: Built-in Exceptions — https://docs.python.org/3/library/exceptions.html
- The Python Tutorial: Floating-Point Arithmetic — https://docs.python.org/3/tutorial/floatingpoint.html
- The Python Tutorial: Input and Output — https://docs.python.org/3/tutorial/inputoutput.html
- What's New In Python 3.8 — https://docs.python.org/3/whatsnew/3.8.html

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
