#!/usr/bin/env python3
"""Close a delivered day: record what the room reached against the plan and mark the day taught (D-0050, D-0055).

The trainer performs the day's walkthrough blocks live in the public demo repository (config.json `demoRepo`,
cloned at `demoRepo.localDir`, gitignored like trainer/), on its `branch` (and the week's feature branches). The
authored end state of every block is a commit on the week's prep branch (`demoRepo.prepBranch`, written by
harness/workflows/demo-series.js). This script is the ONLY writer of `taught` in curriculum.json. For a
`demoFormat: "walkthrough"` day it:

  1. reads the day's blocks from the week plan (harness/plan_check.day_rows) and the commits of that date in the
     demo repo (every branch); matches each block's commit message against the day's live commits (--match
     <block>=<sha> overrides a match) and against the prep branch; classifies each block as `reached` (the live
     tree equals the prep tree under the thread folder), `diverged` (it differs: the diffstat is recorded so the
     trainer can fold the room's reality back into the walkthrough and the prep branch by hand), or
     `not reached` (no live commit with that message on that date);
  2. writes trainer/<rel>/delivery.json (day, date, format, blocks with their shas and states, demo repo URL and
     the day's last commit, notes);
  3. appends a "> **DELIVERY RECORD (<date>)**" blockquote under each block's walkthrough header
     (trainer/week-WW/demos/NN-<slug>.md, once per date) and a "## Delivery record (<date>)" section to
     trainer/<rel>/runbook.md (once per date);
  4. sets `taught` on the day in curriculum.json;
  5. re-renders trainer/week-WW/demos/README.md (harness/series_readme.py) so the Delivered column is current,
     splices the index block (as harness/build_index.py does), records a `manual` run in harness/runs.jsonl,
     rebuilds the tracker once, then prints the STATUS.md log line to paste.

Re-running with --apply converges: delivery.json is rewritten, the records are not duplicated. A `demoFormat:
"none"` day has nothing to close and is refused. A day that is not live (planned, or authored but its week not yet
released by harness/release_week.py) is refused too: taught implies live (D-0052). Nothing is published to the
learner site and nothing is copied into this repository (D-0055).

Usage:
    python harness/close_day.py <week> <day>                      # dry run: print the plan, change nothing
    python harness/close_day.py <week> <day> --apply              # do it
      [--date YYYY-MM-DD]        the day's date in the demo repo history (default: the day's calendar date)
      [--match NN-slug=<sha> ...] the live commit of a block, when its message was not typed verbatim
      [--notes "..."]            a line for delivery.json and the records
      [--no-pull]                skip `git pull --ff-only` in the demo repo clone
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import plan_check  # noqa: E402

ROOT = bi.ROOT
TRAINER = ROOT / "trainer"
RUN_REPORT = ROOT / "harness" / "run-report.tmp.json"
RECORD_HEAD = "## Delivery record ({date})"
WALK_HEAD = "> **DELIVERY RECORD ({date})**"
CHEAT_HEAD = "## Presenter cheat-sheet"
STATES = ("reached", "diverged", "not reached")


# ---------------------------------------------------------------- lookup
def locate(week_no: int, day_no: int):
    """(cur, week, day, rel, cfg) for a walkthrough day; refuses `none` days and unreleased days."""
    cfg = json.loads((ROOT / "harness" / "config.json").read_text(encoding="utf-8"))
    cur = bi.load_curriculum()
    week = next((w for w in cur["weeks"] if w["week"] == week_no), None)
    if week is None:
        raise SystemExit(f"no week {week_no}")
    day = next((d for d in week["days"] if d.get("day") == day_no), None)
    if day is None or day.get("kind") == "holiday":
        raise SystemExit(f"week {week_no} day {day_no} is not a teaching day")
    rel = f"{week['dir']}/{day['slug']}"
    if day.get("demoFormat") == "none":
        raise SystemExit(f"{day['id']} is demoFormat none: nothing to close (no walkthrough that day)")
    # D-0052: taught implies live; closing an unreleased day would leave it taught but not live
    if day.get("status") != "live":
        raise SystemExit(f"{day['id']} is {day.get('status')!r}, not live: a day is closed only after its week is released. "
                         f"Run python harness/release_week.py {week['week']} --today YYYY-MM-DD first. Nothing was written.")
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


def prep_branch(cfg: dict, week_no: int) -> str:
    return (cfg["demoRepo"].get("prepBranch") or "prep/week-{WW}").replace("{WW}", f"{week_no:02d}")


def branch_exists(repo: Path, branch: str) -> bool:
    res = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", f"refs/heads/{branch}"], capture_output=True)
    if res.returncode == 0:
        return True
    res = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", f"refs/remotes/origin/{branch}"], capture_output=True)
    return res.returncode == 0


def ref(repo: Path, branch: str) -> str:
    """The local branch, else its origin tracking ref (a prep branch the session pushed from another clone)."""
    res = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", f"refs/heads/{branch}"], capture_output=True)
    return branch if res.returncode == 0 else f"origin/{branch}"


def commits_on(repo: Path, branch: str) -> list[tuple[str, str]]:
    """(sha, subject) of every commit reachable from `branch`, newest first."""
    if not branch_exists(repo, branch):
        return []
    out = _git(repo, "log", ref(repo, branch), "--format=%H%x09%s")
    return [tuple(ln.split("\t", 1)) for ln in out.splitlines() if "\t" in ln]


def commits_dated(repo: Path, date: str) -> list[tuple[str, str]]:
    """(sha, subject) of every commit on any branch whose author date is `date`, newest first."""
    out = _git(repo, "log", "--all", "--date=short", "--format=%H%x09%ad%x09%s")
    rows = []
    for ln in out.splitlines():
        parts = ln.split("\t", 2)
        if len(parts) == 3 and parts[1] == date:
            rows.append((parts[0], parts[2]))
    return rows


def last_commit_by(repo: Path, date: str) -> str:
    """The repository's last commit on or before the end of `date` (any branch), '' when none."""
    out = _git(repo, "log", "--all", "-1", f"--until={date}T23:59:59", "--format=%H").strip()
    return out


def diffstat(repo: Path, a: str, b: str, path: str) -> str:
    """`git diff --stat a b -- path`, '' when the trees are equal there."""
    return _git(repo, "diff", "--stat", a, b, "--", path).strip()


def classify(prep_sha: str | None, live_sha: str | None, stat: str) -> str:
    if live_sha is None:
        return "not reached"
    if prep_sha is None or not stat:
        return "reached"
    return "diverged"


def match_blocks(blocks: list[dict], prep: list[tuple[str, str]], live: list[tuple[str, str]], overrides: dict[str, str],
                 repo: Path | None, path: str) -> list[dict]:
    """One record per block: its prep and live commits (by message), the diffstat between them and the state."""
    prep_by = {}
    for sha, subject in prep:
        prep_by.setdefault(subject, sha)
    live_by = {}
    for sha, subject in live:
        live_by.setdefault(subject, sha)
    out = []
    for b in blocks:
        msg = b["commitMessage"]
        prep_sha = prep_by.get(msg) if msg else None
        live_sha = overrides.get(b["name"]) or (live_by.get(msg) if msg else None)
        stat = diffstat(repo, prep_sha, live_sha, path) if (repo and prep_sha and live_sha) else ""
        out.append({"name": b["name"], "slot": b.get("slot", ""), "commitMessage": msg, "prepSha": prep_sha, "liveSha": live_sha,
                    "state": classify(prep_sha, live_sha, stat), "diffstat": stat})
    return out


# ---------------------------------------------------------------- what gets written
def delivery_record(day: dict, date: str, blocks: list[dict], cfg: dict, sha: str, notes: str | None) -> dict:
    return {"day": day["id"], "date": date, "format": "walkthrough", "blocks": blocks,
            "demoRepo": cfg["demoRepo"]["url"], "demoRepoSha": sha, "notes": notes or ""}


def _short(sha: str | None) -> str:
    return sha[:7] if sha else "none"


def walkthrough_record(date: str, b: dict, notes: str | None) -> str:
    detail = {"reached": f"the room's commit {_short(b['liveSha'])} matches the prep commit {_short(b['prepSha'])}",
              "diverged": f"the room's commit {_short(b['liveSha'])} differs from the prep commit {_short(b['prepSha'])}: fold the room's reality back into this walkthrough and the prep branch by hand",
              "not reached": "no live commit with this block's message on that date; the unreached steps carry over"}[b["state"]]
    lines = [f"{WALK_HEAD.format(date=date)} {b['state'].upper()}. {detail}."]
    if b["diffstat"]:
        lines += ["> Diff (prep -> live):", "> ```", *["> " + ln for ln in b["diffstat"].splitlines()], "> ```"]
    if notes:
        lines.append(f"> Notes: {notes}")
    return "\n".join(lines) + "\n"


def append_walkthrough(path: Path, record: str, date: str) -> bool:
    """Insert the record before '## Presenter cheat-sheet' unless this date's record is already there. True when written."""
    text = path.read_text(encoding="utf-8")
    if WALK_HEAD.format(date=date) in text:
        return False
    if CHEAT_HEAD in text:
        head, tail = text.split(CHEAT_HEAD, 1)
        new = head.rstrip("\n") + "\n\n" + record + "\n" + CHEAT_HEAD + tail
    else:
        new = text.rstrip("\n") + "\n\n" + record
    path.write_text(new, encoding="utf-8", newline="\n")
    return True


def runbook_section(date: str, blocks: list[dict], url: str, sha: str, notes: str | None) -> str:
    rows = [f"- {b['name']}: {b['state']} (live {_short(b['liveSha'])}, prep {_short(b['prepSha'])})" for b in blocks] or ["- no walkthrough block in the plan for this day"]
    return (f"\n{RECORD_HEAD.format(date=date)}\n\n"
            "- Format: walkthrough (D-0055)\n"
            + "\n".join(rows) + "\n"
            f"- Demo repo: {url.rstrip('/')}/commit/{sha}\n"
            f"- Notes: {notes or 'none'}\n")


def append_runbook(path: Path, section: str, date: str) -> bool:
    """Append the section unless this date's record is already there. True when written."""
    text = path.read_text(encoding="utf-8")
    if RECORD_HEAD.format(date=date) in text:
        return False
    path.write_text(text.rstrip("\n") + "\n" + section, encoding="utf-8", newline="\n")
    return True


def parse_matches(items: list[str] | None) -> dict[str, str]:
    out = {}
    for it in items or []:
        if "=" not in it:
            raise SystemExit(f"--match entries read NN-slug=<sha>, got {it!r}")
        name, sha = it.split("=", 1)
        out[name.strip()] = sha.strip()
    return out


# ---------------------------------------------------------------- plan / apply
def plan(week_no: int, day_no: int, date: str | None = None, notes: str | None = None, pull: bool = True,
         matches: dict[str, str] | None = None) -> dict:
    """Everything the close will do, validated; writes nothing (except the optional git pull)."""
    cur, week, day, rel, cfg = locate(week_no, day_no)
    repo = ROOT / cfg["demoRepo"]["localDir"]
    if not is_git_repo(repo):
        raise SystemExit(clone_hint(cfg))
    if not TRAINER.exists():
        raise SystemExit("trainer/ (the private repo) is not cloned here; delivery.json and the records live there")
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
    pfile = ROOT / "harness" / "plans" / f"week-{week_no:02d}.md"
    blocks = plan_check.day_rows(plan_check.load_plan(pfile), day["id"])["blockRows"] if pfile.is_file() else []
    thread_dirs = sorted({t.get("repoDir", "") for t in (cfg.get("threads") or {}).values() if isinstance(t, dict) and t.get("repoDir")})
    path = thread_dirs[0] if len(thread_dirs) == 1 else "."
    prep = prep_branch(cfg, week_no)
    matched = match_blocks(blocks, commits_on(repo, prep), commits_dated(repo, date), matches or {}, repo, path)
    for name in (matches or {}):
        if name not in {b["name"] for b in blocks}:
            raise SystemExit(f"--match {name}: not a block of {day['id']} in the plan ({[b['name'] for b in blocks]})")
    sha = last_commit_by(repo, date)
    if notes is None:  # a re-run without --notes keeps the notes of an earlier close of the same date
        prev = TRAINER / rel / "delivery.json"
        if prev.is_file():
            old = json.loads(prev.read_text(encoding="utf-8"))
            notes = old.get("notes", "") if old.get("date") == date else None
    demos_dir = TRAINER / week["dir"] / "demos"
    return {"cur": cur, "week": week, "day": day, "rel": rel, "cfg": cfg, "repo": repo, "date": date, "prep": prep,
            "prepExists": branch_exists(repo, prep), "blocks": matched, "sha": sha, "notes": notes or "",
            "url": cfg["demoRepo"]["url"], "demosDir": demos_dir,
            "walkthroughs": {b["name"]: demos_dir / f"{b['name']}.md" for b in matched}}


def describe(p: dict) -> list[str]:
    rel = p["rel"]
    out = [f"{p['day']['id']} ({rel}), demoFormat walkthrough, taught {p['date']}"
           + (f" (already taught {p['day']['taught']})" if p["day"].get("taught") else ""),
           f"demo repo {p['repo'].name} ({p['url']}): last commit by the end of {p['date']} is {_short(p['sha'])}; prep branch {p['prep']} "
           + ("found" if p["prepExists"] else "MISSING (every block will read as reached-without-prep or not reached)")]
    if not p["blocks"]:
        out.append("no walkthrough block for this day in the week plan: delivery.json records the day with no blocks")
    for b in p["blocks"]:
        out.append(f"{b['name']}: {b['state']} (live {_short(b['liveSha'])}, prep {_short(b['prepSha'])})"
                   + (f"; diff: {b['diffstat'].splitlines()[-1].strip()}" if b["diffstat"] else ""))
        wt = p["walkthroughs"][b["name"]]
        out.append(f"  walkthrough: {'append DELIVERY RECORD to ' + wt.relative_to(ROOT).as_posix() if wt.is_file() else 'none on disk (' + wt.relative_to(ROOT).as_posix() + ')'}")
    out += [f"write trainer/{rel}/delivery.json",
            f"set taught={p['date']} on {p['day']['id']} in harness/curriculum.json",
            f"runbook: append '{RECORD_HEAD.format(date=p['date'])}'" if (TRAINER / rel / "runbook.md").exists() else "runbook: none on disk",
            "then: series README, index block, a manual run record, one tracker rebuild"]
    return out


def apply(p: dict) -> list[str]:
    day, rel, date, cfg, sha, blocks = p["day"], p["rel"], p["date"], p["cfg"], p["sha"], p["blocks"]
    out: list[str] = []
    # (1) the delivery record in the private repo
    rec_path = TRAINER / rel / "delivery.json"
    rec_path.parent.mkdir(parents=True, exist_ok=True)
    rec_path.write_text(json.dumps(delivery_record(day, date, blocks, cfg, sha, p["notes"]), indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")
    out.append(f"wrote trainer/{rel}/delivery.json")
    # (2) the walkthrough records
    for b in blocks:
        wt = p["walkthroughs"][b["name"]]
        if wt.is_file():
            wrote = append_walkthrough(wt, walkthrough_record(date, b, p["notes"]), date)
            out.append(f"{wt.name}: DELIVERY RECORD " + ("appended" if wrote else "already there"))
    # (3) taught (this script is its only writer); byte-exact round trip of curriculum.json
    day["taught"] = date
    with open(bi.CURRICULUM, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(p["cur"], indent=2, ensure_ascii=False) + "\n")
    out.append(f"set taught={date} on {day['id']}")
    # (4) runbook record
    rb = TRAINER / rel / "runbook.md"
    if rb.exists():
        wrote = append_runbook(rb, runbook_section(date, blocks, cfg["demoRepo"]["url"], sha, p["notes"]), date)
        out.append("runbook Delivery record " + ("appended" if wrote else "already there"))
    # (5) the series README's Delivered column
    if p["demosDir"].is_dir():
        import series_readme
        series_readme.write(p["week"]["week"])
        out.append(f"rendered trainer/{p['week']['dir']}/demos/README.md")
    # (6) index block, in process (build_index.main would also rebuild the tracker; that happens once, below)
    html = bi.INDEX.read_text(encoding="utf-8")
    new_html = bi.splice(html, bi.render())
    if new_html != html:
        bi.INDEX.write_text(new_html, encoding="utf-8", newline="\n")
        out.append("docs/index.html updated")
    # (7) manual run record
    import log_run  # late import: it pulls in build_tracker
    states = ", ".join(f"{b['name']} {b['state']}" for b in blocks) or "no blocks"
    RUN_REPORT.write_text(json.dumps({
        "kind": "manual", "date": dt.date.today().isoformat(), "week": p["week"]["week"], "days": [day["id"]],
        "runId": None, "agents": None, "minutes": None, "tokens": None, "tiers": {"labels": "", "verified": None},
        "artifacts": [], "flagged": 0, "flags": [], "tests": None, "resolved": False,
        "note": f"close_day {day['id']}: {states}; demo-repo@{_short(sha)}",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    log_run.add(RUN_REPORT)
    out.append("manual run record added to harness/runs.jsonl")
    # (8) tracker, once
    import build_tracker
    build_tracker.build(quiet=True)
    # (9) the STATUS.md log line
    out.append(f"- {dt.date.today().isoformat()} — close_day W{p['week']['week']}D{day['day']} (taught {date}): {states}; "
               f"demo-repo@{_short(sha)}; delivery.json, walkthrough and runbook Delivery records, manual run record; tracker rebuilt.")
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
    ap.add_argument("--match", nargs="+")
    ap.add_argument("--notes")
    ap.add_argument("--no-pull", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ns = ap.parse_args(argv)
    p = plan(ns.week, ns.day, date=ns.date, notes=ns.notes, pull=not ns.no_pull, matches=parse_matches(ns.match))
    if not ns.apply:
        print("DRY RUN (nothing written; add --apply):")
        for line in describe(p):
            print("  " + line)
        return 0
    lines = apply(p)
    for line in lines[:-1]:
        print(line)
    print("\nSTATUS.md log line:\n" + lines[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
