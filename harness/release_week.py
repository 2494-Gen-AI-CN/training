#!/usr/bin/env python3
"""Release a week: flip every authored day of it to live (the Friday gate, D-0052).

Status model: planned -> authored -> live. An authored day has every artifact on disk and passed; its page is
written but not linked from docs/index.html (build_index.render links live days only), so the week stays hidden.
That is not access control: GitHub Pages still serves the file to anyone who knows its path. This script is the
one step that makes a week visible. It refuses, naming every reason on its own line, unless:

  a. harness/plans/week-WW.md exists and passes harness/plan_check.py (the same check args_for.py gates on);
  b. every teaching day of the week is authored or already live (a planned day is named);
  c. every authored day has docs/weeks/<rel>.html and exercises/<rel>/README.md on disk, and its page passes
     harness/notes_check.py (counts, phrases, stamps, citations; no network link phase);
  d. harness/last-tests.json exists, its last contract test run is green, and it is not older than the newest
     authored page of the week (its `at` timestamp against the page mtime; its `date` when `at` is absent);
  e. every teaching day dated strictly before --today, in every week whose Monday is on or before --today, that
     harness/close_day.py can close (every demoFormat but none) is closed: trainer/<rel>/delivery.json exists
     (D-0050, D-0055). --today itself is not due yet;
  f. when trainer/week-WW/demos/ exists (the week's walkthroughs, D-0055), every walkthrough passes
     harness/demo_check.py and the series README is fresh (harness/series_readme.py --check).

When every day of the week is already live there is nothing to release (exit 0). Otherwise, with every check
passing, it renders the new index block and validates the run record, and only then sets status live on each
authored day (byte-exact round trip of curriculum.json), writes the index block, records a `manual` run in
harness/runs.jsonl, rebuilds the tracker once and prints the STATUS.md log line to paste.

Usage:
    python harness/release_week.py <week> --today YYYY-MM-DD --check   # print the reasons or OK; never writes
    python harness/release_week.py <week> --today YYYY-MM-DD           # release
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

ROOT = bi.ROOT
RECORDED = ("authored", "live")
# The demoFormats harness/close_day.py closes (its locate() refuses `none`: nothing to close that day).
CLOSABLE_FORMATS = ("walkthrough",)
NOTES_PHASES = {"counts", "phrases", "stamps", "citations", "style"}


# ---------------------------------------------------------------- paths (all relative to a root, so tests can use a temp tree)
def curriculum_path(root: Path) -> Path:
    return root / "harness" / "curriculum.json"


def plan_file(week_no: int, root: Path) -> Path:
    return root / "harness" / "plans" / f"week-{week_no:02d}.md"


def last_tests_path(root: Path) -> Path:
    return root / "harness" / "last-tests.json"


def index_path(root: Path) -> Path:
    return root / "docs" / "index.html"


def run_report_path(root: Path) -> Path:
    return root / "harness" / "run-report.tmp.json"


def load(root: Path) -> dict:
    return json.loads(curriculum_path(root).read_text(encoding="utf-8"))


def write_curriculum(cur: dict, root: Path) -> None:
    """Byte-exact round trip (same idiom as close_day.py)."""
    with open(curriculum_path(root), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(cur, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- checks
def plan_problems(week_no: int, root: Path = ROOT) -> list[str]:
    """plan_check's problems with the week plan (the gate args_for.py applies before any day args). Run once per
    gate; tests patch this seam."""
    import plan_check  # late import: it loads demo_check
    metrics = json.loads((root / "harness" / "metrics.json").read_text(encoding="utf-8"))["demos"]
    return plan_check.check_plan(plan_file(week_no, root), metrics, root=root)


def demo_reasons(wk: dict, root: Path = ROOT) -> list[str]:
    """Reasons from the week's walkthrough folder when it exists (D-0055): demo_check problems and a stale README."""
    ddir = root / "trainer" / wk["dir"] / "demos"
    if not ddir.is_dir():
        return []
    import demo_check  # late imports: both load the curriculum
    import series_readme
    out = [f"trainer/{wk['dir']}/demos: {x}" for x in demo_check.check_dir(ddir)]
    out += [f"series README: {x}" for x in series_readme.check(wk["week"], root)]
    return out


def demo_reasons(wk: dict, root: Path = ROOT) -> list[str]:
    """Reasons from the week's walkthrough folder when it exists (D-0055): demo_check problems and a stale README."""
    ddir = root / "trainer" / wk["dir"] / "demos"
    if not ddir.is_dir():
        return []
    import demo_check  # late imports: both load the curriculum
    import series_readme
    out = [f"trainer/{wk['dir']}/demos: {x}" for x in demo_check.check_dir(ddir)]
    out += [f"series README: {x}" for x in series_readme.check(wk["week"], root)]
    return out


def plan_reason(week_no: int, root: Path, problems: list[str]) -> str | None:
    """One reason line derived from plan_problems' list (None when the plan passes; check_plan reports a missing
    file as a problem, so an empty list always means the plan exists and passes)."""
    rel = f"harness/plans/week-{week_no:02d}.md"
    if not problems:
        return None
    if not plan_file(week_no, root).is_file():
        return (f"{rel} is missing: write the week plan first (python harness/args_for.py {week_no} --plan --today <date>, "
                "then the week-plan workflow)")
    return f"{rel} fails plan_check ({len(problems)} problem(s)): run python harness/plan_check.py {rel}"


def notes_findings(page: Path) -> list[str]:
    """notes_check's findings for one page, without the network link phase; the word band gets the same
    metrics.notes.wordTolerance the contract tests allow. Tests patch this seam."""
    import notes_check
    m = notes_check.metrics()
    return notes_check.check_page(page, set(NOTES_PHASES), m, tolerance=m.get("wordTolerance", 0))["findings"]


def newest_page(pages: list[tuple[str, Path]]) -> tuple[str, dt.datetime] | None:
    """(repo-relative path, local mtime) of the most recently modified page that exists."""
    found = [(rel, p.stat().st_mtime) for rel, p in pages if p.is_file()]
    if not found:
        return None
    rel, mtime = max(found, key=lambda x: x[1])
    return rel, dt.datetime.fromtimestamp(mtime).replace(microsecond=0)


def tests_reason(root: Path, pages: list[tuple[str, Path]]) -> str | None:
    """last-tests.json must exist, be green, and not predate the newest authored page: its `at` (local datetime)
    against the page mtime when present, else its `date` against the mtime's date."""
    path = last_tests_path(root)
    if not path.is_file():
        return "harness/last-tests.json is missing: run python harness/log_run.py tests"
    try:
        res = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return "harness/last-tests.json is not valid JSON: run python harness/log_run.py tests"
    if res.get("ok") is not True:
        return (f"last contract test run is red ({res.get('failures', '?')} failure(s), {res.get('errors', '?')} error(s) "
                f"of {res.get('ran', '?')} run on {res.get('date', '?')}): fix them, then run python harness/log_run.py tests")
    try:
        ran_day = dt.date.fromisoformat(str(res.get("date")))
    except ValueError:
        return f"harness/last-tests.json has no valid date ({res.get('date')!r}): run python harness/log_run.py tests"
    ran_at = None
    if res.get("at"):
        try:
            ran_at = dt.datetime.fromisoformat(str(res["at"])).replace(tzinfo=None)
        except ValueError:
            ran_at = None
    newest = newest_page(pages)
    if not newest:
        return None
    page, mtime = newest
    if ran_at is not None:
        if ran_at < mtime:
            return (f"last-tests.json ({ran_at.isoformat()}) predates the newest authored page ({page}, "
                    f"{mtime.isoformat()}): run python harness/log_run.py tests")
    elif ran_day < mtime.date():
        return (f"last-tests.json ({ran_day.isoformat()}) predates the newest authored page ({page}, "
                f"{mtime.date().isoformat()}): run python harness/log_run.py tests")
    return None


def started_weeks(cur: dict, today: dt.date) -> list[dict]:
    """Every week whose Monday is on or before `today`."""
    return [w for w in cur["weeks"] if bi.expand_week(cur, w)["start"] <= today]


def unclosed_days(cur: dict, today: dt.date, root: Path) -> list[str]:
    """Reasons for closable teaching days dated strictly before `today` (any started week) without delivery.json.
    Only CLOSABLE_FORMATS are required: close_day.py refuses the others, so demanding their record would dead-end
    the gate on a command that cannot run (O-18 widens this)."""
    out = []
    for wk in started_weeks(cur, today):
        for d in bi.teaching_days(wk):
            if d.get("demoFormat") not in CLOSABLE_FORMATS:
                continue
            when = bi.slot_date(cur, wk["week"], d["day"])
            rel = f"{wk['dir']}/{d['slug']}"
            if when < today and not (root / "trainer" / rel / "delivery.json").is_file():
                out.append(f"{d['id']} ({when.isoformat()}) is not closed: trainer/{rel}/delivery.json is missing "
                           f"(python harness/close_day.py {wk['week']} {d['day']} --apply)")
    return out


def gate(week_no: int, today: dt.date, cur: dict, root: Path = ROOT) -> dict:
    """What a release of `week_no` would do and why it may not: {week, authored, live, reasons, nothing}."""
    wk = next((w for w in cur["weeks"] if w["week"] == week_no), None)
    if wk is None:
        raise SystemExit(f"week {week_no} is not in the curriculum")
    teaching = bi.teaching_days(wk)
    live = [d for d in teaching if d.get("status") == "live"]
    authored = [d for d in teaching if d.get("status") == "authored"]
    out = {"week": wk, "authored": authored, "live": live, "reasons": [], "nothing": len(live) == len(teaching)}
    if out["nothing"]:
        return out
    reasons = out["reasons"]
    pr = plan_reason(week_no, root, plan_problems(week_no, root))
    if pr:
        reasons.append(pr)
    reasons += demo_reasons(wk, root)
    reasons += demo_reasons(wk, root)
    for d in teaching:
        if d.get("status") not in RECORDED:
            reasons.append(f"{d['id']} is {d.get('status')} (not authored)")
    pages = []
    for d in authored:
        rel = f"{wk['dir']}/{d['slug']}"
        page = f"docs/weeks/{rel}.html"
        pages.append((page, root / page))
        for need in (page, f"exercises/{rel}/README.md"):
            if not (root / need).is_file():
                reasons.append(f"{d['id']} is authored but {need} is missing")
        if (root / page).is_file():
            reasons += [f"notes_check {page}: {f}" for f in notes_findings(root / page)]
    tr = tests_reason(root, pages)
    if tr:
        reasons.append(tr)
    reasons += unclosed_days(cur, today, root)
    return out


# ---------------------------------------------------------------- release
def run_record(cur: dict, week_no: int, ids: list[str], today: dt.date) -> dict:
    """The `manual` run record, normalized and validated by log_run BEFORE anything is written."""
    import log_run  # late import: it pulls in build_tracker
    rec = log_run.normalize({
        "kind": "manual", "date": today.isoformat(), "week": week_no, "days": ids,
        "runId": None, "agents": None, "minutes": None, "tokens": None, "tiers": {"labels": "", "verified": None},
        "artifacts": [], "flagged": 0, "flags": [], "tests": None, "resolved": False,
        "note": f"release_week W{week_no}: {','.join(ids)} authored -> live",
    })
    problems = log_run.validate(rec, cur)
    if problems:
        raise SystemExit("run record rejected, nothing was written:\n  " + "\n  ".join(problems))
    return rec


def new_index(cur: dict, root: Path) -> tuple[str, str]:
    """(current, new) docs/index.html with the re-rendered block, computed before any write; the same marker guard
    build_index.main uses."""
    path = index_path(root)
    if not path.is_file():
        raise SystemExit(f"{path} is missing, nothing was written")
    html = path.read_text(encoding="utf-8")
    if bi.BEGIN not in html or bi.END not in html:
        raise SystemExit(f"markers missing in {path}, nothing was written")
    return html, bi.splice(html, bi.render(cur))


def append_run(rec: dict) -> None:
    """The (already validated) run record; the tmp report never outlives the call. Real repo only."""
    import log_run
    report = run_report_path(ROOT)
    try:
        report.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        log_run.add(report)
    finally:
        report.unlink(missing_ok=True)


def release(week_no: int, today: dt.date, root: Path = ROOT, check: bool = False) -> tuple[int, list[str]]:
    """(exit code, lines to print). `check` never writes."""
    cur = load(root)
    g = gate(week_no, today, cur, root)
    if g["nothing"]:
        return 0, [f"nothing to release: every day of week {week_no} is live"]
    if g["reasons"]:
        return 1, [f"REFUSED: week {week_no} cannot be released ({len(g['reasons'])} reason(s)):"] + [f"  {r}" for r in g["reasons"]]
    ids = [d["id"] for d in g["authored"]]
    if check:
        return 0, [f"OK: week {week_no} ready to release ({len(ids)} days authored)"]
    # everything that can fail, before the first write
    rec = run_record(cur, week_no, ids, today)
    flipped = json.loads(json.dumps(cur))
    for d in bi.teaching_days(next(w for w in flipped["weeks"] if w["week"] == week_no)):
        if d.get("status") == "authored":
            d["status"] = "live"
    old_html, new_html = new_index(flipped, root)
    # writes
    write_curriculum(flipped, root)
    out = [f"set status live on {', '.join(ids)} in harness/curriculum.json"]
    if new_html != old_html:
        index_path(root).write_text(new_html, encoding="utf-8", newline="\n")
        out.append("docs/index.html updated")
    if root.resolve() == ROOT.resolve():
        append_run(rec)
        out.append("manual run record added to harness/runs.jsonl")
        import build_exit_pages  # D-0063: authored -> live changes which days the exit-criteria pages link
        build_exit_pages.build(quiet=True)
        out.append("exit-criteria pages rebuilt")
        import build_tracker
        build_tracker.build(quiet=True)
        out.append("tracker rebuilt")
    else:
        out.append(f"(root {root} is not the repo: run log and tracker left alone)")
    out.append(f"- {today.isoformat()} — release_week W{week_no}: {','.join(ids)} authored -> live; index and tracker rebuilt")
    return 0, out


def main(argv: list[str], root: Path = ROOT) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("week", type=int)
    ap.add_argument("--today", required=True, help="YYYY-MM-DD (the session's date; this script reads no clock)")
    ap.add_argument("--check", action="store_true", help="print the reasons or OK; write nothing")
    ns = ap.parse_args(argv)
    try:
        today = dt.date.fromisoformat(ns.today)
    except ValueError:
        raise SystemExit(f"--today must be YYYY-MM-DD, got {ns.today!r}")
    code, lines = release(ns.week, today, root=root, check=ns.check)
    if code == 0 and not ns.check and lines and lines[-1].startswith("- "):
        for line in lines[:-1]:
            print(line)
        print("\nSTATUS.md log line:\n" + lines[-1])
    else:
        for line in lines:
            print(line)
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
