# Week 01 plan — Agile for developers, Git & Python fundamentals

Week 1 · 2026-10-12 to 2026-10-16 · phase py · project P0 · plan written 2026-10-12

<!--
Week plan (D-0034). Monday 2026-10-12 is a holiday; the week has four teaching days, Tue to Fri. Regrouped into
walkthrough blocks on 2026-10-15 (D-0055) for the record only: the week was taught as loose days (D-0050) before the
block contract existed, its delivery records live in trainer/week-01/<day>/delivery.json and no walkthrough folder
exists under trainer/week-01/demos/. The former rung scripts and keys stay under trainer/week-01/<day>/demos/ as
history. The block Adds cells keep the former rung texts as (a), (b), (c) parts.
-->

## Weekly Epic

By Friday afternoon a trainee opens the demo repo (`ticket-desk/ticket_desk.py`), checks out `main`, and runs `python ticket_desk.py`: a support-ticket desk that reads a new ticket at the prompt, keeps tickets as `Ticket` objects inside a `Desk` that iterates them, looks up each ticket's SLA by priority, computes its deadline with `datetime`, and prints the queue sorted by priority and age. The trainee has typed that file alongside the trainer across Wednesday, Thursday and Friday, one commit per walkthrough block, on a feature branch per day merged into `main`, so `git log --oneline` reads as the story of the week. Project 0 needs exactly this: a Python model of the domain's records (title, priority, status, history, deadline) written to PEP 8, that week 2 can split into modules, log, serialise to JSON and test with pytest.

## Assumes from the previous week

- First week: the audience persona from config.json (D-0048). Recent CS graduates (University of Toronto cohort), no industry experience, backgrounds vary. Assumed: general programming ideas from any language (a variable, a branch, a loop, a function). Not assumed: Python syntax and types, Git (including `clone`, `add`, `commit`, `push`), the terminal, or CS theory such as the compiler-versus-interpreter distinction; each is taught on its home day before anything depends on it.
- Does NOT assume: that `python --version` on their laptop prints 3.15, that `git` is installed and configured with a name and email, or that they have resolved a merge conflict. Tuesday's `01_tooling_check` and `02_local_git_loop` Step 1 re-check all three before anything depends on them.
- Does NOT assume any team practice: SDLC, Scrum, story points, feature branches, commit hygiene and code review are taught from the start on Tuesday.

## Threads

### p0-ticket-desk

- Domain: a support-ticket desk for a small software team: tickets with a title, priority, status, assignee and history, filed by customers and triaged by agents. The same records survive every week of the scope: week 1 holds them in Python variables, tuples, a dict and then a `Ticket` class inside a `Desk`; week 2 splits `ticket_desk.py` into modules, adds logging, saves the desk to a JSON file, matches ticket text with regex and tests the rules with pytest; week 3 moves tickets, customers and agents into MySQL tables with joins and a transaction on assignment; week 4 loads ticket events into a BigQuery star schema through an ETL job; week 5 sends tickets to an LLM for triage, summaries and draft replies.
- Scope: weeks 1–5 (project P0); this week plans blocks 1–7.
- Start state this week: cold (01-tooling-and-git creates the Tuesday scratch repo with `git init`).
- End state this week: the commit of `07-ticket-and-desk-classes`: `ticket_desk.py` on `main` of the demo repo (`ticket-desk/ticket_desk.py`), about 200 lines; seven commits on top of Tuesday's scratch repo, the three day-end merges of `feature/ticket-record`, `feature/data-types` and `feature/design-choices` fast-forwarding. Recorded for the tracker only: the week ran as loose days (D-0050) and week 2 restarts the thread cold.

| Block | Day | Slot | Walkthrough | Starts from | Adds | End state | Commit message |
|---|---|---|---|---|---|---|---|
| 1 | w01d2 | PM | 01-tooling-and-git | cold | One commit at the end of the block (the former per-rung commits fold into it; the `git add` / `git commit` named inside the earlier parts are not made). (a) on-ramp tooling check (which Python, the REPL, a saved script, the `__pycache__` folder); no repository exists yet and the day note caps the on-ramp at one demo (b) git identity and init.defaultBranch; the scratch repo (historic name `team-repo`) with `git init`; `hello.py` (greet) and `.gitignore` committed; `feature/farewell` branch merged fast-forward; `feature/shout` conflict on the print line resolved by hand (c) bare `origin.git` next to the repo, `git remote add`, `push -u`; a `teammate/` clone that adds `README.md`; fetch, pull, a diverged history merged with `--no-rebase`; a commit with a body line | scratch repo on `main` with 10 commits, up to date with `origin/main`; `README.md` with four content lines ending `Run it with: python hello.py`; the same history on GitHub after the live closing minute | Document how to run hello.py |
| 2 | w01d3 | AM | 02-ticket-record-and-rules | 01-tooling-and-git | One commit at the end of the block (the former per-rung commits fold into it; the `git add` / `git commit` named inside the earlier parts are not made). (a) `git switch -c feature/ticket-record`; new file `ticket_desk.py`: module docstring, `SLA_HOURS_HIGH`, `SLA_HOURS_NORMAL`, `SLA_HOURS_LOW` constants, one ticket as flat variables (`ticket_id`, `title`, `priority`, `is_open`, `hours_open`, `reporter`), one why-comment kept and one restating comment deleted, an f-string print of the record; `python ticket_desk.py` (b) `age_days = hours_open // 24` next to `/`, `hours_left = SLA_HOURS_HIGH - hours_open`, `is_breached = is_open and hours_left < 0`, a chained comparison `0 <= hours_open < 24`, `priority_ok` written with three `==` after the `priority == "high" or "normal"` pitfall is shown and deleted, `hours_open += 0.5`, `%` for every-third escalation, `-2 ** 2` precedence, `round`; prints of each result | the script prints age, hours left, breach flag and the priority check for the one ticket | Compute ticket age and SLA breach |
| 3 | w01d3 | PM | 03-desk-intake | 02-ticket-record-and-rules | `import sys` at the top; a plain four-line guard `if sys.stdin.isatty():` that reads `title` and `priority` with `input()` and otherwise keeps the sample values (talking point: the only `if` of the day, explained in one line here; Friday teaches `if` properly); `print` with `sep` and `end`; a board header and row with f-string alignment `{title:<30}{priority:>8}{hours_open:>6.1f}`; a warning line to `sys.stderr`; `git switch main` and `git merge feature/ticket-record` | at a terminal the script asks for a title and priority, then prints a two-line board; unattended it prints the board for the sample ticket; `main` has the day's three commits | Read a new ticket at the prompt and print the board |
| 4 | w01d4 | AM | 04-ticket-text-and-queue | 03-desk-intake | One commit at the end of the block (the former per-rung commits fold into it; the `git add` / `git commit` named inside the earlier parts are not made). (a) (if Wednesday's merge slid: `git switch main`, `git merge feature/ticket-record` first) `git switch -c feature/data-types`; `title.strip()`, `priority.strip().lower()`, `title[:40]`, `.startswith`, `.replace`, `len`, `in`; `ticket_id` read as text with `input()` inside the same `if sys.stdin.isatty():` guard then cast with `int()` (`hours_open` stays the literal float from rung 3), `float("4.5")`, `int("3.5")` and `int(3.9)` shown then deleted, `str(ticket_id)`; `bool("False")`, `bool("")`, `bool(0)` shown then deleted, truthiness `is_open and title` kept, `== True` pitfall deleted (b) `queue = []` with three `(rank, ticket_id, title)` tuples appended, three per-tuple prints `print(queue[0])`, `print(queue[1])`, `print(queue[2])` (the repeated prints rung 10's `for` loop replaces), `queue[-1]`, `queue[1:]`, `len(queue)` prints, `sorted(queue)` on tuple order, `.sort()` returning `None` shown then deleted, `backup = queue` aliasing shown then replaced by `queue.copy()`, tuple unpacking `rank, tid, text = queue[0]` shown then deleted (transient, so nothing carries into rung 11's dict queue), `(1,)` versus `(1)`, `ids = list(range(1, 4))`, `reporters = {"dana", "lee", "dana"}`, `.add`, `in`, `&`, `-`, `set()` for an empty set | the queue of three tuples prints sorted by rank then id; `reporters` prints two names; the one-ticket variables still print | Queue tickets as tuples; track reporters as a set |
| 5 | w01d4 | PM | 05-ticket-dict-and-clock | 04-ticket-text-and-queue | One commit at the end of the block (the former per-rung commits fold into it; the `git add` / `git commit` named inside the earlier parts are not made). (a) `raw = title.encode("utf-8")`, `len("café")` against `len("café".encode())`, `raw.decode()`, `bytes + str` TypeError shown then deleted; `assignee = None`, `assignee is None` replacing `== None`, `print(print(...))` shown then deleted; `SLA_HOURS = {"high": 4, "normal": 24, "low": 72}` replacing the three constants AND rung 4's `hours_left = SLA_HOURS_HIGH - hours_open`, rewritten as `hours_left = SLA_HOURS[priority] - hours_open` (replaced block names all four lines), `ticket = {"id": ..., "title": ..., "priority": ..., "assignee": None, "history": []}`, `ticket["owner"]` KeyError shown then deleted, `.get("owner", "unassigned")`, `ticket["assignee"] = "lee"`, `ticket["history"].append(...)`, `"id" in ticket`, `list(ticket.items())`, `tickets_by_id = {ticket["id"]: ticket}` (b) `0.1 + 0.2 == 0.3` shown then replaced by `round(..., 2)` and `abs(a - b) < 1e-9`, `10 / 4` against `10 // 4`, `divmod(int(hours_open), 24)`, `1_000_000`; `from datetime import datetime, timedelta`, `opened_at = datetime(2026, 10, 15, 9, 30)`, `NOW = datetime(2026, 10, 15, 14, 0)` after `datetime.now()` is typed and pinned, `age = NOW - opened_at`, `hours_open = age.total_seconds() / 3600` replacing the literal `hours_open` line from rung 3 and deleting rung 4's `hours_open += 0.5` bump (both in the replaced block, so the value is the clock's alone), `deadline = opened_at + timedelta(hours=SLA_HOURS[priority])`, `NOW > deadline`, `.isoformat()`, `.strftime("%a %H:%M")`; `import datetime` shadowing shown then deleted, `dir()`, `__name__`, `del backup`; `git switch main` and `git merge feature/data-types` | `hours_open` is computed from two datetimes, the deadline prints in ISO form, the breach flag follows the clock; `main` has the day's four commits | Track ticket age with datetime |
| 6 | w01d5 | AM | 06-desk-control-flow-and-functions | 05-ticket-dict-and-clock | One commit at the end of the block (the former per-rung commits fold into it; the `git add` / `git commit` named inside the earlier parts are not made). (a) (if Thursday's merge slid: `git switch main`, `git merge feature/data-types` first) `git switch -c feature/design-choices`; `if NOW > deadline: status = "breached" elif ... else` replacing the `is_breached` boolean lines (replaced block), a guard-clause rewrite of a nested `if` shown then flattened, `for rank, tid, text in sorted(queue): print(...)` replacing rung 7's three per-tuple prints `print(queue[0])`, `print(queue[1])`, `print(queue[2])` (replaced block), `for key, value in ticket.items()`, `while priority not in SLA_HOURS: priority = input(...)` added inside the `if sys.stdin.isatty():` guard from rung 5, `break` on an empty title (b) `def make_ticket(ticket_id, title, priority, opened_at):` returning the dict (replaces the literal dict lines with the call `ticket = make_ticket(ticket_id, title, priority, opened_at)`; `ticket_id` is the first parameter, the same signature rung 12's `__init__` takes, so every dict has an `"id"` for `tickets_by_id` and the appends), `def deadline_for(ticket):` (rung 9's inline `deadline = opened_at + timedelta(...)` line is rewritten as `deadline = deadline_for(ticket)`, so `NOW > deadline`, `.isoformat()` and `.strftime("%a %H:%M")` carry unchanged), `def is_overdue(ticket, now=NOW):` (replaces the status lines), one-line docstrings, a function with no `return` printing `None` shown then deleted, `history=[]` mutable default shown then replaced by `None`; the three tuple appends and `sorted(queue)` from rung 7 and the `for rank, tid, text in sorted(queue)` loop from rung 10 are replaced (replaced block) by three `queue.append(make_ticket(...))` lines, the third written as a kept keyword call `make_ticket(ticket_id=3, title=..., priority="low", opened_at=...)`, and `for t in queue:`; `queue.sort(key=lambda t: (PRIORITY_RANK[t["priority"]], t["opened_at"]))` with `PRIORITY_RANK` replacing the tuple-order sort; `from array import array`, `ages = array("d", [...])` three lines | ticket rules live in three named functions called from the script body; the queue holds dicts sorted by a lambda key on priority rank then `opened_at`; `ages` is a typed array next to the list | Extract ticket rules into functions |
| 7 | w01d5 | PM | 07-ticket-and-desk-classes | 06-desk-control-flow-and-functions | One commit at the end of the block (the former per-rung commits fold into it; the `git add` / `git commit` named inside the earlier parts are not made). (a) `class Ticket:` with `__init__(self, ticket_id, title, priority, opened_at)`, `__repr__`, `deadline(self)`, `assign(self, agent)`, `close(self)` (replaces `make_ticket`, `deadline_for` and the `ticket[...]` access lines, replaced block); the replaced block also names, each with its rewrite, every line that still used the dict or the deleted functions: rung 11's `ticket = make_ticket(ticket_id, title, priority, opened_at)` (rewritten as `ticket = Ticket(ticket_id, title, priority, opened_at)`) and `deadline = deadline_for(ticket)` (rewritten as `deadline = ticket.deadline()`), rung 11's three `queue.append(make_ticket(...))` lines (rewritten as two `queue.append(Ticket(...))` and one `queue.append(UrgentTicket(...))`), rung 10's `for key, value in ticket.items():` (rewritten as `for key, value in vars(ticket).items():`), rung 8's `ticket.get("owner", "unassigned")`, `"id" in ticket` and `list(ticket.items())` (rewritten as `ticket.assignee or "unassigned"`, `hasattr(ticket, "ticket_id")` and `vars(ticket)`), `ticket["assignee"] = "lee"` and `ticket["history"].append(...)` (rewritten as `ticket.assign("lee")`), the body of `is_overdue` (rewritten as `return now > ticket.deadline()`) and `tickets_by_id = {ticket["id"]: ticket}` (rewritten as `tickets_by_id = {ticket.ticket_id: ticket}`), so the key runs on its own; `class UrgentTicket(Ticket):` overriding `deadline` with `super().deadline()` halved, `isinstance(t, Ticket)`; `t.priority` and `t.opened_at` reads replacing `t["priority"]` and `t["opened_at"]` in the lambda (b) `class Desk:` with `self._tickets = []`, `add(self, ticket)`, `__len__`, `__iter__` returning `iter(self._tickets)`, `overdue(self, now)` returning a list; in Step 3, transient and typed BEFORE the queue is removed: `it = iter(queue)`, `next(it)` twice, `StopIteration` shown then deleted; then the replaced block names every surviving `queue` line with its fate: `queue = []` and the three `queue.append(...)` lines become `desk = Desk()` and three `desk.add(...)`; `for t in queue:` becomes `for t in sorted(desk, key=lambda x: (PRIORITY_RANK[x.priority], x.opened_at)):` (the iteration variable stays `t`, so the carried loop-body lines and rung 12's `isinstance(t, Ticket)` keep their binding and the module-level `ticket` record is never rebound); `queue.sort(...)` is deleted (the sorted call replaces it); rung 7's `queue[-1]`, `queue[1:]` and `len(queue)` prints are deleted (`print(len(desk))` replaces the last); `backup = queue.copy()` and rung 9's `del backup` are deleted; rung 12's rewritten `tickets_by_id = {ticket.ticket_id: ticket}` is deleted (the `Desk` is the registry); `global next_id` counter shown then replaced by the class attribute `Desk.next_id`, a four-line LEGB demonstration kept as `def label():` with a local shadowing a module name; `desk = Desk()`, three `desk.add(...)`, `print(len(desk))`; `git switch main` and `git merge feature/design-choices` | `python ticket_desk.py` builds a `Desk`, adds three tickets, iterates them in one `for` sorted by priority then `opened_at`, prints the overdue ones; `main` has the day's four commits and the file is about 200 lines | Add a Desk that owns and iterates its tickets |

<!--
Block rules (checked by plan_check.py): blocks numbered 1..n in teaching order; Slot is AM or PM, one block per slot;
Starts from is "cold" on the first block of the thread's whole scope (or after a cold restart), otherwise EXACTLY the
previous block's Walkthrough; the block's commit on the demo repo's prep branch is its answer key (D-0055); Adds fits
about metrics.demos.maxTypedLinesPerBlock typed lines. An authored or live day's rows are recorded as-is from its
walkthroughs on disk (D-0052).
-->

## Conventions

<!-- Backfilled 2026-10-16 (D-0057) from the plan's own text; week 1 ran as loose days (D-0050), so these rows are the
     record of what the walkthroughs assumed, not a rule the room followed. -->

| Convention | Kind | Applies from | Rule | Why |
|---|---|---|---|---|
| typed-line tally | tally | all | every non-blank line the room types counts: editor lines, REPL lines and shell commands; lines moved or re-indented in place do not | the Adds budgets are checked against it |
| feature branch per day | git | 02-ticket-record-and-rules | Wednesday, Thursday and Friday each open one branch (`feature/ticket-record`, `feature/data-types`, `feature/design-choices`) in the AM block; the PM block's commit ends the day and the branch fast-forwards into `main` | the end state is seven commits on top of Tuesday's scratch repo with three fast-forward merges |
| replaced blocks | carried-lines | 04-ticket-text-and-queue | a block that rewrites earlier lines names every line it replaces in its Adds ("replaced block"): the three SLA constants and rung 4's `hours_left` line (block 5), the `is_breached` booleans and the per-tuple prints (block 6), `make_ticket`, `deadline_for` and the `ticket[...]` accesses (block 7); a replaced line is deleted in the same step, never left beside its replacement | the week-1 critic rounds all found carried-line gaps; naming the fate of every surviving line up front is what closed them |

## Standalone demos

<!-- Blocks that fit no thread (A23). None this week. -->

| Day | Slot | Walkthrough | Minutes | Why it fits no thread |
|---|---|---|---|---|

## Demo ladder

| # | Day | Walkthrough | Minutes | Must follow | Guarantees |
|---|---|---|---|---|---|
| 1 | w01d2 | 01-tooling-and-git | 85 | — | `python --version` prints 3.15 on every machine; the room tells the shell, the `>>>` REPL and a running script apart; `w01d2-scratch/hello.py` exists and `__pycache__/` has appeared once; git identity and `init.defaultBranch main` configured; `w01d2-scratch/team-repo/` (the scratch repo) on `main` with 5 commits, `hello.py`, `.gitignore`, a fast-forward merge and a hand-resolved conflict with no markers left; the scratch repo has `origin` (bare `../origin.git`, then GitHub), `main` tracks `origin/main`, 10 commits, `README.md` with four content lines ending `Run it with: python hello.py`; the room has seen fetch, pull, a diverged merge and a commit body |
| 2 | w01d3 | 02-ticket-record-and-rules | 60 | 1 | branch `feature/ticket-record`; `ticket-desk/ticket_desk.py` exists, runs, prints one ticket from flat variables; the ticket variable names every later rung reads, and three `SLA_HOURS_*` constants that rung 8 replaces; `age_days`, `hours_left`, `is_breached`, `priority_ok` computed from the ticket variables; the room has typed `//`, `%`, `**`, `and`, `or`, `not`, `in` and a chained comparison |
| 3 | w01d3 | 03-desk-intake | 35 | 2 | `import sys` at the top of the file; `title` and `priority` come from `input()` inside an `if sys.stdin.isatty():` guard at a terminal and from the sample otherwise; the board prints with aligned f-strings; `main` holds rungs 3–5 merged |
| 4 | w01d4 | 04-ticket-text-and-queue | 65 | 3 | branch `feature/data-types`; `title` and `priority` are stripped and lower-cased before use; `ticket_id` is an `int` cast from typed text; the room can predict `bool(x)` for strings and numbers; `queue` is a list of `(rank, ticket_id, title)` tuples that sorts by tuple order; each tuple is printed by its own `print(queue[i])` line (the three lines Friday's `for` replaces); `reporters` is a set; `ids` comes from `range`; the room has seen aliasing and `.sort()` returning `None` |
| 5 | w01d4 | 05-ticket-dict-and-clock | 65 | 4 | `SLA_HOURS` dict replaces the three constants; `ticket` is a dict with `assignee` (`None` until assigned) and `history`; `tickets_by_id` maps id to ticket; `.get` with a default is the lookup idiom; `from datetime import datetime, timedelta` at the top; `opened_at`, `NOW`, `age`, `deadline` exist and `hours_open` derives from them (the rung 3 literal is gone); `main` holds rungs 6–9 merged |
| 6 | w01d5 | 06-desk-control-flow-and-functions | 70 | 5 | branch `feature/design-choices`; `status` is set by `if/elif/else`; the queue prints by one `for`; the intake loop re-asks with `while` inside an `if sys.stdin.isatty():` guard; the deadline rule lives only in `deadline_for` and `is_overdue` (rung 8's `hours_left` line stays as the body's SLA arithmetic); `make_ticket` builds every ticket dict; `PRIORITY_RANK` exists; the queue holds dicts and sorts by a `lambda` key on priority rank then `opened_at`; `array` is imported |
| 7 | w01d5 | 07-ticket-and-desk-classes | 70 | 6 | `Ticket` and `UrgentTicket` classes replace the dict record; every rule function takes a `Ticket`; `print(ticket)` is readable through `__repr__`; `Desk` owns the tickets, supports `len()` and `for`; `Desk.next_id` replaces the global counter; `main` holds rungs 10–13 merged and `ticket_desk.py` is the state week 2 rung 1 starts from |

## Per-day shape

### w01d2 — Orientation, Agile & Git fundamentals (Tue Oct 13, 2026)

- AM: setup check (10), Facilitation: What is Python, why Python (8), Facilitation: Professionalism at Revature (7), Facilitation: Full stack overview (7), Facilitation: SDLC and introduction to SDLC (15), Facilitation: Agile vs waterfall (15), break (15), Facilitation: Scrum ceremonies (20), Facilitation: Story pointing (20), lunch (45, as the live runbook records it).
- PM: Facilitation: Source control management (git, vcs, cvcs, dvcs) (10), Walkthrough 01-tooling-and-git (85; the tooling check with the Interpreter vs compiler explanation and REPL and Jupyter, the local git loop, a 10-minute break after the conflict, then the remote round trip), notes page handoff and 6-question check (15), exercise briefing (10; the Git exercise facilitation, rubric-marked), exercise (60), wrap-up (10). Total 362.
- Demo minutes: 85 (01-tooling-and-git 85).

### w01d3 — Python basics (Wed Oct 14, 2026)

- AM: setup check (10; `python --version` 3.15 and a clean `git status` in the demo repo, the state Tuesday left), framing (5; the page's first sentence: today assumes the tooling check passed and the demo repo exists), Facilitation: PEP 8 as the team's contract (10; five rules on the board: names, blank lines, line length, imports first, comments say why), Walkthrough 02-ticket-record-and-rules (60; Python syntax, Comments, Variables and datatypes, a 15-minute break after the record prints, then Operators), lunch (60).
- PM: Walkthrough 03-desk-intake (35; User input and output; its `if sys.stdin.isatty():` guard is the day's only `if`, explained in one line with the talking point that Friday teaches `if` properly; then the merge into `main`), break (10), notes page handoff and 6-question check (15), exercise briefing (10; a pytest-checked module the trainee writes to PEP 8: a ticket summary line from given variables, with the operators and the f-string formats of the day), exercise (100), wrap-up (10). Total 340.
- Demo minutes: 95 (02-ticket-record-and-rules 60, 03-desk-intake 35).

### w01d4 — Python data types (Thu Oct 15, 2026)

- AM: setup check (10; `python ticket_desk.py` runs from `main`, `git status` clean), framing (5; today assumes Wednesday's conventions and the intake lines; the page's first sentence says so), Walkthrough 04-ticket-text-and-queue (65; Strings, Casting, Boolean, a 15-minute break after the casting steps, then Lists, Tuples, Range, Sets), lunch (60).
- PM: Walkthrough 05-ticket-dict-and-clock (65; Binary types, NoneType, Dictionaries, then Numbers, Datetime, Namespaces and the merge into `main`; the notes page puts Numbers and Datetime together on step 6 because the float pitfalls appear in the same `hours_open` computation as the clock), break (10), notes page handoff and 6-question check (15), exercise briefing (10; a pytest-checked module: normalise a ticket title, build the queue as tuples, look up SLA hours from a dict, compute a deadline with `timedelta`), exercise (90), wrap-up (10). Total 355.
- Demo minutes: 130 (04-ticket-text-and-queue 65, 05-ticket-dict-and-clock 65).

### w01d5 — Control flow, functions & classes (Fri Oct 16, 2026)

- AM: setup check (10; `python ticket_desk.py` runs from `main`, prints the dated board), framing (5; today assumes Thursday's dict, queue and clock; the page's first sentence says so), Walkthrough 06-desk-control-flow-and-functions (70; If-else, While loops, For loops, a 15-minute break after the loops, then Functions, Lambda, Arrays), lunch (60).
- PM: Walkthrough 07-ticket-and-desk-classes (70; OOP concepts, Inheritance, then Iterators, Scope, Classes and objects and the merge into `main`), break (10), notes page handoff and 6-question check (15), exercise briefing (10; a pytest-checked module: a `Ticket` class with a deadline method, a `Desk` that iterates, a sort by lambda key, a guard clause), exercise (80), wrap-up (10), weekly feedback form (10). Total 365.
- Demo minutes: 140 (06-desk-control-flow-and-functions 70, 07-ticket-and-desk-classes 70).

## Stop points

| Walkthrough | Clean stop point | Resume at |
|---|---|---|
| 01-tooling-and-git | after the conflict is resolved and merged (the local git loop is closed) | the remote round trip opens Wednesday's framing as a five-minute trainer-only push, or runs in the exercise briefing |
| 02-ticket-record-and-rules | after the one-ticket record prints (the operators steps are the tail) | 03-desk-intake opens with `%`, `**` precedence and `round` before the intake guard |
| 03-desk-intake | after the `if sys.stdin.isatty():` guard and the board print | the `sys.stderr` warning line's talking points move to Thursday's framing; the merge into `main` slides to 04-ticket-text-and-queue Step 1 |
| 04-ticket-text-and-queue | after the strings and casting steps (the truthiness step is the tail) | 05-ticket-dict-and-clock opens with the Boolean truthiness step, then the Sets step, before Binary types |
| 05-ticket-dict-and-clock | after the ticket dict and `SLA_HOURS` lookup | `tickets_by_id` and the clock steps move to Friday's framing; the merge into `main` slides to 06-desk-control-flow-and-functions Step 1 |
| 06-desk-control-flow-and-functions | after `if/elif/else` and the `for` loop over the queue | 07-ticket-and-desk-classes opens with the `while` intake loop and the functions steps |
| 07-ticket-and-desk-classes | after `Ticket` and `UrgentTicket` replace the dict | the `Desk` steps' talking points move into the notes page handoff with the lines pasted from the walkthrough before the commit; the merge into `main` happens in the wrap-up; nothing lands on Monday of week 2 |

## Squeeze priorities

**Cut first** (lowest cost to the through-line):

1. Facilitation: Full stack overview down to two minutes, then the pair rounds in SDLC and Agile vs waterfall, then the morning break back to 10.
2. Facilitation: PEP 8 as the team's contract (its five rules repeat as talking points inside 02-ticket-record-and-rules).
3. The transient lines of the Binary types steps in 05-ticket-dict-and-clock and the `iter()`/`next()` manual stepping in 07-ticket-and-desk-classes (talking points only).
4. The exercise: Wednesday 100 to 80, Thursday 90 to 75, Friday 80 to 60; the wrap-up to 5 minutes.

**Never cut** (the lesson dies without these):

- 01-tooling-and-git: the conflict step (the exercise marks it and Wednesday starts from this repo) and the remote round trip's first three steps.
- 02-ticket-record-and-rules: every variable name (every later block reads them).
- 03-desk-intake: the intake lines and `import sys` (Thursday's blocks start from them).
- 04-ticket-text-and-queue and 05-ticket-dict-and-clock: the kept lines (`SLA_HOURS`, the ticket dict, `NOW`, `opened_at`, `deadline` feed Friday's functions and class).
- 06-desk-control-flow-and-functions and 07-ticket-and-desk-classes: every kept line (`Desk` is the end state week 2 would have started from).
- The exercise briefing of every day; the weekly feedback form.

## Hard-stop rule

A within-day stop point moves a step's talking points only; the step's kept lines are pasted from the walkthrough before the block's commit, so every commit equals the block's end state. When a whole step slides to a later block of the same day, the commit slides with it and is made before the next block's first typed line. Only a day-end merge into `main` may slide to the next day's first block. If a walkthrough hits 80% of its slot with half its steps left, stop at the clean stop point above and resume there next slot; never double-speed a code-along on week 1.

## Scaffold bundle

Week 1 is all first-contact: built entirely from scratch, nothing pre-provided. The scaffolding is the lesson (the first `git init`, the first push, the first `.py` file).

| Day | Hand-out | Pre-provided | Why rote |
|---|---|---|---|
| w01d2 | — | none | first-contact tooling and git; the typing is the lesson |
| w01d3 | — | none | the first Python file is typed from the first line |
| w01d4 | — | none | every data type is typed against the same ticket |
| w01d5 | — | none | functions and classes are the refactor the room types |

| Never pre-provide | Walkthrough |
|---|---|
| `git init`, the first commit, the conflict resolution, the remote push | 01-tooling-and-git |
| the ticket variables and every operator line | 02-ticket-record-and-rules |
| the `input()` guard and the f-string board | 03-desk-intake |
| string methods, casts, the tuple queue, the set | 04-ticket-text-and-queue |
| the ticket dict, `SLA_HOURS`, the `datetime` lines | 05-ticket-dict-and-clock |
| `if/elif/else`, the loops, every `def` | 06-desk-control-flow-and-functions |
| `Ticket`, `UrgentTicket`, `Desk` | 07-ticket-and-desk-classes |

## Run prerequisites

- Python 3.15 installed on every laptop (the W1D2 tooling check proves it); Git installed with a name and email; a GitHub account in the `2494-Gen-AI-CN` organisation.
- The demo repo `2494-Gen-AI-CN/demos` created and cloned at `demo-repo/` (D-0050); no container, no package, no key this week.

## Anti-spoiler ledger

| Day | Defers | To | Why |
|---|---|---|---|
| w01d2 | Python syntax, conventions and any `.py` beyond the five-line `hello.py` | w01d3 | the day note: at most one on-ramp demo; the day is about how teams work |
| w01d2 | pytest and starter modules (the Git exercise is rubric-marked) | week 2 | the day note forbids pytest; testing is week 2 day 3 |
| w01d2 | rebase, `--amend`, `restore`, `reset`, `revert`, force-push | week 2 | the scripts name them only as "the other option"; the only escape hatch this week is `git merge --abort` |
| w01d3 | casting typed text to numbers (`int(input(...))`); intake stays `title` and `priority` strings | w01d4 | Casting is a Thursday subtopic; Wednesday's I/O lesson is prompt, `print` options and f-string formats |
| w01d3 | lists, tuples, sets, dicts, `None` (the ticket stays flat variables and three `SLA_HOURS_*` constants) | w01d4 | Thursday teaches the data types; Wednesday keeps the ticket as flat variables |
| w01d3 | string methods (`.strip()`, `.lower()`, slicing on `title` and `priority`; Wednesday's intake uses the text as typed) | w01d4 | Strings is a Thursday subtopic; rung 6 normalises the same two variables |
| w01d3 | `if` as a lesson, loops, functions (the intake guard is one plain `if sys.stdin.isatty():` explained in one line; repeated prints stay repeated) | w01d5 | control flow and functions are Friday's topics; Friday's rung 10 adds the `while` re-ask inside the same guard |
| w01d3 | `datetime`; `hours_open` is a literal float | w01d4 | Datetime is a Thursday subtopic; the literal keeps Wednesday's operators lesson arithmetic-only |
| w01d4 | `for` over the queue, `if` on ticket state (every record is printed by its own `print`; the breach flag stays a boolean expression) | w01d5 | loops and branching are Friday's topics; Thursday shows the data and leaves the control flow to Friday |
| w01d4 | functions and `lambda` (the queue sorts by tuple order; a sort key needs Friday's lambda) | w01d5 | sort keys need a function; tuple order is the Thursday idiom that motivates Friday's lambda |
| w01d4 | classes (the ticket is a dict; `tickets_by_id` is the registry) | w01d5 | "when a class" is Friday's question; the dict is what the class replaces |
| w01d4 | `iter()`, `next()`, `__iter__` (Thursday's lists and dicts are consumed only by indexing and `sorted`) | w01d5 | Iterators is a Friday subtopic; rung 13 steps a list by hand before `Desk.__iter__` |
| w01d4 | `import math`, `isclose`, `statistics` (float comparison uses `round` and `abs(a - b) < 1e-9`) | week 2 | the Math module is week 2 day 1 |
| w01d4 | time zones and `zoneinfo` (datetimes are naive and `NOW` is pinned) | week 2 | enough `datetime` to compute a deadline; zones arrive with file and log timestamps |
| w01d5 | `if __name__ == "__main__":` around the script body (the body stays module-level) | week 2 | week 2 day 1 splits the file into modules; the guard is that day's first edit |
| w01d5 | generators, `yield`, `__next__` on `Desk` (`__iter__` returns `iter(self._tickets)`) | week 2 | the iterator protocol is shown through `iter()`/`next()` on a list; writing one by hand is beyond the day |
| w01d5 | exceptions, `try/except` (`StopIteration`, `KeyError`, `ValueError` are shown and deleted, never caught) | week 2 | Exceptions are week 2 day 2 |
| w01d5 | pytest on the thread (the exercise runs pytest; the demos never write a test) | week 2 | Testing is week 2 day 3; week 1 demos stay a single runnable script |
| w01d5 | dataclasses, properties, `__eq__`, `__lt__` | week 2 | one class with `__init__` and `__repr__` is the Friday design choice; the rest is review week material |

## Real-world framing and deliberate deviations

A support desk at a small software company works like this: a customer files a ticket (title, description, who they are), an agent triages it (priority, assignee), the team's SLA says how many hours a priority may stay open, and "done" means the ticket is closed with a history that explains what happened. A professional team builds this as a package with modules, a database behind it, a web form or email intake, logging, tests on every rule, and a CI job that runs them on every pull request; nobody keeps tickets in a single script's variables. The demos build the single script on purpose and ledger each shortcut below so the trainer can name it in one sentence when the room asks.

| Deviation | Workplace reality | Pedagogical reason |
|---|---|---|
| a bare folder `../origin.git` stands in for GitHub until the closing minute of 03_remote_round_trip | a hosted remote with branch protection and PR review | no credentials on the projector; every push, fetch and pull is reproducible offline, and the live `git remote set-url origin <GitHub URL>` shows the swap is one command |
| the trainer plays the teammate from a second terminal tab (`teammate/` clone) | a second person on another machine | one shell shows both sides of fetch, pull and divergence in eight minutes |
| one `ticket_desk.py` file holds the whole desk | a package (`tickets/`, `sla/`, `cli/`) with tests | one file keeps week 1's typing on the language, not on packaging; week 2 day 1 does the split |
| tickets live in Python variables, then tuples, then a dict, then objects in memory | a database table; nothing survives the process exit | the data-type ladder is the lesson; week 3 moves the same records into MySQL |
| the "customer" is the trainer at `input()` and a sample ticket when no terminal is attached (`sys.stdin.isatty()`) | a web form, email intake or an API; argparse for a CLI | `input()` is the Wednesday subtopic; the guard lets the committed file run unattended for the critic and CI |
| `NOW` is a pinned `datetime(2026, 10, 15, 14, 0)` | `datetime.now(tz=...)` at call time | a pinned clock makes the key's output stable and the breach flag predictable in class; Friday's `is_overdue(ticket, now=NOW)` takes the clock as an argument so the pin is one line to change |
| SLA hours are a dict literal in the file | a configuration table or file, per customer tier | the lookup-table idiom is the Thursday lesson; week 2 reads it from JSON |
| ticket ids come from `range` and then a class attribute counter | the database assigns ids | id generation is a scope lesson (global versus class attribute) on Friday |
| commits land on one feature branch per day merged by the trainer | a pull request reviewed by a teammate before merge | PR review is a notes-page topic this week; the demo budget goes to Python, and the Tuesday exercise already marks the branch workflow |
| no tests on the thread this week | every rule has a pytest test before merge | pytest is week 2 day 3; the exercises run pytest so the room meets the tool before it is taught |
| hard-coded sample tickets ("Printer on floor 3 jams") | records from real intake | fixed data keeps every rung's expected output printable in the script's Check blocks |
| `hello.py` and `README.md` from Tuesday stay in the scratch repo untouched | a repo holds one project | they are the Git history the room built; deleting them would spend typed lines on nothing |
| the blocks were authored but not delivered: W1D2–W1D5 ran as loose days (D-0050) | a team demos what the work needs, not a pre-typed ladder | the trainer improvised in the public demo repo; the former scripts and keys stay in trainer/week-01/<day>/demos/ as history and `close_day.py` recorded what was actually typed |
| the ticket-desk thread restarts cold in the week-2 plan (`args_for.py 2 --plan --cold`) | work continues in the codebase that exists | the room's week-1 code was not the ladder's end state, so week 2 starts from a fresh rung 1 instead of the week-1 key |
| the `array` module cameo is three lines | numpy arrays for numeric work | the curriculum lists Arrays on Friday; numpy is week 2 day 3 |
| `UrgentTicket` halves the SLA by overriding one method | a real desk keeps priority as data on the record and never subclasses for it | one subclass with `super()` is the smallest honest inheritance example; the notes page says when a subclass is the wrong tool |

## Coverage map

| Subtopic | Day | Demo | Notes step |
|---|---|---|---|
| What is Python, why Python | w01d2 | facilitation | 1 |
| Professionalism at Revature | w01d2 | facilitation | 1 |
| Python orientation (tooling check) | w01d2 | 01-tooling-and-git | 1 |
| Interpreter vs compiler | w01d2 | 01-tooling-and-git | 1 |
| REPL and Jupyter | w01d2 | 01-tooling-and-git | 1 |
| Full stack overview | w01d2 | facilitation | 1 |
| SDLC and introduction to SDLC | w01d2 | facilitation | 2 |
| Agile vs waterfall | w01d2 | facilitation | 2 |
| Scrum ceremonies | w01d2 | facilitation | 3 |
| Story pointing | w01d2 | facilitation | 4 |
| Source control management (git, vcs, cvcs, dvcs) | w01d2 | facilitation | 5 |
| Git fundamentals | w01d2 | 01-tooling-and-git | 5 |
| Initializing a repository | w01d2 | 01-tooling-and-git | 5 |
| Commit, branch, merge, push, pull | w01d2 | 01-tooling-and-git | 6 |
| Pushing to a remote repository | w01d2 | 01-tooling-and-git | 7 |
| Git exercise | w01d2 | facilitation | 8 |
| Python syntax | w01d3 | 02-ticket-record-and-rules | 1 |
| Comments | w01d3 | 02-ticket-record-and-rules | 2 |
| Variables and datatypes | w01d3 | 02-ticket-record-and-rules | 3 |
| Operators | w01d3 | 02-ticket-record-and-rules | 4 |
| User input and output | w01d3 | 03-desk-intake | 5 |
| Strings | w01d4 | 04-ticket-text-and-queue | 1 |
| Casting | w01d4 | 04-ticket-text-and-queue | 2 |
| Boolean | w01d4 | 04-ticket-text-and-queue | 2 |
| Lists | w01d4 | 04-ticket-text-and-queue | 3 |
| Tuples | w01d4 | 04-ticket-text-and-queue | 3 |
| Range | w01d4 | 04-ticket-text-and-queue | 3 |
| Sets | w01d4 | 04-ticket-text-and-queue | 4 |
| Binary types | w01d4 | 05-ticket-dict-and-clock | 4 |
| NoneType | w01d4 | 05-ticket-dict-and-clock | 5 |
| Dictionaries | w01d4 | 05-ticket-dict-and-clock | 5 |
| Numbers | w01d4 | 05-ticket-dict-and-clock | 6 |
| Datetime | w01d4 | 05-ticket-dict-and-clock | 6 |
| Namespaces | w01d4 | 05-ticket-dict-and-clock | 7 |
| If-else | w01d5 | 06-desk-control-flow-and-functions | 1 |
| While loops | w01d5 | 06-desk-control-flow-and-functions | 2 |
| For loops | w01d5 | 06-desk-control-flow-and-functions | 2 |
| Functions | w01d5 | 06-desk-control-flow-and-functions | 3 |
| Lambda | w01d5 | 06-desk-control-flow-and-functions | 4 |
| Arrays | w01d5 | 06-desk-control-flow-and-functions | 5 |
| OOP concepts | w01d5 | 07-ticket-and-desk-classes | 6 |
| Inheritance | w01d5 | 07-ticket-and-desk-classes | 7 |
| Iterators | w01d5 | 07-ticket-and-desk-classes | 8 |
| Scope | w01d5 | 07-ticket-and-desk-classes | 9 |
| Classes and objects | w01d5 | 07-ticket-and-desk-classes | 6 |

## Exit criteria map

| ID | Tier | Criterion | Day | Where | Notes step |
|---|---|---|---|---|---|
| qc1.agile.R01 | Required | Describe the difference between iterative and linear SDLC techniques. | w01d2 | facilitation | 2 |
| qc1.agile.R02 | Required | Explain the benefits of using the Agile process. | w01d2 | facilitation | 2 |
| qc1.agile.R03 | Required | Describe the scrum ceremonies. | w01d2 | facilitation | 3 |
| qc1.agile.R04 | Required | Describe the phases of SDLC. | w01d2 | facilitation | 2 |
| qc1.agile.R05 | Required | Participate in developing a sprint backlog | w01d2 | notes-only | 3 |
| qc1.agile.P01 | Preferred | Describe the scrum process. | w01d2 | facilitation | 3 |
| qc1.agile.P02 | Preferred | Participate in at least one scrum ceremony (e.g. sprint planning, daily stand-up, sprint review, retrospective) and demonstrate understanding of their purpose and outcomes. | w01d2 | notes-only | 3 |
| qc1.agile.P03 | Preferred | Develop a user story by breaking down its components (e.g. role, feature, benefit) and create tasks to complete it. | w01d2 | notes-only | 4 |
| qc1.agile.S01 | Stretch | Describe story pointing and burndown charts. | w01d2 | facilitation | 4 |
| qc1.agile.S02 | Stretch | Demonstrate knowledge of velocity. | w01d2 | facilitation | 4 |
| qc1.git.R01 | Required | Describe the purpose of git. | w01d2 | facilitation | 5 |
| qc1.git.R02 | Required | Describe the difference between git and a git-based cloud service provider. | w01d2 | notes-only | 5 |
| qc1.git.R03 | Required | Clone an existing repository. | w01d2 | 01-tooling-and-git | 5 |
| qc1.git.R04 | Required | Utilize a command line interface to add and commit to a local repository. | w01d2 | 01-tooling-and-git | 5 |
| qc1.git.R05 | Required | Utilize a command line interface to push to and pull from a remote repository. | w01d2 | 01-tooling-and-git | 7 |
| qc1.git.R06 | Required | Describe a simple git workflow to publish local changes to a remote repository. | w01d2 | 01-tooling-and-git | 7 |
| qc1.git.R07 | Required | Describe the function of branching in a git repository, and how it differs from forking a repository. | w01d2 | 01-tooling-and-git | 6 |
| qc1.git.R08 | Required | Create a branch on an existing repository, commit changes to it, and push it to the remote repository. | w01d2 | 01-tooling-and-git | 6 |
| qc1.git.R09 | Required | Create a pull or merge request through a git-based cloud service provider to merge two branches together while resolving any conflicts. | w01d2 | notes-only | 6 |
| qc1.git.R10 | Required | Using a command line interface, switch between branches of a repository. | w01d2 | 01-tooling-and-git | 6 |
| qc1.git.R11 | Required | Describe common git workflow patterns and branching strategies (e.g. git flow) used by teams on collaborative projects, and their benefits. | w01d2 | notes-only | 8 |
| qc1.git.R12 | Required | Explain why merge conflicts happen, and resolve them while merging two branches using a command line interface. | w01d2 | 01-tooling-and-git | 6 |
| qc1.git.R13 | Required | Describe the purpose of rebase, fast-forward, and squash options when merging. | w01d2 | 01-tooling-and-git | 6 |
| qc1.git.P01 | Preferred | Utilize a .gitignore file to prevent build files from being committed to a repo. | w01d2 | 01-tooling-and-git | 5 |
| qc1.git.P02 | Preferred | Utilize a command line interface to initialize a new local git repository. | w01d2 | 01-tooling-and-git | 5 |
| qc1.git.P03 | Preferred | Use git stash to save code changes without committing and git stash pop to restore those changes. | w01d2 | notes-only | 6 |
| qc1.git.P04 | Preferred | Using git diff, inspect a file for changes across branches prior to creating a merge request. | w01d2 | notes-only | 5 |
| qc1.git.P05 | Preferred | Using a command line interface, navigate a repository's commit history to branch from a previous commit. | w01d2 | notes-only | 6 |
| qc1.git.P06 | Preferred | Complete a rebase, fast-forward, and/or squash merge. | w01d2 | 01-tooling-and-git | 6 |
| qc1.git.S01 | Stretch | Utilize CLI flags to combine the add and commit steps. | w01d2 | notes-only | 5 |
| qc1.git.S02 | Stretch | Utilize a command line interface to view the current state of a local repository. | w01d2 | 01-tooling-and-git | 5 |
| qc1.git.S03 | Stretch | Utilize a command line interface to view a log of recent commits. | w01d2 | 01-tooling-and-git | 8 |
| qc1.python.R01 | Required | Executes and describes basic programming constructs | w01d3 | 02-ticket-record-and-rules | 1 |
| qc1.python.R03 | Required | Understands control flow, variable scopes, functions/methods and parameters | w01d5 | 06-desk-control-flow-and-functions | 3 |
| qc1.python.R04 | Required | Uses appropriate data types and can elaborate on all basic Python datatypes | w01d4 | 04-ticket-text-and-queue | 3 |
| qc1.python.R05 | Required | Explain the advantages and benefits of using the Python Language | w01d2 | facilitation | 1 |
| qc1.python.R06 | Required | Understands how and when to apply different conditional logic based on problem set requirements | w01d5 | 06-desk-control-flow-and-functions | 1 |
| qc1.python.R07 | Required | Explain, elaborate, and incorporate the 4 OOP principles: abstraction, encapsulation, polymorphism, inheritance | w01d5 | 07-ticket-and-desk-classes | 6 |
| qc1.python.R08 | Required | Knows the difference between method overloading and method overriding | w01d5 | 07-ticket-and-desk-classes | 7 |
| qc1.python.R09 | Required | Create and invoke constructors to instantiate objects | w01d5 | 07-ticket-and-desk-classes | 6 |
| qc1.python.R10 | Required | Explain the difference between classes and objects | w01d5 | 07-ticket-and-desk-classes | 6 |
| qc1.python.R12 | Required | Override methods within a child class that extends a parent class | w01d5 | 07-ticket-and-desk-classes | 7 |
| qc1.python.R13 | Required | Explain encapsulation with the naming convention-based approach, similar to access modifiers | w01d5 | 07-ticket-and-desk-classes | 6 |
| qc1.python.R15 | Required | Can explain and implement multiple inheritance in Python | w01d5 | notes-only | 7 |
| qc1.python.R23 | Required | Demonstrates understanding of scope and namespaces | w01d5 | 07-ticket-and-desk-classes | 9 |
| qc1.python.P04 | Preferred | Can explain Python's "Call by Object Reference" or "Call by assignment" system | w01d3 | notes-only | 3 |
| qc1.python.P08 | Preferred | Can explain what garbage collection is in Python and identify when objects become eligible for collection | w01d2 | notes-only | 1 |
| qc1.python.P11 | Preferred | Explains interpreter vs. compiler differences | w01d2 | 01-tooling-and-git | 1 |
| qc1.python.P14 | Preferred | Good understanding of functional programming (lambdas, higher-order functions, functions as variables, pure vs. impure functions) | w01d5 | 06-desk-control-flow-and-functions | 4 |
| qc1.python.P16 | Preferred | Understands the difference between 'is' and '==' in Python | w01d3 | 02-ticket-record-and-rules | 3 |
| qc1.python.S02 | Stretch | Able to use and elaborate on Namespaces in Python | w01d4 | 05-ticket-dict-and-clock | 7 |
| qc1.python.S03 | Stretch | Can use Python's zip(), enumerate(), and map() effectively | w01d5 | notes-only | 2 |
