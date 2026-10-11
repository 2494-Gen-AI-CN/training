"""05 - The remote round trip: push fails, remote added, push -u, a teammate
pushes, fetch vs pull, and the commit message the rubric wants.

PURPOSE
  A bare repository in a temp folder stands in for GitHub so the whole trip
  runs offline and for real. Trainees then do the same against an empty GitHub
  repo (the credential-manager browser prompt is the only extra step).

EXPECTED OUTPUT (hashes and temp paths differ every run)
  STEP 1  push fails: "fatal: No configured push destination."
  STEP 2  remote -v lists origin twice; push -u ends with
          "branch 'main' set up to track 'origin/main'."
  STEP 3  teammate clone: "Cloning into 'teammate'...", one commit pushed
  STEP 4  fetch changes nothing in the working tree; status says
          "Your branch is behind 'origin/main' by 1 commit"; log HEAD..origin/main
          lists exactly the teammate's commit; pull says
          "Fast-forward"; log now shows the teammate's commit on top
  STEP 5  two one-line logs side by side and the rubric rule for messages
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
BASE = os.path.realpath(tempfile.mkdtemp(prefix="w01d2-remote-"))
ME, HUB, MATE = (os.path.join(BASE, d) for d in ("me", "github.git", "teammate"))


def git(*args, cwd=None):
    print("\n$ git " + " ".join(f'"{a}"' if " " in a else a for a in args))
    r = subprocess.run(["git", *IDENTITY, *args], cwd=cwd or ME, text=True, capture_output=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print("  " + out.replace("\n", "\n  "))


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# --- STEP 1: a local repo with one commit; push has nowhere to go ---
os.makedirs(ME)
git("init")
write(os.path.join(ME, "README.md"), "# Team repo\n")
git("add", "README.md")
git("commit", "-m", "Add README")
git("push")                         # no remote yet -> the error trainees will see

# --- STEP 2: name a remote, push with -u so later push/pull need no arguments ---
git("init", "--bare", HUB, cwd=BASE)  # stands in for the empty repo you create on github.com
git("remote", "add", "origin", HUB)
git("remote", "-v")
git("push", "-u", "origin", "main")

# --- STEP 3: a teammate clones and pushes (same as editing on the GitHub web UI) ---
git("clone", HUB, "teammate", cwd=BASE)
write(os.path.join(MATE, "README.md"), "# Team repo\n\nStand-up at 9:15 daily.\n")
git("commit", "-am", "Add stand-up time to README", cwd=MATE)
git("push", cwd=MATE)

# --- STEP 4: fetch downloads history only; pull is fetch + merge ---
git("fetch")
git("status")                       # behind by 1, but README.md on disk is unchanged
git("log", "--oneline", "HEAD..origin/main")   # what origin has that we do not
git("pull")
git("log", "--oneline")
shutil.rmtree(BASE, onexc=lambda fn, p, _: (os.chmod(p, stat.S_IWRITE), fn(p)))  # .git objects are read-only on Windows

# --- STEP 5: the commit message the rubric marks ---
print("\nSTEP 5  `git log --oneline` shows ONLY the first line. Which log tells the story?")
print("        a1b2c3d fix                                 <- marked down")
print("        a1b2c3d Add greeting function to hello.py   <- full marks")
print("        Rule: imperative mood, ~50 chars, blank line, then WHY in the body.")
print("        Now do STEPs 1-4 for real: empty repo on github.com, remote add, push -u,")
print("        edit README in the web UI, then `git pull` and read the log.")
