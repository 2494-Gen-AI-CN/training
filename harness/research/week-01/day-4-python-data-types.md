# w01d4 — Python data types

gate: light
verified: 2026-10-12
week: 1 · Agile for developers, Git & Python fundamentals
day: 4 · python-data-types

version-stamps:
  - python: 3.12 (verified 2026-10-12)
  - datetime (standard library): bundled with Python 3.12 (verified 2026-10-12)
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

## Sources (official / primary docs preferred; ≥3; full gate: every URL fetched and confirmed)

- Python 3.12 Built-in Types — https://docs.python.org/3/library/stdtypes.html
- Python 3.12 Built-in Functions — https://docs.python.org/3/library/functions.html
- Python 3.12 Tutorial: Data Structures — https://docs.python.org/3/tutorial/datastructures.html
- Python 3.12 Tutorial: Floating-Point Arithmetic — https://docs.python.org/3/tutorial/floatingpoint.html
- Python 3.12 datetime module — https://docs.python.org/3/library/datetime.html
- Python 3.12 Sorting Techniques — https://docs.python.org/3/howto/sorting.html
- Python 3.12 Tutorial: Scopes and Namespaces — https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces

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
