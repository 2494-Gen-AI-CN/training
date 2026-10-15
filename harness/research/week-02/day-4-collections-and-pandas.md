# w02d4 — Collections & pandas

gate: light
verified: 2026-10-15
week: 2 · Python advanced
day: 4 · collections-and-pandas

version-stamps:
  - python: 3.15 (verified 2026-10-15)
  - pandas: 3.0.6 (verified 2026-10-15)   # Python 3.15 wheel on PyPI: pandas-3.0.6-cp315-cp315-win_amd64.whl
  - numpy: 2.5.4 (verified 2026-10-15)   # already in the venv from Wednesday; Python 3.15 wheel on PyPI: numpy-2.5.4-cp315-cp315-win_amd64.whl
  - pytest: 9.1.1 (verified 2026-10-15)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- `collections.Counter` is a dict subclass for counting hashable objects; elements are stored as keys and counts as values — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter)
- A Counter returns 0 for a missing key instead of raising KeyError — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter)
- `Counter.most_common(n)` returns the n most common elements as (element, count) pairs, highest count first — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter.most_common)
- `Counter.update(iterable)` adds counts; `dict.update` would replace values — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter.update)
- `namedtuple(typename, field_names)` returns a tuple subclass whose fields are reachable by name and by index — [collections docs](https://docs.python.org/3/library/collections.html#collections.namedtuple)
- Named tuple instances are immutable; `_replace(**kwargs)` returns a new instance and `_asdict()` returns a dict of the fields — [collections docs](https://docs.python.org/3/library/collections.html#collections.somenamedtuple._replace)
- `TicketRow._fields` lists the field names as a tuple of strings — [collections docs](https://docs.python.org/3/library/collections.html#collections.somenamedtuple._fields)
- `OrderedDict` is a dict subclass that remembers the order its keys were inserted — [collections docs](https://docs.python.org/3/library/collections.html#collections.OrderedDict)
- `OrderedDict` adds `move_to_end(key, last=True)` and `popitem(last=True)`, which reorder or remove at either end — [collections docs](https://docs.python.org/3/library/collections.html#collections.OrderedDict.move_to_end)
- Since Python 3.7 a plain dict also keeps insertion order; OrderedDict still differs in order-sensitive equality and in `move_to_end` — [collections docs](https://docs.python.org/3/library/collections.html#ordereddict-objects)
- `defaultdict(list)` calls the factory to create a missing value on first access — [collections docs](https://docs.python.org/3/library/collections.html#collections.defaultdict)
- `deque` gives O(1) appends and pops at both ends, where a list is O(n) at the left end — [collections docs](https://docs.python.org/3/library/collections.html#collections.deque)
- `ChainMap` groups several mappings into one view, searched in order — [collections docs](https://docs.python.org/3/library/collections.html#collections.ChainMap)
- `sorted(iterable, key=...)` returns a new list; the key function is called once per element — [Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
- A DataFrame is a two-dimensional, size-mutable, labelled tabular structure with columns of potentially different types — [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)
- `pandas.read_json(path)` reads a JSON file into a DataFrame; a list of objects becomes one row per object — [pandas.read_json](https://pandas.pydata.org/docs/reference/api/pandas.read_json.html)
- `pandas.to_datetime` converts strings to datetime64 values; subtracting two datetime columns gives timedeltas, and `.dt.total_seconds()` converts them to floats — [pandas.to_datetime](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html)
- Missing values in a numeric column are stored as NaN (not a number) and are skipped by `mean()` by default — [pandas missing data guide](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- `Series.value_counts()` returns the count of each distinct value, sorted by count descending — [pandas.Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)
- `DataFrame.groupby(col)[other].mean()` splits rows by a key, applies an aggregation per group and combines the results — [pandas groupby guide](https://pandas.pydata.org/docs/user_guide/groupby.html)
- A boolean Series inside brackets, `df[df["priority"] == "high"]`, selects the rows where it is True; `df.loc[row, col]` selects by label — [pandas indexing guide](https://pandas.pydata.org/docs/user_guide/indexing.html)
- Pinning `pandas==3.0.6` in `requirements.txt` lets `python -m pip install -r requirements.txt` rebuild the same environment on a fresh clone — [Installing Python Modules](https://docs.python.org/3/installing/index.html); supplementary: [pip: Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Counters
- Interview questions: What does Counter do that a plain dict does not?; How do you get the three most common items?; Why does `counts["x"]` not raise KeyError, and does reading it add the key?
- Adjacent concept: Counting with a dict and `dict.get(key, 0) + 1` — the manual pattern Counter replaces.
- Trade-off or limit: Counter accepts only hashable elements, and its `+` and `-` operators drop zero and negative counts — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter)
- Recognise on sight: `Counter(item.status for item in items)` or `counts.most_common(3)`
- Claims:
  - Counter is a dict subclass, so `dict(counter)` and `counter == {...}` comparisons work — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter)
  - Passing an iterable to the constructor counts its elements — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter)
  - Reading a missing key returns 0 without inserting it — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter)
  - `elements()` expands counts back into repeated items — [collections docs](https://docs.python.org/3/library/collections.html#collections.Counter.elements)

### Named tuples
- Interview questions: Why use a namedtuple over a plain tuple?; How does it differ from a class or a dict?; How do you "change" a field on an immutable row?
- Adjacent concept: Tuple unpacking — a named tuple unpacks like any tuple, which is why it can stand in for a tuple in older code.
- Trade-off or limit: Fields cannot be reassigned (AttributeError); build a new row with `_replace` — [collections docs](https://docs.python.org/3/library/collections.html#collections.somenamedtuple._replace)
- Recognise on sight: `Point = namedtuple("Point", ["x", "y"])` then `p.x`
- Claims:
  - Instances use no per-instance dict, so they take the same memory as a plain tuple — [collections docs](https://docs.python.org/3/library/collections.html#collections.namedtuple)
  - Field names may be passed as a list or a space/comma separated string — [collections docs](https://docs.python.org/3/library/collections.html#collections.namedtuple)
  - A named tuple is still a tuple, so `row[1]` and `len(row)` work — [collections docs](https://docs.python.org/3/library/collections.html#collections.namedtuple)
  - `typing.NamedTuple` is the class-syntax equivalent with type annotations — [typing docs](https://docs.python.org/3/library/typing.html#typing.NamedTuple)

### Ordered dicts
- Interview questions: Dicts keep insertion order now, so why does OrderedDict exist?; What does `move_to_end` do?; How do two OrderedDicts compare for equality versus two dicts?
- Adjacent concept: Sorting with `key=` and a lambda to decide the order the OrderedDict is built in.
- Trade-off or limit: OrderedDict uses more memory than a plain dict and its equality is order-sensitive — [collections docs](https://docs.python.org/3/library/collections.html#ordereddict-objects)
- Recognise on sight: `queue.move_to_end(key, last=False)` or `queue.popitem(last=False)` in queue or LRU-cache code
- Claims:
  - `popitem(last=False)` removes the first-inserted pair, giving queue behaviour — [collections docs](https://docs.python.org/3/library/collections.html#collections.OrderedDict.popitem)
  - `move_to_end(key, last=False)` moves a key to the front — [collections docs](https://docs.python.org/3/library/collections.html#collections.OrderedDict.move_to_end)
  - Comparing an OrderedDict with a plain dict ignores order; comparing two OrderedDicts does not — [collections docs](https://docs.python.org/3/library/collections.html#ordereddict-objects)
  - Insertion order of plain dicts is a language guarantee from Python 3.7 — [dict docs](https://docs.python.org/3/library/stdtypes.html#dict)

### Collections module
- Interview questions: When would you reach for defaultdict?; Why use deque instead of a list as a queue?; What is ChainMap for?
- Adjacent concept: Hashing and why dict keys must be hashable — the reason Counter and defaultdict keys behave as they do.
- Trade-off or limit: A defaultdict inserts the key on every lookup of a missing key, including a read — [collections docs](https://docs.python.org/3/library/collections.html#collections.defaultdict)
- Recognise on sight: `groups = defaultdict(list); groups[key].append(x)`; `import collections; dir(collections)`
- Claims:
  - `defaultdict(list)` removes the need for an `if key not in d` check before appending — [collections docs](https://docs.python.org/3/library/collections.html#defaultdict-examples)
  - `deque(maxlen=n)` discards from the opposite end when full — [collections docs](https://docs.python.org/3/library/collections.html#collections.deque)
  - ChainMap lookups search each mapping in order; writes go to the first — [collections docs](https://docs.python.org/3/library/collections.html#collections.ChainMap)
  - `dir(module)` lists the names a module defines — [built-in functions](https://docs.python.org/3/library/functions.html#dir)

### Pandas
- Interview questions: What is a DataFrame and how does it differ from a list of dicts?; How do you select rows matching a condition?; What does `groupby` do, and how does `value_counts` relate to it?
- Adjacent concept: NaN and missing data — `mean()` skips NaN, and a still-open ticket has no closing time.
- Trade-off or limit: A DataFrame lives in memory and brings a large dependency; for a handful of records a Counter or list of namedtuples is lighter — [pandas: Scaling to large datasets](https://pandas.pydata.org/docs/user_guide/scale.html)
- Recognise on sight: `df = pd.read_json("tickets.json")`, `df["status"].value_counts()`, `df.groupby("priority")["hours"].mean()`
- Claims:
  - `df.head()`, `df.shape`, `df.dtypes` and `df.columns` describe a frame's first rows, size, column types and labels — [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)
  - `df["col"]` returns a Series; `df[["a", "b"]]` returns a DataFrame — [pandas indexing guide](https://pandas.pydata.org/docs/user_guide/indexing.html)
  - `value_counts()` yields the same numbers as Counter over the same column, as a Series — [pandas.Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)
  - `groupby(...).mean()` skips NaN by default — [pandas groupby guide](https://pandas.pydata.org/docs/user_guide/groupby.html)
  - Row filters combine conditions with `&` (and), `|` (or) and `~` (not), with each comparison in parentheses; Python's `and`/`or` ask a whole Series for one True or False and raise "The truth value of a Series is ambiguous" — [pandas indexing guide: boolean indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing); supplementary: [pandas gotchas: using if/truth statements with pandas](https://pandas.pydata.org/docs/user_guide/gotchas.html#using-if-truth-statements-with-pandas)
  - A missing value in a datetime column is shown as `NaT` (not a time), the datetime counterpart of NaN; a JSON `null` becomes NaN in a number column and NaT once the column is converted with `to_datetime` — [pandas missing data guide](https://pandas.pydata.org/docs/user_guide/missing_data.html)
  - `Series.isna()` returns a boolean Series marking missing values, so `df[df["hours"].isna()]` selects the rows whose hours are missing — [pandas missing data guide](https://pandas.pydata.org/docs/user_guide/missing_data.html)
  - `sort_values("col", ascending=False)` returns a new sorted frame and leaves the original unchanged — [pandas.DataFrame.sort_values](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html)
  - pandas installs from PyPI with `python -m pip install pandas` and is imported by convention as `import pandas as pd` — [pandas installation](https://pandas.pydata.org/docs/getting_started/install.html)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Python docs: collections — https://docs.python.org/3/library/collections.html
- Python docs: Sorting HOW TO — https://docs.python.org/3/howto/sorting.html
- Python docs: typing.NamedTuple — https://docs.python.org/3/library/typing.html#typing.NamedTuple
- Python docs: built-in types, dict — https://docs.python.org/3/library/stdtypes.html#dict
- Python docs: built-in functions — https://docs.python.org/3/library/functions.html
- pandas: DataFrame reference — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
- pandas: read_json — https://pandas.pydata.org/docs/reference/api/pandas.read_json.html
- pandas: to_datetime — https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
- pandas: Series.value_counts — https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
- pandas: DataFrame.sort_values — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
- pandas user guide: group by — https://pandas.pydata.org/docs/user_guide/groupby.html
- pandas user guide: indexing and selecting data — https://pandas.pydata.org/docs/user_guide/indexing.html
- pandas user guide: missing data — https://pandas.pydata.org/docs/user_guide/missing_data.html
- pandas user guide: frequently asked questions (gotchas) — https://pandas.pydata.org/docs/user_guide/gotchas.html
- pandas: installation — https://pandas.pydata.org/docs/getting_started/install.html
- pandas user guide: scaling to large datasets — https://pandas.pydata.org/docs/user_guide/scale.html
- Python docs: Installing Python Modules — https://docs.python.org/3/installing/index.html
- pip: Requirements File Format — https://pip.pypa.io/en/stable/reference/requirements-file-format/

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- Counter | A dictionary subclass from the collections module that counts how many times each item appears. | aka: collections.Counter, counter object
- namedtuple | A tuple whose positions also have names, so a field is read as row.status as well as row[2]. | aka: named tuple, named tuples, namedtuples
- defaultdict | A dictionary that builds a starting value, such as an empty list, the first time a missing key is used. | aka: default dict, default dictionaries
- deque | A double-ended queue that adds and removes items at either end quickly. | aka: double-ended queue, deques
- DataFrame | The pandas table of labelled rows and columns, where each column holds one kind of value. | aka: data frame, dataframes, df
- Series | One column of a pandas DataFrame: a labelled sequence of values of one type. | aka: pandas Series, series object
- NaN | The "not a number" value pandas uses to mark a missing number. | aka: NaN value, not a number, missing value

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Treating Counter like a plain dict: expecting KeyError for a missing key (it returns 0), or using `update` expecting replacement (it adds).
- Assigning to a namedtuple field (`row.status = "closed"`) and being surprised by AttributeError; the fix is `_replace`, which returns a new row.
- Believing OrderedDict is needed for ordering in all code: plain dicts keep insertion order, and OrderedDict matters for `move_to_end`, `popitem(last=False)` and order-sensitive equality.
- Forgetting that a defaultdict creates the key on a read, so a lookup to "check" a key changes the dict.
- In pandas, confusing `df["col"]` (a Series) with `df[["col"]]` (a DataFrame), and chaining `and` instead of `&` with parentheses in row filters.
- Expecting NaN to behave like a number: `NaN == NaN` is False, and a column with NaN is float, so an open ticket's hours look odd until `mean()` skips them.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- 01_status_counter (rung 14): show `counts["escalated"]` giving 0 beside a plain dict's KeyError and `counts.most_common(1)`, then `test_status_counts(sample_desk)` asserting `== {"closed": 2, "assigned": 1, "open": 1}` going green; rung 17's test compares against `status_counts`, so this demo is never cut.
- 02_ticket_rows (rung 15): show `rows()` building `TicketRow`s (hours `None` while open) read as `row.status` and `row[1]`, and `row.status = "closed"` raising AttributeError; show `work_queue` as an `OrderedDict` built soonest deadline first with `sorted(..., key=lambda t: t.deadline())`, and `move_to_end(tid, last=False)` escalating a ticket to the front; show `by_agent` as a `defaultdict(list)` filling without an `if key not in` check. `row._replace` and `popitem(last=False)` are optional (first cut), and `dir(collections)` naming `deque` and `ChainMap` may move to the notes handoff.
- 03_ticket_frame (rung 16): show `load_frame("tickets.json")` returning the six-row DataFrame, then `df.head()`, `df.shape` and `df.dtypes` (the datetime columns), with `list(df.columns)` beside `TicketRow._fields` so columns are tied to the namedtuple fields; `load_frame` is never cut because Friday's charts read it.
- 04_frame_groups (rung 17): show the `hours` column computed from `closed_at - opened_at`, with NaN for the open ticket, then `hours_by_priority(df)` skipping that NaN in its mean; show `status_table(df)` printing the same numbers as the Counter and `test_value_counts_match_counter` going green. The `hours` column and `status_table` are never cut (Friday's charts draw them); the merge into `main` is not a must-show, since the stop point can slide it to Friday's Demo 1.
