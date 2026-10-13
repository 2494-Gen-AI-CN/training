# w01d2 — Orientation, Agile & Git fundamentals

gate: light
verified: 2026-10-13
week: 1 · Agile for developers, Git & Python fundamentals
day: 2 · day-2-orientation-agile-and-git

version-stamps:
  - python: 3.12 (verified 2026-10-13)
  - git: 2.50 (verified 2026-10-13)   # any 2.28+ works (init.defaultBranch); 2.23+ needed for `git switch`; the git demos are typed live in the terminal (D-0030: script + transcript answer key), no Python wrapper
  - git (trainer marking only): 2.52 (verified 2026-10-13)   # the rubric's expected outputs were produced on 2.52; its AC5 arbiter `git merge-tree --write-tree` needs 2.38+ on the trainer machine, trainees need nothing newer than 2.28
  - notebook: 7.x (verified 2026-10-13)   # Jupyter Notebook, opened once in the on-ramp tooling check; not imported by demos

## Claims (each MUST carry a source on a full gate; light gate: source optional but recommended)

- Python is "interpreted" in the everyday sense: `python hello.py` runs the source directly with no separate build step producing an executable; under the hood CPython compiles each module to bytecode first and caches it in `__pycache__/*.pyc`, which is why that folder appears after the first import and why it belongs in `.gitignore` — [Python glossary: interpreted, bytecode](https://docs.python.org/3/glossary.html#term-interpreted)
- The General Python FAQ describes Python as a general-purpose language and points at the standard library's coverage of string processing, internet protocols, software-engineering tools and operating-system interfaces; python.org's "Applications for Python" page lists the main uses as Web and Internet Development, Scientific and Numeric, Software Development, Business Applications, Education and Desktop GUIs; in a full-stack picture (browser front end, server back end, database, infrastructure) Python's seat in this course is the back end and the data/ML layer — [General Python FAQ: What is Python good for?](https://docs.python.org/3/faq/general.html#what-is-python-good-for) and [Applications for Python](https://www.python.org/about/apps/)
- "Professionalism at Revature" (first 10 minutes of the on-ramp) is Revature-internal material: expectations about attendance, communication, written updates and conduct during training; there is no external source for it and the notes author must not invent a citation; present it as house rules, not as a sourced claim
- Running `python` with no arguments starts the interactive interpreter (REPL) with the `>>>` prompt; `python -i script.py` runs the script and then drops into the REPL with the script's names still defined; you leave with `exit()` or `quit()`, Ctrl-Z then Enter on Windows, Ctrl-D elsewhere — [Using the Python Interpreter](https://docs.python.org/3/tutorial/interpreter.html)
- In interactive mode the value of the last printed expression is kept in the read-only name `_` — [An Informal Introduction to Python](https://docs.python.org/3/tutorial/introduction.html)
- On Windows the `py` launcher ships with the python.org installer and `py -3.12` selects a specific version; `py --version` or `python --version` is the one-line tooling check that proves the shell will run the interpreter you think it will — [Python Launcher for Windows](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)
- A Jupyter Notebook is a document of code and Markdown cells; each code cell is sent to a running kernel and its output appears underneath, so a notebook is a REPL with a memory of every cell executed, in execution order rather than top-to-bottom order — [Jupyter documentation](https://docs.jupyter.org/en/latest/)
- The software development life cycle (SDLC) is the sequence of phases every piece of software passes through regardless of methodology: requirements/planning, design, implementation, testing, deployment and maintenance; methodologies differ in whether those phases happen once in order (waterfall) or repeat in short cycles (Agile); Scrum is founded on empiricism (transparency, inspection, adaptation) and runs all the phases inside every Sprint — [The 2020 Scrum Guide: Scrum Theory](https://scrumguides.org/scrum-guide.html)
- Waterfall is the sequential model: each phase is completed and signed off before the next begins, requirements are frozen early and working software appears only at the end; the Agile principles instead call for delivering working software frequently, "from a couple of weeks to a couple of months", and welcoming changing requirements even late in development — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)
- The Agile Manifesto (2001) values individuals and interactions over processes and tools, working software over comprehensive documentation, customer collaboration over contract negotiation, and responding to change over following a plan, while still valuing the items on the right — [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- Scrum defines three accountabilities (Product Owner, Scrum Master, Developers), five events (the Sprint, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective) and three artifacts (Product Backlog, Sprint Backlog, Increment) — [The 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html)
- A Sprint is a fixed-length event of one month or less; the Daily Scrum is time-boxed to 15 minutes; for a one-month Sprint, Sprint Planning is capped at eight hours, the Sprint Review at four hours and the Retrospective at three hours, with shorter caps for shorter Sprints — [The 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html)
- The Scrum Guide says the Developers who will do the work are responsible for sizing Product Backlog items, and that their past performance, upcoming capacity and Definition of Done inform their Sprint forecasts; it never mentions story points, velocity or hours — [The 2020 Scrum Guide: Product Backlog](https://scrumguides.org/scrum-guide.html). Story pointing (relative effort sizes on a Fibonacci-like scale 1, 2, 3, 5, 8, 13, agreed by comparing items) and velocity (points completed per Sprint, meaningful only within one team) are practices layered on Scrum, not Guide content, so a page states them without a Scrum Guide citation.
- Version control systems come in three generations: local (RCS), centralised (CVS, Subversion: one server holds the history, clients check out a working copy) and distributed (Git, Mercurial: every clone mirrors the full repository, so `log`, `diff`, `commit` and `branch` work offline and only `push`/`pull`/`fetch` touch the network) — [Pro Git: About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
- Git stores each commit as a snapshot of the whole tree (unchanged files are stored as links to the previous identical file), not as a list of per-file diffs; a file is in one of three states (modified, staged, committed) matching three areas (working tree, staging area/index, .git directory), and `git status` reports which — [Pro Git: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)
- `git init` creates a `.git` subdirectory in the current folder and nothing is tracked until you `git add` it; `git add` both starts tracking new files and stages modified ones — [Pro Git: Getting a Git Repository](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository)
- Git guesses an author identity from the OS username and hostname; when it cannot (the usual case on Windows) the first commit fails with "Author identity unknown ... Please tell me who you are" until `git config --global user.name` and `user.email` are set; `init.defaultBranch` (Git 2.28+) names the initial branch, defaulting to `master` unless set to `main` — [git-config documentation](https://git-scm.com/docs/git-config)
- `git commit -m "message"` records the staged snapshot; `git commit` without `-m` opens the configured editor; `git log --oneline` lists one commit per line and is the quickest way to read a branch's story — [Pro Git: Recording Changes](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository)
- A good commit message is a short summary line (about 50 characters, imperative mood: "Add login form", not "Added" or "fix"), a blank line, then a body explaining what and why rather than how; the git-commit documentation and Pro Git's contribution guidelines both describe this shape and note that tools such as `git log --oneline` and `git shortlog` show only the first line — [git-commit documentation: Discussion](https://git-scm.com/docs/git-commit#_discussion) and [Pro Git: Contributing to a Project, Commit Guidelines](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project)
- A `.gitignore` file lists patterns Git should not track; for Python projects that means at least `__pycache__/`, `*.pyc` and `.venv/`, and a pattern added after a file was already committed does not untrack it — [gitignore documentation](https://git-scm.com/docs/gitignore)
- `git branch <name>` creates a branch but does not switch to it; `git switch <name>` (Git 2.23+) or `git checkout <name>` moves HEAD, and `git switch -c <name>` creates and switches in one step — [git-switch documentation](https://git-scm.com/docs/git-switch)
- A merge is a fast-forward when the target branch has no new commits since the feature branch diverged, so Git simply moves the pointer; otherwise Git creates a merge commit with two parents, and when both sides changed the same lines it stops with conflict markers `<<<<<<<`, `=======`, `>>>>>>>` for you to edit, `git add` and `git commit`; `git merge --abort` backs out entirely — [Pro Git: Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
- `git remote add origin <url>` names a remote; `git push -u origin main` uploads the branch and sets its upstream so later `git push` and `git pull` need no arguments; `git remote -v` shows what is configured — [Pro Git: Working with Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes)
- `git pull` is `git fetch` followed by `git merge` of the tracked upstream branch (or a rebase when `pull.rebase` is set); `git fetch` alone downloads new history without changing the working tree — [git-pull documentation](https://git-scm.com/docs/git-pull)
- When the local branch and its upstream have diverged (a local commit made before pulling a remote one) and neither `pull.rebase` nor a `--rebase`, `--no-rebase` or `--ff-only` flag says how to reconcile them, recent Git (2.33.1 and later) refuses with "Need to specify how to reconcile divergent branches"; versions 2.27 to 2.33.0 printed the same text as a warning and merged anyway — [git-pull documentation](https://git-scm.com/docs/git-pull) and [Git 2.33.1 release notes](https://github.com/git/git/blob/master/Documentation/RelNotes/2.33.1.adoc)
- `git merge-tree --write-tree <branch1> <branch2>` (Git 2.38+) performs a real merge of two commits in memory without touching the working tree or index, prints the resulting tree and exits 1 with `CONFLICT (content)` lines when the two sides genuinely conflict; the marking guide uses it to prove a trainee's merge parents collided — [git-merge-tree documentation](https://git-scm.com/docs/git-merge-tree)
- GitHub remotes can be addressed over HTTPS or SSH; HTTPS pushes authenticate with a personal access token or a credential helper (Git Credential Manager, bundled with Git for Windows, opens a browser sign-in on first push), never with the account password — [GitHub Docs: About remote repositories](https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories)
- On Windows 10/11, a `python` command that opens the Microsoft Store is the App execution alias stub; its resolved path contains `WindowsApps` (`where.exe python` or `sys.executable` shows it), which is the tell on a trainee's screen — [Python on Windows: Microsoft Store package and the py launcher](https://docs.python.org/3/using/windows.html)
- The Store stub is turned off in Windows Settings under Apps > Advanced app settings > App execution aliases (the two `python` / `python3` entries); using `py` sidesteps it without changing settings — [Python on Windows: Python Launcher for Windows](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)
- `git commit --amend --reset-author` rewrites the most recent commit with the author set from the current `user.name` / `user.email` config; it only repairs the tip, so commits made earlier with a wrong identity are either left and noted or require an interactive rebase, which is not on today's syllabus — [git-commit reference: --reset-author](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---reset-author)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### What is Python, why Python
- Interview questions: What kind of language is Python (typing, memory management, paradigms)?; Why would a team pick Python for a back-end service or a data task?; Follow-up: what does the global interpreter lock limit, and what is the usual way around it?
- Adjacent concept: CPython versus other implementations — an interviewer asks which Python you actually run, and the answer is the reference implementation.
- Trade-off or limit: CPython's global interpreter lock lets only one thread execute Python bytecode at a time, so CPU-bound threads do not run in parallel — [Python glossary: global interpreter lock](https://docs.python.org/3/glossary.html#term-global-interpreter-lock)
- Recognise on sight: the `#!/usr/bin/env python3` first line, or `if __name__ == "__main__":` at the bottom of a script (named only; its mechanics are Wednesday's).
- Claims:
  - The General Python FAQ describes Python as an interpreted, interactive, object-oriented language that incorporates modules, exceptions, dynamic typing, very high level dynamic data types and classes — [General Python FAQ: What is Python?](https://docs.python.org/3/faq/general.html#what-is-python)
  - Python frees memory that is no longer used by garbage collection, through reference counting plus a cyclic garbage collector that detects and breaks reference cycles, so the programmer does not free memory by hand — [Python glossary: garbage collection](https://docs.python.org/3/glossary.html#term-garbage-collection)
  - CPython is the reference implementation, the one distributed on python.org and the one this course runs — [Python glossary: CPython](https://docs.python.org/3/glossary.html#term-CPython)
  - "Readability counts" and "There should be one-- and preferably only one --obvious way to do it" are lines of the Zen of Python — [PEP 20 – The Zen of Python](https://peps.python.org/pep-0020/)
  - The standard library covers string processing, internet protocols, software-engineering tools and operating-system interfaces, which is the usual "batteries included" argument — [General Python FAQ: What is Python good for?](https://docs.python.org/3/faq/general.html#what-is-python-good-for)
  - Python 3.12 is the version this course pins; each release's changes are catalogued in its "What's New" page — [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)

### Professionalism at Revature
- Interview questions: How do you communicate a blocker to your team?; Why do written updates matter on a distributed team?; Follow-up: how do you disagree with a teammate's approach without stalling the Sprint?
- Adjacent concept: the working agreement — teams write down their norms (core hours, response times, definition of done) so expectations are not guessed.
- Trade-off or limit: the Agile principles name face-to-face conversation as the most efficient and effective way to convey information to and within a development team, but a spoken update reaches only the people present and leaves no record, so distributed teams pair short synchronous meetings with written updates — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)
- Recognise on sight: a team wiki page titled "Working agreement" or "Team norms"; a daily written status update in a standard shape (done, doing, blocked).
- Claims:
  - The Agile principles say that at regular intervals the team reflects on how to become more effective, then tunes and adjusts its behavior accordingly — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)
  - The Agile principles say business people and developers must work together daily throughout the project — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)
  - Scrum rests on transparency, so progress and problems are made visible rather than reported late — [The 2020 Scrum Guide: Scrum Theory](https://scrumguides.org/scrum-guide.html)
  - The Agile Manifesto values individuals and interactions over processes and tools — [Manifesto for Agile Software Development](https://agilemanifesto.org/)

### Python orientation (tooling check)
- Interview questions: How do you check which Python version and which interpreter a shell will run?; How do you tell the shell prompt, the `>>>` REPL and a running script apart?; Follow-up: two Pythons are installed and `python` runs the wrong one; how do you find out which one runs and fix it?
- Adjacent concept: PATH resolution — the shell runs the first `python` it finds on PATH, so `where.exe python` lists the candidates in search order, `py -0p` lists every installed interpreter with its path, and `sys.executable` names the one actually running.
- Trade-off or limit: the bare `python` command runs whichever interpreter comes first on PATH, while the Windows `py` launcher locates installed versions itself and, unlike PATH, selects the most appropriate one; the cost is that `py` exists only on Windows, so instructions shared with macOS or Linux teammates still name `python` or `python3` — [Python on Windows: Python Launcher for Windows](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)
- Recognise on sight: `where.exe python` printing two paths with the first under `WindowsApps`; `py -0p` listing `-V:3.12 *` beside a full path; `import sys; sys.executable` typed at the `>>>` prompt.
- Claims:
  - `python --version` (or `-V`) prints the Python version number and exits — [Command line and environment](https://docs.python.org/3/using/cmdline.html)
  - `sys.executable` is a string giving the absolute path of the executable binary for the running interpreter — [sys.executable](https://docs.python.org/3/library/sys.html#sys.executable)
  - The `py` launcher on Windows selects an installed version with `py -3.12` — [Python Launcher for Windows](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)
  - `py --list-paths` (short form `py -0p`) lists the installed Python versions the launcher can find, with the path of each — [Python Launcher for Windows](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)
  - On Windows the Microsoft Store `python` stub is an app execution alias that appears in WindowsApps paths — [Using Python on Windows](https://docs.python.org/3/using/windows.html)

### Interpreter vs compiler
- Interview questions: What is the difference between a compiler and an interpreter?; Is Python compiled or interpreted?; Follow-up: what is in a `.pyc` file and when does Python refuse to reuse it?
- Adjacent concept: a virtual machine executing bytecode — the same shape as the JVM, which the interviewer often uses as the comparison.
- Trade-off or limit: running bytecode on a virtual machine is slower than native machine code, which is why CPython 3.11 added a specializing interpreter to narrow the gap, reporting 10-60% faster runs than 3.10 — [What's New In Python 3.11](https://docs.python.org/3/whatsnew/3.11.html)
- Recognise on sight: a `__pycache__/` folder holding `hello.cpython-312.pyc` once `hello` has been imported (running `python hello.py` alone writes none); a `SyntaxError` reported before any line of the script runs.
- Claims:
  - CPython compiles source to bytecode and executes that bytecode on a virtual machine; the glossary defines bytecode as the internal representation of a program — [Python glossary: bytecode](https://docs.python.org/3/glossary.html#term-bytecode)
  - Cached bytecode lives in `__pycache__` with the interpreter version in the filename (for example `cpython-312`) so several versions can share one source tree — [PEP 3147 – PyCache](https://peps.python.org/pep-3147/)
  - The `dis` module disassembles functions into their bytecode instructions — [dis module](https://docs.python.org/3/library/dis.html)
  - Python always recompiles the module loaded directly from the command line and does not store the result, so only imported modules are cached as `.pyc` — [Modules: "Compiled" Python files](https://docs.python.org/3/tutorial/modules.html#compiled-python-files)
  - The built-in `compile()` turns source into a code object and raises `SyntaxError` if the source is invalid — [Built-in Functions: compile](https://docs.python.org/3/library/functions.html#compile)

### REPL and Jupyter
- Interview questions: What is a REPL and when do you reach for one?; What is a Jupyter notebook made of?; Follow-up: why can a notebook give different results after "Restart and Run All" than before?
- Adjacent concept: kernels — the process that holds a notebook's state, separate from the browser tab that displays it.
- Trade-off or limit: a notebook's state lives in its kernel and follows execution order (the `In [n]` counter), not the order of cells on the page, so out-of-order runs leave hidden state that a script run top to bottom would not have — [Jupyter Notebook documentation: The Jupyter Notebook](https://jupyter-notebook.readthedocs.io/en/stable/notebook.html)
- Recognise on sight: the `>>>` and `...` prompts; `In [3]:` execution counters; a `.ipynb` file in a repository.
- Claims:
  - Running `python` with no arguments starts the interactive interpreter, and `exit()` leaves it — [Using the Python Interpreter](https://docs.python.org/3/tutorial/interpreter.html)
  - In interactive mode the last printed value is bound to `_` — [An Informal Introduction to Python](https://docs.python.org/3/tutorial/introduction.html)
  - `python -i script.py` runs the script and then leaves the REPL open with its names defined — [Command line and environment](https://docs.python.org/3/using/cmdline.html)
  - A notebook file is a JSON document of cells, and its format is specified by nbformat — [nbformat documentation](https://nbformat.readthedocs.io/en/latest/)
  - Each code cell is sent to a kernel and its output appears beneath the cell — [Jupyter documentation](https://docs.jupyter.org/en/latest/)

### Full stack overview
- Interview questions: What are the layers of a web application?; What does a back end do that a front end cannot?; Follow-up: a page is slow; how would you decide whether the browser, the server or the database is at fault?
- Adjacent concept: HTTP as a request and response protocol — every layer in the stack is described by what it sends and receives.
- Trade-off or limit: the standard library's `http.server` is enough to see a back end answer a request, but it is not recommended for production because it implements only basic security checks; real back ends run behind a production web server or framework — [http.server — HTTP servers](https://docs.python.org/3/library/http.server.html)
- Recognise on sight: a repository with `frontend/`, `backend/` and a `docker-compose.yml`; a URL that returns JSON instead of HTML.
- Claims:
  - HTTP is a stateless, application-level request/response protocol: a client sends a request and a server returns a response — [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
  - python.org lists web and internet development, scientific and numeric computing, software development, business applications, education and desktop GUIs as main uses — [Applications for Python](https://www.python.org/about/apps/)
  - The standard library ships `sqlite3`, a DB-API interface to the SQLite database engine — [sqlite3 module](https://docs.python.org/3/library/sqlite3.html)
  - The standard library includes internet-protocol support, so a Python process can act as a server or a client — [General Python FAQ](https://docs.python.org/3/faq/general.html#what-is-python-good-for)

### SDLC and introduction to SDLC
- Interview questions: Name the phases of the software development life cycle; Where does testing happen in Scrum?; Follow-up: what happens to the phases when a team releases every two weeks instead of every year?
- Adjacent concept: definition of done — the agreed checklist that decides when an item has passed through every phase.
- Trade-off or limit: the Scrum Guide describes a framework that is "purposefully incomplete", so phases such as design and deployment practice are left to each team to define — [The 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html)
- Recognise on sight: a board with columns To Do, In Progress, Review, Done; a pipeline file that builds and tests on every push.
- Claims:
  - All the work necessary to achieve the Product Goal, including Sprint Planning, Daily Scrums, Sprint Review and Sprint Retrospective, happens within Sprints, so a Scrum team runs every SDLC phase inside each Sprint rather than once per project — [The 2020 Scrum Guide: The Sprint](https://scrumguides.org/scrum-guide.html)
  - The Definition of Done is a formal description of the state of the Increment when it meets the quality measures required for the product — [The 2020 Scrum Guide: Increment](https://scrumguides.org/scrum-guide.html)
  - In Scrum each Increment is additive to all prior Increments and thoroughly verified, so testing happens inside the Sprint — [The 2020 Scrum Guide: Increment](https://scrumguides.org/scrum-guide.html)
  - The Agile principles call for continuous attention to technical excellence and good design — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)

### Agile vs waterfall
- Interview questions: What is the difference between Agile and waterfall?; Name two values from the Agile Manifesto; Follow-up: when might a waterfall-like plan still be the right choice?
- Adjacent concept: feedback loops — the shorter the cycle between building and a customer seeing it, the cheaper a wrong assumption is.
- Trade-off or limit: the Manifesto says there is value in the items on the right (processes, documentation, contracts, plans), only that the left items are valued more, so Agile does not mean "no documentation" — [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- Recognise on sight: a Gantt chart with phases in sequence (waterfall) versus a Sprint board with a burndown (Agile).
- Claims:
  - The Agile Manifesto was written in 2001 and has four value statements — [Manifesto for Agile Software Development](https://agilemanifesto.org/)
  - Agile principles deliver working software frequently, from a couple of weeks to a couple of months, with a preference for the shorter timescale — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)
  - Agile processes welcome changing requirements, even late in development — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)
  - Working software is the primary measure of progress — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)
  - The Scrum Guide defines Scrum as a lightweight framework founded on empiricism and lean thinking, and never calls itself the definition of Agile — [The 2020 Scrum Guide: Scrum Definition](https://scrumguides.org/scrum-guide.html)

### Scrum ceremonies
- Interview questions: Name the Scrum events and who attends each; What is a Sprint Goal?; Follow-up: what is the difference between a Sprint Review and a Sprint Retrospective?
- Adjacent concept: the three artifacts and their commitments (Product Backlog with the Product Goal, Sprint Backlog with the Sprint Goal, Increment with the Definition of Done).
- Trade-off or limit: the Scrum Team is typically 10 or fewer people, small enough to stay nimble, because the guide notes that smaller teams communicate better and are more productive; a larger group is expected to reorganise into several cohesive Scrum Teams focused on the same product — [The 2020 Scrum Guide: Scrum Team](https://scrumguides.org/scrum-guide.html)
- Recognise on sight: "What did I do yesterday, what will I do today, any blockers?" at a stand-up; a retrospective board with Start, Stop, Continue columns.
- Claims:
  - Scrum has three accountabilities (Product Owner, Scrum Master, Developers) and five events (Sprint, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective) — [The 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html)
  - A Sprint is one month or less, and a new Sprint starts immediately after the previous one ends — [The 2020 Scrum Guide: The Sprint](https://scrumguides.org/scrum-guide.html)
  - Sprint Planning addresses why the Sprint is valuable, what can be done and how the chosen work will get done — [The 2020 Scrum Guide: Sprint Planning](https://scrumguides.org/scrum-guide.html)
  - The Daily Scrum is 15 minutes and the Developers choose its structure and techniques — [The 2020 Scrum Guide: Daily Scrum](https://scrumguides.org/scrum-guide.html)
  - The Sprint Review inspects the outcome with stakeholders, while the Retrospective plans ways to increase quality and effectiveness of the team itself — [The 2020 Scrum Guide: Sprint Retrospective](https://scrumguides.org/scrum-guide.html)
  - Only the Product Owner can cancel a Sprint — [The 2020 Scrum Guide: The Sprint](https://scrumguides.org/scrum-guide.html)

### Story pointing
- Interview questions: What is a story point?; How does a team estimate with planning poker?; Follow-up: why is comparing velocity between two teams misleading?
- Adjacent concept: backlog refinement — estimates are added as items are broken down, before Sprint Planning needs them.
- Trade-off or limit: the Scrum Guide gives no estimation unit; points are a team convention, so one team's 5 is not another team's 5 and neither equals hours — [The 2020 Scrum Guide: Product Backlog](https://scrumguides.org/scrum-guide.html)
- Recognise on sight: cards or buttons showing 1, 2, 3, 5, 8, 13; a Jira or board ticket with a "Story Points" field; a team velocity chart.
- Claims:
  - The Developers who will do the work are responsible for sizing Product Backlog items — [The 2020 Scrum Guide: Product Backlog](https://scrumguides.org/scrum-guide.html)
  - Product Backlog refinement adds detail such as description, order and size to items — [The 2020 Scrum Guide: Product Backlog](https://scrumguides.org/scrum-guide.html)
  - The Scrum Guide does not mention story points, planning poker or velocity; they are practices layered on top — [The 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html)
  - The Sprint Backlog is the Sprint Goal, the selected Product Backlog items and a plan for delivering them — [The 2020 Scrum Guide: Sprint Backlog](https://scrumguides.org/scrum-guide.html)
  - The more the Developers know about their past performance, their upcoming capacity and their Definition of Done, the more confident they will be in their Sprint forecasts — [The 2020 Scrum Guide: Sprint Planning](https://scrumguides.org/scrum-guide.html)

### Source control management (git, vcs, cvcs, dvcs)
- Interview questions: What problems does version control solve?; What is the difference between centralised and distributed version control?; Follow-up: if every clone has the full history, what does the "central" GitHub repository actually do?
- Adjacent concept: Git versus GitHub — Git is the tool, GitHub is one hosting service for remotes.
- Trade-off or limit: a centralised VCS is a single point of failure: if the server goes down nobody can collaborate or save versioned changes, and if the central disk is lost without backups the whole history goes with it; a DVCS removes that because every clone is a full backup of the repository — [Pro Git: About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
- Recognise on sight: a `.git` folder in a project root; `svn checkout` (centralised) versus `git clone` (distributed) in a README.
- Claims:
  - Local, centralised and distributed are the three generations of version control systems — [Pro Git: About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
  - In a distributed system clients fully mirror the repository including its history, so any clone can restore a lost server — [Pro Git: About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
  - Git stores snapshots rather than per-file differences — [Pro Git: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)
  - Most Git operations need only local files and resources, so commits and logs work offline — [Pro Git: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)
  - GitHub hosts Git repositories as remotes reachable over HTTPS or SSH — [GitHub Docs: About remote repositories](https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories)

### Git fundamentals
- Interview questions: What are the three areas in Git and what moves a change between them?; What does a commit contain?; Follow-up: why does `git diff` show nothing after `git add`, and which command shows the staged change?
- Adjacent concept: HEAD — the pointer to the commit or branch you are on, which `git log` and `git status` both report from.
- Trade-off or limit: `git commit -a` skips the staging area by staging every change to a file that is already tracked, which saves the `git add` step but silently leaves a new, untracked file out of the commit — [Pro Git: Recording Changes, Skipping the Staging Area](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository)
- Recognise on sight: `git status` output with "Changes to be committed" and "Changes not staged for commit"; a 40-character commit hash.
- Claims:
  - A file is modified, staged or committed, matching the working tree, staging area and Git directory — [Pro Git: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)
  - Git checksums everything with a hash before storing it, so content cannot change without Git noticing — [Pro Git: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)
  - `git status` reports which of the three states each file is in — [git-status documentation](https://git-scm.com/docs/git-status)
  - `git diff` compares the working tree to the index, and `git diff --staged` compares the index to the last commit — [git-diff documentation](https://git-scm.com/docs/git-diff)
  - The staging area is a file in the Git directory that stores what will go into the next commit, and its technical name is the index — [Pro Git: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)

### Initializing a repository
- Interview questions: What does `git init` do?; How is `git init` different from `git clone`?; Follow-up: what happens if you run `git init` inside a folder that already sits inside another repository?
- Adjacent concept: `.gitignore` — decides what a new repository never tracks, so it is usually the first or second commit.
- Trade-off or limit: the entire history lives in the `.git` directory, so deleting that folder removes the repository's history while leaving the working files — [Pro Git: Getting a Git Repository](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository)
- Recognise on sight: `git init -b main`; a `.git/` folder containing `HEAD`, `config` and `objects`.
- Claims:
  - `git init` creates a `.git` subdirectory and nothing is tracked until files are added — [Pro Git: Getting a Git Repository](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository)
  - `git init -b <name>` (`--initial-branch`) names the first branch, and `init.defaultBranch` sets the default — [git-init documentation](https://git-scm.com/docs/git-init)
  - `user.name` and `user.email` must be configured before the first commit on a machine without a guessable identity — [git-config documentation](https://git-scm.com/docs/git-config)
  - A pattern added to `.gitignore` after a file is committed does not untrack it — [gitignore documentation](https://git-scm.com/docs/gitignore)
  - `git clone` copies an existing repository with its history, while `git init` starts an empty one — [Pro Git: Getting a Git Repository](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository)

### Commit, branch, merge, push, pull
- Interview questions: What is a branch in Git?; What is a fast-forward merge and when can it not happen?; Follow-up: you pull and Git stops with a conflict; walk through finishing the merge or backing out.
- Adjacent concept: the feature-branch workflow — short-lived branches merged to a main line, which is how teams isolate work in progress.
- Trade-off or limit: `git pull` is fetch plus merge, so it can create an unplanned merge commit or a conflict in your working tree; `git fetch` first lets you inspect before integrating — [git-pull documentation](https://git-scm.com/docs/git-pull)
- Recognise on sight: `<<<<<<< HEAD`, `=======` and `>>>>>>> feature/shout` inside a source file; `git log --oneline --graph` drawing a diamond.
- Claims:
  - A branch is a lightweight movable pointer to a commit — [Pro Git: Branches in a Nutshell](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)
  - `git switch -c <name>` creates a branch and switches to it in one step — [git-switch documentation](https://git-scm.com/docs/git-switch)
  - A fast-forward merge only moves the branch pointer; a diverged merge creates a commit with two parents — [Pro Git: Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
  - `git merge --no-ff` forces a merge commit even when a fast-forward is possible — [git-merge documentation](https://git-scm.com/docs/git-merge)
  - `git merge --abort` restores the pre-merge state after a conflicted merge — [git-merge documentation](https://git-scm.com/docs/git-merge)
  - `git log --oneline --graph` draws the commit graph one line per commit — [git-log documentation](https://git-scm.com/docs/git-log)

### Pushing to a remote repository
- Interview questions: What is `origin`?; Why was my push rejected?; Follow-up: what does `-u` do on `git push -u origin main` and why only once?
- Adjacent concept: authentication to the remote — HTTPS with a token or credential manager versus SSH keys.
- Trade-off or limit: a push is refused when the remote branch has commits you do not have (a non-fast-forward update), so you integrate with fetch and merge first rather than overwrite them — [git-push documentation](https://git-scm.com/docs/git-push)
- Recognise on sight: `! [rejected] main -> main (fetch first)`; `git remote -v` printing `origin` twice with `(fetch)` and `(push)`.
- Claims:
  - `origin` is the default name Git gives the remote you cloned from, and it is only a shortname for a URL — [Pro Git: Working with Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes)
  - `git remote add <name> <url>` registers a remote, and `git remote -v` lists them — [Pro Git: Working with Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes)
  - `git push -u origin main` sets the upstream so later `git push` and `git pull` need no arguments — [git-push documentation](https://git-scm.com/docs/git-push)
  - `git fetch` downloads remote history without changing the working tree — [git-fetch documentation](https://git-scm.com/docs/git-fetch)
  - A bare repository has no working tree and is what a shared server holds — [Pro Git: Getting Git on a Server](https://git-scm.com/book/en/v2/Git-on-the-Server-Getting-Git-on-a-Server)
  - From Git 2.33.1 a pull of diverged branches without a stated strategy stops with an error — [git-pull documentation](https://git-scm.com/docs/git-pull) and [Git 2.33.1 release notes](https://github.com/git/git/blob/master/Documentation/RelNotes/2.33.1.adoc)

### Git exercise
- Interview questions: What makes a good commit message?; How do you resolve a merge conflict?; Follow-up: how would you check a merge did not leave conflict markers in the code?
- Adjacent concept: branching strategies — feature branches versus working on main, which a team chooses and writes down.
- Trade-off or limit: Pro Git asks for each commit to be a logically separate changeset, which takes discipline before committing (splitting work into focused commits) but lets `git log` readers and reviewers follow one change at a time — [Pro Git: Contributing to a Project, Commit Guidelines](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project)
- Recognise on sight: a log reading "fix", "update", "final2" (poor) beside "Add farewell function to hello.py" (good); a stray `>>>>>>>` line in a committed file.
- Claims:
  - A commit message is a short imperative summary line of about 50 characters, a blank line, then a body explaining what and why — [Pro Git: Commit Guidelines](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project)
  - `git log --oneline` shows only each message's first line, so the summary must stand alone — [git-commit documentation: Discussion](https://git-scm.com/docs/git-commit#_discussion)
  - `git diff --check` warns when changes introduce conflict markers or whitespace errors — [git-diff documentation](https://git-scm.com/docs/git-diff)
  - Resolving a conflict means editing the file, removing all three marker lines, then `git add` and `git commit` — [Pro Git: Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
  - Feature branches isolate work in progress from the main line until it is ready to merge — [Pro Git: Branching Workflows](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)

## Sources (official / primary docs preferred; ≥3; full gate: every URL fetched and confirmed)

- Python tutorial — Using the Python Interpreter — https://docs.python.org/3/tutorial/interpreter.html
- Python tutorial — An Informal Introduction to Python — https://docs.python.org/3/tutorial/introduction.html
- Python glossary (interpreted, bytecode, CPython) — https://docs.python.org/3/glossary.html
- General Python FAQ — What is Python good for? — https://docs.python.org/3/faq/general.html
- python.org — Applications for Python — https://www.python.org/about/apps/
- Python on Windows — the py launcher — https://docs.python.org/3/using/windows.html
- Jupyter documentation — https://docs.jupyter.org/en/latest/
- Manifesto for Agile Software Development — https://agilemanifesto.org/
- Principles behind the Agile Manifesto — https://agilemanifesto.org/principles.html
- The 2020 Scrum Guide — https://scrumguides.org/scrum-guide.html
- Pro Git — About Version Control — https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
- Pro Git — What is Git? — https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F
- Pro Git — Getting a Git Repository — https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository
- Pro Git — Recording Changes to the Repository — https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
- Pro Git — Basic Branching and Merging — https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
- Pro Git — Working with Remotes — https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
- Pro Git — Contributing to a Project (commit guidelines) — https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project
- git-config reference — https://git-scm.com/docs/git-config
- git-commit reference — https://git-scm.com/docs/git-commit
- gitignore reference — https://git-scm.com/docs/gitignore
- git-switch reference — https://git-scm.com/docs/git-switch
- git-pull reference — https://git-scm.com/docs/git-pull
- Git 2.33.1 release notes (pull: divergent branches become a hard error) — https://github.com/git/git/blob/master/Documentation/RelNotes/2.33.1.adoc
- git-merge-tree reference — https://git-scm.com/docs/git-merge-tree
- GitHub Docs — About remote repositories — https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories
- What's New In Python 3.12 — https://docs.python.org/3/whatsnew/3.12.html
- What's New In Python 3.11 — https://docs.python.org/3/whatsnew/3.11.html
- PEP 20 – The Zen of Python — https://peps.python.org/pep-0020/
- PEP 3147 – PyCache — https://peps.python.org/pep-3147/
- sys module — https://docs.python.org/3/library/sys.html
- Command line and environment — https://docs.python.org/3/using/cmdline.html
- dis module — https://docs.python.org/3/library/dis.html
- sqlite3 module — https://docs.python.org/3/library/sqlite3.html
- An overview of HTTP (MDN) — https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview
- nbformat documentation — https://nbformat.readthedocs.io/en/latest/
- git-init reference — https://git-scm.com/docs/git-init
- git-status reference — https://git-scm.com/docs/git-status
- git-diff reference — https://git-scm.com/docs/git-diff
- git-merge reference — https://git-scm.com/docs/git-merge
- git-push reference — https://git-scm.com/docs/git-push
- git-fetch reference — https://git-scm.com/docs/git-fetch
- git-log reference — https://git-scm.com/docs/git-log
- gitglossary — https://git-scm.com/docs/gitglossary
- Pro Git — Branches in a Nutshell — https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
- Pro Git — Branching Workflows — https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows
- Pro Git — Getting Git on a Server — https://git-scm.com/book/en/v2/Git-on-the-Server-Getting-Git-on-a-Server
- Python tutorial — Modules: "Compiled" Python files — https://docs.python.org/3/tutorial/modules.html#compiled-python-files
- Built-in Functions — compile — https://docs.python.org/3/library/functions.html#compile
- RFC 9110 — HTTP Semantics (primary source for HTTP; MDN overview above is a supplement) — https://www.rfc-editor.org/rfc/rfc9110
- http.server — HTTP servers (not recommended for production) — https://docs.python.org/3/library/http.server.html
- Jupyter Notebook documentation — The Jupyter Notebook — https://jupyter-notebook.readthedocs.io/en/stable/notebook.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- Agile | A way of building software in short iterations that each deliver working software and welcome changing requirements, as set out in the 2001 Agile Manifesto. | aka: Agile Manifesto, agile methodology
- waterfall | A sequential delivery model where each SDLC phase is finished and signed off before the next begins, so working software appears only at the end. | aka: waterfall model
- backlog | The ordered list of everything the product might need, owned by the Product Owner; the Sprint Backlog is the slice the team commits to for one Sprint. | aka: product backlog, sprint backlog
- Daily Scrum | A 15-minute event where the Developers inspect progress toward the Sprint Goal and plan the next day's work. | aka: stand-up, standup, daily stand-up
- DVCS | Distributed Version Control System — every clone holds the full history, so commits, branches and logs work offline and only push, pull and fetch touch the network. | aka: distributed version control, distributed version control system
- merge conflict | What Git reports when both branches changed the same lines; it writes the three conflict markers into the file so you can edit, stage and commit the version you want. | aka: conflict markers
- fast-forward | A merge where the target branch has no new commits of its own, so Git simply moves the branch pointer forward and creates no merge commit. | aka: fast-forward merge, ff merge
- upstream | The remote branch a local branch tracks, set by git push -u, so that plain git push and git pull know where to go. | aka: upstream branch, tracking branch

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Tooling check surprises: on a fresh Windows laptop `python` can open the Microsoft Store stub instead of the interpreter (use `py --version` or fix App execution aliases), and trainees who land in the `>>>` REPL type `git status` or `python hello.py` there, get `SyntaxError`, and conclude Python is broken; they must tell the PowerShell prompt, the REPL prompt and a running script apart, and leave the REPL with `exit()`.
- Commit mechanics and messages: `git commit -m` right after editing reports "no changes added to commit" because `git add` was skipped; on a fresh machine the first commit fails with "Author identity unknown" until `user.name` and `user.email` are configured; forgetting `-m` drops them into an editor they cannot exit; and once it works the messages are "fix", "update", "final2", which the rubric marks down because `git log --oneline` must read as the story of the work.
- `git branch feature` creates the branch but does not switch to it, so the next commits still land on `main`; trainees then merge and see "Already up to date" and wonder why the feature branch is empty. Teach `git switch -c feature` and check `git status` or `git branch` before every commit.
- Remote round trip: `git push` fails with "no configured push destination" or "no upstream branch" until `git remote add origin` and `push -u` have been done once; GitHub rejects the account password over HTTPS (a token or credential manager is needed); and running `git init` inside a folder that is already a repository (such as all of Documents) creates nested repos that confuse every later command.
- Conflicts: trainees treat `git pull` as a download and are surprised by "Your local changes would be overwritten by merge" or by a merge they did not expect; when a conflict appears they delete the markers blindly, commit the file with `<<<<<<<` still inside, or run `git merge --abort` and submit without ever resolving it; the fix is to read both sides, keep the right lines, remove all three markers, then `git add` and `git commit`.
- Reading story points as hours or days: trainees convert "5 points" to "5 hours", compare points between teams, or let the loudest voice set the number; points are relative effort agreed by the whole team through comparison with other items, and velocity is only meaningful within one team over several Sprints.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- On-ramp, once and briefly: run `py --version`, then show the same three lines of Python three ways on the projector — the `>>>` REPL (with `_` holding the last result and `exit()` to leave), `python hello.py` as a saved file, and the same code in one Jupyter cell so trainees see a notebook is a REPL with a memory; point out the `__pycache__` folder that appears after an import and use it as the segue into `.gitignore` when the Git loop starts.
- The local Git loop with `git status` after every single step so the three states become visible: `git init`, create `hello.py` and `.gitignore`, `git add`, `git commit -m`, `git log --oneline`; then `git switch -c feature`, commit, `git switch main`, `git merge feature` and name it as a fast-forward; then edit the same line on both branches to force a real conflict, show the `<<<<<<< ======= >>>>>>>` markers in the editor, resolve, `git add`, `git commit`, and show the two-parent merge commit in `git log --oneline --graph`. The trainer types every git command live (D-0030); the answer key is a transcript of the commands and their real output, and the only .py file is the `hello.py` being committed.
- The remote round trip for real: create an empty GitHub repository on the web UI, `git remote add origin <url>`, `git push -u origin main` (let the credential manager prompt appear on screen so trainees recognise it), make a one-line edit on the GitHub web UI, then `git pull` locally and show in the log that pull is fetch plus merge; write two commit messages side by side ("fix" versus "Add greeting function to hello.py") and read the rubric line that marks them before trainees start the exercise.
- A two-minute planning-poker round on two toy backlog items (for example "add a hello script" versus "set up the team's shared repo with branch protection") so trainees experience relative sizing and the "why is yours a 3 and mine an 8?" conversation; tie the discussion back to the Sprint, Daily Scrum and Sprint Review time-boxes from the Scrum Guide and to where the Git exercise would sit in a Sprint Backlog.
