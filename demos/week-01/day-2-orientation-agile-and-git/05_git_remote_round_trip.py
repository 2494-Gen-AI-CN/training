"""05_git_remote_round_trip.py - push to a remote, a teammate pushes too,
then pull: fetch + merge, shown for real without the network.

PURPOSE
  Stand in for GitHub with a local bare repository, then walk the remote loop
  exactly as it goes on GitHub: `git push` fails until a remote exists, then
  `git remote add origin` + `git push -u origin main`, a second clone (the
  teammate) pushes a commit, and `git fetch` vs `git pull` show that pull is
  fetch followed by merge. Each `$ git ...` line is what trainees type next
  against their own empty GitHub repo.

RUN
  python 05_git_remote_round_trip.py   # needs git on PATH (exits 0 with a message if not)

EXPECTED OUTPUT (commit hashes and temp paths differ every run)
  $ git push                       fatal: No configured push destination ...
  $ git remote add origin ...      (silent)
  $ git remote -v                  origin  ...origin.git (fetch) / (push)
  $ git push -u origin main        branch 'main' set up to track 'origin/main'.
  $ git clone ... teammate         Cloning into 'teammate'...
  $ git push                       (teammate) main -> main
  $ git fetch                      xxxxxxx..yyyyyyy  main -> origin/main
  $ git log --oneline main..origin/main   yyyyyyy teammate adds README
  $ git pull                       Fast-forward ... README.md | 1 +
  $ git log --oneline              both commits
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

if shutil.which("git") is None:
    print("git is not on PATH - install Git for Windows, reopen PowerShell, rerun.")
    sys.exit(0)

GIT = ["git", "-c", "user.name=Trainee", "-c", "user.email=trainee@example.com",
       "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false"]


def git(*args, cwd, ok=True):
    """Print the command the way a trainee types it, run it, print what git said."""
    print("\n$ git", " ".join(f'"{a}"' if " " in a else a for a in args))
    r = subprocess.run([*GIT, *args], cwd=cwd, capture_output=True, text=True)
    print((r.stdout + r.stderr).rstrip())
    if ok and r.returncode:
        sys.exit(f"unexpected git failure (exit {r.returncode})")


work = Path(tempfile.mkdtemp(prefix="w01d2-remote-")).resolve()
mine, origin, teammate = work / "mine", work / "origin.git", work / "teammate"
mine.mkdir()

# --- STEP 1: a local repo with one commit, and the pitfall: push with no remote ---
git("init", cwd=mine)
(mine / "hello.py").write_text('print("hello")\n')
git("add", "hello.py", cwd=mine)
git("commit", "-m", "add hello script", cwd=mine)
git("push", cwd=mine, ok=False)                     # "No configured push destination"

# --- STEP 2: create the remote (GitHub stand-in), git remote add origin, git push -u ---
git("init", "--bare", str(origin), cwd=work)         # GitHub's "New repository" button
git("remote", "add", "origin", origin.as_posix(), cwd=mine)
git("remote", "-v", cwd=mine)
git("push", "-u", "origin", "main", cwd=mine)       # -u: later push/pull need no arguments

# --- STEP 3: a teammate clones, commits, pushes (same as editing on the GitHub web UI) ---
git("clone", origin.as_posix(), "teammate", cwd=work)
(teammate / "README.md").write_text("# hello\n")
git("add", "README.md", cwd=teammate)
git("commit", "-m", "teammate adds README", cwd=teammate)
git("push", cwd=teammate)

# --- STEP 4: back home - fetch downloads history, pull = fetch + merge ---
git("fetch", cwd=mine)                               # history arrives, working tree untouched
print("\n# files in my working tree after fetch:", sorted(p.name for p in mine.iterdir() if p.name != ".git"))
git("log", "--oneline", "main..origin/main", cwd=mine)   # what origin has that I do not
git("pull", cwd=mine)
print("\n# files in my working tree after pull: ", sorted(p.name for p in mine.iterdir() if p.name != ".git"))
git("log", "--oneline", cwd=mine)

shutil.rmtree(work, onexc=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))
print("\n(temp repos deleted - now repeat STEPS 2 and 4 against your own empty GitHub repo)")
