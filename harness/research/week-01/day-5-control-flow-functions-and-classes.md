# w01d5 — Control flow, functions & classes

gate: light
verified: 2026-10-12
week: 1 · Agile for developers, Git & Python fundamentals
day: 5 · day-5-control-flow-functions-and-classes

version-stamps:
  - python: 3.12 (verified 2026-10-12)
  - array (stdlib): 3.12 (verified 2026-10-12)
  - datetime (stdlib): 3.12 (verified 2026-10-12)

## Claims (each MUST carry a source on a full gate; light gate: source optional but recommended)

- `if`, `elif` and `else` pick exactly one branch; `while` re-tests its condition each pass, and `break` leaves the nearest enclosing loop — [Python tutorial: More Control Flow Tools](https://docs.python.org/3/tutorial/controlflow.html)
- `for` iterates over any iterable, and `for rank, tid, text in sorted(queue)` unpacks each tuple in the loop header — [Python tutorial: More Control Flow Tools](https://docs.python.org/3/tutorial/controlflow.html)
- Default argument values are evaluated once, when `def` runs, so a mutable default such as `history=[]` is shared between calls; the idiom is `None` plus a check — [Python tutorial: Default Argument Values](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
- A function with no `return` statement returns `None` — [Python tutorial: Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
- A `lambda` is a single-expression anonymous function, commonly passed as `key=` to `sorted()` and `list.sort()` — [Python tutorial: Lambda Expressions](https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions)
- `array.array("d", [...])` stores values of one numeric type code compactly, unlike a list that holds any objects — [array module](https://docs.python.org/3/library/array.html)
- Name lookup follows local, enclosing, global, built-in (LEGB); assigning to a name inside a function makes it local unless declared `global` or `nonlocal` — [Python tutorial: Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
- A class attribute is shared by all instances (`Desk.next_id`), while `self.x` set in `__init__` belongs to one instance — [Python tutorial: Class and Instance Variables](https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables)
- A subclass overrides a method by redefining it and reaches the parent version with `super()`; `isinstance()` is true for instances of subclasses — [Python tutorial: Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- `__repr__` supplies the string `print()` and the REPL show when no `__str__` exists — [Data model: object.__repr__](https://docs.python.org/3/reference/datamodel.html#object.__repr__)
- `iter(obj)` calls `obj.__iter__()`, `next(it)` advances it, and `StopIteration` signals exhaustion; a class that defines `__iter__` works in a `for` loop — [Python tutorial: Iterators](https://docs.python.org/3/tutorial/classes.html#iterators)
- `vars(obj)` returns an instance's `__dict__`, and `hasattr(obj, name)` tests for an attribute — [Built-in functions](https://docs.python.org/3/library/functions.html)

## Sources (official / primary docs preferred; ≥3; full gate: every URL fetched and confirmed)

- Python tutorial: More Control Flow Tools — https://docs.python.org/3/tutorial/controlflow.html
- Python tutorial: Classes — https://docs.python.org/3/tutorial/classes.html
- Python data model reference — https://docs.python.org/3/reference/datamodel.html
- array module — https://docs.python.org/3/library/array.html
- Built-in functions — https://docs.python.org/3/library/functions.html
- Python glossary — https://docs.python.org/3/glossary.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- guard clause | An early `if` that handles a bad or special case and returns or continues at once, so the main logic stays unnested below it. | aka: early return, guard clauses
- lambda | A one-expression anonymous function written inline, most often as the `key=` argument of `sorted()`. | aka: lambda expression, anonymous function
- LEGB rule | The order Python searches for a name: local, enclosing, global, built-in. | aka: LEGB, variable scope, name lookup order
- mutable default argument | A default such as `history=[]` that Python creates once at definition time and so shares across every call that omits it. | aka: mutable default, default argument trap
- method override | A subclass redefining a method it inherited so that calls on its objects run the new version, optionally reaching the parent's through `super()`. | aka: override, overriding, super()
- __repr__ | The special method that returns the developer-facing string for an object, used by `print()` when no `__str__` exists. | aka: repr, dunder repr
- instance attribute | A value stored on one object through `self`, as opposed to a class attribute shared by all objects of the class. | aka: self attribute, class attribute

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Using `history=[]` as a default parameter: every call without the argument appends to the same list, so tickets leak history into each other; the fix is `history=None` then `if history is None: history = []`.
- Forgetting `return` (or printing instead of returning) so the caller receives `None`, then comparing or sorting on that `None`.
- Writing `next_id += 1` inside a function without `global` raises `UnboundLocalError`, because the assignment makes the name local before it is read; a plain `next_id = 1` raises nothing and silently creates a local, leaving the module-level counter unchanged. Reaching for `global` then hides state that belongs on the class (`Desk.next_id`).
- Writing `key=lambda t: t["priority"]` sorts the priority strings alphabetically (`"high"` < `"low"` < `"normal"`, so low tickets jump ahead of normal ones) instead of mapping priority to a rank first with `PRIORITY_RANK`; also calling the function (`key=f()`) rather than passing it (`key=f`).
- Writing `self.deadline` without parentheses, which yields the bound method instead of the datetime, or forgetting `self` as the first parameter of a method; and in a subclass, redefining `deadline` without calling `super().deadline()`, so the parent's rule is copied or silently lost (the general case is any overridden method, `__init__` included).
- Treating an iterator as reusable: after a manual `next()` loop or one `for` pass over an iterator, a second pass yields nothing, whereas `Desk.__iter__` returning a fresh `iter(self._tickets)` can be looped repeatedly.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- 01_desk_control_flow: show `if/elif/else` setting `status` in place of the `is_breached` boolean lines and a nested `if` flattened into a guard clause; then `for rank, tid, text in sorted(queue): print(...)` replacing the three per-tuple prints `print(queue[0])`, `print(queue[1])`, `print(queue[2])`, and `for key, value in ticket.items()`; then the `while priority not in SLA_HOURS` re-ask with `break` on an empty title inside `if sys.stdin.isatty():`, running the script both interactively and with input redirected so the unattended board still prints.
- 02_desk_functions: show the dict-to-function step on the same thread: `make_ticket`, `deadline_for` and `is_overdue` called from the script body, a function with no `return` printing `None` then deleted, the `history=[]` trap run twice to expose the shared list before its `None` fix, the `queue.sort(key=lambda t: (PRIORITY_RANK[t["priority"]], t["opened_at"]))` sort replacing tuple order, and the three-line `from array import array` / `ages = array("d", [...])` cameo next to the list.
- 03_ticket_class: show the `Ticket` and `UrgentTicket` rewrite with every dict access line rewritten to attribute access (`vars(ticket).items()`, `ticket.assign("lee")`, `ticket.deadline()`), then `print(ticket)` before and after `__repr__`, `UrgentTicket.deadline` built on `super().deadline()`, and `isinstance(t, Ticket)` true for the subclass.
- 04_desk_object: show `it = iter(queue)`, `next(it)` twice and the transient `StopIteration` before the queue is removed; then `class Desk` with `add`, `__len__` and `__iter__` returning `iter(self._tickets)`, `desk = Desk()` plus three `desk.add(...)`, `print(len(desk))` and one `for t in sorted(desk, key=lambda x: ...)`; then the `global next_id` counter replaced by the class attribute `Desk.next_id`, the four-line LEGB `label()` shadowing demo, and the `git switch main` / `git merge feature/design-choices` that lands the day.
