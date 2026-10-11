# w01d2 — Orientation, Agile & Git fundamentals

gate: light
verified: 2026-10-13
week: 1 · Agile for developers, Git & Python fundamentals
day: 2 · day-2-orientation-agile-and-git

version-stamps:
  - python: 3.12 (verified 2026-10-13)
  - git: 2.47 (verified 2026-10-13)   # any 2.28+ works; 2.23+ needed for `git switch`
  - pytest: 8.3 (verified 2026-10-13)   # exercise loop only; demos are stdlib
  - notebook: 7.x (verified 2026-10-13)   # Jupyter Notebook, shown briefly; not imported by demos

## Claims (each MUST carry a source on a full gate; light gate: source optional but recommended)

- Python is an interpreted language in the everyday sense: you run `python hello.py` and the interpreter executes the source directly, with no separate build step producing an executable — [Python glossary: "interpreted"](https://docs.python.org/3/glossary.html#term-interpreted)
- Under the hood CPython first compiles each module to bytecode and then interprets that bytecode on a virtual machine; bytecode is cached in `__pycache__/*.pyc` files, which is why a `__pycache__` folder appears after the first import — [Python glossary: "bytecode"](https://docs.python.org/3/glossary.html#term-bytecode)
- A "full stack" application has a front end (what runs in the browser: HTML, CSS, JavaScript), a back end (server-side code that receives requests, applies business rules and talks to storage), a database (where data persists between requests, e.g. MySQL) and infrastructure (where it all runs: a laptop today, a cloud such as GCP later); Python's sweet spot in this course is the back end and the data/ML layer, and the Python FAQ lists web development, scripting and data analysis among its main uses — [General Python FAQ: What is Python good for?](https://docs.python.org/3/faq/general.html#what-is-python-good-for)
- Running `python` with no arguments starts the interactive interpreter (REPL) with the `>>>` primary prompt and `...` continuation prompt; `python -i script.py` runs the script and then drops into the REPL with the script's variables still defined — [Using the Python Interpreter](https://docs.python.org/3/tutorial/interpreter.html)
- In interactive mode the value of the last printed expression is kept in the read-only variable `_`, which lets you chain calculator-style work — [An Informal Introduction to Python](https://docs.python.org/3/tutorial/introduction.html)
- You leave the REPL with `exit()` or `quit()` on any platform, with Ctrl-Z then Enter on Windows, or Ctrl-D on Linux/macOS — [Using the Python Interpreter](https://docs.python.org/3/tutorial/interpreter.html)
- On Windows the `py` launcher is installed alongside Python and `py -3.12` selects a specific version; `python --version` or `py --version` confirms which interpreter the shell will run — [Python Launcher for Windows](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)
- A Jupyter Notebook is a document of cells (code or Markdown); each code cell is sent to a running kernel and the output appears under the cell, so it is a REPL with memory of every cell you have executed, in execution order rather than top-to-bottom order — [Jupyter documentation](https://docs.jupyter.org/en/latest/)
- pytest collects files named `test_*.py` or `*_test.py` and runs functions whose names start with `test`; a plain `assert` is enough, and pytest rewrites it to show the compared values on failure — [pytest: Get Started](https://docs.pytest.org/en/stable/getting-started.html)
- The software development life cycle (SDLC) is the sequence of phases every piece of software passes through regardless of methodology: requirements/planning, design, implementation (build), testing, deployment and maintenance; what differs between methodologies is whether those phases happen once in order or are repeated in short cycles — Scrum, for example, is founded on empiricism (transparency, inspection, adaptation) and runs all of the phases inside every Sprint so that knowledge comes from experience rather than from up-front planning — [The 2020 Scrum Guide: Scrum Theory](https://scrumguides.org/scrum-guide.html)
- Waterfall is the sequential model: each SDLC phase is completed and signed off before the next begins, so requirements are frozen early and working software appears only at the end; Agile is the iterative model: the Agile principles call for delivering working software frequently, "from a couple of weeks to a couple of months", welcoming changing requirements even late, and in Scrum every Sprint must produce a usable Increment — [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles.html)
- The Agile Manifesto (2001) values individuals and interactions over processes and tools, working software over comprehensive documentation, customer collaboration over contract negotiation, and responding to change over following a plan — [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- Scrum defines three accountabilities (Product Owner, Scrum Master, Developers), five events (the Sprint, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective) and three artifacts (Product Backlog, Sprint Backlog, Increment) — [The 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html)
- A Sprint is a fixed-length event of one month or less; the Daily Scrum is time-boxed to 15 minutes; for a one-month Sprint, Sprint Planning is capped at eight hours, the Sprint Review at four hours and the Retrospective at three hours, and shorter Sprints use shorter caps — [The 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html)
- The Scrum Guide does not mention story points; story pointing is a widely used estimation practice layered on Scrum in which the team assigns relative effort sizes (commonly a Fibonacci-like scale 1, 2, 3, 5, 8, 13) to backlog items rather than hour estimates — [The 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html)
- Git is a distributed version control system: every clone holds the full history, so `log`, `diff`, `commit` and `branch` work offline and only `push`/`pull`/`fetch` touch the network — [Pro Git: About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
- Git stores each commit as a snapshot of the whole tree (unchanged files are stored as links to the previous identical file), not as a list of per-file diffs the way CVS and Subversion do — [Pro Git: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)
- A file in a Git repository is in one of three states (modified, staged, committed) matching three areas (working tree, staging area/index, .git directory); `git status` reports which state each file is in — [Pro Git: What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)
- `git init` creates a `.git` subdirectory in the current folder and nothing is tracked until you `git add` it; `git add` both starts tracking new files and stages modified ones — [Pro Git: Getting a Git Repository](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository)
- Git tries to guess an author identity from the OS username and hostname, and when that guess fails (the usual case on Windows) the first commit on a fresh machine typically fails with "Author identity unknown ... Please tell me who you are" until `user.name` and `user.email` are set (`git config --global user.name "..."`); the initial branch name is set by `init.defaultBranch` (Git 2.28+), defaulting to `master` unless configured to `main` — [git-config documentation](https://git-scm.com/docs/git-config)
- `git commit -m "message"` records the staged snapshot; `git commit` without `-m` opens the configured editor, and `git log --oneline` lists commits one per line — [Pro Git: Recording Changes](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository)
- `git branch <name>` creates a branch but does not switch to it; `git switch <name>` (Git 2.23+) or `git checkout <name>` moves HEAD, and `git switch -c <name>` creates and switches in one step — [git-switch documentation](https://git-scm.com/docs/git-switch)
- A merge is a fast-forward when the target branch has no new commits since the feature branch diverged, so Git simply moves the pointer; otherwise Git creates a merge commit with two parents, and if both sides changed the same lines it stops with conflict markers `<<<<<<<`, `=======`, `>>>>>>>` for you to resolve, `git add` and `git commit` — [Pro Git: Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
- `git remote add origin <url>` names a remote; `git push -u origin main` uploads the branch and sets the upstream so later `git push` and `git pull` need no arguments — [Pro Git: Working with Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes)
- `git pull` is `git fetch` followed by `git merge` of the tracked upstream branch (or a rebase if `pull.rebase` is set); `git fetch` alone downloads new history without changing your working tree — [git-pull documentation](https://git-scm.com/docs/git-pull)
- Version control systems come in three generations: local (RCS), centralised (CVS, Subversion: one server holds the history, clients check out a working copy) and distributed (Git, Mercurial: every client mirrors the full repository) — [Pro Git: About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)

## Sources (official / primary docs preferred; ≥3; full gate: every URL fetched and confirmed)

- Python tutorial — Using the Python Interpreter — https://docs.python.org/3/tutorial/interpreter.html
- Python tutorial — An Informal Introduction to Python — https://docs.python.org/3/tutorial/introduction.html
- Python glossary (interpreted, bytecode, CPython) — https://docs.python.org/3/glossary.html
- General Python FAQ — What is Python good for? — https://docs.python.org/3/faq/general.html
- Python on Windows — the py launcher — https://docs.python.org/3/using/windows.html
- Jupyter documentation — https://docs.jupyter.org/en/latest/
- pytest — Get Started — https://docs.pytest.org/en/stable/getting-started.html
- Manifesto for Agile Software Development — https://agilemanifesto.org/
- Principles behind the Agile Manifesto — https://agilemanifesto.org/principles.html
- The 2020 Scrum Guide — https://scrumguides.org/scrum-guide.html
- Pro Git — About Version Control — https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
- Pro Git — What is Git? — https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F
- Pro Git — Getting a Git Repository — https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository
- Pro Git — Recording Changes to the Repository — https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
- Pro Git — Basic Branching and Merging — https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
- Pro Git — Working with Remotes — https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
- git-config reference — https://git-scm.com/docs/git-config
- git-switch reference — https://git-scm.com/docs/git-switch
- git-pull reference — https://git-scm.com/docs/git-pull

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- repository | A folder whose full change history Git tracks in a hidden .git directory. | aka: repo, repositories
- staging area | The holding area where you put changes with git add before they become part of the next commit. | aka: staged, git index
- remote | A copy of a repository hosted elsewhere (such as GitHub) that you push to and pull from. | aka: origin
- SDLC | Software Development Life Cycle — the stages software goes through from idea to retirement: plan, design, build, test, deploy, maintain. | aka: software development life cycle
- Scrum | An Agile framework that delivers work in short fixed-length Sprints with defined roles, events and artifacts. | aka: scrum framework
- sprint | A fixed time-box of one month or less in which a Scrum team turns backlog items into a usable increment. | aka:
- story point | A relative, unit-less estimate of how much effort a backlog item takes compared with other items, not a number of hours. | aka:
- Jupyter notebook | A browser document of code and text cells where each code cell runs in a live kernel and shows its output underneath. | aka: notebook, Jupyter, .ipynb

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Typing a shell command at the Python prompt: trainees see `>>>` and type `python hello.py` or `git status`, get `SyntaxError`, and conclude Python is broken; they must learn to tell the PowerShell prompt, the `>>>` REPL prompt and a running script apart, and to leave the REPL with `exit()`.
- Committing without staging (or without an identity): `git commit -m "..."` right after editing reports "no changes added to commit" because `git add` was skipped, and on a fresh machine the first commit typically fails with "Author identity unknown" until `git config --global user.name` and `user.email` are set; forgetting `-m` also drops them into an editor they cannot exit.
- `git branch feature` creates the branch but does not switch to it, so the next commits still land on `main`; trainees then wonder why the feature branch is empty. Teach `git switch -c feature` (or `git checkout -b`) and check `git status` / `git branch` before committing.
- Pushing before the remote and upstream exist: `git push` fails with "no configured push destination" or "no upstream branch"; and running `git init` a second time, or inside a folder that is already inside another repository (for example the whole Documents folder), creates nested repos that confuse every later command.
- Treating `git pull` as a plain download: it fetches and merges, so uncommitted local edits produce "Your local changes would be overwritten by merge" and divergent history produces a merge (or conflict) they did not expect; commit or stash first, and read the conflict markers instead of deleting them.
- Reading story points as hours or days: trainees convert "5 points" to "5 hours", compare points between teams, or let the loudest voice set the number; points are relative effort agreed by the whole team, and velocity is only meaningful within one team over several Sprints.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Show the three ways to run Python side by side on the projector: the `>>>` REPL (with `_` holding the last result and `exit()` to leave), `python hello.py` running a saved file, and `python -i hello.py` to inspect the script's variables afterwards; open the same code in a Jupyter notebook once so trainees see cells are just a REPL with a memory, and point out the `__pycache__` folder that appears after an import.
- Walk the full local Git loop with `git status` after every single step so the three states become visible: `git init`, create a file, `git add`, `git commit -m`, `git log --oneline`; then `git switch -c feature`, commit, `git switch main`, `git merge feature` (fast-forward), and finally edit the same line on both branches to force a real conflict and resolve the `<<<<<<< ======= >>>>>>>` markers live.
- Do the remote round trip for real: `git remote add origin <url>`, `git push -u origin main`, make an edit on the GitHub web UI, then `git pull` locally and show in `git log` that pull is fetch plus merge; let trainees repeat it against their own empty GitHub repo before the exercise.
- Run a two-minute planning-poker round on two toy backlog items (for example "add a hello script" versus "set up the team's shared repo") so trainees experience relative sizing and the "why is yours a 3 and mine an 8?" conversation; tie it back to the Sprint, Daily Scrum and Review time-boxes from the Scrum Guide.
