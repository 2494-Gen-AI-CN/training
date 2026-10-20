# Exercise — Orientation, Agile & Git fundamentals

Week 1 · Day 2 · `w01d2` · Tue 2026-10-13 · ~60–90 min · marked against a rubric (no automated tests)
Notes: [weeks/week-01/day-2-orientation-agile-and-git.html](https://2494-gen-ai-cn.github.io/training/weeks/week-01/day-2-orientation-agile-and-git.html) · Demos: [2494-Gen-AI-CN/demos](https://github.com/2494-Gen-AI-CN/demos)

## Task

Build the first repository you would be proud to show a teammate. On your own machine, start a Git repository for a tiny Python project (`hello.py`, a Python `.gitignore`, a `README.md`), put it on GitHub, and then work on it the way a Scrum team does: a backlog in the README with story points, a feature branch merged back into `main`, a second branch that **collides** with `main` on the same line so you resolve one real merge conflict by hand, a one-line edit made on the GitHub web UI and pulled back down, and commit messages that read as the story of the work. Nothing here is about Python: `hello.py` stays trivial. The point is the workflow, because this repository stays yours for the whole course: from Wednesday on every exercise is handed in through it, your code-along copies and explorations live in it, and the first thing a reviewer reads is `git log --oneline`.

Suggested time-box: 10 min set-up and first push · 15 min backlog and feature branch · 25 min the conflict · 10 min the web-UI round trip · 10 min read your own log and tidy the messages.

## Deliverable

The HTTPS URL of a **public** GitHub repository named `<FirstnameLastname>` (your first and last name as on the class roster, run together in PascalCase, plain letters and digits; a hyphen or underscore between the names is fine, for example `GraceHopper` or `Grace-Hopper`), owned by the `2494-Gen-AI-CN` organisation and not by your personal account, default branch `main`, submitted the way your trainer announces. Its history, as cloned by the trainer at the end of today, must show every acceptance criterion below; nothing on your laptop counts unless it was pushed. Be ready to open the repository on screen and walk through `git log --oneline --graph --all` in under two minutes.

## Acceptance criteria

- [ ] **AC1 Remote.** The repository is public, lives in the `2494-Gen-AI-CN` organisation as `<FirstnameLastname>`, its default branch is `main`, and your local `origin` points at it (`git remote -v` shows `https://github.com/2494-Gen-AI-CN/<FirstnameLastname>.git`).
- [ ] **AC2 Clean first commit.** The first commit contains `hello.py` and a `.gitignore` listing at least `__pycache__/`, `*.pyc` and `.venv/`; no `.pyc` file or `__pycache__/` folder is tracked anywhere in the history.
- [ ] **AC3 Backlog with points.** `README.md` on `main` contains a Sprint Backlog table of 3–5 items, each sized with a story point from the 1-2-3-5-8-13 scale; one row is "this exercise" and one sentence names which item was the reference item everything else was compared against.
- [ ] **AC4 Feature branch, fast-forwarded.** A branch named `feature/<something>` with at least one commit was merged into `main` as a fast-forward (no merge commit) and was pushed, so it appears under `origin/` too.
- [ ] **AC5 One real conflict, resolved by hand.** A second branch and `main` changed the **same line** of the same file; the merge produced a conflict that you resolved; the resulting merge commit has two parents, its message says what you kept and why, and no `<<<<<<<`, `=======` or `>>>>>>>` marker survives in any file.
- [ ] **AC6 Round trip through the web UI.** One commit was made on the GitHub web UI (editing `README.md` is fine), pulled into your local `main`, and at least one later local commit was pushed on top of it.
- [ ] **AC7 Commit messages tell the story.** `main` has at least six commits; every subject line is in the imperative mood ("Add …", "Resolve …", not "added", "fix", "update", "final"), at most 72 characters, and at least two commits have a body (blank line, then *why*).
- [ ] **AC8 Real identity.** Every commit you made locally carries your real name and a working e-mail address (`git shortlog -sne`); no "Demo Trainer", `root@localhost` or machine-generated identity.

## Rubric

| Criterion | Meets | Partial | Missing |
|---|---|---|---|
| AC1 Remote | Public repo `2494-Gen-AI-CN/<FirstnameLastname>`, default branch `main`, `origin` set, local `main` fully pushed | Repo exists but sits under your personal account, is not named after you (a hyphen or underscore between first and last name is fine; a clash with a classmate gets a trailing digit), has default branch `master`, or local has unpushed commits | No repository on GitHub, or the trainer cannot open the URL |
| AC2 Clean first commit | First commit = `hello.py` + `.gitignore` with all three patterns; nothing in `__pycache__/` ever tracked | `.gitignore` added in a later commit, or missing one pattern, but no `.pyc` tracked | `.pyc`/`__pycache__/` committed at any point, or no `.gitignore` |
| AC3 Backlog with points | 3–5 rows, every row sized from the 1-2-3-5-8-13 scale, "this exercise" present, reference item named | Table present but a row uses hours/days or an off-scale number, or the reference item is not named | No backlog table in `README.md` |
| AC4 Feature branch, fast-forwarded | `feature/*` branch pushed, merged into `main`, exactly one *feature* merge commit in the whole history (the AC5 one; a `Merge branch 'main' of github.com/...` commit created by `git pull` in AC6 does not count against you) | Branch exists and is merged but was not pushed, or the feature merge created an unneeded merge commit, or the branch is named `feature` with no `/<something>` | No feature branch; all work committed straight onto `main` |
| AC5 One real conflict | Merge commit with two parents whose re-merge (`git merge-tree --write-tree <p1> <p2>`) reports `CONFLICT (content)`, proof the two sides really collided; message explains what was kept and why; no markers left | Merge commit exists but its two parents merge cleanly (both sides changed *different* lines, so nothing was resolved), or markers remain in a file, or message is just the default "Merge branch 'x'", or you kept one side and cannot say why | No two-parent merge commit, or the conflict was dodged with `git merge --abort` / a force-push |
| AC6 Round trip | A commit with committer `GitHub <noreply@github.com>` sits in `main`'s history with at least one later local commit pushed on top | Web-UI commit exists but is the tip (nothing pulled and pushed after it), or was pulled but lives on an unpushed local branch | No commit from the web UI |
| AC7 Commit messages | ≥ 6 commits, all subjects imperative and ≤ 72 chars, ≥ 2 bodies that say why | ≥ 6 commits but one or two weak subjects ("fix", past tense, > 72 chars) or only one body | Fewer than 6 commits, or messages mostly "update"/"final2"/"asdf" |
| AC8 Real identity | One identity across all local commits: real name + working e-mail | Correct name but a placeholder e-mail, or two spellings of the same person | Demo/placeholder identity, or `Author identity unknown` left unresolved so commits are missing |

Overall: **Meets** on all eight = full marks. Any **Missing** on AC4, AC5 or AC7 means the exercise is re-done before Wednesday, because those three are the workflow every later hand-in depends on.

## Getting started

Run these in PowerShell. Set identity once (skip if `git config --global --list` already shows your name, e-mail and `init.defaultbranch=main`), and create the folder somewhere that is **not** already inside a Git repository (so not inside `w01d2-scratch/` from the demos). Type your own name wherever you see `<FirstnameLastname>`.

```
py --version
git --version
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main

mkdir <FirstnameLastname>
cd <FirstnameLastname>
git init
git status

# first commit: hello.py + .gitignore, then push to an EMPTY repo you create on github.com
# (New repository -> Owner 2494-Gen-AI-CN -> name <FirstnameLastname> -> Public -> no README/.gitignore/licence)
git add .
git commit -m "Add hello script and Python .gitignore"
git remote add origin https://github.com/2494-Gen-AI-CN/<FirstnameLastname>.git
git push -u origin main

# backlog in README.md on main, then a feature branch
git switch -c feature/greet
# ... edit, commit with a message that says why ...
git switch main
git merge feature/greet          # expect: Fast-forward
git push origin main feature/greet

# the conflict: change the SAME line on a new branch AND on main, then merge
git switch -c feature/city
# ... change line 1 of hello.py, commit ...
git switch main
# ... change line 1 of hello.py differently, commit ...
git merge feature/city           # expect: CONFLICT (content)
# ... edit hello.py: keep what you want, delete all three marker lines ...
git add hello.py
git commit                       # subject + blank line + why you kept what you kept
git log --oneline --graph --all
git push origin main feature/city

# round trip: edit README.md on github.com (pencil icon, Commit changes), then
git pull
# ... one more local commit ...
git push
git status                       # expect: nothing to commit, up to date with 'origin/main'
```

## Hints

- On GitHub's "New repository" page the **Owner** dropdown starts on your personal account. Change it to `2494-Gen-AI-CN` before you click Create, and choose Public. If the organisation is not in the list, you have not accepted the invitation e-mail yet: accept it, then reload the page. A repository created under your own account can be moved afterwards (Settings → Transfer ownership), but it is quicker to get it right the first time.
- This repository outlives today. It is marked as it stands at the end of today, and from Wednesday on each day's work goes in its own folder inside it, so leave `hello.py`, `.gitignore` and `README.md` where they are at the top level.
- `git status` before every commit. The two silent mistakes of the day are `git branch x` without `git switch x` (your "feature" commits land on `main`) and `git commit -m` without `git add` ("no changes added to commit"). `git switch -c` does both steps at once; `git commit -am` stages *modified* files only, never new ones.
- A conflict only happens when **both** branches changed the **same** lines after they diverged. If `git merge` says "Fast-forward" or "Merge made by the 'ort' strategy" with no CONFLICT, `main` did not change that line: make a commit on `main` that touches the same line and merge again. Changing the same line of `hello.py` on both sides, as Demo 2 does with the `print(greet(...))` line, is the simplest shape; copy the shape, not the names or the identity: your branches must be `feature/<something>` (AC4) and your commits must carry your own name and e-mail, not the demo's (AC8).
- When the conflict appears, open the file in your editor and read both sides. Keep the lines you want, delete the `<<<<<<<`, `=======` and `>>>>>>>` lines, then `git add` and `git commit`. `git grep -n "<<<<<<<"` must print nothing before you commit. If you panic, `git merge --abort` returns you to before the merge, but an aborted merge does not count: do it again.
- Write the subject as the completion of "If applied, this commit will …": "Add greet function to hello.py", not "added greet" or "fix". Keep it around 50 characters, then a blank line, then a sentence on *why*. `git log --oneline` shows only the subject, which is exactly what a reviewer scans first. `git commit` without `-m` opens an editor for the body; if it is Vim, type `i` to edit, `Esc`, then `:wq` to save and exit.
- Story points are relative effort, not hours. Pick the easiest backlog item as your reference (a 1 or 2) and size the others by asking "is this about twice that, or five times?" Put "this exercise" in the table at whatever it felt like after you finished, and say in one sentence why.
- First push over HTTPS opens a Git Credential Manager browser window: sign in there, never type your GitHub password into the terminal (GitHub rejects it). If `python` opens the Microsoft Store, use `py` or turn off the App execution alias; if you see `>>>`, you are in the REPL, type `exit()` and run shell commands in PowerShell.
