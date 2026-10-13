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

- `if`/`elif`/`else` runs at most one branch, the first whose condition is true (`else` only when none is); `while` re-tests its condition each pass, and `break` leaves the nearest enclosing loop — [Python tutorial: More Control Flow Tools](https://docs.python.org/3/tutorial/controlflow.html)
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

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### If-else
- Interview questions: What does `elif` do that a second `if` does not?; Which values count as false in an `if` test?; How does a guard clause differ from nesting, and when would you pick each?
- Adjacent concept: The conditional expression `a if cond else b` — it is the expression form of the same branch and is the usual next question after the statement form.
- Trade-off or limit: A long `if/elif` chain on one value grows linearly and is hard to extend; a dict lookup keeps the table as data, at the cost of the chain's ability to test arbitrary conditions per branch — [Python tutorial: if Statements](https://docs.python.org/3/tutorial/controlflow.html#if-statements)
- Recognise on sight: `if x is None: return` at the top of a function (guard clause), followed by unindented main logic.
- Claims:
  - `if`, `elif` and `else` run at most one block, the first whose condition is true; `else` runs only when none is — [Python tutorial: if Statements](https://docs.python.org/3/tutorial/controlflow.html#if-statements)
  - Empty containers, `0`, `0.0`, `""` and `None` are false in a condition; most other objects are true — [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
  - Python marks blocks by indentation, and PEP 8 sets four spaces per level — [PEP 8: Indentation](https://peps.python.org/pep-0008/#indentation)
  - `and` and `or` short-circuit and return one of their operands, not necessarily a bool — [Boolean operations](https://docs.python.org/3/reference/expressions.html#boolean-operations)
  - Compare to `None` with `is` or `is not`, not `==`, per PEP 8's programming recommendations — [PEP 8: Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)

### While loops
- Interview questions: When would you choose `while` over `for`?; What do `break` and `continue` do?; What does the `else` clause on a loop mean, and when does it not run?
- Adjacent concept: The re-ask (validation) loop — `while` is the natural shape for "repeat until the input is valid", which is how interviewers usually frame it.
- Trade-off or limit: A `while` loop whose condition never becomes false runs forever, so the body must change something the condition reads; `for` over a finite iterable cannot have that bug — [Python tutorial: More Control Flow Tools](https://docs.python.org/3/tutorial/controlflow.html)
- Recognise on sight: `while value not in allowed: value = input(...)`, or `while True:` with a `break` inside.
- Claims:
  - A `while` statement tests its condition before every pass and stops when it is false — [The while statement](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement)
  - `break` leaves the nearest enclosing loop; `continue` jumps to the next pass of it — [break and continue Statements](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops)
  - A loop's `else` block runs when the loop ends without `break` — [break and continue Statements](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops)
  - `while True:` never fails its own test, so it runs until a `break` executed inside the body ends it (skipping any loop `else`), which lets the exit test sit in the middle of the body — [The while statement](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement)

### For loops
- Interview questions: What can a `for` loop iterate over?; How do you loop with an index in Python, and what do `enumerate` and `zip` give you?; What happens if you add or remove items from a list while looping over it?
- Adjacent concept: Iterable versus iterator — a `for` loop calls `iter()` on its target, which leads directly to the question of what an iterable is.
- Trade-off or limit: Changing a list's size while iterating over it can skip elements or repeat them, so loop over a copy or build a new list — [Python tutorial: for Statements](https://docs.python.org/3/tutorial/controlflow.html#for-statements)
- Recognise on sight: `for rank, tid, text in sorted(queue):` (tuple unpacking in the header) or `for k, v in d.items():`.
- Claims:
  - `for` takes items from any iterable in order, and each pass binds the loop variable — [The for statement](https://docs.python.org/3/reference/compound_stmts.html#the-for-statement)
  - `range(n)` yields `0` to `n-1` and does not build a list of all the numbers up front — [Python tutorial: The range() Function](https://docs.python.org/3/tutorial/controlflow.html#the-range-function)
  - `enumerate(iterable, start=0)` yields `(index, item)` pairs — [Built-in functions: enumerate](https://docs.python.org/3/library/functions.html#enumerate)
  - `zip` stops at the shortest input unless `strict=True` is passed — [Built-in functions: zip](https://docs.python.org/3/library/functions.html#zip)
  - `dict.items()` yields key and value pairs that can be unpacked in the loop header — [Python tutorial: Looping Techniques](https://docs.python.org/3/tutorial/datastructures.html#looping-techniques)

### Functions
- Interview questions: What is the difference between a parameter and an argument?; What does a function return if it has no `return`?; Why is `def f(x, history=[])` a bug?
- Adjacent concept: Positional versus keyword arguments, `*args` and `**kwargs` — the next question is always how callers may pass values.
- Trade-off or limit: Default values are evaluated once at definition, so a mutable default is shared between calls; the cost of the `None` idiom is one extra check in the body — [Python tutorial: Default Argument Values](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
- Recognise on sight: `def f(items=None):` followed by `if items is None: items = []`.
- Claims:
  - `def` creates a function object and binds it to a name when the statement runs — [Python tutorial: Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
  - A function with no `return` statement, or a bare `return`, gives back `None` — [Python tutorial: Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
  - Arguments can be passed by keyword, and a keyword argument may not precede a positional one in a call — [Python tutorial: Keyword Arguments](https://docs.python.org/3/tutorial/controlflow.html#keyword-arguments)
  - The first statement of a function body, if it is a string literal, becomes its docstring, readable as `__doc__` — [Python tutorial: Documentation Strings](https://docs.python.org/3/tutorial/controlflow.html#documentation-strings)
  - PEP 257 asks for a one-line docstring that ends with a period and describes the effect as a command — [PEP 257: One-line Docstrings](https://peps.python.org/pep-0257/#one-line-docstrings)
  - Functions are objects, so they can be passed as arguments and returned — [Data model: Callable types](https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy)

### Lambda
- Interview questions: What is a lambda, and how does it differ from a `def` function?; How do you sort a list of records by a field?; Why does `key=f()` fail where `key=f` works?
- Adjacent concept: `sorted()` versus `list.sort()` and stable sorting — sort keys are where lambdas appear in most code reviews.
- Trade-off or limit: A lambda body is one expression with no statements and no name in tracebacks, so anything longer, reused or needing a docstring belongs in a `def` — [Python tutorial: Lambda Expressions](https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions)
- Recognise on sight: `sorted(rows, key=lambda r: (r.rank, r.opened_at))`.
- Claims:
  - `lambda args: expr` builds an anonymous function whose body is a single expression — [Expressions: lambda](https://docs.python.org/3/reference/expressions.html#lambda)
  - `sorted()` and `list.sort()` call the `key` function once per item and compare the results — [Sorting Techniques: Key Functions](https://docs.python.org/3/howto/sorting.html#key-functions)
  - A tuple key sorts by its first element, then the second on ties — [Sorting Techniques](https://docs.python.org/3/howto/sorting.html)
  - Python's sort is stable, so equal keys keep their original order — [Sorting Techniques: Sort Stability](https://docs.python.org/3/howto/sorting.html#sort-stability-and-complex-sorts)
  - PEP 8 says to write `def f(x): ...` rather than assign a lambda to a name — [PEP 8: Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)

### Arrays
- Interview questions: Is a Python list an array?; When would you use `array.array` instead of a list?; Why does `array('d', ...)` use less memory than a list of floats?
- Adjacent concept: List performance — a list is a dynamic array of references, so `append` is amortised O(1) while `insert(0, x)` and `pop(0)` are O(n) because every other element shifts, which is why the usual next question is about list performance — [Design and History FAQ: How are lists implemented in CPython?](https://docs.python.org/3/faq/design.html#how-are-lists-implemented-in-cpython); [Python tutorial: Using Lists as Queues](https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-queues)
- Trade-off or limit: An `array.array` packs values into a compact C buffer and saves memory, but it accepts only values of its type code, and it has no list-only methods such as `sort()` — [array module](https://docs.python.org/3/library/array.html)
- Recognise on sight: `array("d", [1.5, 2.0])` with a type code string as the first argument.
- Claims:
  - `array.array(typecode, initializer)` stores items of one fixed numeric type, and the type code `"d"` is a C double — [array module](https://docs.python.org/3/library/array.html)
  - Arrays support indexing, slicing, `append` and `len()` like lists, but reject a value of the wrong type — [array module](https://docs.python.org/3/library/array.html)
  - A list is a mutable sequence of references that may mix types — [Python tutorial: More on Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
  - Slicing a list returns a new shallow copy — [Python tutorial: Lists](https://docs.python.org/3/tutorial/introduction.html#lists)
  - `list.copy()` makes a shallow copy, so nested objects are shared between the copies — [Python tutorial: More on Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)

### OOP concepts
- Interview questions: What are encapsulation, inheritance and polymorphism?; What is the difference between a class and an object?; When would you write a class instead of using a dict?
- Adjacent concept: Composition versus inheritance — "has-a or is-a" is the question that follows the four OOP principles.
- Trade-off or limit: A class bundles data with the rules that use it, but adds ceremony; for a record with no behaviour a dict or tuple is lighter, and Python does not enforce privacy, only a naming convention — [Python tutorial: Private Variables](https://docs.python.org/3/tutorial/classes.html#private-variables)
- Recognise on sight: `self._tickets = []` in `__init__` (single underscore marks internal use) and methods that read `self`.
- Claims:
  - Python classes support inheritance, overriding and multiple base classes, and all members are public by default — [Python tutorial: Classes](https://docs.python.org/3/tutorial/classes.html)
  - A leading underscore marks a name as internal by convention only; the language does not block access — [Python tutorial: Private Variables](https://docs.python.org/3/tutorial/classes.html#private-variables)
  - Polymorphism in Python is by behaviour: any object with the needed method works, whatever its class — [Python glossary: duck-typing](https://docs.python.org/3/glossary.html#term-duck-typing)
  - Calling a class creates an instance and passes it as `self` to `__init__` — [Python tutorial: Class Objects](https://docs.python.org/3/tutorial/classes.html#class-objects)
  - An instance can store other objects in its data attributes (the tutorial's instance variables), which is how a `Desk` holds its list of tickets — [Python tutorial: Class and Instance Variables](https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables)

### Inheritance
- Interview questions: How does a subclass override a method?; What does `super()` do?; What is the difference between `isinstance` and `type(x) == C`?
- Adjacent concept: Method resolution order with multiple inheritance — the question that follows once `super()` is explained.
- Trade-off or limit: A subclass depends on the attributes and methods it inherits, and a base-class method that calls another method on `self` may end up running the subclass's override, so the two classes are coupled and a change in the parent changes the child — [Python tutorial: Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance). Editorial guidance, not from the source: keep inheritance for a true is-a relation and prefer holding an object (composition) otherwise.
- Recognise on sight: `class UrgentTicket(Ticket):` with a method that calls `super().method()`.
- Claims:
  - A derived class is written `class Derived(Base):`, and attribute lookup falls through to the base when the name is missing — [Python tutorial: Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
  - `super()` returns a proxy that delegates method calls to the parent class — [Built-in functions: super](https://docs.python.org/3/library/functions.html#super)
  - `isinstance(obj, Cls)` is true for instances of `Cls` and of its subclasses — [Built-in functions: isinstance](https://docs.python.org/3/library/functions.html#isinstance)
  - `issubclass(Sub, Base)` tests class relationships rather than instances — [Built-in functions: issubclass](https://docs.python.org/3/library/functions.html#issubclass)
  - If a subclass defines `__init__` it must call the parent's `__init__` itself, or the parent's setup does not run — [Data model: object.__init__](https://docs.python.org/3/reference/datamodel.html#object.__init__)

### Iterators
- Interview questions: What is the difference between an iterable and an iterator?; What does a `for` loop do under the hood?; Why can an iterator be consumed only once?
- Adjacent concept: Iterable containers versus one-shot iterators, and why `__iter__` returns a fresh iterator — this keeps a container re-loopable.
- Trade-off or limit: An iterator keeps one position and gives each item once, so it saves memory but cannot be rewound or indexed; to loop twice, ask the iterable for a new iterator — [Python tutorial: Iterators](https://docs.python.org/3/tutorial/classes.html#iterators)
- Recognise on sight: `it = iter(items); next(it)` or a class with `def __iter__(self): return iter(self._items)`.
- Claims:
  - `for` calls `iter()` on the target, then `next()` on the result until `StopIteration` is raised — [Python tutorial: Iterators](https://docs.python.org/3/tutorial/classes.html#iterators)
  - The iterator protocol needs `__iter__` returning an iterator, and the iterator needs `__next__` — [Iterator Types](https://docs.python.org/3/library/stdtypes.html#iterator-types)
  - `next(it)` on an exhausted iterator raises `StopIteration` — [Built-in exceptions: StopIteration](https://docs.python.org/3/library/exceptions.html#StopIteration)
  - `len()` on an object works only if its class defines `__len__` — [Data model: object.__len__](https://docs.python.org/3/reference/datamodel.html#object.__len__)
  - A list is an iterable, and each `iter(list)` call returns a new, independent iterator — [Iterator Types](https://docs.python.org/3/library/stdtypes.html#iterator-types)

### Scope
- Interview questions: What is the LEGB rule?; What do `global` and `nonlocal` do?; Why does `count += 1` inside a function raise `UnboundLocalError`?
- Adjacent concept: Closures — a nested function that reads an enclosing variable is the next question after the enclosing level of LEGB.
- Trade-off or limit: `global` lets a function rebind a module name but hides state in a place callers cannot see; putting the state on an object or class makes the dependency explicit — [Python tutorial: Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
- Recognise on sight: `global counter` at the top of a function body, or a local name that shadows a module-level one.
- Claims:
  - Python looks up a name in local, enclosing, global and built-in scopes in that order — [Python tutorial: Scopes and Namespaces](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
  - An assignment anywhere in a function makes that name local for the whole function — [Execution model: Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
  - Reading a module-level name inside a function needs no declaration; rebinding it needs `global` — [The global statement](https://docs.python.org/3/reference/simple_stmts.html#the-global-statement)
  - `nonlocal` rebinds a name in the nearest enclosing function scope — [The nonlocal statement](https://docs.python.org/3/reference/simple_stmts.html#the-nonlocal-statement)
  - Loop variables and names bound by `if` blocks belong to the enclosing function or module, because only modules, functions (including lambdas), classes and comprehensions create scopes; `if`, `for` and `while` blocks do not — [Execution model: Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding); [Expressions: Displays for lists, sets and dictionaries](https://docs.python.org/3/reference/expressions.html#displays-for-lists-sets-and-dictionaries)

### Classes and objects
- Interview questions: What does `self` refer to?; What is the difference between a class attribute and an instance attribute?; What happens to `Desk.next_id` if you write `desk.next_id += 1` on an instance?
- Adjacent concept: `__str__` versus `__repr__` — printing an object is the first thing a reviewer tries after writing a class.
- Trade-off or limit: A class attribute is shared by every instance, so a mutable one such as a list is a shared-state bug unless sharing is the point; assigning through an instance creates a separate instance attribute that hides it — [Python tutorial: Class and Instance Variables](https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables)
- Recognise on sight: `def __init__(self, ticket_id, title): self.ticket_id = ticket_id` and `def __repr__(self): return f"Ticket({self.ticket_id!r})"`.
- Claims:
  - `__init__` initialises a new instance; it is called by the class call and must return `None` — [Data model: object.__init__](https://docs.python.org/3/reference/datamodel.html#object.__init__)
  - Without `__repr__`, `print(obj)` shows the default `<module.Class object at 0x...>` text — [Data model: object.__repr__](https://docs.python.org/3/reference/datamodel.html#object.__repr__)
  - A method's first parameter `self` is the instance, passed automatically when called as `obj.method()` — [Python tutorial: Method Objects](https://docs.python.org/3/tutorial/classes.html#method-objects)
  - `ticket.deadline` without parentheses is the bound method object; `ticket.deadline()` calls it — [Python tutorial: Method Objects](https://docs.python.org/3/tutorial/classes.html#method-objects)
  - `vars(obj)` returns the instance's `__dict__` of attributes — [Built-in functions: vars](https://docs.python.org/3/library/functions.html#vars)
  - `hasattr(obj, "name")` returns true when the attribute exists — [Built-in functions: hasattr](https://docs.python.org/3/library/functions.html#hasattr)

## Sources (official / primary docs preferred; ≥3; full gate: every URL fetched and confirmed)

- Python tutorial: More Control Flow Tools — https://docs.python.org/3/tutorial/controlflow.html
- Python tutorial: Classes — https://docs.python.org/3/tutorial/classes.html
- Python data model reference — https://docs.python.org/3/reference/datamodel.html
- array module — https://docs.python.org/3/library/array.html
- Built-in functions — https://docs.python.org/3/library/functions.html
- Python glossary — https://docs.python.org/3/glossary.html
- Python tutorial: Data Structures — https://docs.python.org/3/tutorial/datastructures.html
- Python tutorial: An Informal Introduction — https://docs.python.org/3/tutorial/introduction.html
- Python language reference: Compound statements — https://docs.python.org/3/reference/compound_stmts.html
- Python language reference: Simple statements — https://docs.python.org/3/reference/simple_stmts.html
- Python language reference: Expressions — https://docs.python.org/3/reference/expressions.html
- Python language reference: Execution model — https://docs.python.org/3/reference/executionmodel.html
- Standard library: Built-in Types — https://docs.python.org/3/library/stdtypes.html
- Standard library: Built-in Exceptions — https://docs.python.org/3/library/exceptions.html
- Sorting Techniques (HOWTO) — https://docs.python.org/3/howto/sorting.html
- PEP 8 — Style Guide for Python Code — https://peps.python.org/pep-0008/
- PEP 257 — Docstring Conventions — https://peps.python.org/pep-0257/
- Design and History FAQ — https://docs.python.org/3/faq/design.html

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
