# Week 01 plan — Agile for developers, Git & Python fundamentals

Week 1 · 2026-10-12 to 2026-10-16 · phase py · project P0 · plan written 2026-10-12

<!--
Week plan (D-0034). Monday 2026-10-12 is a holiday; the week has four teaching days, Tue to Fri. w01d2 is live and
its rows are recorded as-is from trainer/week-01/day-2-orientation-agile-and-git/demos/. The thread's working file in
the repository is `team-repo/ticket_desk.py`; each rung's key under demos/key/ is the copy of that file at the end of
the rung (D-0033).
-->

## Weekly Epic

By Friday afternoon a trainee opens `team-repo`, checks out `main`, and runs `python ticket_desk.py`: a support-ticket desk that reads a new ticket at the prompt, keeps tickets as `Ticket` objects inside a `Desk` that iterates them, looks up each ticket's SLA by priority, computes its deadline with `datetime`, and prints the queue sorted by priority and age. The trainee has typed that file alongside the trainer across Wednesday, Thursday and Friday, one commit per rung, on a feature branch per day merged into `main`, so `git log --oneline` reads as the story of the week. Project 0 needs exactly this: a Python model of the domain's records (title, priority, status, history, deadline) written to PEP 8, that week 2 can split into modules, log, serialise to JSON and test with pytest.

## Assumes from the previous week

- First week: the audience persona from config.json. Recent CS graduates (University of Toronto cohort), no industry experience. They know Python syntax and the standard data types from coursework, `git clone`, `add`, `commit`, `push`, and the compiler-versus-interpreter distinction.
- Does NOT assume: that `python --version` on their laptop prints 3.15, that `git` is installed and configured with a name and email, or that they have resolved a merge conflict. Tuesday's `01_tooling_check` and `02_local_git_loop` Step 1 re-check all three before anything depends on them.
- Does NOT assume any team practice: SDLC, Scrum, story points, feature branches, commit hygiene and code review are taught from the start on Tuesday.

## Threads

### p0-ticket-desk

- Domain: a support-ticket desk for a small software team: tickets with a title, priority, status, assignee and history, filed by customers and triaged by agents. The same records survive every week of the scope: week 1 holds them in Python variables, tuples, a dict and then a `Ticket` class inside a `Desk`; week 2 splits `ticket_desk.py` into modules, adds logging, saves the desk to a JSON file, matches ticket text with regex and tests the rules with pytest; week 3 moves tickets, customers and agents into MySQL tables with joins and a transaction on assignment; week 4 loads ticket events into a BigQuery star schema through an ETL job; week 5 sends tickets to an LLM for triage, summaries and draft replies.
- Scope: weeks 1–5 (project P0); this week plans rungs 1–13.
- Start state this week: cold (rung 1 creates `team-repo` with `git init`).
- Stop-point rule (every day below): a within-day stop point moves a step's talking points only; the step's kept lines are pasted from the rung's key before the rung's commit, so every commit equals its key. When a whole step slides to a later demo of the same day, the rung's commit slides with it and is made before the next demo's first typed line. Only a day-end merge into `main` may slide to the next day's first rung.
- End state this week: `trainer/week-01/day-5-control-flow-functions-and-classes/demos/key/04_desk_object.py` (the last rung below), about 200 lines (199 as authored, one under the 200-line thread-key cap, so week 2's first rung has no headroom until the module split) (`ticket_desk.py` on `main` of `team-repo`, 11 commits on top of Tuesday's ten; the three day-end merges of `feature/ticket-record`, `feature/data-types` and `feature/design-choices` fast-forward because `main` gains no commit meanwhile, as Tuesday's `feature/farewell` merge showed).

| Rung | Day | Demo | Key | Starts from | Adds | End state | Commit message |
|---|---|---|---|---|---|---|---|
| 1 | w01d2 | 02_local_git_loop | 02_local_git_loop.md | cold | git identity and init.defaultBranch; `team-repo` with `git init`; `hello.py` (greet) and `.gitignore` committed; `feature/farewell` branch merged fast-forward; `feature/shout` conflict on the print line resolved by hand | `team-repo` on `main` with 5 commits, `hello.py` printing `HELLO, TORONTO!` and the farewell, a two-parent merge commit in `git log --oneline --graph` | Merge feature/shout into main |
| 2 | w01d2 | 03_remote_round_trip | 03_remote_round_trip.md | trainer/week-01/day-2-orientation-agile-and-git/demos/key/02_local_git_loop.md | bare `origin.git` next to the repo, `git remote add`, `push -u`; a `teammate/` clone that adds `README.md`; fetch, pull, a diverged history merged with `--no-rebase`; a commit with a body line | `team-repo` on `main` with 10 commits, up to date with `origin/main`; `README.md` with four content lines ending `Run it with: python hello.py`; the same history on GitHub after the live closing minute | Document how to run hello.py |
| 3 | w01d3 | 01_ticket_record | 01_ticket_record.py | trainer/week-01/day-2-orientation-agile-and-git/demos/key/03_remote_round_trip.md | `git switch -c feature/ticket-record`; new file `ticket_desk.py`: module docstring, `SLA_HOURS_HIGH`, `SLA_HOURS_NORMAL`, `SLA_HOURS_LOW` constants, one ticket as flat variables (`ticket_id`, `title`, `priority`, `is_open`, `hours_open`, `reporter`), one why-comment kept and one restating comment deleted, an f-string print of the record; `python ticket_desk.py` | `python ticket_desk.py` prints the one ticket on one line; file follows PEP 8 (snake_case, UPPER_CASE constants, two blank lines, under 79 columns) | Add ticket desk with one ticket record |
| 4 | w01d3 | 02_ticket_rules | 02_ticket_rules.py | trainer/week-01/day-3-python-basics/demos/key/01_ticket_record.py | `age_days = hours_open // 24` next to `/`, `hours_left = SLA_HOURS_HIGH - hours_open`, `is_breached = is_open and hours_left < 0`, a chained comparison `0 <= hours_open < 24`, `priority_ok` written with three `==` after the `priority == "high" or "normal"` pitfall is shown and deleted, `hours_open += 0.5`, `%` for every-third escalation, `-2 ** 2` precedence, `round`; prints of each result | the script prints age, hours left, breach flag and the priority check for the one ticket | Compute ticket age and SLA breach |
| 5 | w01d3 | 03_desk_intake | 03_desk_intake.py | trainer/week-01/day-3-python-basics/demos/key/02_ticket_rules.py | `import sys` at the top; a plain four-line guard `if sys.stdin.isatty():` that reads `title` and `priority` with `input()` and otherwise keeps the sample values (talking point: the only `if` of the day, known from coursework; Friday treats `if` as a design choice); `print` with `sep` and `end`; a board header and row with f-string alignment `{title:<30}{priority:>8}{hours_open:>6.1f}`; a warning line to `sys.stderr`; `git switch main` and `git merge feature/ticket-record` | at a terminal the script asks for a title and priority, then prints a two-line board; unattended it prints the board for the sample ticket; `main` has the day's three commits | Read a new ticket at the prompt and print the board |
| 6 | w01d4 | 01_ticket_text | 01_ticket_text.py | trainer/week-01/day-3-python-basics/demos/key/03_desk_intake.py | (if Wednesday's merge slid: `git switch main`, `git merge feature/ticket-record` first) `git switch -c feature/data-types`; `title.strip()`, `priority.strip().lower()`, `title[:40]`, `.startswith`, `.replace`, `len`, `in`; `ticket_id` read as text with `input()` inside the same `if sys.stdin.isatty():` guard then cast with `int()` (`hours_open` stays the literal float from rung 3), `float("4.5")`, `int("3.5")` and `int(3.9)` shown then deleted, `str(ticket_id)`; `bool("False")`, `bool("")`, `bool(0)` shown then deleted, truthiness `is_open and title` kept, `== True` pitfall deleted | normalised title and priority, `ticket_id` an `int` cast from typed text, the board prints the trimmed title | Normalise ticket text and cast typed numbers |
| 7 | w01d4 | 02_ticket_queue | 02_ticket_queue.py | trainer/week-01/day-4-python-data-types/demos/key/01_ticket_text.py | `queue = []` with three `(rank, ticket_id, title)` tuples appended, three per-tuple prints `print(queue[0])`, `print(queue[1])`, `print(queue[2])` (the repeated prints rung 10's `for` loop replaces), `queue[-1]`, `queue[1:]`, `len(queue)` prints, `sorted(queue)` on tuple order, `.sort()` returning `None` shown then deleted, `backup = queue` aliasing shown then replaced by `queue.copy()`, tuple unpacking `rank, tid, text = queue[0]` shown then deleted (transient, so nothing carries into rung 11's dict queue), `(1,)` versus `(1)`, `ids = list(range(1, 4))`, `reporters = {"dana", "lee", "dana"}`, `.add`, `in`, `&`, `-`, `set()` for an empty set | the queue of three tuples prints sorted by rank then id; `reporters` prints two names; the one-ticket variables still print | Queue tickets as tuples; track reporters as a set |
| 8 | w01d4 | 03_ticket_dict | 03_ticket_dict.py | trainer/week-01/day-4-python-data-types/demos/key/02_ticket_queue.py | `raw = title.encode("utf-8")`, `len("café")` against `len("café".encode())`, `raw.decode()`, `bytes + str` TypeError shown then deleted; `assignee = None`, `assignee is None` replacing `== None`, `print(print(...))` shown then deleted; `SLA_HOURS = {"high": 4, "normal": 24, "low": 72}` replacing the three constants AND rung 4's `hours_left = SLA_HOURS_HIGH - hours_open`, rewritten as `hours_left = SLA_HOURS[priority] - hours_open` (replaced block names all four lines), `ticket = {"id": ..., "title": ..., "priority": ..., "assignee": None, "history": []}`, `ticket["owner"]` KeyError shown then deleted, `.get("owner", "unassigned")`, `ticket["assignee"] = "lee"`, `ticket["history"].append(...)`, `"id" in ticket`, `list(ticket.items())`, `tickets_by_id = {ticket["id"]: ticket}` | the ticket record is a dict looked up by id, its SLA comes from `SLA_HOURS[priority]`, its history holds one entry; encode and decode round-trip prints | Model a ticket as a dict with an SLA lookup table |
| 9 | w01d4 | 04_ticket_clock | 04_ticket_clock.py | trainer/week-01/day-4-python-data-types/demos/key/03_ticket_dict.py | `0.1 + 0.2 == 0.3` shown then replaced by `round(..., 2)` and `abs(a - b) < 1e-9`, `10 / 4` against `10 // 4`, `divmod(int(hours_open), 24)`, `1_000_000`; `from datetime import datetime, timedelta`, `opened_at = datetime(2026, 10, 15, 9, 30)`, `NOW = datetime(2026, 10, 15, 14, 0)` after `datetime.now()` is typed and pinned, `age = NOW - opened_at`, `hours_open = age.total_seconds() / 3600` replacing the literal `hours_open` line from rung 3 and deleting rung 4's `hours_open += 0.5` bump (both in the replaced block, so the value is the clock's alone), `deadline = opened_at + timedelta(hours=SLA_HOURS[priority])`, `NOW > deadline`, `.isoformat()`, `.strftime("%a %H:%M")`; `import datetime` shadowing shown then deleted, `dir()`, `__name__`, `del backup`; `git switch main` and `git merge feature/data-types` | `hours_open` is computed from two datetimes, the deadline prints in ISO form, the breach flag follows the clock; `main` has the day's four commits | Track ticket age with datetime |
| 10 | w01d5 | 01_desk_control_flow | 01_desk_control_flow.py | trainer/week-01/day-4-python-data-types/demos/key/04_ticket_clock.py | (if Thursday's merge slid: `git switch main`, `git merge feature/data-types` first) `git switch -c feature/design-choices`; `if NOW > deadline: status = "breached" elif ... else` replacing the `is_breached` boolean lines (replaced block), a guard-clause rewrite of a nested `if` shown then flattened, `for rank, tid, text in sorted(queue): print(...)` replacing rung 7's three per-tuple prints `print(queue[0])`, `print(queue[1])`, `print(queue[2])` (replaced block), `for key, value in ticket.items()`, `while priority not in SLA_HOURS: priority = input(...)` added inside the `if sys.stdin.isatty():` guard from rung 5, `break` on an empty title | the script branches on ticket state, prints the queue with one loop, and re-asks at the prompt until the priority is valid; unattended it still prints the sample board | Branch on ticket state and loop over the queue |
| 11 | w01d5 | 02_desk_functions | 02_desk_functions.py | trainer/week-01/day-5-control-flow-functions-and-classes/demos/key/01_desk_control_flow.py | `def make_ticket(ticket_id, title, priority, opened_at):` returning the dict (replaces the literal dict lines with the call `ticket = make_ticket(ticket_id, title, priority, opened_at)`; `ticket_id` is the first parameter, the same signature rung 12's `__init__` takes, so every dict has an `"id"` for `tickets_by_id` and the appends), `def deadline_for(ticket):` (rung 9's inline `deadline = opened_at + timedelta(...)` line is rewritten as `deadline = deadline_for(ticket)`, so `NOW > deadline`, `.isoformat()` and `.strftime("%a %H:%M")` carry unchanged), `def is_overdue(ticket, now=NOW):` (replaces the status lines), one-line docstrings, a function with no `return` printing `None` shown then deleted, `history=[]` mutable default shown then replaced by `None`; the three tuple appends and `sorted(queue)` from rung 7 and the `for rank, tid, text in sorted(queue)` loop from rung 10 are replaced (replaced block) by three `queue.append(make_ticket(...))` lines, the third written as a kept keyword call `make_ticket(ticket_id=3, title=..., priority="low", opened_at=...)`, and `for t in queue:`; `queue.sort(key=lambda t: (PRIORITY_RANK[t["priority"]], t["opened_at"]))` with `PRIORITY_RANK` replacing the tuple-order sort; `from array import array`, `ages = array("d", [...])` three lines | ticket rules live in three named functions called from the script body; the queue holds dicts sorted by a lambda key on priority rank then `opened_at`; `ages` is a typed array next to the list | Extract ticket rules into functions |
| 12 | w01d5 | 03_ticket_class | 03_ticket_class.py | trainer/week-01/day-5-control-flow-functions-and-classes/demos/key/02_desk_functions.py | `class Ticket:` with `__init__(self, ticket_id, title, priority, opened_at)`, `__repr__`, `deadline(self)`, `assign(self, agent)`, `close(self)` (replaces `make_ticket`, `deadline_for` and the `ticket[...]` access lines, replaced block); the replaced block also names, each with its rewrite, every line that still used the dict or the deleted functions: rung 11's `ticket = make_ticket(ticket_id, title, priority, opened_at)` (rewritten as `ticket = Ticket(ticket_id, title, priority, opened_at)`) and `deadline = deadline_for(ticket)` (rewritten as `deadline = ticket.deadline()`), rung 11's three `queue.append(make_ticket(...))` lines (rewritten as two `queue.append(Ticket(...))` and one `queue.append(UrgentTicket(...))`), rung 10's `for key, value in ticket.items():` (rewritten as `for key, value in vars(ticket).items():`), rung 8's `ticket.get("owner", "unassigned")`, `"id" in ticket` and `list(ticket.items())` (rewritten as `ticket.assignee or "unassigned"`, `hasattr(ticket, "ticket_id")` and `vars(ticket)`), `ticket["assignee"] = "lee"` and `ticket["history"].append(...)` (rewritten as `ticket.assign("lee")`), the body of `is_overdue` (rewritten as `return now > ticket.deadline()`) and `tickets_by_id = {ticket["id"]: ticket}` (rewritten as `tickets_by_id = {ticket.ticket_id: ticket}`), so the key runs on its own; `class UrgentTicket(Ticket):` overriding `deadline` with `super().deadline()` halved, `isinstance(t, Ticket)`; `t.priority` and `t.opened_at` reads replacing `t["priority"]` and `t["opened_at"]` in the lambda | tickets are `Ticket` and `UrgentTicket` objects; `print(ticket)` uses `__repr__`; the queue sorts and prints by attribute; `is_overdue` takes a `Ticket`; `tickets_by_id` is keyed by `ticket.ticket_id` | Replace the ticket dict with a Ticket class |
| 13 | w01d5 | 04_desk_object | 04_desk_object.py | trainer/week-01/day-5-control-flow-functions-and-classes/demos/key/03_ticket_class.py | `class Desk:` with `self._tickets = []`, `add(self, ticket)`, `__len__`, `__iter__` returning `iter(self._tickets)`, `overdue(self, now)` returning a list; in Step 3, transient and typed BEFORE the queue is removed: `it = iter(queue)`, `next(it)` twice, `StopIteration` shown then deleted; then the replaced block names every surviving `queue` line with its fate: `queue = []` and the three `queue.append(...)` lines become `desk = Desk()` and three `desk.add(...)`; `for t in queue:` becomes `for t in sorted(desk, key=lambda x: (PRIORITY_RANK[x.priority], x.opened_at)):` (the iteration variable stays `t`, so the carried loop-body lines and rung 12's `isinstance(t, Ticket)` keep their binding and the module-level `ticket` record is never rebound); `queue.sort(...)` is deleted (the sorted call replaces it); rung 7's `queue[-1]`, `queue[1:]` and `len(queue)` prints are deleted (`print(len(desk))` replaces the last); `backup = queue.copy()` and rung 9's `del backup` are deleted; rung 12's rewritten `tickets_by_id = {ticket.ticket_id: ticket}` is deleted (the `Desk` is the registry); `global next_id` counter shown then replaced by the class attribute `Desk.next_id`, a four-line LEGB demonstration kept as `def label():` with a local shadowing a module name; `desk = Desk()`, three `desk.add(...)`, `print(len(desk))`; `git switch main` and `git merge feature/design-choices` | `python ticket_desk.py` builds a `Desk`, adds three tickets, iterates them in one `for` sorted by priority then `opened_at`, prints the overdue ones; `main` has the day's four commits and the file is about 200 lines | Add a Desk that owns and iterates its tickets |

<!--
Rung rules (checked by plan_check.py): rungs numbered 1..n in teaching order; Starts from is "cold" on the first
rung of the thread's whole scope, otherwise EXACTLY the previous rung's key path trainer/<weekDir>/<slug>/demos/key/<Key>
(the previous week's last rung for the first rung of a later week); Key is Demo + .py|.md|.ipynb; a .py key is the
thread's whole end state at that rung and fits metrics.demos.maxLinesPerThreadKey; Adds fits
metrics.demos.maxTypedLinesPerRung typed lines. A live day's rows are recorded as-is from its scripts on disk.
-->

## Standalone demos

| Day | Demo | Key | Minutes | Why it fits no thread |
|---|---|---|---|---|
| w01d2 | 01_tooling_check | 01_tooling_check.py | 15 | on-ramp tooling check (which Python, the REPL, a saved script, the `__pycache__` folder); no repository exists yet and the day note caps the on-ramp at one demo |

## Demo ladder

| # | Day | Demo | Minutes | Must follow | Guarantees |
|---|---|---|---|---|---|
| 1 | w01d2 | 01_tooling_check | 15 | — | `python --version` prints 3.15 on every machine; the room tells the shell, the `>>>` REPL and a running script apart; `w01d2-scratch/hello.py` exists and `__pycache__/` has appeared once |
| 2 | w01d2 | 02_local_git_loop | 40 | 1 | git identity and `init.defaultBranch main` configured; `w01d2-scratch/team-repo/` on `main` with 5 commits, `hello.py`, `.gitignore`, a fast-forward merge and a hand-resolved conflict with no markers left |
| 3 | w01d2 | 03_remote_round_trip | 30 | 2 | `team-repo` has `origin` (bare `../origin.git`, then GitHub), `main` tracks `origin/main`, 10 commits, `README.md` with four content lines ending `Run it with: python hello.py`; the room has seen fetch, pull, a diverged merge and a commit body |
| 4 | w01d3 | 01_ticket_record | 30 | 3 | branch `feature/ticket-record`; `team-repo/ticket_desk.py` exists, runs, prints one ticket from flat variables; the ticket variable names every later rung reads, and three `SLA_HOURS_*` constants that rung 8 replaces |
| 5 | w01d3 | 02_ticket_rules | 30 | 4 | `age_days`, `hours_left`, `is_breached`, `priority_ok` computed from the ticket variables; the room has typed `//`, `%`, `**`, `and`, `or`, `not`, `in` and a chained comparison |
| 6 | w01d3 | 03_desk_intake | 35 | 5 | `import sys` at the top of the file; `title` and `priority` come from `input()` inside an `if sys.stdin.isatty():` guard at a terminal and from the sample otherwise; the board prints with aligned f-strings; `main` holds rungs 3–5 merged |
| 7 | w01d4 | 01_ticket_text | 30 | 6 | branch `feature/data-types`; `title` and `priority` are stripped and lower-cased before use; `ticket_id` is an `int` cast from typed text; the room can predict `bool(x)` for strings and numbers |
| 8 | w01d4 | 02_ticket_queue | 35 | 7 | `queue` is a list of `(rank, ticket_id, title)` tuples that sorts by tuple order; each tuple is printed by its own `print(queue[i])` line (the three lines Friday's `for` replaces); `reporters` is a set; `ids` comes from `range`; the room has seen aliasing and `.sort()` returning `None` |
| 9 | w01d4 | 03_ticket_dict | 35 | 8 | `SLA_HOURS` dict replaces the three constants; `ticket` is a dict with `assignee` (`None` until assigned) and `history`; `tickets_by_id` maps id to ticket; `.get` with a default is the lookup idiom |
| 10 | w01d4 | 04_ticket_clock | 30 | 9 | `from datetime import datetime, timedelta` at the top; `opened_at`, `NOW`, `age`, `deadline` exist and `hours_open` derives from them (the rung 3 literal is gone); `main` holds rungs 6–9 merged |
| 11 | w01d5 | 01_desk_control_flow | 35 | 10 | branch `feature/design-choices`; `status` is set by `if/elif/else`; the queue prints by one `for`; the intake loop re-asks with `while` inside an `if sys.stdin.isatty():` guard |
| 12 | w01d5 | 02_desk_functions | 35 | 11 | the deadline rule lives only in `deadline_for` and `is_overdue` (rung 8's `hours_left` line stays as the body's SLA arithmetic); `make_ticket` builds every ticket dict; `PRIORITY_RANK` exists; the queue holds dicts and sorts by a `lambda` key on priority rank then `opened_at`; `array` is imported |
| 13 | w01d5 | 03_ticket_class | 35 | 12 | `Ticket` and `UrgentTicket` classes replace the dict record; every rule function takes a `Ticket`; `print(ticket)` is readable through `__repr__` |
| 14 | w01d5 | 04_desk_object | 35 | 13 | `Desk` owns the tickets, supports `len()` and `for`; `Desk.next_id` replaces the global counter; `main` holds rungs 10–13 merged and `ticket_desk.py` is the state week 2 rung 1 starts from |

## Per-day shape

### w01d2 — Orientation, Agile & Git fundamentals (Tue Oct 13, 2026)

- AM: setup check (10), Facilitation: What is Python, why Python (8), Facilitation: Professionalism at Revature (7), Demo 1 (01_tooling_check, 15 min; carries the Interpreter vs compiler recap and REPL and Jupyter), Facilitation: Full stack overview (7), Facilitation: SDLC and introduction to SDLC (15), Facilitation: Agile vs waterfall (15), break (15), Facilitation: Scrum ceremonies (20), Facilitation: Story pointing (20), lunch (45, as the live runbook records it).
- PM: Facilitation: Source control management (git, vcs, cvcs, dvcs) (10), Demo 2 (02_local_git_loop, 40 min), break (10), Demo 3 (03_remote_round_trip, 30 min), notes page handoff and 6-question check (15), exercise briefing (10; the Git exercise facilitation, rubric-marked), exercise (60), wrap-up (10). Total 362.
- Demo minutes: 85 (01_tooling_check 15, 02_local_git_loop 40, 03_remote_round_trip 30).
- Stop points: if the day runs long after Demo 1 Step 2 → shorten Step 1 instead, Step 3 stays (it is the `.gitignore` segue); after Demo 2 Step 4 → the conflict (Step 5) runs right after the break as the first minutes of Demo 3's slot; after Demo 3 Step 3 → Step 4's commit-message comparison moves into the exercise briefing and the real-GitHub push becomes a 2-minute trainer-only close.
- Cut first: Facilitation: Full stack overview down to two minutes, then the pair rounds in SDLC and Agile vs waterfall, then the morning break back to 10.
- Never cut: Demo 2 Step 5 (the conflict; the exercise marks it and rung 3 starts from this repo), Demo 3 Steps 1–3 (rung 3 starts from the `03_remote_round_trip` end state), the exercise briefing, the exercise below 45 minutes.

### w01d3 — Python basics (Wed Oct 14, 2026)

- AM: setup check (10; `python --version` 3.15 and a clean `git status` in `team-repo`, the state Tuesday left), framing (5; the page's first sentence: today assumes the tooling check passed and `team-repo` exists), Facilitation: PEP 8 as the team's contract (10; five rules on the board: names, blank lines, line length, imports first, comments say why), Demo 1 (01_ticket_record, 30 min; Python syntax, Comments, Variables and datatypes), break (15), Demo 2 (02_ticket_rules, 30 min; Operators), lunch (60).
- PM: Demo 3 (03_desk_intake, 35 min; User input and output; its `if sys.stdin.isatty():` guard is the day's only `if`, named as known from coursework with the talking point that Friday treats `if` as a design choice; then the merge into `main`), break (10), notes page handoff and 6-question check (15), exercise briefing (10; a pytest-checked module the trainee writes to PEP 8: a ticket summary line from given variables, with the operators and the f-string formats of the day), exercise (100), wrap-up (10). Total 340.
- Demo minutes: 95 (01_ticket_record 30, 02_ticket_rules 30, 03_desk_intake 35).
- Stop points: if the day runs long after Demo 1 Step 3 → the comment-deletion talking points move to the start of the PM before Demo 3, while the deletion itself is made from `01_ticket_record.py` before rung 3's commit; after Demo 2 Step 3 → `%`, `**` precedence and `round` move to Demo 3's first step; after Demo 3 Step 3 → the `sys.stderr` warning line's talking points move to Thursday's framing while the line itself is pasted from `03_desk_intake.py` before the rung's commit (the room's file equals the key); only the merge into `main` slides to Thursday's Demo 1 Step 1 (w01d4 01_ticket_text's row absorbs it before `git switch -c feature/data-types`).
- Cut first: Facilitation: PEP 8 as the team's contract (its five rules are repeated as talking points inside Demo 1), then the exercise from 100 to 80 minutes.
- Never cut: Demo 1 (rung 3; every later rung reads its variable names), Demo 2 (rung 4; rung 5 starts from it), Demo 3 Steps 1–2 (rung 5; Thursday's rungs start from the intake lines and `import sys`), the exercise briefing.

### w01d4 — Python data types (Thu Oct 15, 2026)

- AM: setup check (10; `python ticket_desk.py` runs from `main`, `git status` clean), framing (5; today assumes Wednesday's conventions and the intake lines; the page's first sentence says so), Demo 1 (01_ticket_text, 30 min; Strings, Casting, Boolean), Demo 2 (02_ticket_queue, 35 min; Lists, Tuples, Range, Sets), break (15), Demo 3 (03_ticket_dict, 35 min; Binary types, NoneType, Dictionaries), lunch (60).
- PM: Demo 4 (04_ticket_clock, 30 min; Numbers, Datetime, Namespaces, then the merge into `main`; the notes page puts Numbers and Datetime together on step 6 because the float pitfalls appear in the same `hours_open` computation as the clock), break (10), notes page handoff and 6-question check (15), exercise briefing (10; a pytest-checked module: normalise a ticket title, build the queue as tuples, look up SLA hours from a dict, compute a deadline with `timedelta`), exercise (90), wrap-up (10). Total 355.
- Demo minutes: 130 (01_ticket_text 30, 02_ticket_queue 35, 03_ticket_dict 35, 04_ticket_clock 30).
- Stop points: if the day runs long after Demo 1 Step 2 → the Boolean truthiness step moves to the start of Demo 2; after Demo 2 Step 3 → the Sets step moves to the start of Demo 3 before Binary types; after Demo 3 Step 3 → `tickets_by_id` moves to Demo 4 Step 1; after Demo 4 Step 2 → the Namespaces talking points (`dir()`, `__name__`, the shadowing pitfall) move to Friday's framing as a five-minute opener while the step's kept lines (`del backup`, the `__name__` print) are pasted from `04_ticket_clock.py` before the rung's commit; only the merge into `main` slides to Friday's Demo 1 Step 1 (w01d5 01_desk_control_flow's row absorbs it).
- Cut first: the transient lines of Demo 3's Binary types step (`len("café")` against `len("café".encode())`, the `bytes + str` TypeError), keeping the two kept lines `raw = title.encode("utf-8")` and `raw.decode()` so the room's file still equals `03_ticket_dict.py`; then the exercise from 90 to 75 minutes.
- Never cut: Demo 1 (rung 6), Demo 2 (rung 7), Demo 3's kept lines (rung 8; `SLA_HOURS` and the ticket dict are what Friday's functions and class replace; only its Binary types transient lines may go), Demo 4 Steps 1–2 (rung 9; `NOW`, `opened_at` and `deadline` feed Friday's `if` and `deadline_for`), the exercise briefing.

### w01d5 — Control flow, functions & classes (Fri Oct 16, 2026)

- AM: setup check (10; `python ticket_desk.py` runs from `main`, prints the dated board), framing (5; today assumes Thursday's dict, queue and clock; the page's first sentence says so), Demo 1 (01_desk_control_flow, 35 min; If-else, While loops, For loops), break (15), Demo 2 (02_desk_functions, 35 min; Functions, Lambda, Arrays), Demo 3 (03_ticket_class, 35 min; OOP concepts, Inheritance), lunch (60).
- PM: Demo 4 (04_desk_object, 35 min; Iterators, Scope, Classes and objects, then the merge into `main`), break (10), notes page handoff and 6-question check (15), exercise briefing (10; a pytest-checked module: a `Ticket` class with a deadline method, a `Desk` that iterates, a sort by lambda key, a guard clause), exercise (80), wrap-up (10), weekly feedback form (10). Total 365.
- Demo minutes: 140 (01_desk_control_flow 35, 02_desk_functions 35, 03_ticket_class 35, 04_desk_object 35).
- Stop points: if the day runs long after Demo 1 Step 2 → the `while` intake loop moves to the start of Demo 2; after Demo 2 Step 3 → the `array` cameo's talking points move into the notes page handoff and its three lines are pasted from `02_desk_functions.py` so the room's file still equals the key; after Demo 3 Step 2 → `UrgentTicket` moves to Demo 4 Step 1; after Demo 4 Step 3 → the LEGB `label()` talking points move to the notes page handoff while its four kept lines are pasted from `04_desk_object.py` before the rung's commit, and the merge into `main` happens in the wrap-up; nothing lands on Monday of week 2 (week 2 rung 1 starts from `04_desk_object.py` as committed).
- Cut first: the exercise from 80 to 60 minutes, then the wrap-up to 5 minutes, then the talking points (never the lines) of Demo 4 Step 3's `iter()`/`next()` manual stepping, whose lines are transient (`StopIteration` shown then deleted) so the end state is unchanged. No kept line of rungs 10–13 is cut: every one is carried into the key week 2 starts from.
- Never cut: Demo 1 (rung 10), Demo 2 (rung 11), Demo 3 (rung 12), Demo 4 Steps 1–2 (rung 13; `Desk` is the end state week 2 starts from), the exercise briefing, the weekly feedback form.

## Anti-spoiler ledger

| Day | Defers | To | Why |
|---|---|---|---|
| w01d2 | Python syntax, conventions and any `.py` beyond the five-line `hello.py` | w01d3 | the day note: at most one on-ramp demo; the day is about how teams work |
| w01d2 | pytest and starter modules (the Git exercise is rubric-marked) | week 2 | the day note forbids pytest; testing is week 2 day 3 |
| w01d2 | rebase, `--amend`, `restore`, `reset`, `revert`, force-push | week 2 | the scripts name them only as "the other option"; the only escape hatch this week is `git merge --abort` |
| w01d3 | casting typed text to numbers (`int(input(...))`); intake stays `title` and `priority` strings | w01d4 | Casting is a Thursday subtopic; Wednesday's I/O lesson is prompt, `print` options and f-string formats |
| w01d3 | lists, tuples, sets, dicts, `None` (the ticket stays flat variables and three `SLA_HOURS_*` constants) | w01d4 | Thursday goes deep on data types through idioms; Wednesday is conventions |
| w01d3 | string methods (`.strip()`, `.lower()`, slicing on `title` and `priority`; Wednesday's intake uses the text as typed) | w01d4 | Strings is a Thursday subtopic; rung 6 normalises the same two variables |
| w01d3 | `if` as a lesson, loops, functions (the intake guard is one plain `if sys.stdin.isatty():` named as known from coursework; repeated prints stay repeated) | w01d5 | control flow and functions are Friday's design choices; Friday's rung 10 adds the `while` re-ask inside the same guard |
| w01d3 | `datetime`; `hours_open` is a literal float | w01d4 | Datetime is a Thursday subtopic; the literal keeps Wednesday's operators lesson arithmetic-only |
| w01d4 | `for` over the queue, `if` on ticket state (every record is printed by its own `print`; the breach flag stays a boolean expression) | w01d5 | loops and branching as design choices are Friday; Thursday shows the data and leaves the control flow to Friday |
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
| one `ticket_desk.py` file holds the whole desk | a package (`tickets/`, `sla/`, `cli/`) with tests | single-file keys keep the typed-live contract checkable; week 2 day 1 does the split |
| tickets live in Python variables, then tuples, then a dict, then objects in memory | a database table; nothing survives the process exit | the data-type ladder is the lesson; week 3 moves the same records into MySQL |
| the "customer" is the trainer at `input()` and a sample ticket when no terminal is attached (`sys.stdin.isatty()`) | a web form, email intake or an API; argparse for a CLI | `input()` is the Wednesday subtopic; the guard lets the committed file run unattended for the critic and CI |
| `NOW` is a pinned `datetime(2026, 10, 15, 14, 0)` | `datetime.now(tz=...)` at call time | a pinned clock makes the key's output stable and the breach flag predictable in class; Friday's `is_overdue(ticket, now=NOW)` takes the clock as an argument so the pin is one line to change |
| SLA hours are a dict literal in the file | a configuration table or file, per customer tier | the lookup-table idiom is the Thursday lesson; week 2 reads it from JSON |
| ticket ids come from `range` and then a class attribute counter | the database assigns ids | id generation is a scope lesson (global versus class attribute) on Friday |
| commits land on one feature branch per day merged by the trainer | a pull request reviewed by a teammate before merge | PR review is a notes-page topic this week; the demo budget goes to Python, and the Tuesday exercise already marks the branch workflow |
| no tests on the thread this week | every rule has a pytest test before merge | pytest is week 2 day 3; the exercises run pytest so the room meets the tool before it is taught |
| hard-coded sample tickets ("Printer on floor 3 jams") | records from real intake | fixed data keeps every rung's expected output printable in the script's Check blocks |
| `hello.py` and `README.md` from Tuesday stay in `team-repo` untouched | a repo holds one project | they are the Git history the room built; deleting them would spend typed lines on nothing |
| the `array` module cameo is three lines | numpy arrays for numeric work | the curriculum lists Arrays on Friday; numpy is week 2 day 3 |
| `UrgentTicket` halves the SLA by overriding one method | a real desk keeps priority as data on the record and never subclasses for it | one subclass with `super()` is the smallest honest inheritance example; the notes page says when a subclass is the wrong tool |

## Coverage map

| Subtopic | Day | Demo | Notes step |
|---|---|---|---|
| What is Python, why Python | w01d2 | facilitation | 1 |
| Professionalism at Revature | w01d2 | facilitation | 1 |
| Python orientation (tooling check) | w01d2 | 01_tooling_check | 1 |
| Interpreter vs compiler | w01d2 | 01_tooling_check | 1 |
| REPL and Jupyter | w01d2 | 01_tooling_check | 1 |
| Full stack overview | w01d2 | facilitation | 1 |
| SDLC and introduction to SDLC | w01d2 | facilitation | 2 |
| Agile vs waterfall | w01d2 | facilitation | 2 |
| Scrum ceremonies | w01d2 | facilitation | 3 |
| Story pointing | w01d2 | facilitation | 4 |
| Source control management (git, vcs, cvcs, dvcs) | w01d2 | facilitation | 5 |
| Git fundamentals | w01d2 | 02_local_git_loop | 5 |
| Initializing a repository | w01d2 | 02_local_git_loop | 5 |
| Commit, branch, merge, push, pull | w01d2 | 02_local_git_loop | 6 |
| Pushing to a remote repository | w01d2 | 03_remote_round_trip | 7 |
| Git exercise | w01d2 | facilitation | 8 |
| Python syntax | w01d3 | 01_ticket_record | 1 |
| Comments | w01d3 | 01_ticket_record | 2 |
| Variables and datatypes | w01d3 | 01_ticket_record | 3 |
| Operators | w01d3 | 02_ticket_rules | 4 |
| User input and output | w01d3 | 03_desk_intake | 5 |
| Strings | w01d4 | 01_ticket_text | 1 |
| Casting | w01d4 | 01_ticket_text | 2 |
| Boolean | w01d4 | 01_ticket_text | 2 |
| Lists | w01d4 | 02_ticket_queue | 3 |
| Tuples | w01d4 | 02_ticket_queue | 3 |
| Range | w01d4 | 02_ticket_queue | 3 |
| Sets | w01d4 | 02_ticket_queue | 4 |
| Binary types | w01d4 | 03_ticket_dict | 4 |
| NoneType | w01d4 | 03_ticket_dict | 5 |
| Dictionaries | w01d4 | 03_ticket_dict | 5 |
| Numbers | w01d4 | 04_ticket_clock | 6 |
| Datetime | w01d4 | 04_ticket_clock | 6 |
| Namespaces | w01d4 | 04_ticket_clock | 7 |
| If-else | w01d5 | 01_desk_control_flow | 1 |
| While loops | w01d5 | 01_desk_control_flow | 2 |
| For loops | w01d5 | 01_desk_control_flow | 2 |
| Functions | w01d5 | 02_desk_functions | 3 |
| Lambda | w01d5 | 02_desk_functions | 4 |
| Arrays | w01d5 | 02_desk_functions | 5 |
| OOP concepts | w01d5 | 03_ticket_class | 6 |
| Inheritance | w01d5 | 03_ticket_class | 7 |
| Iterators | w01d5 | 04_desk_object | 8 |
| Scope | w01d5 | 04_desk_object | 9 |
| Classes and objects | w01d5 | 04_desk_object | 6 |
