"""04 - The local Git loop, replayed from one file: init, add, commit, branch,
fast-forward merge, then one real conflict resolved by hand.

PURPOSE
  Every git command is printed as `$ git ...` and run for real (subprocess) in
  a temporary folder, with `git status` after each step so the three states
  (modified / staged / committed) stay visible. Trainees then repeat the same
  STEPs by hand in PowerShell.

EXPECTED OUTPUT (commit hashes and the temp path differ every run)
  STEP 1  "Initialized empty Git repository", status: "No commits yet"
  STEP 2  status shows hello.py and .gitignore untracked, then staged,
          then "1 file changed"x2 in the commit; log has one line
  STEP 3  "Switched to a new branch 'feature'", one commit, switch back,
          merge reports "Fast-forward"; log has two lines
  STEP 4  merge reports "CONFLICT (content): Merge conflict in hello.py",
          the file is printed with <<<<<<< ======= >>>>>>> markers, resolved,
          committed; `log --graph` shows the merge commit with two parents
"""
import os
import shutil
import stat
import subprocess
import sys
import tempfile

IDENTITY = ["-c", "user.name=Demo Trainer", "-c", "user.email=trainer@example.com",
            "-c", "init.defaultBranch=main", "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false"]
if shutil.which("git") is None:
    print("git is not on PATH: install Git for Windows, reopen PowerShell, re-run")
    sys.exit(0)
REPO = os.path.realpath(tempfile.mkdtemp(prefix="w01d2-git-"))


def git(*args):
    print("\n$ git " + " ".join(f'"{a}"' if " " in a else a for a in args))
    r = subprocess.run(["git", *IDENTITY, *args], cwd=REPO, text=True, capture_output=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print("  " + out.replace("\n", "\n  "))


def write(name, text):
    with open(os.path.join(REPO, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"\n(edit) {name} is now:\n  " + text.rstrip().replace("\n", "\n  "))


# --- STEP 1: git init - a distributed VCS: the whole history lives in .git ---
print("STEP 1  local (RCS) -> centralised (SVN) -> distributed (Git): every clone")
print("        holds the full history, so everything below works offline. Repo:", REPO)
git("init")
git("status")

# --- STEP 2: untracked -> staged -> committed, with git status at each state ---
write("hello.py", 'print("Hello, team")\n')
write(".gitignore", "__pycache__/\n*.pyc\n.venv/\n")
git("status", "--short")            # ?? = untracked: git knows nothing about them
git("add", ".")
git("status", "--short")            # A  = staged, ready for the snapshot
git("commit", "-m", "Add hello script and Python .gitignore")
git("log", "--oneline")

# --- STEP 3: a feature branch and a fast-forward merge ---
git("switch", "-c", "feature")     # creates AND switches (git branch alone does not)
write("hello.py", 'print("Hello, team")\n\n\ndef greet(name):\n    return f"Hello, {name}"\n')
git("commit", "-am", "Add greet function to hello.py")
git("switch", "main")
git("merge", "feature")             # main had no new commits -> pointer just moves
git("log", "--oneline")

# --- STEP 4: force a real conflict on the same line, resolve it, commit ---
git("switch", "-c", "greeting")
write("hello.py", 'print("Hello, Toronto")\n\n\ndef greet(name):\n    return f"Hello, {name}"\n')
git("commit", "-am", "Greet Toronto instead of the team")
git("switch", "main")
write("hello.py", 'print("Hello, cohort 2494")\n\n\ndef greet(name):\n    return f"Hello, {name}"\n')
git("commit", "-am", "Greet the cohort by number")
git("merge", "greeting")            # both sides changed line 1 -> Git stops
with open(os.path.join(REPO, "hello.py"), encoding="utf-8") as f:
    print("\n(cat) hello.py with conflict markers:\n  " + f.read().rstrip().replace("\n", "\n  "))
print("\n(edit) keep the right lines, delete ALL THREE marker lines, then add + commit")
write("hello.py", 'print("Hello, cohort 2494 in Toronto")\n\n\ndef greet(name):\n    return f"Hello, {name}"\n')
git("add", "hello.py")
git("commit", "-m", "Merge branch 'greeting': combine both greetings on line 1")
git("log", "--oneline", "--graph")
shutil.rmtree(REPO, onexc=lambda fn, p, _: (os.chmod(p, stat.S_IWRITE), fn(p)))  # .git objects are read-only on Windows
print("\n(temp repo deleted) Now repeat STEPs 1-4 by hand in PowerShell: mkdir w01d2-git; cd w01d2-git; git init ...")
