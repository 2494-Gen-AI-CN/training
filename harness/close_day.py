#!/usr/bin/env python3
"""Close a delivered day: publish what was typed live and mark the day taught (D-0050).

The trainer types the day's code in the public demo repository (config.json `demoRepo`, cloned at
`demoRepo.localDir`, gitignored like trainer/). This script is the ONLY writer of `taught` in
curriculum.json. For a `demoFormat: "loose"` day (the trainer improvised; the authored scripts under
trainer/<rel>/demos/, if any, were the fallback and are never published) it:

  1. pins the day's commit (the newest commit of that date under <rel>/, else the last one before it)
     and finds the files committed under <rel>/ on that date that still exist there (or takes --files,
     relative paths inside <rel>/ only); everything is validated, the demo card included, before any write;
  2. flips the notes page's pending demo card to the file links, or to "No code demo this day";
  3. writes each file's content AT THAT COMMIT (`git show`, byte for byte, not the working tree) into
     demos/<rel>/ (subfolders kept, files no longer listed removed) and demos/<rel>/README.md listing
     them; a day with no files still gets the README. A README.md the trainer committed under <rel>/ is
     not published (a warning says so): the generated README takes that name;
  4. writes trainer/<rel>/delivery.json (day, date, format, files, demo repo URL and that commit, notes);
  5. sets `taught` on the day in curriculum.json;
  6. appends a "## Delivery record (<date>)" section to trainer/<rel>/runbook.md (once per date);
  7. splices the index block (as harness/build_index.py does), records a `manual` run in
     harness/runs.jsonl, rebuilds the tracker once, then prints the STATUS.md log line to paste.

Re-running with --apply converges: files are recopied, delivery.json rewritten, the runbook section
and the card are not duplicated. Thread days (py / nb: a rung diff against the demo repo) are not built
yet and are refused.

Usage:
    python harness/close_day.py <week> <day>                      # dry run: print the plan, change nothing
    python harness/close_day.py <week> <day> --apply              # do it
      [--date YYYY-MM-DD]   the day's date in the demo repo history (default: the day's calendar date)
      [--files f1 f2 ...]   paths under <rel>/ in the demo repo, instead of that date's commits
      [--notes "..."]       a line for delivery.json and the runbook record
      [--no-pull]           skip `git pull --ff-only` in the demo repo clone
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import publish_demos as pd  # noqa: E402

ROOT = bi.ROOT
TRAINER = pd.TRAINER
RUN_REPORT = ROOT / "harness" / "run-report.tmp.json"
RECORD_HEAD = "## Delivery record ({date})"


# ---------------------------------------------------------------- lookup
def locate(week_no: int, day_no: int):
    """(cur, week, day, rel, cfg) for a loose day; refuses every other demoFormat."""
    cfg, day, rel, cur, week = pd._locate(week_no, day_no)
    if day.get("demoFormat") != "loose":
        raise SystemExit(f"{day['id']} is demoFormat {day.get('demoFormat')!r}: thread-day close (rung diff against demo-repo) "
                         "is not built yet; see docs/process/codify-plan.md Stage 4 and STATUS.md O-18")
    return cur, week, day, rel, cfg


def _git(repo: Path, *args: str) -> str:
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {repo}:\n{(res.stderr or res.stdout).strip()}")
    return res.stdout


def is_git_repo(repo: Path) -> bool:
    return repo.is_dir() and (repo / ".git").exists()


def clone_hint(cfg: dict) -> str:
    dr = cfg["demoRepo"]
    return (f"{dr['localDir']}/ is not a clone of the demo repo ({dr['url']}). From the repo root run:\n"
            f"    gh repo clone {dr['org']}/{dr['name']} {dr['localDir']}")


def pull_repo(repo: Path) -> None:
    """Bring the clone up to date with what the trainer pushed (fast-forward only)."""
    _git(repo, "pull", "--ff-only")


def head_sha(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").strip()


def _excluded(name: str) -> bool:
    """Same exclusions as build_index.published_files: demos/<rel>/README.md is ours."""
    parts = name.split("/")
    return parts[-1] == "README.md" or "__pycache__" in parts


def _day_log(repo: Path, rel: str) -> list[tuple[str, str, list[str]]]:
    """(sha, author date YYYY-MM-DD, paths) for every commit touching <rel>, newest first."""
    out = _git(repo, "-c", "core.quotepath=off", "log", "--date=short", "--format=%x01%H %ad", "--name-only", "--", rel)
    commits: list[tuple[str, str, list[str]]] = []
    for line in out.splitlines():
        if line.startswith("\x01"):
            sha, _, when = line[1:].strip().partition(" ")
            commits.append((sha, when.strip(), []))
        elif line.strip() and commits:
            commits[-1][2].append(line.strip())
    return commits


def day_sha(repo: Path, rel: str, date: str) -> str:
    """The commit that holds <rel>/ as it stood at the end of `date`: the newest commit of that date touching
    <rel>, else the last one before it touching <rel>, else the repository's last commit by then, else HEAD
    (a repository created after the day; empty string for one with no commits)."""
    for sha, when, _ in _day_log(repo, rel):
        if when == date:
            return sha
    for scope in (["--", rel], []):
        before = _git(repo, "log", "-1", f"--until={date}T23:59:59", "--format=%H", *scope).strip()
        if before:
            return before
    res = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", "HEAD"], capture_output=True, text=True)
    return res.stdout.strip()


def tree_at(repo: Path, sha: str, rel: str) -> set[str]:
    """Files under <rel>/ at commit `sha`, relative to <rel>, posix."""
    if not sha:
        return set()
    out = _git(repo, "-c", "core.quotepath=off", "ls-tree", "-r", "--name-only", sha, "--", rel + "/")
    return {ln.strip()[len(rel) + 1:] for ln in out.splitlines() if ln.strip().startswith(rel + "/")}


def files_for(repo: Path, rel: str, date: str, sha: str | None = None) -> list[str]:
    """Paths under <rel>/ (relative to it, posix) committed on `date` that still exist at the day's commit."""
    sha = sha if sha is not None else day_sha(repo, rel, date)
    present = tree_at(repo, sha, rel)
    found = {p[len(rel) + 1:] for _, when, paths in _day_log(repo, rel) if when == date
             for p in paths if p.startswith(rel + "/")}
    return sorted(n for n in found if n in present and not _excluded(n))


def show_bytes(repo: Path, sha: str, path: str) -> bytes:
    """A file's content at a commit, byte for byte (binary safe)."""
    # cat-file, not `git show`: show also stats <sha>:<path> as a file name, which fails on long Windows paths
    res = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"{sha}:{path}"], capture_output=True)
    if res.returncode != 0:
        raise SystemExit(f"git cat-file blob {sha[:7]}:{path} failed in {repo}:\n{res.stderr.decode('utf-8', 'replace').strip()}")
    return res.stdout


def safe_names(repo: Path, rel: str, names: list[str]) -> list[str]:
    """Validate --files entries: relative paths that stay inside <repo>/<rel>/. SystemExit otherwise."""
    base = (repo / rel).resolve()
    out: set[str] = set()
    for raw in names:
        name = raw.replace("\\", "/").strip()
        pure = PurePosixPath(name)
        if not name or pure.is_absolute() or PureWindowsPath(raw).drive or PureWindowsPath(raw).is_absolute() \
                or ".." in pure.parts or ":" in name:
            raise SystemExit(f"--files entry {raw!r} must be a relative path under {rel}/ (no '..', no absolute path or drive)")
        target = (base / name).resolve()
        if target != base and base not in target.parents:
            raise SystemExit(f"--files entry {raw!r} resolves outside {rel}/")
        out.add(target.relative_to(base).as_posix())
    return sorted(out)


def readme_warning(present: set[str], rel: str, cfg: dict) -> str | None:
    if "README.md" in present:
        return (f"WARNING: {cfg['demoRepo']['localDir']} {rel}/README.md is not published; "
                "the generated README takes that name")
    return None


# ---------------------------------------------------------------- what gets written
def render_readme(day: dict, rel: str, date: str, files: list[str], url: str, branch: str = "main") -> str:
    lines = [f"# {day['title']} — files typed live", "",
             f"`{day['id']}` · the code typed in the session, copied from the demo repository after class.", ""]
    if files:
        lines += ["| # | File |", "|---|------|"]
        lines += [f"| {i} | `{f}` |" for i, f in enumerate(files, 1)]
    else:
        lines.append("No code demo this day.")
    lines += ["", f"Typed live on {date}; from {url.rstrip('/')}/tree/{branch}/{rel}"]
    return "\n".join(lines) + "\n"


def delivery_record(day: dict, date: str, files: list[str], cfg: dict, sha: str, notes: str | None) -> dict:
    return {"day": day["id"], "date": date, "format": "loose", "files": list(files),
            "demoRepo": cfg["demoRepo"]["url"], "demoRepoSha": sha, "notes": notes or ""}


def runbook_section(date: str, files: list[str], url: str, sha: str, rel: str, notes: str | None) -> str:
    typed = f"{', '.join(f'`{f}`' for f in files)} ({len(files)})" if files else "none"
    return (f"\n{RECORD_HEAD.format(date=date)}\n\n"
            "- Format: loose (the trainer improvised; the authored scripts were the fallback)\n"
            f"- Files typed live: {typed}\n"
            f"- Demo repo: {url.rstrip('/')}/tree/{sha}/{rel}\n"
            f"- Notes: {notes or 'none'}\n")


def append_runbook(path: Path, section: str, date: str) -> bool:
    """Append the section unless this date's record is already there. True when written."""
    text = path.read_text(encoding="utf-8")
    if RECORD_HEAD.format(date=date) in text:
        return False
    path.write_text(text.rstrip("\n") + "\n" + section, encoding="utf-8", newline="\n")
    return True


def card_plan(html: str | None, files: list[str], cfg: dict, rel: str) -> tuple[str, str | None]:
    """(card action, flipped page or None), decided before anything is written.

    A pending card that cannot be flipped (e.g. its "Published after class" line is gone) stops the close
    here, so a day is never left half closed. Comments are ignored when looking for a card.
    """
    if html is None:
        return "no notes page", None
    live = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    if pd.CARD_PENDING in live:
        try:
            if files:
                new = pd.flip_card(html, cfg["repoUrl"], cfg.get("repoBranch", "main"), rel, files, meta=pd.LOOSE_META)
            else:
                new = pd.flip_card_none(html)
        except ValueError as e:
            raise SystemExit(f"docs/weeks/{rel}.html: the pending demo card cannot be flipped ({e}); "
                             "fix the page first. Nothing was written.")
        return ("flip to links" if files else "flip to none"), new
    if pd.CARD_PUBLISHED in live or pd.CARD_NONE in live:
        return "already flipped", None
    return "no demo card", None


# ---------------------------------------------------------------- plan / apply
def plan(week_no: int, day_no: int, date: str | None = None, files: list[str] | None = None,
         notes: str | None = None, pull: bool = True) -> dict:
    """Everything the close will do, validated; writes nothing (except the optional git pull)."""
    cur, week, day, rel, cfg = locate(week_no, day_no)
    repo = ROOT / cfg["demoRepo"]["localDir"]
    if not is_git_repo(repo):
        raise SystemExit(clone_hint(cfg))
    if not TRAINER.exists():
        raise SystemExit("trainer/ (the private repo) is not cloned here; delivery.json and the runbook record live there")
    if pull:
        pull_repo(repo)
    slot = bi.slot_date(cur, week_no, day_no)
    date = date or slot.isoformat()
    try:
        when = dt.date.fromisoformat(date)
    except ValueError:
        raise SystemExit(f"--date must be YYYY-MM-DD, got {date!r}")
    if when < slot:
        raise SystemExit(f"{day['id']} is on {slot.isoformat()}; it cannot be taught on {date}")
    # content as of the end of the day, not HEAD
    sha = day_sha(repo, rel, date)
    present = tree_at(repo, sha, rel)
    if files is None:
        files = files_for(repo, rel, date, sha)
    else:
        files = safe_names(repo, rel, files)
        generated = [f for f in files if _excluded(f)]
        if generated:
            raise SystemExit(f"--files cannot publish {', '.join(generated)}: README.md is generated and __pycache__ is skipped")
        missing = [f for f in files if f not in present]
        if missing:
            raise SystemExit(f"not in {cfg['demoRepo']['localDir']}/{rel}/ at {sha[:7] or '(no commit)'}: {', '.join(missing)}")
    if notes is None:  # a re-run without --notes keeps the notes of an earlier close of the same date
        prev = TRAINER / rel / "delivery.json"
        if prev.is_file():
            old = json.loads(prev.read_text(encoding="utf-8"))
            notes = old.get("notes", "") if old.get("date") == date else None
    page = ROOT / "docs" / "weeks" / f"{rel}.html"
    card, page_html = card_plan(page.read_text(encoding="utf-8") if page.exists() else None, files, cfg, rel)
    warnings = [w for w in [readme_warning(present, rel, cfg)] if w]
    return {"cur": cur, "week": week, "day": day, "rel": rel, "cfg": cfg, "repo": repo, "date": date,
            "files": files, "sha": sha, "notes": notes or "", "url": cfg["demoRepo"]["url"],
            "page": page, "card": card, "page_html": page_html, "warnings": warnings}


def describe(p: dict) -> list[str]:
    rel, files = p["rel"], p["files"]
    out = list(p["warnings"])
    out += [f"{p['day']['id']} ({rel}), demoFormat loose, taught {p['date']}"
            + (f" (already taught {p['day']['taught']})" if p["day"].get("taught") else ""),
            f"demo repo {p['repo'].name}@{p['sha'][:7] or '(no commit)'} ({p['url']}): {rel}/ as of the end of {p['date']}"]
    if files:
        out += [f"copy {p['repo'].name}/{rel}/{f} @ {p['sha'][:7]} -> demos/{rel}/{f}" for f in files]
    else:
        out.append(f"no files committed under {rel}/ on {p['date']}: README only, card says no code demo")
    stale = [f.relative_to(ROOT / "demos" / rel).as_posix() for f in bi.published_files(ROOT / "demos" / rel)]
    out += [f"remove demos/{rel}/{f} (not typed on {p['date']})" for f in stale if f not in files]
    out += [f"demo card: {p['card']}",
            f"write demos/{rel}/README.md, trainer/{rel}/delivery.json",
            f"set taught={p['date']} on {p['day']['id']} in harness/curriculum.json",
            f"runbook: append '{RECORD_HEAD.format(date=p['date'])}'" if (TRAINER / rel / "runbook.md").exists() else "runbook: none on disk",
            "then: index block, a manual run record, one tracker rebuild"]
    return out


def apply(p: dict) -> list[str]:
    day, rel, files, date, cfg, repo, sha = p["day"], p["rel"], p["files"], p["date"], p["cfg"], p["repo"], p["sha"]
    out: list[str] = list(p["warnings"])
    # read every file's content at the day's commit before writing anything
    content = {name: show_bytes(repo, sha, f"{rel}/{name}") for name in files}
    # (1) the notes page's demo card (validated in plan)
    card = {"flip to links": "flipped to links", "flip to none": "flipped to none"}.get(p["card"], p["card"])
    if p["page_html"] is not None:
        p["page"].write_text(p["page_html"], encoding="utf-8", newline="\n")
    out.append(f"demo card {card}")
    # (2) demos/<rel>/: exactly the day's files plus README.md
    pub = ROOT / "demos" / rel
    pub.mkdir(parents=True, exist_ok=True)
    for f in bi.published_files(pub):
        if f.relative_to(pub).as_posix() not in files:
            f.unlink()
            out.append(f"removed demos/{rel}/{f.relative_to(pub).as_posix()}")
    for d in sorted((x for x in pub.rglob("*") if x.is_dir()), key=lambda x: len(x.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    for name, data in content.items():
        tgt = pub / name
        tgt.parent.mkdir(parents=True, exist_ok=True)
        tgt.write_bytes(data)
    out.append(f"copied {len(files)} file(s) to demos/{rel}/ from {repo.name}@{sha[:7]}")
    (pub / "README.md").write_text(render_readme(day, rel, date, files, cfg["demoRepo"]["url"], cfg["demoRepo"].get("branch", "main")),
                                   encoding="utf-8", newline="\n")
    # (3) the delivery record in the private repo
    rec_path = TRAINER / rel / "delivery.json"
    rec_path.parent.mkdir(parents=True, exist_ok=True)
    rec_path.write_text(json.dumps(delivery_record(day, date, files, cfg, sha, p["notes"]), indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")
    out.append(f"wrote trainer/{rel}/delivery.json")
    # (4) taught (this script is its only writer); byte-exact round trip of curriculum.json
    day["taught"] = date
    with open(bi.CURRICULUM, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(p["cur"], indent=2, ensure_ascii=False) + "\n")
    out.append(f"set taught={date} on {day['id']}")
    # (5) runbook record
    rb = TRAINER / rel / "runbook.md"
    if rb.exists():
        wrote = append_runbook(rb, runbook_section(date, files, cfg["demoRepo"]["url"], sha, rel, p["notes"]), date)
        out.append("runbook Delivery record " + ("appended" if wrote else "already there"))
    # (6) index block, in process (build_index.main would also rebuild the tracker; that happens once, below)
    html = bi.INDEX.read_text(encoding="utf-8")
    new_html = bi.splice(html, bi.render())
    if new_html != html:
        bi.INDEX.write_text(new_html, encoding="utf-8", newline="\n")
        out.append("docs/index.html updated")
    # (7) manual run record
    import log_run  # late import: it pulls in build_tracker
    sha7 = sha[:7]
    RUN_REPORT.write_text(json.dumps({
        "kind": "manual", "date": dt.date.today().isoformat(), "week": p["week"]["week"], "days": [day["id"]],
        "runId": None, "agents": None, "minutes": None, "tokens": None, "tiers": {"labels": "", "verified": None},
        "artifacts": [], "flagged": 0, "flags": [], "tests": None, "resolved": False,
        "note": f"close_day {day['id']} loose: {len(files)} file(s) from demo-repo@{sha7}",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    log_run.add(RUN_REPORT)
    out.append("manual run record added to harness/runs.jsonl")
    # (8) tracker, once
    import build_tracker
    build_tracker.build(quiet=True)
    # self-check: the state publish_demos.py --check expects
    problems = pd.check(day, rel, cfg)
    out += [f"CHECK: {x}" for x in problems] or ["publish_demos check: consistent"]
    if card == "already flipped" and problems:
        out.append("the card was flipped by an earlier close with other files; fix the card by hand to match demos/" + rel)
    # (9) the STATUS.md log line
    names = ", ".join(files) if files else "none"
    out.append(f"- {dt.date.today().isoformat()} — close_day W{p['week']['week']}D{day['day']} (loose, taught {date}): "
               f"{len(files)} file(s) ({names}) from demo-repo@{sha7}; demos/{rel}/ + README, delivery.json, card {card}, "
               "runbook Delivery record, manual run record; tracker rebuilt.")
    return out


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("week", type=int)
    ap.add_argument("day", type=int)
    ap.add_argument("--date")
    ap.add_argument("--files", nargs="+")
    ap.add_argument("--notes")
    ap.add_argument("--no-pull", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ns = ap.parse_args(argv)
    p = plan(ns.week, ns.day, date=ns.date, files=ns.files, notes=ns.notes, pull=not ns.no_pull)
    if not ns.apply:
        print("DRY RUN (nothing written; add --apply):")
        for line in describe(p):
            print("  " + line)
        return 0
    lines = apply(p)
    for line in lines[:-1]:
        print(line)
    print("\nSTATUS.md log line:\n" + lines[-1])
    return 1 if any(x.startswith("CHECK: ") for x in lines) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
