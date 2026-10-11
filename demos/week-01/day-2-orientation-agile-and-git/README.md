# Orientation, Agile & Git fundamentals — code-along demos

Week 1 · Day 2 · `w01d2` · Tue 2026-10-13
Notes: [docs/weeks/week-01/day-2-orientation-agile-and-git.html](../../../docs/weeks/week-01/day-2-orientation-agile-and-git.html) · Exercise: [exercises/week-01/day-2-orientation-agile-and-git](../../../exercises/week-01/day-2-orientation-agile-and-git)

## Prerequisites

- Python 3.12 (`python --version` or `py --version` in PowerShell)
- Git 2.47 or any 2.28+ on PATH (`git --version`); demos 04 and 05 exit politely if git is missing
- No `requirements.txt` — every demo is standard library only
- No keys — this day makes no LLM calls, so there is no `.env.example`

## Run order

| # | File | Shows | Run | Needs key? |
|---|---|---|---|---|
| 1 | `01_hello_python.py` | Python orientation: a script runs top to bottom; the full-stack map; CPython compiles to bytecode (`dis`, `__pycache__`) then interprets; REPL / `_` / `exit()` / `python -i` / Jupyter tips | `python 01_hello_python.py` then `python -i 01_hello_python.py` | no |
| 2 | `02_sdlc_waterfall_vs_agile.py` | SDLC phases; the same backlog delivered waterfall (one pass, software at week 10) vs Agile (two-week Sprints, Increment every Sprint, late change absorbed); the four Manifesto values | `python 02_sdlc_waterfall_vs_agile.py` | no |
| 3 | `03_story_points_and_scrum.py` | Story pointing with a Fibonacci-like scale and a planning-poker round that converges; Scrum accountabilities / events / artifacts; time-boxes scaled from the Scrum Guide's one-month caps to our two-week Sprint | `python 03_story_points_and_scrum.py` | no |
| 4 | `04_git_local_loop.py` | VCS generations (local, centralised, distributed) and the three states; real `git init / status / add / commit / log`, `switch -c` + fast-forward merge, a forced conflict with `<<<<<<< ======= >>>>>>>` markers resolved and committed — all in a temp folder it deletes afterwards | `python 04_git_local_loop.py` | no |
| 5 | `05_git_remote_round_trip.py` | `git push` failing with no remote; a bare repo standing in for GitHub; `remote add origin`, `push -u origin main`, a teammate clone pushing; `fetch` (history only) vs `pull` (fetch + merge) | `python 05_git_remote_round_trip.py` | no |

Each file is split into `# --- STEP n: ... ---` checkpoints. The trainer types STEP by STEP; trainees follow along. The top docstring states what the file demonstrates and the expected output.

## How the git demos are meant to be used

Demos 04 and 05 print every command as `$ git ...` before running it, so the projector shows the exact keystrokes and git's real reply. After each runs, trainees repeat the same STEPs by hand in PowerShell:

- after 04: `mkdir w01d2-git; cd w01d2-git; git init` and continue through add, commit, `git switch -c feature`, merge, and one deliberate conflict;
- after 05: create an empty repo on GitHub, `git remote add origin <url>`, `git push -u origin main`, edit a file in the GitHub web UI, `git pull`, read `git log --oneline`.

Watch for the pitfalls the brief lists: typing shell commands at the `>>>` prompt, committing before `git add`, "Author identity unknown" (set `git config --global user.name` / `user.email` once), `git branch x` without switching, `git push` before a remote exists, and running `git init` inside a folder that is already a repo.

The scripts pass identity and `init.defaultBranch=main` with `-c` so they run on any machine; trainees set the same values once with `git config --global`.

## Steps per file

- **01** STEP 1 hello + version · STEP 2 full-stack map · STEP 3 bytecode via `dis` and `py_compile` (a `__pycache__/` folder appears; it is gitignored) · STEP 4 REPL tips, then open `python` live and try `2 + 3`, `_ * 10`, `exit()`.
- **02** STEP 1 phases · STEP 2 waterfall timeline · STEP 3 Agile Sprints with a mid-way requirement change · STEP 4 Manifesto values.
- **03** STEP 1 scale · STEP 2 planning poker (one-step spread converges, wider spread triggers discussion and a re-vote) · STEP 3 Scrum roles/events/artifacts · STEP 4 time-boxes.
- **04** STEP 1 VCS generations + three states · STEP 2 init/status/add/commit/log · STEP 3 branch + fast-forward merge · STEP 4 conflict and resolution.
- **05** STEP 1 one commit, then `git push` with no remote · STEP 2 bare "origin", `remote add`, `push -u` · STEP 3 teammate clone pushes · STEP 4 `fetch` vs `pull`.
