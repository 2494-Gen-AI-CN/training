# w01d4 — Python data types

gate: light
verified: 2026-10-12
week: 1 · Agile for developers, Git & Python fundamentals
day: 4 · python-data-types

version-stamps:
  - python: 3.15 (verified 2026-10-13)
  - datetime (standard library): bundled with Python 3.15 (verified 2026-10-13)
  - pytest: 8.x (verified 2026-10-12)

## Claims (each MUST carry a source on a full gate; light gate: source optional but recommended)

- `str.strip()`, `.lower()`, `.startswith()` and `.replace()` return new strings; strings are immutable, so the original is never changed — [Built-in Types: Text Sequence Type](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)
- `bool(x)` follows truthiness: empty sequences, zero, `None` and `False` are false; every non-empty string, including `"False"`, is true — [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
- `int("3.5")` raises `ValueError`, while `int(3.9)` truncates toward zero to 3 — [Built-in Functions: int](https://docs.python.org/3/library/functions.html#int)
- `list.sort()` sorts in place and returns `None`; `sorted()` returns a new list; tuples compare element by element, so a list of tuples sorts by tuple order — [Sorting Techniques](https://docs.python.org/3/howto/sorting.html)
- Assigning a list to a second name binds the same object; `list.copy()` makes a shallow copy — [Mutable Sequence Types](https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types)
- `(1,)` is a one-element tuple; the comma makes the tuple, not the parentheses — [Tuples and Sequences](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences)
- `range` is an immutable sequence that computes its items on demand, and its stop value is excluded — [Ranges](https://docs.python.org/3/library/stdtypes.html#ranges)
- Set elements must be hashable; `{}` creates an empty dict, so an empty set is `set()`; `&` and `-` give intersection and difference — [Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- `str.encode()` returns `bytes` (UTF-8 by default), `bytes.decode()` reverses it, and `len` counts bytes for `bytes` but code points for `str` — [Binary Sequence Types](https://docs.python.org/3/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview)
- `None` is the sole value of `NoneType`; compare with `is None`, not `==` — [The Null Object](https://docs.python.org/3/library/stdtypes.html#the-null-object)
- `dict[key]` raises `KeyError` on a missing key, `dict.get(key, default)` does not; dicts keep insertion order since Python 3.7 — [Mapping Types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- Binary floating point cannot represent 0.1 exactly, so `0.1 + 0.2 == 0.3` is `False`; `/` is true division and `//` is floor division — [Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- Subtracting two `datetime` objects gives a `timedelta`; `total_seconds()` converts it to a float; naive datetimes carry no time zone — [datetime module](https://docs.python.org/3/library/datetime.html)
- `dir()` lists names in the current scope, `__name__` is `"__main__"` when a file runs as a script, and a later `import datetime` rebinds a name already imported with `from datetime import datetime` — [Python Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Strings
- Interview questions: Are Python strings mutable, and what does `s.upper()` do to `s`?; What is the difference between `s.strip()` and `s.replace(" ", "")`?; Why is building a long string with `+=` in a loop discouraged, and what replaces it?
- Adjacent concept: slicing and negative indexes (`s[:40]`, `s[-1]`, `s[::-1]`) — the interviewer asks it next because slicing is how strings are truncated and reversed without methods.
- Trade-off or limit: strings are immutable, so repeated concatenation can copy the text each time; collecting parts and calling `"".join(parts)` is the standard way to build a large string — [Built-in Types: Text Sequence Type](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)
- Recognise on sight: `name.strip().lower()` chained on user input, or `text[:40] + "..."` to truncate for display.
- Claims:
  - `str.split()` with no argument splits on runs of whitespace and discards empty strings, while `split(" ")` keeps empty strings between adjacent spaces — [String Methods](https://docs.python.org/3/library/stdtypes.html#string-methods)
  - `str.startswith()` accepts a tuple of prefixes and returns `True` if any matches — [String Methods](https://docs.python.org/3/library/stdtypes.html#string-methods)
  - Slicing never raises `IndexError`: an out-of-range slice such as `"abc"[:40]` returns the whole string, while an out-of-range single index raises — [An Informal Introduction to Python: Strings](https://docs.python.org/3/tutorial/introduction.html#strings)
  - `in` on strings tests for a substring, so `"ab" in "cabd"` is `True` — [Common Sequence Operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations)
  - F-strings evaluate their expressions at runtime and support format specs such as `{x:.2f}` — [PEP 498: Literal String Interpolation](https://peps.python.org/pep-0498/)

### Casting
- Interview questions: What is the difference between `int("42")`, `int(4.7)` and `int("4.7")`?; How do you safely convert user input to a number?; What does `str(x)` give for an object with no custom text form?
- Adjacent concept: `str.isdigit()` / `str.isdecimal()` as a pre-check before `int()`, and `round()` versus `int()` truncation — once a cast is known to fail on bad text or drop the fraction, the interviewer asks how to test the text first and how to round instead of truncate; `isdigit()` is not an exact pre-check for `int()`: it rejects signs and surrounding whitespace that `int()` accepts, and accepts superscript digits such as `"²"` that `int()` rejects; `isdecimal()` is the closer match, and `try`/`except ValueError` is the reliable test — [String Methods: str.isdigit](https://docs.python.org/3/library/stdtypes.html#str.isdigit), [String Methods: str.isdecimal](https://docs.python.org/3/library/stdtypes.html#str.isdecimal)
- Trade-off or limit: `int()` truncates toward zero rather than rounding, so `int(-3.9)` is `-3`; use `round()` when rounding is meant — [Built-in Functions: int](https://docs.python.org/3/library/functions.html#int)
- Recognise on sight: `age = int(input("Age: "))`, or `float(row["price"])` on text read from a file.
- Claims:
  - `int("3.5")` raises `ValueError` because the text is not an integer literal, but `int(float("3.5"))` works — [Built-in Functions: int](https://docs.python.org/3/library/functions.html#int)
  - `int()` accepts an optional base, so `int("ff", 16)` is 255 — [Built-in Functions: int](https://docs.python.org/3/library/functions.html#int)
  - `float()` accepts strings such as `"nan"` and `"inf"`, so a successful cast does not guarantee a finite number — [Built-in Functions: float](https://docs.python.org/3/library/functions.html#float)
  - `str()` returns the readable form of an object while `repr()` returns the unambiguous form — [Built-in Functions: repr](https://docs.python.org/3/library/functions.html#repr)
  - `input()` always returns a `str`, so a number typed by the user needs an explicit cast — [Built-in Functions: input](https://docs.python.org/3/library/functions.html#input)

### Boolean
- Interview questions: Which values are falsy in Python?; Is `bool` a subclass of `int`, and what is `True + True`?; Why is `if x == True` considered poor style?
- Adjacent concept: short-circuit evaluation of `and` / `or` returning an operand, not a bool — it explains why `is_open and title` yields the title string.
- Trade-off or limit: truthiness makes `if items:` concise but treats `0`, `0.0` and `""` the same as `None`, so a legitimate zero can be mistaken for "missing" — [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
- Recognise on sight: `if not queue:` guarding an empty list, or `value = name or "anonymous"` supplying a default.
- Claims:
  - `bool` is a subclass of `int`, so `True == 1` and `sum([True, False, True])` is 2 — [Boolean Type - bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)
  - `and` and `or` return one of their operands rather than a `bool`, and stop evaluating once the result is known — [Boolean Operations](https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not)
  - Objects are false when they define `__bool__` returning `False` or `__len__` returning 0; otherwise they are true — [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
  - PEP 8 advises against comparing boolean values to `True` or `False` with `==` — [PEP 8: Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)

### Lists
- Interview questions: What is the difference between `append`, `extend` and `insert`?; What does `b = a` do for a list, and how do you get an independent copy?; What is the difference between `a.sort()` and `sorted(a)`?
- Adjacent concept: shallow versus deep copy — `list.copy()` copies the outer list only, so nested lists are still shared, which is why `copy.deepcopy` exists.
- Trade-off or limit: `list.pop(0)` and `list.insert(0, x)` shift every element and cost O(n), so a list is a poor queue for large data; `collections.deque` handles both ends in O(1) — [Tutorial: Using Lists as Queues](https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-queues), [Python Wiki: Time Complexity](https://wiki.python.org/moin/TimeComplexity) (supplement)
- Recognise on sight: `queue = queue.sort()` (a bug that leaves `None`), or `rows = [[0] * 3] * 3` (three aliases of one row).
- Claims:
  - `list.append`, `extend`, `insert`, `remove`, `pop`, `sort` and `reverse` mutate the list in place; the ones that change order or size return `None` (except `pop`, which returns the removed item) — [More on Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
  - Negative indexes count from the end, so `queue[-1]` is the last item, and a slice `queue[1:]` returns a new list — [Common Sequence Operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations)
  - `sorted()` is stable: equal items keep their original relative order — [Sorting Techniques](https://docs.python.org/3/howto/sorting.html)
  - `[x] * n` repeats references to the same object, so mutable elements are shared — [Common Sequence Operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations)
  - `copy.deepcopy` recursively copies nested objects, unlike the shallow `list.copy()` — [copy module](https://docs.python.org/3/library/copy.html)

### Tuples
- Interview questions: What is the difference between a list and a tuple?; Why does `(1)` not make a tuple?; Can a tuple be a dict key, and when can it not?
- Adjacent concept: tuple unpacking and starred targets (`first, *rest = items`) — unpacking is the idiom that makes returning several values from a tuple readable.
- Trade-off or limit: a tuple is immutable only at its own level; a tuple holding a list can still have that list changed, and such a tuple is not hashable — [Tuples and Sequences](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences)
- Recognise on sight: `rank, tid, text = row`, or a trailing comma such as `SIZE = (640,)`.
- Claims:
  - Tuples compare lexicographically, so `(1, 9) < (2, 0)` and sorting a list of tuples orders by the first field, then the second — [Sorting Techniques](https://docs.python.org/3/howto/sorting.html)
  - A tuple is hashable only if all of its elements are hashable — [Glossary: hashable](https://docs.python.org/3/glossary.html#term-hashable)
  - The empty tuple is written `()` and a one-element tuple needs a trailing comma — [Tuples and Sequences](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences)
  - Unpacking requires the number of targets to match the number of items unless a starred target absorbs the rest — [Tuples and Sequences](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences)
  - Tuples support `count()` and `index()` but have no methods that change them — [Tuples](https://docs.python.org/3/library/stdtypes.html#tuples)

### Range
- Interview questions: What does `range(1, 4)` contain?; Is `range` a list in Python 3?; How do you get the numbers 10 down to 1?
- Adjacent concept: `list(range(...))` to materialise values and `range` with a step — it is the standard way to produce a numeric sequence without writing it out.
- Trade-off or limit: a `range` stores only start, stop and step, so it uses the same small memory for any size, but it holds integers only; floats need another approach — [Ranges](https://docs.python.org/3/library/stdtypes.html#ranges)
- Recognise on sight: `list(range(1, 4))`, or `range(len(items))` used to get positions.
- Claims:
  - `range(start, stop, step)` excludes `stop`, and a negative step counts down, as in `range(10, 0, -1)` — [Built-in Functions: range](https://docs.python.org/3/library/functions.html#func-range)
  - `len(range(...))`, indexing and membership tests work on a `range` without building the values — [Ranges](https://docs.python.org/3/library/stdtypes.html#ranges)
  - A step of 0 raises `ValueError` — [Ranges](https://docs.python.org/3/library/stdtypes.html#ranges)
  - `range` accepts only integer arguments; `range(0.5, 3)` raises `TypeError` — [Built-in Functions: range](https://docs.python.org/3/library/functions.html#func-range)

### Sets
- Interview questions: How do you remove duplicates from a list, and what do you lose?; Why is `x in some_set` faster than `x in some_list`?; Why does `{}` not create an empty set?
- Adjacent concept: set algebra with `|`, `&`, `-` and `^` and the matching methods — it answers "which reporters are in both lists" in one expression.
- Trade-off or limit: a set has no order and no indexing, and its elements must be hashable, so a list cannot be a member; `list(set(items))` removes duplicates but does not keep the original order — [Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- Recognise on sight: `seen = set()` or `unique = set(names)`.
- Claims:
  - A set is an unordered collection of distinct hashable objects built for fast membership testing: it locates an element by its hash value, while `x in some_list` compares against the items one by one — [Tutorial: Sets](https://docs.python.org/3/tutorial/datastructures.html#sets)
  - `set.add` ignores an element already present, and `set.remove` raises `KeyError` for a missing one while `discard` does not — [Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
  - `frozenset` is the immutable, hashable variant and can be a dict key or a set member — [Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
  - `a & b`, `a | b`, `a - b` and `a ^ b` give intersection, union, difference and symmetric difference — [Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
  - Values that compare equal, such as `1` and `1.0`, count as one set element — [Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)

### Binary types
- Interview questions: What is the difference between `str` and `bytes`?; Why can `len(text)` differ from `len(text.encode())`?; What happens if you decode bytes with the wrong encoding?
- Adjacent concept: `bytearray` as the mutable variant — it is the usual follow-up once `bytes` is known to be immutable.
- Trade-off or limit: UTF-8 uses one to four bytes per character, so byte length is not character count, and cutting bytes at an arbitrary position can split a character and make decoding fail — [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
- Recognise on sight: `payload.decode("utf-8")` on data from a file, socket or HTTP response, or a `b"..."` literal.
- Claims:
  - `str.encode()` defaults to UTF-8 and `bytes.decode()` reverses it — [Built-in Types: bytes Objects](https://docs.python.org/3/library/stdtypes.html#bytes-objects)
  - `"café"` has 4 characters but 5 UTF-8 bytes, because `é` takes two bytes — [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
  - Indexing a `bytes` object returns an `int` from 0 to 255, not a one-byte `bytes` — [Built-in Types: bytes Objects](https://docs.python.org/3/library/stdtypes.html#bytes-objects)
  - Python 3 does not implicitly mix `str` and `bytes`; `b"a" + "b"` raises `TypeError` — [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
  - Decoding with the wrong codec either raises `UnicodeDecodeError` (for example, bytes that are not valid UTF-8 decoded as UTF-8) or silently produces wrong characters (for example, UTF-8 bytes decoded as latin-1, which accepts every byte); `errors="replace"` substitutes U+FFFD instead of raising — [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)

### NoneType
- Interview questions: What is `None` and what type is it?; Why use `is None` instead of `== None`?; Why does `print(print("x"))` show `x` and then `None`, and which other built-in calls hand back `None`?
- Adjacent concept: `None` as the value `dict.get(key)` returns when the key is missing and no default is given — it is the usual next question because it explains why `ticket.get("owner") is None` is a missing-key test and why `.get(key, default)` exists — [Mapping Types: dict.get](https://docs.python.org/3/library/stdtypes.html#dict.get)
- Trade-off or limit: `None` is falsy, so `if not value:` cannot tell `None` from `0` or `""`; use `is None` when "missing" must be distinct from "empty" — [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
- Recognise on sight: `assignee = None` as a placeholder, or `print(print("x"))` printing `None`.
- Claims:
  - `None` is the only value of `NoneType` and is a singleton, so identity comparison with `is` is reliable — [The Null Object](https://docs.python.org/3/library/stdtypes.html#the-null-object)
  - PEP 8 says comparisons to singletons such as `None` should use `is` or `is not`, never the equality operators — [PEP 8: Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)
  - `print()` returns `None`, so `print(print("x"))` prints `x` then `None` — [Built-in Functions: print](https://docs.python.org/3/library/functions.html#print)
  - In-place list methods such as `sort()` return `None` — [More on Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
  - `None` cannot be ordered against numbers: `None < 1` raises `TypeError` — [Comparisons](https://docs.python.org/3/library/stdtypes.html#comparisons)

### Dictionaries
- Interview questions: What can be a dict key, and why?; What is the difference between `d[k]` and `d.get(k)`?; Do dicts keep their order?
- Adjacent concept: how a hash table gives average constant-time lookup — the follow-up that links dict, set and hashability.
- Trade-off or limit: keys must be hashable, so a list cannot be a key, and a dict gives fast lookup by key at the cost of memory and no lookup by value — [Mapping Types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- Recognise on sight: `config.get("timeout", 30)`, or `by_id = {t["id"]: t for t in tickets}`-style registries (the comprehension form is only recognised, not taught).
- Claims:
  - `dict.get(key, default)` returns the default for a missing key without raising and without inserting it — [Mapping Types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
  - `dict.setdefault(key, default)` inserts the default if the key is absent and returns the value — [Mapping Types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
  - `.keys()`, `.values()` and `.items()` return views that reflect later changes to the dict, so `list(d.items())` is needed for a stable snapshot — [Dictionary view objects](https://docs.python.org/3/library/stdtypes.html#dict-views)
  - `key in d` tests keys, not values — [Mapping Types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
  - Dictionaries preserve insertion order, a guarantee of the language since Python 3.7 — [Mapping Types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict), [Tutorial: Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)

### Numbers
- Interview questions: Why is `0.1 + 0.2 == 0.3` false?; What is the difference between `/` and `//`?; How large can a Python `int` get?
- Adjacent concept: the `decimal` module for exact decimal arithmetic — the usual answer when asked how to handle money.
- Trade-off or limit: floats are fast and compact but approximate; `decimal.Decimal` is exact for decimal fractions but slower — [Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- Recognise on sight: `abs(a - b) < 1e-9` in place of `==` on floats, or `1_000_000` with digit separators.
- Claims:
  - Python `int` has arbitrary precision, so integer overflow does not occur — [Numeric Types](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)
  - `/` always returns a float while `//` floors the result, so `-7 // 2` is `-4` — [PEP 238: Changing the Division Operator](https://peps.python.org/pep-0238/)
  - `divmod(a, b)` returns the quotient and remainder as a tuple — [Built-in Functions: divmod](https://docs.python.org/3/library/functions.html#divmod)
  - `round()` rounds half to even, so `round(2.5)` is 2 — [Built-in Functions: round](https://docs.python.org/3/library/functions.html#round)
  - Underscores in numeric literals, such as `1_000_000`, are ignored by the interpreter and exist for readability — [PEP 515: Underscores in Numeric Literals](https://peps.python.org/pep-0515/)
  - `decimal.Decimal("0.1") + Decimal("0.2") == Decimal("0.3")` is true — [decimal module](https://docs.python.org/3/library/decimal.html)

### Datetime
- Interview questions: What does subtracting two `datetime` objects return?; What is the difference between `timedelta.seconds` and `total_seconds()`?; How do you print a datetime in ISO 8601 form?
- Adjacent concept: `strftime` and `strptime` format codes — formatting to and parsing from text is the next thing asked once arithmetic is understood.
- Trade-off or limit: a naive datetime carries no time zone, so comparing or subtracting values from different zones silently gives wrong answers; this page keeps every value naive and pinned — [datetime module](https://docs.python.org/3/library/datetime.html)
- Recognise on sight: `datetime.now() - created_at`, or `deadline = start + timedelta(hours=24)`.
- Claims:
  - `datetime - datetime` returns a `timedelta`, and `datetime + timedelta` returns a `datetime` — [datetime module](https://docs.python.org/3/library/datetime.html)
  - `timedelta.seconds` is only the seconds part after whole days, so `total_seconds()` is the correct total — [datetime module: timedelta](https://docs.python.org/3/library/datetime.html#timedelta-objects)
  - `datetime.isoformat()` returns an ISO 8601 string such as `2026-10-15T09:30:00` — [datetime module: datetime](https://docs.python.org/3/library/datetime.html#datetime-objects)
  - `strftime("%a %H:%M")` formats weekday abbreviation and 24-hour time — [strftime and strptime Behavior](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)
  - Comparing a naive and an aware datetime with `<` raises `TypeError` — [datetime module](https://docs.python.org/3/library/datetime.html)
  - `datetime.now()` reads the system clock on every call, so code that calls it directly gives different results on every run — [datetime module: datetime](https://docs.python.org/3/library/datetime.html#datetime-objects)

### Namespaces
- Interview questions: What is a namespace in Python?; What happens when `import datetime` follows `from datetime import datetime`?; What does `if __name__ == "__main__":` do?
- Adjacent concept: shadowing a built-in at module level and recovering it through the `builtins` module, together with how `import x` binds the module name while `from x import y` binds only `y` — the interviewer asks it next because it is the same rebinding that breaks `datetime(...)` after a second `import datetime`; `builtins.list` still reaches the original after `list = [1]` — [builtins module](https://docs.python.org/3/library/builtins.html)
- Trade-off or limit: a later binding silently replaces an earlier one with no warning, so a name can shadow a built-in such as `list` or `id` and break code further down — [Python Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
- Recognise on sight: `if __name__ == "__main__":` at the bottom of a script, or `del backup` removing a name.
- Claims:
  - A namespace maps names to objects; examples are the built-in names, a module's global names and a function call's local names — [Python Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
  - `__name__` is `"__main__"` when a file is run directly and the module name when it is imported — [__main__: Top-level code environment](https://docs.python.org/3/library/__main__.html)
  - `dir()` without arguments lists the names in the current scope — [Built-in Functions: dir](https://docs.python.org/3/library/functions.html#dir)
  - `del name` removes the binding, not necessarily the object, which is freed only when no names refer to it — [The del statement](https://docs.python.org/3/reference/simple_stmts.html#the-del-statement)
  - Assigning to a built-in's name, such as `list = [1]`, makes the module-level name hide the built-in until it is deleted — [Python Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)

## Sources (official / primary docs preferred; ≥3; full gate: every URL fetched and confirmed)

- Python 3.15 Built-in Types — https://docs.python.org/3/library/stdtypes.html
- Python 3.15 Built-in Functions — https://docs.python.org/3/library/functions.html
- Python 3.15 Tutorial: Data Structures — https://docs.python.org/3/tutorial/datastructures.html
- Python 3.15 Tutorial: Floating-Point Arithmetic — https://docs.python.org/3/tutorial/floatingpoint.html
- Python 3.15 datetime module — https://docs.python.org/3/library/datetime.html
- Python 3.15 Sorting Techniques — https://docs.python.org/3/howto/sorting.html
- Python 3.15 Tutorial: Scopes and Namespaces — https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces
- Python 3.15 Tutorial: An Informal Introduction (Strings) — https://docs.python.org/3/tutorial/introduction.html#strings
- Python 3.15 Unicode HOWTO — https://docs.python.org/3/howto/unicode.html
- Python 3.15 copy module — https://docs.python.org/3/library/copy.html
- Python 3.15 decimal module — https://docs.python.org/3/library/decimal.html
- Python 3.15 Glossary — https://docs.python.org/3/glossary.html
- Python 3.15 __main__ top-level code environment — https://docs.python.org/3/library/__main__.html
- Python 3.15 Language Reference: Simple statements (del) — https://docs.python.org/3/reference/simple_stmts.html#the-del-statement
- Python 3.15 builtins module — https://docs.python.org/3/library/builtins.html
- Python 3.15 Built-in Types: str.isdigit — https://docs.python.org/3/library/stdtypes.html#str.isdigit
- Python 3.15 Built-in Types: str.isdecimal — https://docs.python.org/3/library/stdtypes.html#str.isdecimal
- Python 3.15 Built-in Types: dict.get — https://docs.python.org/3/library/stdtypes.html#dict.get
- Python 3.15 Tutorial: Sets — https://docs.python.org/3/tutorial/datastructures.html#sets
- PEP 8 Style Guide for Python Code — https://peps.python.org/pep-0008/
- PEP 238 Changing the Division Operator — https://peps.python.org/pep-0238/
- PEP 498 Literal String Interpolation — https://peps.python.org/pep-0498/
- PEP 515 Underscores in Numeric Literals — https://peps.python.org/pep-0515/
- Python Wiki: Time Complexity — https://wiki.python.org/moin/TimeComplexity

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- truthiness | How Python decides whether any value counts as True or False in a condition or `bool()` call: empty containers, zero and `None` are false, nearly everything else is true. | aka: truthy, falsy, truth value
- mutable | An object whose contents can change in place after it is created, such as a list, set or dict, unlike a str, tuple or int. | aka: mutability
- aliasing | Two names bound to the same object, so changing it through one name shows up through the other. | aka: alias, aliases
- hashable | An object with a fixed hash value for its lifetime, which is what lets it be a set member or a dict key. | aka: hashability
- floating-point error | The tiny rounding gap that appears because binary floats cannot store most decimal fractions exactly, so `0.1 + 0.2` is not `0.3`. | aka: float precision, rounding error
- naive datetime | A datetime with no time zone attached, so it names a clock reading but not an exact moment. | aka: naive datetimes
- namespace | A mapping from names to objects, such as a module's globals, that decides which object a name refers to at that point. | aka: namespaces
- bytes | An immutable sequence of integers from 0 to 255, the raw form that text becomes after `.encode()`. | aka: byte string

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Trusting `bool("False")`, `bool("0")` or `== True`: any non-empty string is truthy, and comparing to `True` with `==` fails for values like `2` or a non-empty string; test the value directly.
- Writing `queue = queue.sort()` or printing `queue.sort()`: it sorts in place and returns `None`, so the list is lost; use `sorted(queue)` for a new list.
- Believing `backup = queue` is a copy: both names are one list, so appending to either changes both; use `queue.copy()`, and remember it is shallow.
- Indexing a dict with a key that may be absent (`ticket["owner"]` raises `KeyError`) and testing optional values with `== None` instead of `is None`; use `.get(key, default)` and `is None`.
- Comparing floats with `==` and expecting `/` to behave like `//`: `0.1 + 0.2 == 0.3` is `False`, `10 / 4` is 2.5 while `10 // 4` is 2; compare with `abs(a - b) < 1e-9` or round.
- Using `int("3.5")` or assuming `int(3.9)` rounds (it truncates), and shadowing `datetime` with a second `import datetime` that rebinds the name so `datetime(...)` fails with `TypeError: 'module' object is not callable`.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- `01_ticket_text` (rung 6; Strings, Casting, Boolean): start with `git switch -c feature/data-types`, then normalise with `title.strip()` and `priority.strip().lower()` and show `title[:40]`, `.startswith`, `.replace`, `len` and `in`; read `ticket_id` as typed text inside the existing `if sys.stdin.isatty():` guard and cast it with `int()`. Have the room predict before each run, then delete the transient lines so the file equals the key: `int("3.5")` (ValueError), `int(3.9)` (3, truncated), `bool("False")`, `bool("")`, `bool(0)` and the `== True` comparison; the truthiness line `is_open and title` stays.
- `02_ticket_queue` (rung 7; Lists, Tuples, Range, Sets): build `queue = []` from three `(rank, ticket_id, title)` tuples and print each with its own `print(queue[0])`, `print(queue[1])`, `print(queue[2])` line (no loop today), then `queue[-1]`, `queue[1:]`, `len(queue)` and `sorted(queue)` on tuple order. Predict, run, then delete `.sort()` returning `None` and the unpacking `rank, tid, text = queue[0]`; show `backup = queue` changing both names before replacing it with `queue.copy()`; contrast `(1,)` with `(1)`, build `ids = list(range(1, 4))`, and finish on `reporters = {"dana", "lee", "dana"}` printing two names, with `.add`, `in`, `&`, `-` and `set()` for an empty set.
- `03_ticket_dict` (rung 8; Binary types, NoneType, Dictionaries): show the round-trip `raw = title.encode("utf-8")` and `raw.decode()` (kept), with `len("café")` against `len("café".encode())` and the `bytes + str` TypeError as transient lines; set `assignee = None` and test it with `assignee is None` in place of `== None`, with `print(print(...))` shown then deleted. Replace the three constants with `SLA_HOURS` and rewrite the earlier line as `hours_left = SLA_HOURS[priority] - hours_open`; build the `ticket` dict, run `ticket["owner"]` to get the KeyError, delete it and keep `.get("owner", "unassigned")`; assign `ticket["assignee"] = "lee"`, append to `ticket["history"]`, and end with `tickets_by_id = {ticket["id"]: ticket}`.
- `04_ticket_clock` (rung 9; Numbers, Datetime, Namespaces): predict `0.1 + 0.2 == 0.3`, run it, then replace it with `round(..., 2)` and `abs(a - b) < 1e-9`; contrast `10 / 4` with `10 // 4` and show `divmod(int(hours_open), 24)` and `1_000_000`. Add `from datetime import datetime, timedelta`, type `datetime.now()` and pin it as `NOW = datetime(2026, 10, 15, 14, 0)`, set `opened_at = datetime(2026, 10, 15, 9, 30)`, derive `hours_open` from `(NOW - opened_at).total_seconds() / 3600` (the literal and the `+= 0.5` bump go), compute `deadline` with `timedelta(hours=SLA_HOURS[priority])`, and print `NOW > deadline`, `.isoformat()` and `.strftime("%a %H:%M")`. Then the namespace lines: `import datetime` shadowing shown failing and deleted, `dir()`, the `__name__` print and `del backup`, before `git switch main` and `git merge feature/data-types` puts the day's four commits on `main`.
