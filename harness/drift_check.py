#!/usr/bin/env python3
"""Drift check: read-only report of repo state that has drifted from the rules (D-0052).

Run it before every push. It never writes to any of the three repos (root, trainer/, demo-repo/).

Checks (each a function taking the repo root, so tests can point it at a temporary tree):
  decisions  HARD  decisions/README.md index rows and the D-NNNN-*.md files are the same set,
                   IDs run from D-0001 with no gap, every row's Status is proposed|accepted|superseded
  markers    HARD  `TBD` / `OWED` in prose (case-sensitive)
             SOFT  `pending` / `blocked until` in prose (case-insensitive)
                   scans *.md at the root and under docs/, harness/, trainer/ plus docs/**/*.html;
                   code fences, code spans, and in HTML script/style/pre/code elements, comments and
                   tags with their attributes are stripped first (so an attribute value never matches)
                   (root-level .html is never scanned, so the generated tracker.html is not either)
  git        HARD  untracked files and deletions in the root repo, trainer/ and demo-repo/
             SOFT  a repo that is absent or has no .git (it was not checked)
  curriculum HARD  a taught day without trainer/<rel>/delivery.json or a `## Delivery record` in its
                   runbook, a taught day whose status is not live
  tracker    HARD  tracker.html missing or stale (real repo with trainer/ only)
  projects   HARD  build_projects.check() problems (spec grammar, stale or unexpected pages) for projects/ (skipped
                   when projects/ is absent; SOFT if build_projects.py cannot be imported)
  notes      HARD  notes_check.py --all-authored --json findings: every authored or live page is swept
                   (D-0052); dead links are SOFT unless --strict (real repo only)

Usage:
    python harness/drift_check.py [--root DIR] [--strict] [--no-git] [--no-links] [--no-notes]
                                  [--no-markers] [--no-tracker] [--no-projects] [--json]

Prints one line per finding (`HARD <check>: <detail>` / `SOFT <check>: <detail>`) and a summary line,
or with --json one JSON object. Exit code 1 iff any HARD finding, else 0.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

HARD, SOFT = "HARD", "SOFT"
STATUSES = ("proposed", "accepted", "superseded")
ROW_RE = re.compile(r"^\| (D-\d{4}) \| ([^|]*?) \| ([^|]*?) \|")
FILE_RE = re.compile(r"^(D-\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")

EXCLUDED_DIRS = {"decisions", "Reference-Example", "demo-repo", ".git", "__pycache__", "node_modules"}
MD_SCAN_DIRS = ("docs", "harness", "trainer", "projects")
HARD_MARKERS = [("TBD", re.compile(r"\bTBD\b")), ("OWED", re.compile(r"\bOWED\b"))]
SOFT_MARKERS = [("pending", re.compile(r"\bpending\b", re.I)), ("blocked until", re.compile(r"blocked until", re.I))]

DELIVERY_HEADING = "## Delivery record"


def finding(level: str, check: str, detail: str) -> dict:
    return {"level": level, "check": check, "detail": detail}


# ---------------------------------------------------------------- 1. decisions
def check_decisions(root: Path) -> list[dict]:
    ddir = root / "decisions"
    index = ddir / "README.md"
    if not index.is_file():
        return [finding(HARD, "decisions", "decisions/README.md is missing")]
    out = []
    rows = []
    for ln in index.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(ln)
        if m:
            rows.append((m.group(1), m.group(3).strip()))
    files = {}
    for p in ddir.glob("D-*.md"):
        m = FILE_RE.match(p.name)
        if m:
            files[m.group(1)] = p.name
        else:
            out.append(finding(HARD, "decisions", f"entry file name is not D-NNNN-<slug>.md: {p.name}"))
    row_ids = [r[0] for r in rows]
    for eid in sorted({i for i in row_ids if row_ids.count(i) > 1}):
        out.append(finding(HARD, "decisions", f"{eid} appears more than once in the index"))
    for eid in sorted(set(row_ids) - set(files)):
        out.append(finding(HARD, "decisions", f"{eid} is in the index but has no entry file"))
    for eid in sorted(set(files) - set(row_ids)):
        out.append(finding(HARD, "decisions", f"{eid} has an entry file ({files[eid]}) but no index row"))
    nums = sorted({int(i[2:]) for i in set(row_ids) | set(files)})
    if nums:
        missing = sorted(set(range(1, nums[-1] + 1)) - set(nums))
        for n in missing:
            out.append(finding(HARD, "decisions", f"gap in IDs: D-{n:04d} is missing (IDs run from D-0001)"))
    for eid, status in rows:
        if status not in STATUSES:
            out.append(finding(HARD, "decisions", f"{eid} status {status!r} is not one of {'|'.join(STATUSES)}"))
    return out


# ---------------------------------------------------------------- 2. markers
def _blank(m: re.Match) -> str:
    """Replacement that keeps only the newlines, so line numbers survive the strip."""
    return "\n" * m.group(0).count("\n")


def _space(m: re.Match) -> str:
    return re.sub(r"[^\n]", " ", m.group(0))


FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
HTML_ELEMENTS_RE = re.compile(r"<(script|style|pre|code)\b[^>]*>.*?</\1\s*>", re.S | re.I)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
HTML_TAG_RE = re.compile(r"<[!/?]?[A-Za-z][^>]*>", re.S)


def strip_markdown(text: str) -> str:
    """Blank fenced code blocks and inline code spans; line count is unchanged."""
    lines = text.split("\n")
    out = []
    fence = None
    for ln in lines:
        m = FENCE_RE.match(ln)
        if fence is None:
            if m:
                fence = m.group(1)
                out.append("")
                continue
            out.append(CODE_SPAN_RE.sub(_space, ln))
        else:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not ln.strip()[len(m.group(1)):].strip():
                fence = None
            out.append("")
    return "\n".join(out)


def strip_html(text: str) -> str:
    """Blank script/style/pre/code elements, comments and every tag (with attributes); line count is unchanged."""
    text = HTML_COMMENT_RE.sub(_blank, text)
    text = HTML_ELEMENTS_RE.sub(_blank, text)
    return HTML_TAG_RE.sub(_space, text)


def _excluded(rel: Path) -> bool:
    if any(p in EXCLUDED_DIRS for p in rel.parts):
        return True
    if rel.parent.as_posix() == "docs/process" and "catalog" in rel.name:
        return True
    return False


def marker_files(root: Path) -> list[Path]:
    found = set(root.glob("*.md"))
    for d in MD_SCAN_DIRS:
        if (root / d).is_dir():
            found.update((root / d).rglob("*.md"))
    if (root / "docs").is_dir():
        found.update((root / "docs").rglob("*.html"))
    return sorted(p for p in found if p.is_file() and not _excluded(p.relative_to(root)))


def scan_text(text: str, html: bool) -> list[tuple[int, str, str]]:
    """(line number, level, marker) for every marker hit in the prose of `text`."""
    clean = strip_html(text) if html else strip_markdown(text)
    hits = []
    for n, ln in enumerate(clean.split("\n"), 1):
        for name, rx in HARD_MARKERS:
            if rx.search(ln):
                hits.append((n, HARD, name))
        for name, rx in SOFT_MARKERS:
            if rx.search(ln):
                hits.append((n, SOFT, name))
    return hits


def check_markers(root: Path) -> list[dict]:
    out = []
    for p in marker_files(root):
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            out.append(finding(SOFT, "markers", f"{p.relative_to(root).as_posix()}: unreadable ({e.__class__.__name__})"))
            continue
        rel = p.relative_to(root).as_posix()
        for n, level, name in scan_text(text, p.suffix.lower() == ".html"):
            out.append(finding(level, "markers", f"{rel}:{n}: {name}"))
    return out


# ---------------------------------------------------------------- 3. git
def classify_porcelain(line: str) -> str | None:
    """'untracked' | 'deleted' | None for one `git status --porcelain` line (XY code, space, path).
    A D in either column is a deletion (' D', 'D ', 'MD', 'AD', 'RD', ...)."""
    code = line[:2]
    if len(code) < 2:
        return None
    if code == "??":
        return "untracked"
    if code[0] == "D" or code[1] == "D":
        return "deleted"
    return None


def check_git(root: Path) -> list[dict]:
    out = []
    repos = [("root", root), ("trainer", root / "trainer"), ("demo-repo", root / "demo-repo")]
    for name, d in repos:
        if not d.is_dir():
            out.append(finding(SOFT, "git", f"{name}: {d} is absent, not checked"))
            continue
        if not (d / ".git").exists():
            out.append(finding(SOFT, "git", f"{name}: not a git repository ({d}), not checked"))
            continue
        try:
            res = subprocess.run(["git", "-C", str(d), "status", "--porcelain", "--untracked-files=all"],
                                 capture_output=True, text=True, encoding="utf-8", errors="replace")
        except OSError as e:
            out.append(finding(SOFT, "git", f"{name}: git not runnable ({e.__class__.__name__})"))
            continue
        if res.returncode != 0:
            out.append(finding(HARD, "git", f"{name}: git status failed: {res.stderr.strip()}"))
            continue
        for ln in res.stdout.splitlines():
            kind = classify_porcelain(ln)
            if kind:
                out.append(finding(HARD, "git", f"{name}: {kind} {ln[3:]}"))
    return out


# ---------------------------------------------------------------- 4. curriculum
def check_curriculum(root: Path) -> list[dict]:
    cur_path = root / "harness" / "curriculum.json"
    if not cur_path.is_file():
        return [finding(HARD, "curriculum", "harness/curriculum.json is missing")]
    cur = json.loads(cur_path.read_text(encoding="utf-8"))
    trainer = root / "trainer"
    have_trainer = trainer.is_dir()
    out = []
    taught_any = False
    for w in cur.get("weeks", []):
        for d in w.get("days", []):
            if d.get("kind") == "holiday" or not d.get("taught"):
                continue
            taught_any = True
            rel = f"{w['dir']}/{d['slug']}"
            label = d.get("id") or rel
            if d.get("status") != "live":
                out.append(finding(HARD, "curriculum", f"{label} is taught ({d['taught']}) but its status is {d.get('status')!r}, not live"))
            if not have_trainer:
                continue
            if not (trainer / rel / "delivery.json").is_file():
                out.append(finding(HARD, "curriculum", f"{label} is taught but trainer/{rel}/delivery.json is missing (run close_day.py)"))
            runbook = trainer / rel / "runbook.md"
            if not runbook.is_file():
                out.append(finding(HARD, "curriculum", f"{label} is taught but trainer/{rel}/runbook.md is missing"))
            elif DELIVERY_HEADING not in runbook.read_text(encoding="utf-8"):
                out.append(finding(HARD, "curriculum", f"{label} is taught but trainer/{rel}/runbook.md has no '{DELIVERY_HEADING}'"))
    if taught_any and not have_trainer:
        out.append(finding(SOFT, "curriculum", "trainer/ is absent: delivery.json and Delivery record not checked"))
    return out


# ---------------------------------------------------------------- 5. tracker (real repo only)
def check_tracker(root: Path) -> list[dict]:
    if not (root / "trainer").is_dir():
        return [finding(SOFT, "tracker", "trainer/ is absent: tracker not checked")]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import build_tracker  # noqa: E402  (reads no clock, writes nothing when only expected() is called)
    want = build_tracker.expected()
    path = root / "tracker.html"
    if not path.is_file():
        return [finding(HARD, "tracker", "tracker.html is missing; run python harness/build_tracker.py")]
    if path.read_text(encoding="utf-8") != want:
        return [finding(HARD, "tracker", "tracker.html is stale; run python harness/build_tracker.py")]
    return []


# ---------------------------------------------------------------- 5b. projects
def check_projects(root: Path) -> list[dict]:
    if not (root / "projects").is_dir():
        return []
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    try:
        import build_projects  # noqa: E402
    except ImportError:
        return [finding(SOFT, "projects", "harness/build_projects.py is missing or cannot be imported: projects not checked")]
    try:
        lines = build_projects.check(root)  # check() = validate() + stale/unexpected pages
    except ModuleNotFoundError as err:  # the page renderer needs the `markdown` package (requirements-dev.txt)
        return [finding(SOFT, "projects", f"{err}: projects pages not checked (py -m pip install -r requirements-dev.txt)")]
    return [finding(HARD, "projects", f"{line} (run: python harness/build_projects.py)") for line in lines]


# ---------------------------------------------------------------- 6. notes (real repo only)
def parse_notes_output(stdout: str, strict: bool) -> list[dict]:
    """Findings from notes_check.py --json: one JSON object whose pages[].findings lists each finding's text."""
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    if not lines:
        return [finding(HARD, "notes", "notes_check.py printed nothing")]
    try:
        summary = json.loads(lines[-1])
    except ValueError:
        return [finding(HARD, "notes", f"notes_check.py last line is not JSON: {lines[-1][:120]}")]
    out = []
    for p in summary.get("pages", []):
        texts = p.get("findings", [])
        if not isinstance(texts, list):
            return [finding(HARD, "notes", "notes_check.py summary has no findings list (old notes_check.py?)")]
        for text in texts:
            level = SOFT if str(text).startswith("dead link") and not strict else HARD
            out.append(finding(level, "notes", f"{p.get('page', '?')}: {text}"))
    if not summary.get("ok", False) and not out:
        out.append(finding(HARD, "notes", "notes_check.py reports failures but lists no finding"))
    return out


def check_notes(root: Path, links: bool = True, strict: bool = False) -> list[dict]:
    cmd = [sys.executable, str(root / "harness" / "notes_check.py"), "--all-authored",
           "--counts", "--phrases", "--stamps", "--citations", "--style"] + (["--links"] if links else []) + ["--json"]
    res = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode == 2:
        return [finding(SOFT, "notes", "notes_check.py found no authored or live pages")]
    return parse_notes_output(res.stdout, strict)


# ---------------------------------------------------------------- driver
def run(root: Path, real: bool, strict: bool = False, git: bool = True, links: bool = True, notes: bool = True,
        markers: bool = True, tracker: bool = True, projects: bool = True) -> list[dict]:
    out = check_decisions(root)
    if markers:
        out += check_markers(root)
    if git:
        out += check_git(root)
    out += check_curriculum(root)
    if projects:
        out += check_projects(root)
    if real and tracker:
        out += check_tracker(root)
    if real and notes:
        out += check_notes(root, links=links, strict=strict)
    return out


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    args = list(argv)
    if "-h" in args or "--help" in args:
        print(__doc__)
        return 0
    root, real = REPO_ROOT, True
    if "--root" in args:
        i = args.index("--root")
        if i + 1 >= len(args):
            print("--root needs a directory", file=sys.stderr)
            return 2
        root, real = Path(args[i + 1]).resolve(), False
        del args[i:i + 2]
    known = {"--strict", "--no-git", "--no-links", "--no-notes", "--no-markers", "--no-tracker", "--no-projects", "--json"}
    unknown = [a for a in args if a not in known]
    if unknown:
        print(f"unknown arguments: {' '.join(unknown)}", file=sys.stderr)
        return 2
    flags = set(args)
    found = run(root, real, strict="--strict" in flags, git="--no-git" not in flags, links="--no-links" not in flags,
                notes="--no-notes" not in flags, markers="--no-markers" not in flags, tracker="--no-tracker" not in flags,
                projects="--no-projects" not in flags)
    hard = sum(1 for f in found if f["level"] == HARD)
    soft = len(found) - hard
    if "--json" in flags:
        print(json.dumps({"ok": hard == 0, "hard": hard, "soft": soft, "findings": found}, ensure_ascii=False))
    else:
        for f in found:
            print(f"{f['level']} {f['check']}: {f['detail']}")
        print(f"drift check: {hard} hard, {soft} soft ({'FAIL' if hard else 'OK'})")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
