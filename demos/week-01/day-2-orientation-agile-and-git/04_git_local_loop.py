"""04_git_local_loop.py - the local Git loop, driven from Python so every
command and its output lands on the projector in order.

PURPOSE
  Explain the three generations of version control, then run the real git
  commands in a throw-away temp folder: init -> add -> commit -> log, a
  feature branch merged fast-forward, and a genuine conflict resolved by
  hand. Each printed `$ git ...` line is exactly what trainees type next in
  PowerShell against their own folder.

RUN
  python 04_git_local_loop.py        # needs git on PATH (exits 0 with a message if not)

EXPECTED OUTPUT (commit hashes and the temp path differ every run)
  Version control generations: three lines; Three states: modified -> staged -> committed
  $ git init                       Initialized empty Git repository in ...
  $ git commit -m "add hello script"   [main (root-commit) xxxxxxx] add hello script
  $ git switch -c feature          Switched to a new branch 'feature'
  $ git merge feature              Fast-forward ... 1 file changed
  $ git merge greeting             CONFLICT (content): Merge conflict in hello.py
  <<<<<<< HEAD / ======= / >>>>>>> greeting markers, resolving commit, log --graph
"""

import os, shutil, stat, subprocess, sys, tempfile
from pathlib import Path

if shutil.which("git") is None:
    print("git is not on PATH - install Git for Windows, reopen PowerShell, rerun.")
    sys.exit(0)

# Identity + default branch passed with -c so the demo never hits "Author identity unknown".
GIT = ["git", "-c", "user.name=Trainee", "-c", "user.email=trainee@example.com",
       "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false"]


def git(*args, cwd, ok=True):
    """Print the command the way a trainee types it, run it, print what git said."""
    print("\n$ git", " ".join(f'"{a}"' if " " in a else a for a in args))
    r = subprocess.run([*GIT, *args], cwd=cwd, capture_output=True, text=True)
    print((r.stdout + r.stderr).rstrip())
    if ok and r.returncode:
        sys.exit(f"unexpected git failure (exit {r.returncode})")


def edit(path, text):
    print(f"\n# edit {path.name}:  {text.strip()!r}")
    path.write_text(text)


# --- STEP 1: why git - local vs centralised vs distributed, and the three states ---
print("Version control generations:")
print("  local       (RCS)             history on one machine, one file at a time")
print("  centralised (CVS, Subversion) one server holds history; clients check out a copy")
print("  distributed (Git, Mercurial)  every clone mirrors the FULL history; only push/pull need the network")
print("Three states: modified (working tree) -> staged (index) -> committed (.git)")
repo = Path(tempfile.mkdtemp(prefix="w01d2-git-")).resolve()
hello = repo / "hello.py"

# --- STEP 2: git init, create a file, git status, git add, git commit, git log ---
git("init", cwd=repo)
edit(hello, 'print("hello")\n')
git("status", cwd=repo)
git("add", "hello.py", cwd=repo)
git("commit", "-m", "add hello script", cwd=repo)
git("log", "--oneline", cwd=repo)

# --- STEP 3: branch, commit on it, switch back, merge (fast-forward) ---
git("switch", "-c", "feature", cwd=repo)
edit(hello, 'print("hello")\nprint("from feature")\n')
git("commit", "-am", "greet from feature", cwd=repo)
git("switch", "main", cwd=repo)
git("merge", "feature", cwd=repo)
git("log", "--oneline", cwd=repo)

# --- STEP 4: force a conflict - same line changed on both branches - and resolve it ---
git("switch", "-c", "greeting", cwd=repo)
edit(hello, 'print("bonjour")\nprint("from feature")\n')
git("commit", "-am", "say bonjour", cwd=repo)
git("switch", "main", cwd=repo)
edit(hello, 'print("hola")\nprint("from feature")\n')
git("commit", "-am", "say hola", cwd=repo)
git("merge", "greeting", cwd=repo, ok=False)
print("\n# hello.py now contains conflict markers:\n" + hello.read_text())
edit(hello, 'print("hola / bonjour")\nprint("from feature")\n')   # keep both: the human decides
git("add", "hello.py", cwd=repo)
git("commit", "-m", "merge greeting: keep both greetings", cwd=repo)
git("log", "--oneline", "--graph", cwd=repo)

shutil.rmtree(repo, onexc=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))
print("\n(temp repo deleted - now do STEPS 2-4 yourself in a fresh folder)")
