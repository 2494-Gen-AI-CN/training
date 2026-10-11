# Orientation, Agile & Git fundamentals — code-along demos

Week 1 · Day 2 · `w01d2` · Tue 2026-10-13
Notes: [docs/weeks/week-01/day-2-orientation-agile-and-git.html](../../../docs/weeks/week-01/day-2-orientation-agile-and-git.html) · Exercise: [exercises/week-01/day-2-orientation-agile-and-git](../../../exercises/week-01/day-2-orientation-agile-and-git)

## Prerequisites

- Python 3.12 (`py --version` or `python --version` in PowerShell; demo 01 is the check)
- Git 2.28 or newer on PATH (`git --version`; the brief was verified against 2.50). Demos 04 and 05 exit politely if git is missing
- No `requirements.txt`: every demo is standard library only (demos 04 and 05 shell out to git with `subprocess`)
- No keys: this day makes no LLM calls, so there is no `.env.example`
- "Professionalism at Revature" is house rules delivered by the trainer in the first 10 minutes; it has no demo

## Run order

| # | File | Shows | Run | Needs key? |
|---|---|---|---|---|
| 1 | `01_tooling_check.py` | The whole on-ramp in one file: which interpreter the shell runs; CPython compiles to bytecode (`dis`, `__pycache__`) then interprets; why Python and its two seats in the full stack; REPL / `_` / `exit()` / `python -i` / Jupyter as a REPL with memory | `python 01_tooling_check.py`, then `python -i 01_tooling_check.py` | no |
| 2 | `02_sdlc_waterfall_vs_agile.py` | Six SDLC phases; one backlog scheduled waterfall (software in week 10, week-6 change queued) vs Agile (two-week Sprints, Increment each Sprint, week-6 change welcomed); the four Manifesto values | `python 02_sdlc_waterfall_vs_agile.py` | no |
| 3 | `03_scrum_and_story_points.py` | What the 2020 Scrum Guide defines (3 accountabilities, 5 events, 3 artifacts) and its time-boxes next to our two-week budget; the 1-2-3-5-8-13 scale; a planning-poker round that converges and one that forces discussion and a re-vote | `python 03_scrum_and_story_points.py` | no |
| 4 | `04_git_local_loop.py` | VCS generations in one line, then the real local loop in a temp repo: `init`, `status` at each of the three states, `add`, `commit`, `log --oneline`, `switch -c` + fast-forward merge, a forced conflict with `<<<<<<< ======= >>>>>>>` resolved and committed, `log --graph` | `python 04_git_local_loop.py` | no |
| 5 | `05_git_remote_round_trip.py` | `git push` with no remote; a bare repo standing in for GitHub; `remote add origin`, `push -u origin main`; a teammate clone pushes; `fetch` (history only) vs `pull` (fetch + merge); "fix" vs a rubric-grade commit message | `python 05_git_remote_round_trip.py` | no |

Each file is split into `# --- STEP n: ... ---` checkpoints. The trainer types STEP by STEP; trainees follow along. The top docstring states what the file demonstrates and the expected output.

## How the Git demos are meant to be used

Demos 04 and 05 print every command as `$ git ...` before running it, so the projector shows the exact keystrokes and git's real reply; both work offline and delete their temp folders afterwards. The scripts pass identity, `init.defaultBranch=main` and `core.autocrlf=false` with `-c` so they behave the same on every machine; trainees set `user.name`, `user.email` and `init.defaultBranch` once with `git config --global` instead. Immediately after each demo, trainees repeat the same STEPs by hand in PowerShell:

- after 04: `mkdir w01d2-git; cd w01d2-git; git init`, then add, commit, `git switch -c feature`, merge, and one deliberate conflict (the same shape the exercise rubric marks);
- after 05: create an empty repository on github.com, `git remote add origin <url>`, `git push -u origin main` (let the Git Credential Manager browser prompt appear on screen), edit README in the web UI, `git pull`, read `git log --oneline`.

Pitfalls to watch for, from the brief: typing shell commands at the `>>>` prompt; `git commit` before `git add` ("no changes added to commit"); "Author identity unknown" on a fresh machine; `git branch x` without switching, so commits land on `main`; `git push` before a remote exists; `git init` inside a folder that is already a repo; deleting conflict markers blindly or committing with `<<<<<<<` still in the file.

## Steps per file

- **01** STEP 1 version and executable · STEP 2 `dis` of a function and the `.pyc` that `py_compile` writes (segue to `.gitignore`) · STEP 3 why Python and the full-stack map · STEP 4 REPL / script / Jupyter, then open `python` live and try `2 + 3`, `_ * 10`, `exit()`.
- **02** STEP 1 phases · STEP 2 waterfall timeline with the week-6 change · STEP 3 five Sprints with the same change absorbed · STEP 4 Manifesto values.
- **03** STEP 1 what Scrum defines · STEP 2 time-boxes · STEP 3 scale and reference item · STEP 4 planning poker on two toy items (run the same round live with the room before moving on).
- **04** STEP 1 `init` and `status` · STEP 2 untracked → staged → committed · STEP 3 feature branch and fast-forward · STEP 4 forced conflict, markers printed, resolved, `log --graph`.
- **05** STEP 1 `push` with no destination · STEP 2 `remote add`, `remote -v`, `push -u` · STEP 3 teammate clone pushes · STEP 4 `fetch`, `status`, `log HEAD..origin/main`, `pull` · STEP 5 the commit-message rule the rubric applies.
