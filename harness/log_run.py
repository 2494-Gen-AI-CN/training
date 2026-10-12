#!/usr/bin/env python3
"""Record workflow runs and test results for the work tracker (D-0035).

harness/runs.jsonl holds one JSON record per workflow run. Transcripts live outside the repo, so this
file is the only committed trace of how a run went (agents, passes per artifact, flagged items, tiers).
harness/build_tracker.py reads it; every command here rebuilds tracker.html when it is done.

Commands:
    python harness/log_run.py add <report.json> [--keep]
        Validate the record in <report.json>, append it to runs.jsonl, delete the report file (unless
        --keep) and rebuild the tracker. The final Record agent of day-fanout.js and week-plan.js runs
        this with the record the workflow script built.
    python harness/log_run.py amend [--last | --index N] [--run-id wf_x] [--agents N] [--minutes M]
                                    [--tokens T] [--tiers-verified yes|no] [--resolved yes|no]
                                    [--tests pass|fail] [--note "..."] [--match-days w01d3,w01d4]
        Add what a workflow script cannot see: its own run id, usage figures, whether the tiers were
        verified from the transcripts, whether flagged items were resolved by hand. Run by the session.
        The workflow's Verify agent uses it to record the test result (--match-days makes --last refuse
        when the newest record belongs to another run).
    python harness/log_run.py tests
        Rebuild the tracker, run the contract tests, write harness/last-tests.json, rebuild again.

Record fields: kind (day-fanout | week-plan | manual), date (YYYY-MM-DD), week, days[] (curriculum ids,
empty for a week plan), runId, agents, minutes, tokens, tiers {labels, verified}, artifacts[] {day, name,
status, passes}, flagged, flags[] {day, artifact, flags[]}, tests (pass | fail | null), resolved, note.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import build_tracker as bt  # noqa: E402

ROOT = bi.ROOT
RUNS = bt.RUNS
LAST_TESTS = bt.LAST_TESTS
KINDS = bt.RUN_KINDS
FIELDS = ["kind", "date", "week", "days", "runId", "agents", "minutes", "tokens", "tiers", "artifacts",
          "flagged", "flags", "tests", "resolved", "note"]
STATUSES = ("done", "flagged", "cached", "skipped")


def normalize(rec: dict) -> dict:
    """Fill defaults, cap long strings, keep a stable key order."""
    out = {
        "kind": rec.get("kind"), "date": rec.get("date"), "week": rec.get("week"), "days": list(rec.get("days") or []),
        "runId": rec.get("runId"), "agents": rec.get("agents"), "minutes": rec.get("minutes"), "tokens": rec.get("tokens"),
        "tiers": {"labels": str((rec.get("tiers") or {}).get("labels", ""))[:400], "verified": (rec.get("tiers") or {}).get("verified")},
        "artifacts": [{"day": a.get("day"), "name": a.get("name"), "status": a.get("status"), "passes": a.get("passes")}
                      for a in (rec.get("artifacts") or [])],
        "flagged": rec.get("flagged", 0),
        "flags": [{"day": f.get("day"), "artifact": f.get("artifact"), "flags": [str(x)[:300] for x in (f.get("flags") or [])][:6]}
                  for f in (rec.get("flags") or [])],
        "tests": rec.get("tests"), "resolved": bool(rec.get("resolved", False)), "note": str(rec.get("note") or "")[:600],
    }
    return out


def validate(rec: dict, cur: dict | None = None) -> list[str]:
    p: list[str] = []
    cur = cur or bi.load_curriculum()
    if rec.get("kind") not in KINDS:
        p.append(f"kind must be one of {KINDS}, got {rec.get('kind')!r}")
    try:
        dt.date.fromisoformat(rec.get("date") or "")
    except ValueError:
        p.append(f"date must be YYYY-MM-DD, got {rec.get('date')!r}")
    week = next((w for w in cur["weeks"] if w["week"] == rec.get("week")), None)
    if week is None:
        p.append(f"week {rec.get('week')!r} is not in the curriculum")
    else:
        ids = {d["id"] for d in bi.teaching_days(week)}
        for d in rec.get("days") or []:
            if d not in ids:
                p.append(f"day {d!r} is not a teaching day of week {rec['week']}")
    if rec.get("kind") == "day-fanout" and not rec.get("days"):
        p.append("a day-fanout record needs at least one day")
    if rec.get("runId") is not None and not re.fullmatch(r"wf_[a-z0-9-]{6,}", str(rec["runId"])):
        p.append(f"runId must look like wf_xxxxxxxx-xxx, got {rec['runId']!r}")
    for k in ("agents", "tokens", "flagged"):
        if rec.get(k) is not None and not (isinstance(rec[k], int) and rec[k] >= 0):
            p.append(f"{k} must be a non-negative integer or null, got {rec[k]!r}")
    if rec.get("minutes") is not None and not isinstance(rec["minutes"], (int, float)):
        p.append(f"minutes must be a number or null, got {rec['minutes']!r}")
    if rec.get("tests") not in ("pass", "fail", None):
        p.append(f"tests must be 'pass', 'fail' or null, got {rec.get('tests')!r}")
    if (rec.get("tiers") or {}).get("verified") not in (True, False, None):
        p.append("tiers.verified must be true, false or null")
    for a in rec.get("artifacts") or []:
        if not a.get("name") or a.get("status") not in STATUSES:
            p.append(f"artifact needs a name and a status in {STATUSES}, got {a!r}")
    return p


def read_runs(path: Path = RUNS) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def write_runs(runs: list[dict], path: Path = RUNS) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in runs), encoding="utf-8", newline="\n")


def add(report: Path, keep: bool = False, path: Path = RUNS) -> dict:
    rec = normalize(json.loads(report.read_text(encoding="utf-8")))
    problems = validate(rec)
    if problems:
        raise SystemExit("run record rejected:\n  " + "\n  ".join(problems))
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    if not keep:
        report.unlink()
    return rec


def amend(index: int, changes: dict, path: Path = RUNS, match_days: list[str] | None = None) -> dict:
    runs = read_runs(path)
    if not runs:
        raise SystemExit("runs.jsonl is empty; nothing to amend")
    try:
        rec = runs[index]
    except IndexError:
        raise SystemExit(f"no run at index {index} (there are {len(runs)})")
    if match_days is not None and rec.get("days") != match_days:
        raise SystemExit(f"refused: that record is for {rec.get('days')}, not {match_days} (this run's record is missing)")
    for k, v in changes.items():
        if v is None:
            continue
        if k == "tiersVerified":
            rec.setdefault("tiers", {"labels": "", "verified": None})["verified"] = v
        else:
            rec[k] = v
    rec = normalize(rec)
    problems = validate(rec)
    if problems:
        raise SystemExit("amended record rejected:\n  " + "\n  ".join(problems))
    runs[index] = rec
    write_runs(runs, path)
    return rec


def run_tests() -> dict:
    res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=str(ROOT),
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = res.stderr + res.stdout
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    def count(name: str) -> int:
        m = re.search(rf"{name}=(\d+)", out)
        return int(m.group(1)) if m else 0
    return {"date": dt.date.today().isoformat(), "ran": int(ran.group(1)) if ran else 0, "ok": res.returncode == 0,
            "failures": count("failures"), "errors": count("errors"), "skipped": count("skipped")}


def _yn(v: str | None) -> bool | None:
    return None if v is None else v == "yes"


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("report")
    a.add_argument("--keep", action="store_true")
    m = sub.add_parser("amend")
    m.add_argument("--last", action="store_true")
    m.add_argument("--index", type=int)
    m.add_argument("--run-id")
    m.add_argument("--agents", type=int)
    m.add_argument("--minutes", type=float)
    m.add_argument("--tokens", type=int)
    m.add_argument("--tiers-verified", choices=["yes", "no"])
    m.add_argument("--resolved", choices=["yes", "no"])
    m.add_argument("--tests", choices=["pass", "fail"])
    m.add_argument("--note")
    m.add_argument("--match-days", help="comma-separated day ids the record must carry, else refuse (guards --last)")
    sub.add_parser("tests")
    ns = ap.parse_args(argv)
    if ns.cmd == "add":
        rec = add(Path(ns.report), keep=ns.keep)
        print(f"recorded {rec['kind']} week {rec['week']} {' '.join(rec['days']) or '(week plan)'}: "
              f"{rec['flagged']} flagged, tests {rec['tests'] or 'not run'}")
    elif ns.cmd == "amend":
        rec = amend(ns.index if ns.index is not None else -1, {
            "runId": ns.run_id, "agents": ns.agents, "minutes": ns.minutes, "tokens": ns.tokens,
            "tiersVerified": _yn(ns.tiers_verified), "resolved": _yn(ns.resolved), "tests": ns.tests, "note": ns.note},
            match_days=[d for d in ns.match_days.split(",") if d] if ns.match_days is not None else None)
        print(f"amended {rec['kind']} {rec['runId'] or '(no run id)'} week {rec['week']}")
    elif ns.cmd == "tests":
        bt.build(quiet=True)
        result = run_tests()
        LAST_TESTS.write_text(json.dumps(result, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"tests: ran {result['ran']}, {'OK' if result['ok'] else 'FAILED'} "
              f"(failures={result['failures']}, errors={result['errors']}, skipped={result['skipped']})")
        bt.build(quiet=True)
        return 0 if result["ok"] else 1
    if bt.build(quiet=True):
        print("tracker.html updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
