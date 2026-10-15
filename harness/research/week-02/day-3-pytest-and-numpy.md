# w02d3 — Testing with pytest & NumPy

gate: light
verified: 2026-10-15
week: 2 · Python advanced
day: 3 · day-3-pytest-and-numpy

version-stamps:
  - python: 3.15 (verified 2026-10-15)
  - pytest: 9.1.1 (verified 2026-10-15)   # pinned in requirements.txt at rung 10
  - numpy: 2.5.4 (verified 2026-10-15)   # pinned in requirements.txt at rung 12; Python 3.15 wheel on PyPI: numpy-2.5.4-cp315-cp315-win_amd64.whl

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- pytest discovers test files named `test_*.py` or `*_test.py` and, inside them, functions whose names start with `test` — [pytest: Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- A plain `assert` statement is enough in pytest; on failure pytest rewrites the assertion to show the values on both sides — [pytest: How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
- `pytest.raises(ValueError, match="urgent")` passes only when the block raises that exception type and the message matches the regular expression (pytest applies `re.search` to the message) — [pytest: How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
- `pytest.approx` compares floating-point numbers within a tolerance (by default a relative tolerance of 1e-6 and an absolute tolerance of 1e-12), so `0.1 + 0.2 == pytest.approx(0.3)` passes — [pytest: API reference](https://docs.pytest.org/en/stable/reference/reference.html)
- A fixture is a function marked with `@pytest.fixture`; a test receives its return value by naming the fixture as a parameter — [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- `tmp_path` is a built-in fixture giving each test function its own unique temporary directory as a `pathlib.Path` — [pytest: How to use temporary directories and files](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- `@pytest.mark.parametrize` runs one test function once per argument set, and each case is reported separately under its own ID — [pytest: How to parametrize fixtures and test functions](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- `pytest -k expression` selects tests whose names match the expression — [pytest: How to invoke pytest](https://docs.pytest.org/en/stable/how-to/usage.html)
- `pytest -v` raises verbosity so each test is printed on its own line with its result — [pytest: Managing pytest's output](https://docs.pytest.org/en/stable/how-to/output.html)
- A decorator is a function applied with `@` syntax to the function defined on the next line: `@name` above `def f` is shorthand for `f = name(f)` — [Python glossary: decorator](https://docs.python.org/3/glossary.html#term-decorator)
- The standard library ships `unittest`, so a Python install can run unit tests with no third-party package — [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- pytest runs `unittest.TestCase`-based tests as well as its own plain-function tests — [pytest: How to use unittest-based tests with pytest](https://docs.pytest.org/en/stable/how-to/unittest.html)
- On a list, `* 2` repeats the sequence and `+` only concatenates another sequence, so `hours + 1` raises `TypeError` — [Python: Common sequence operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations)
- On a NumPy array, arithmetic with a number such as `arr * 2` or `arr + 1` is applied to every element — [NumPy: the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html)
- Every array has a `dtype` (the type of every element) and a `shape` tuple, such as `(3,)` for three elements in one dimension — [NumPy: The N-dimensional array (ndarray)](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- Indexing an array with a boolean array of the same shape keeps the elements where the boolean is True, so `arr[arr > 24]` filters without a loop — [NumPy: Indexing on ndarrays](https://numpy.org/doc/stable/user/basics.indexing.html)
- `bool()` on an array of more than one element raises `ValueError` because its truth value is ambiguous, which is what `assert arr == [..]` triggers — [NumPy: The N-dimensional array (ndarray)](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- `numpy.array_equal(a1, a2)` returns a single `True` only when both arrays have the same shape and the same elements — [numpy.array_equal](https://numpy.org/doc/stable/reference/generated/numpy.array_equal.html)
- `timedelta.total_seconds()` returns the whole duration as a float, unlike `.seconds`, which is only the seconds component — [datetime — timedelta objects](https://docs.python.org/3/library/datetime.html#timedelta-objects)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Testing overview
- Interview questions: Why do teams write automated tests?; What is the difference between a unit, an integration and an end-to-end test?; Why are there usually more unit tests than end-to-end tests, and what does that cost when it goes wrong?
- Adjacent concept: What does "green before merge" mean in a code review? — a test run is the check a reviewer cannot do by eye, so a team runs the whole suite and expects every test to pass before a branch is merged into `main`.
- Trade-off or limit: A coverage tool reports which lines ran during the tests and which did not; a line that ran was executed, not necessarily checked by an `assert`, so a high coverage figure does not prove the behaviour is right — [Coverage.py documentation](https://coverage.readthedocs.io/)
- Recognise on sight: a `test_*.py` file beside the code or a `tests/` folder, and a "checks passed" line on a pull request; on a whiteboard, the test pyramid: many small fast unit tests at the base (one function at a time), fewer integration tests in the middle (several pieces working together, such as the desk plus its JSON file), and a few slow end-to-end tests at the top (the whole program driven as a user would). Martin Fowler's "Test Pyramid" entry (https://martinfowler.com/bliki/TestPyramid.html) is the usual reading on the picture, a supplement rather than an official source.
- Claims:
  - The standard library ships `unittest`, so a Python install can run unit tests with no third-party package — [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
  - `unittest` names four building blocks: a test fixture (set-up and clean-up), a test case (the individual unit of testing), a test suite (a collection of test cases) and a test runner (which executes the tests and reports the outcome) — [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
  - pytest documents two test layouts: test files in a separate `tests/` folder outside the application code, or test modules placed alongside the application code — [pytest: Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
  - pytest runs existing `unittest.TestCase` tests unchanged, so a team can switch runners without rewriting its suite — [pytest: How to use unittest-based tests with pytest](https://docs.pytest.org/en/stable/how-to/unittest.html)

### Unit testing
- Interview questions: What makes a good unit test?; What is the arrange-act-assert pattern?; How would you test a function that reads a file without touching the real disk?
- Adjacent concept: Test isolation — an interviewer asks how a unit test avoids depending on real files or the clock; here the answer is a temporary directory per test and a fixed `NOW` in `desk.py` in place of the current time.
- Trade-off or limit: A test that writes to a shared real file depends on whatever other tests left there; `tmp_path` gives each test function its own unique directory, which removes that dependency at the cost of the test never touching the real `tickets.json` — [pytest: How to use temporary directories and files](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- Recognise on sight: `def test_overdue_skips_closed_tickets():` with a few set-up lines (arrange), one call (act) and one `assert` (assert)
- Claims:
  - A test case checks for a specific response to a particular set of inputs, which is exactly the shape of one `test_` function — [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
  - pytest's short test summary names each failing test as `file::function`, so a name such as `test_unknown_priority_raises` states which rule broke — [pytest: Managing pytest's output](https://docs.pytest.org/en/stable/how-to/output.html)
  - A fixture in the default function scope is created again for each test that requests it and torn down at the end of that test, so tests do not share mutable data — [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
  - Testing error paths is part of unit testing: `pytest.raises` turns "this input must fail" into an assertion that fails if no exception is raised — [pytest: How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html)

### Pytest
- Interview questions: How does pytest find tests?; What is a fixture and why use one instead of repeating set-up?; How do you run the same test against several inputs?
- Adjacent concept: `unittest` against pytest — interviewers ask why many teams choose pytest; plain `assert` with readable failure reports and fixtures requested by name are the usual answer.
- Trade-off or limit: A parametrised test packs many cases into one definition, which is shorter but hides which case failed unless the report says so; pytest builds an ID from each parameter set (for example `test_sla_hours[high-4]`) and reports every case separately — [pytest: How to parametrize fixtures and test functions](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- Recognise on sight: `@pytest.fixture` above `def sample_desk():`, and `@pytest.mark.parametrize("priority, hours", [("high", 4), ...])` above a test
- Claims:
  - Running `pytest` with no arguments collects `test_*.py` and `*_test.py` files in the current folder and the folders below it, and prints `.` for each pass and `F` for each failure — [pytest: Get Started](https://docs.pytest.org/en/stable/getting-started.html)
  - A failure report shows the failing line, the values compared and the difference between them — [pytest: How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
  - `pytest --version` prints the installed version, the first check after installing pytest — [pytest: Get Started](https://docs.pytest.org/en/stable/getting-started.html)
  - A requirements file lists pinned packages such as `pytest==9.1.1`, and `pip install -r requirements.txt` installs everything in it, which is how a fresh clone rebuilds the same environment — [pip: Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)
  - A test can request several fixtures at once, for example the built-in `tmp_path` and a project fixture such as `sample_desk`, and fixtures can themselves request other fixtures — [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
  - `@name` above a `def` hands the function to `name`; pytest uses that to register a fixture or to mark a test — [Python glossary: decorator](https://docs.python.org/3/glossary.html#term-decorator)

### Numpy
- Interview questions: Why is a NumPy array faster and more compact than a list of numbers?; What does `arr * 2` do, and what does `lst * 2` do?; What are `dtype` and `shape`, and what happens when you put a float into an int array?
- Adjacent concept: Boolean masks — the interviewer asks how to filter an array without a loop; `arr[arr > 24]` and `(a > b).sum()` are the answer, and they are how the breach count is computed.
- Trade-off or limit: An array holds one dtype, so `np.array` picks a type that can represent every value (ints mixed with floats become floats; anything with a string becomes a string); the fixed type is what makes whole-array arithmetic fast but removes the list's freedom to mix types — [numpy.array](https://numpy.org/doc/stable/reference/generated/numpy.array.html)
- Recognise on sight: `import numpy as np` (the import convention the NumPy documentation uses throughout), then `np.array(...)`, `arr.mean()`, `arr > 24` and `np.median(arr)`
- Claims:
  - `np.array([3.0, 30.0, 6.5])` builds a one-dimensional array with `dtype` `float64` and `shape` `(3,)` — [numpy.array](https://numpy.org/doc/stable/reference/generated/numpy.array.html)
  - `arr.mean()` and `arr.max()` are array methods; `np.median(arr)` is a module-level function with no method form — [numpy.median](https://numpy.org/doc/stable/reference/generated/numpy.median.html)
  - Comparing two arrays of the same shape with `>` is an element-by-element operation (a ufunc) that returns a boolean array, so `hours > limits` replaces a loop — [NumPy: Universal functions (ufunc)](https://numpy.org/doc/stable/reference/ufuncs.html)
  - `hours.mean()` returns an `np.float64`, and NumPy 2 prints such a scalar as `np.float64(16.5)` inside a dict or list, so `float(...)` in `summary()` keeps the printed summary plain — [NEP 51: Changing the representation of NumPy scalars](https://numpy.org/neps/nep-0051-scalar-representation.html)
  - `np.float64` inherits from Python `float`, but NumPy's integer scalars do not inherit from `int`, so `json.dumps` accepts the mean yet rejects the `np.int64` from `breached(desk).sum()` ("Object of type int64 is not JSON serializable"); `int(...)` converts it — [NumPy: Scalars](https://numpy.org/doc/stable/reference/arrays.scalars.html), [json: JSONEncoder](https://docs.python.org/3/library/json.html#json.JSONEncoder)
  - Summing a boolean array counts the True values, because booleans behave as the integers 0 and 1 in arithmetic — [Python: Boolean type](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool), [numpy.sum](https://numpy.org/doc/stable/reference/generated/numpy.sum.html)

### Interview mindset - 1st part
- Interview questions: Walk me through how you would approach this problem; What would you do if you did not know the answer?; How would you check that your answer works?
- Adjacent concept: How a junior interview is judged — interviewers weigh how a candidate reasons aloud, asks clarifying questions and checks their own answer as much as the final code; it belongs with testing because "how would you check it works" is a standard closing question, and naming edge cases is the same skill as choosing unit tests.
- Trade-off or limit: A hand-checked answer that compares floats with `==` is fragile, because `0.1 + 0.2 == 0.3` is False in binary floating point; a candidate checking a computed mean says what tolerance counts as equal, as `pytest.approx` does — [Python tutorial: Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- Recognise on sight: a candidate who restates the problem, names an example input and output, states the plan in a sentence or two (thinking aloud costs time on a timed problem, so the plan stays short), writes the simple solution first, then checks one normal case, an empty input and a boundary value
- Claims:
  - `pytest.approx` uses a default relative tolerance of 1e-6 and absolute tolerance of 1e-12, and both can be set explicitly with `rel=` and `abs=` — [pytest: API reference](https://docs.pytest.org/en/stable/reference/reference.html)
  - `max()` raises `ValueError` on an empty iterable unless a `default=` value is given, a standard example of an edge case to name before coding — [Python: Built-in functions, max](https://docs.python.org/3/library/functions.html#max)
  - Python emits no code for `assert` statements when run with optimisation (`python -O`), so `assert` belongs in tests while a function that must reject bad input raises an exception, as `Desk` does with `ValueError` — [Python reference: The assert statement](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- pytest: Get Started — https://docs.pytest.org/en/stable/getting-started.html
- pytest: How to write and report assertions — https://docs.pytest.org/en/stable/how-to/assert.html
- pytest: How to use fixtures — https://docs.pytest.org/en/stable/how-to/fixtures.html
- pytest: How to use temporary directories and files — https://docs.pytest.org/en/stable/how-to/tmp_path.html
- pytest: How to parametrize fixtures and test functions — https://docs.pytest.org/en/stable/how-to/parametrize.html
- pytest: Good Integration Practices — https://docs.pytest.org/en/stable/explanation/goodpractices.html
- pytest: How to invoke pytest — https://docs.pytest.org/en/stable/how-to/usage.html
- pytest: Managing pytest's output — https://docs.pytest.org/en/stable/how-to/output.html
- pytest: How to use unittest-based tests with pytest — https://docs.pytest.org/en/stable/how-to/unittest.html
- pytest: API reference — https://docs.pytest.org/en/stable/reference/reference.html
- unittest — Unit testing framework — https://docs.python.org/3/library/unittest.html
- Python glossary: decorator — https://docs.python.org/3/glossary.html#term-decorator
- Python: Common sequence operations — https://docs.python.org/3/library/stdtypes.html#common-sequence-operations
- Python: Boolean type — https://docs.python.org/3/library/stdtypes.html#boolean-type-bool
- Python: Built-in functions, max — https://docs.python.org/3/library/functions.html#max
- Python reference: The assert statement — https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement
- Python tutorial: Floating-Point Arithmetic: Issues and Limitations — https://docs.python.org/3/tutorial/floatingpoint.html
- json: JSONEncoder — https://docs.python.org/3/library/json.html#json.JSONEncoder
- datetime — timedelta objects — https://docs.python.org/3/library/datetime.html#timedelta-objects
- NumPy: the absolute basics for beginners — https://numpy.org/doc/stable/user/absolute_beginners.html
- NumPy: The N-dimensional array (ndarray) — https://numpy.org/doc/stable/reference/arrays.ndarray.html
- numpy.array — https://numpy.org/doc/stable/reference/generated/numpy.array.html
- NumPy: Indexing on ndarrays — https://numpy.org/doc/stable/user/basics.indexing.html
- NumPy: Universal functions (ufunc) — https://numpy.org/doc/stable/reference/ufuncs.html
- NumPy: Scalars — https://numpy.org/doc/stable/reference/arrays.scalars.html
- NEP 51: Changing the representation of NumPy scalars — https://numpy.org/neps/nep-0051-scalar-representation.html
- numpy.array_equal — https://numpy.org/doc/stable/reference/generated/numpy.array_equal.html
- numpy.median — https://numpy.org/doc/stable/reference/generated/numpy.median.html
- numpy.sum — https://numpy.org/doc/stable/reference/generated/numpy.sum.html
- pip: Requirements File Format — https://pip.pypa.io/en/stable/reference/requirements-file-format/
- Coverage.py documentation — https://coverage.readthedocs.io/
- Martin Fowler: Test Pyramid (supplement only; no claim rests on it) — https://martinfowler.com/bliki/TestPyramid.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- assertion | A statement that a condition must be true, which stops the test with a failure report when it is false. | aka: assert, asserts, assertions
- fixture | A function marked with `@pytest.fixture` that builds test data or set-up once per test and hands it to any test that names it as a parameter. | aka: fixtures, pytest fixture
- test pyramid | A picture of a healthy test suite with many fast unit tests at the base, fewer integration tests in the middle and a few end-to-end tests at the top. | aka: testing pyramid
- decorator | A line starting with `@` above a `def` that passes the function below it through another function, which can register or change it. | aka: decorators, @ syntax
- parametrize | A pytest marker that runs one test function once for each set of inputs and expected values in a list. | aka: parametrise, parametrized test, parameterized test
- NumPy | A third-party Python library whose main object is the array, a fixed-type container that supports arithmetic on every element at once. | aka: numpy
- array | A NumPy container holding same-typed values in a fixed shape, written `np.array([...])` and also called an ndarray. | aka: arrays, ndarray, np.array
- vectorisation | Applying an operation to a whole array in one expression, such as `arr * 2`, instead of looping over the elements. | aka: vectorization, vectorised, vectorized

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Naming the file `desk_test_.py` or the function `check_redact` so pytest collects nothing and reports "no tests ran"; files need `test_*.py` (or `*_test.py`) and functions need the `test` prefix.
- Typing `pytest` in a terminal where Monday's `.venv` is not active, so the shell reports that `pytest` is not found (pytest was installed into `.venv`), or running it from a folder above `ticket-desk/`, so it also collects other `test_*.py` files; activate `.venv`, run from `ticket-desk/`, and use `python -m pytest` when in doubt, which runs pytest with the same Python that `python -m pip install` used.
- Writing `assert resolution_hours(desk) == [3.0, 30.0]` on an array: it raises the "truth value of an array with more than one element is ambiguous" error; use `np.array_equal`, `pytest.approx` or `.tolist()` instead.
- Expecting `hours + 1` or `hours * 2` on a list to act like the array version: `+ 1` raises `TypeError` and `* 2` repeats the list.
- Comparing computed floats with `==`: `0.1 + 0.2 == 0.3` is False, so an assert on a mean of hours such as `0.1` and `0.2` can fail on the last digit; compare with `pytest.approx` (the sample desk's mean of 16.5 happens to be exact, so `approx` there is the habit, not the rescue).
- Calling a fixture like a function (`sample_desk()`) inside a test instead of naming it as a parameter, which pytest rejects with "Fixture "sample_desk" called directly".

## Demo plan hints (2–4; what must be shown live for this topic to land)

- 01_desk_tests (rung 10): show one red failure on purpose: type `"high": 8` into `SLA_HOURS`, run `pytest`, read the assertion line, the two values and the diff, then restore the value and rerun green before `pytest -k redact` and the commit.
- 02_storage_tests (rung 11): explain `@` above a `def` in one line the first time it appears (the `sample_desk` fixture), point back to it at `@pytest.mark.parametrize`, then run `pytest -v` so the three SLA cases show as their own lines with IDs such as `test_sla_hours[high-4]`.
- 03_hours_array (rung 12): in the REPL put the list and the array side by side: `hours * 2`, `hours + 1` (the TypeError), `arr * 2`, `arr + 1`, `arr.dtype`, `arr.shape`, `arr > 24`, `arr[arr > 24]`, and then show the same operations inside `stats.py` and the summary printed by `python ticket_desk.py`.
- 04_hours_tests (rung 13): run `assert resolution_hours(sample_desk) == [3.0, 30.0]` first so the room reads the ambiguous-truth-value error, replace it with the dtype/shape check, `np.array_equal` and `pytest.approx`, run `pytest -v` to fourteen green, then `git switch main`, `git merge feature/desk-tests` and `git push origin main` so `origin/main` on GitHub matches `main`.
