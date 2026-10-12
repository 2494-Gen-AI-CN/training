#!/usr/bin/env python3
"""Print the Workflow `args` JSON for one or more curriculum days, or for a week plan.

Workflow scripts cannot read files or call Date(), so everything the day-fanout
script needs — day metadata, calendar date, metrics, config, today's date, the
week plan's rows for the day — travels in args. Dates come from build_index.slot_date
(D-0013); holiday slots are refused (D-0014).

Week plan gate (D-0034): day args are refused until harness/plans/week-WW.md exists
and passes harness/plan_check.py; `--no-plan` is the logged escape (prints a warning,
sets args.noPlan; record its use in STATUS.md). `--plan` emits the args for
harness/workflows/week-plan.js instead; it is the only source of week-plan args.

Usage:
    python harness/args_for.py 1 2            # week 1, day 2 (slot 2 = Tue)
    python harness/args_for.py 1 2 3          # week 1, days 2 and 3 (pipelined)
    python harness/args_for.py 1 2 --today 2026-10-13
    python harness/args_for.py 1 2 --skip-research   # reuse the committed brief; demos onward run live
    python harness/args_for.py 1 3 --no-plan         # ESCAPE: ship a day without a week plan (logged)
    python harness/args_for.py 1 --plan --today 2026-10-12   # week-plan args for week 1
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import demo_check  # noqa: E402
import plan_check  # noqa: E402

ROOT = bi.ROOT
CONFIG_KEYS = ("cohort", "siteTitle", "brand", "repoUrl", "repoBranch", "siteUrl", "feedbackFormUrl", "python", "audience", "learnerRepo")


def plan_path(week_no: int) -> Path:
    return ROOT / "harness" / "plans" / f"week-{week_no:02d}.md"


def _fwd(p: Path) -> str:
    return str(p).replace("\\", "/")


def _existing_scripts(rel: str) -> list[dict]:
    """Header facts of the demo scripts already on disk for a day (live days are recorded as-is in the plan)."""
    ddir = ROOT / "trainer" / rel / "demos"
    out = []
    if not ddir.is_dir():
        return out
    for s in sorted(ddir.glob("*.md")):
        if not re.match(r"^\d{2}_", s.name):
            continue
        hdr = demo_check._header(s.read_text(encoding="utf-8"))
        tm = re.fullmatch(r"(\d+)\s*min", hdr.get("Time", ""))
        out.append({"name": s.stem, "key": Path(hdr.get("Answer key", "")).name, "time": int(tm.group(1)) if tm else None,
                    "thread": hdr.get("Thread", ""), "startsFrom": hdr.get("Starts from", ""), "objective": hdr.get("Objective", "")})
    return out


def _day_base(cur: dict, week: dict, d: dict, s: dict) -> dict:
    return {
        **{k: d[k] for k in ("day", "slug", "id", "kind", "gate", "demoFormat", "title", "subtitle", "subtopics")},
        "date": s["date"].isoformat(),
        "weekday": s["weekday"],
        "dateLabel": bi.date_label(s["date"], year=True),
        "feedback": bi.is_feedback(week, d),
        "notes": d.get("notes", ""),
        "exerciseKind": d.get("exerciseKind", "pytest"),
        "status": d.get("status", "planned"),
        "taught": d.get("taught"),
        "rel": f"{week['dir']}/{d['slug']}",
    }


def _common(cur: dict, week: dict, ew: dict, today: str | None, metrics: dict, config: dict) -> dict:
    week_no = week["week"]
    return {
        "root": _fwd(ROOT),
        "today": today or dt.date.today().isoformat(),
        "timezone": cur["timezone"],
        "week": week_no, "weekDir": week["dir"], "theme": week["theme"], "phase": week["phase"], "project": week["project"],
        "weekStart": ew["start"].isoformat(), "weekEnd": ew["end"].isoformat(),
        "weekNotes": week.get("notes", ""),
        "metrics": metrics,
        "llm": config["llm"]["byWeek"].get(str(week_no), config["llm"]["default"]),
        "models": config.get("models", {}),
        "config": {k: config[k] for k in CONFIG_KEYS},
    }


def plan_args(cur: dict, week: dict, today: str | None, metrics: dict, config: dict) -> dict:
    """Args for harness/workflows/week-plan.js: every teaching day of the week, the thread policy for this week,
    the previous week's plan and end state, and the model tiers exactly as day args carry them."""
    ew = bi.expand_week(cur, week)
    by_slot = {s["slot"]: s for s in ew["slots"]}
    days = []
    for d in bi.teaching_days(week):
        base = _day_base(cur, week, d, by_slot[d["day"]])
        base["existingScripts"] = _existing_scripts(base["rel"])
        brief = ROOT / "harness" / "research" / f"{base['rel']}.md"
        base["researchBrief"] = _fwd(brief) if brief.is_file() else None
        days.append(base)
    week_no = week["week"]
    prev = plan_path(week_no - 1)
    prev_end = {}
    if prev.is_file():
        try:
            pp = plan_check.load_plan(prev)
            for t in pp["threads"]:
                if t["rungs"]:
                    prev_end[t["id"]] = t["rungs"][-1]["keyPath"]
        except ValueError:
            pass
    threads = {tid: t for tid, t in (config.get("threads") or {}).items()
               if isinstance(t, dict) and (not t.get("weeks") or t["weeks"][0] <= week_no <= t["weeks"][1])}
    return {
        **_common(cur, week, ew, today, metrics, config),
        "days": days,
        "projects": cur.get("projects", {}),
        "threads": threads,
        "planFile": _fwd(plan_path(week_no)),
        "previousPlan": _fwd(prev) if prev.is_file() else None,
        "previousEndState": prev_end,
        "template": _fwd(ROOT / "harness" / "templates" / "week-plan.md"),
        "critic": _fwd(ROOT / "harness" / "critics" / "week-plan.md"),
        "demoTemplate": _fwd(ROOT / "harness" / "templates" / "demo-script.md"),
        "demosCritic": _fwd(ROOT / "harness" / "critics" / "demos.md"),
    }


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
        except Exception:
            pass
    today = None
    if "--today" in argv:
        i = argv.index("--today")
        today = argv[i + 1]
        del argv[i:i + 2]
    flags = {f: f in argv for f in ("--skip-research", "--plan", "--no-plan")}
    argv = [a for a in argv if a not in flags]
    skip_research, plan_mode, no_plan = flags["--skip-research"], flags["--plan"], flags["--no-plan"]
    nums = [int(a) for a in argv]
    cur = bi.load_curriculum()
    metrics = json.loads((ROOT / "harness" / "metrics.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "harness" / "config.json").read_text(encoding="utf-8"))
    if plan_mode:
        if len(nums) != 1:
            print("--plan takes exactly one week number", file=sys.stderr)
            return 2
        week = next((w for w in cur["weeks"] if w["week"] == nums[0]), None)
        if week is None:
            print(f"no week {nums[0]}", file=sys.stderr)
            return 2
        print(json.dumps(plan_args(cur, week, today, metrics, config), indent=2, ensure_ascii=False))
        return 0
    if len(nums) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    week_no, day_nos = nums[0], nums[1:]
    week = next(w for w in cur["weeks"] if w["week"] == week_no)
    ew = bi.expand_week(cur, week)
    by_slot = {s["slot"]: s for s in ew["slots"]}
    for n in day_nos:
        s = by_slot.get(n)
        if s is None:
            print(f"week {week_no} has no day {n}", file=sys.stderr)
            return 2
        if s["kind"] == "holiday":
            print(f"week {week_no} day {n} is a holiday ({s['label']}, {s['date']}); nothing to author", file=sys.stderr)
            return 2
    # Week plan gate (D-0034): blocking, like the old repo's R-013; --no-plan is the logged escape.
    plan = None
    pfile = plan_path(week_no)
    if no_plan:
        print(f"WARNING: --no-plan escape used for week {week_no} day(s) {day_nos}: the day runs WITHOUT a week plan "
              f"(no thread rows, no coverage rows). Record this in STATUS.md with the reason.", file=sys.stderr)
    else:
        if not pfile.is_file():
            print(f"BLOCKED: no week plan at {pfile}. Run `python harness/args_for.py {week_no} --plan --today <date>` and the "
                  f"week-plan workflow first, or pass --no-plan (logged escape).", file=sys.stderr)
            return 2
        problems = plan_check.check_plan(pfile, metrics["demos"])
        if problems:
            print(f"BLOCKED: {pfile} fails plan_check ({len(problems)} problem(s)); fix the plan or pass --no-plan (logged escape):", file=sys.stderr)
            for pr in problems:
                print("  " + pr, file=sys.stderr)
            return 2
        plan = plan_check.load_plan(pfile)
    teaching = bi.teaching_days(week)
    days = []
    for d in teaching:
        if d["day"] not in day_nos:
            continue
        s = by_slot[d["day"]]
        idx = teaching.index(d)
        nxt = teaching[idx + 1] if idx + 1 < len(teaching) else None
        # Only link forward to a page that exists or that this same run writes (week batch, D-0038);
        # any other planned day falls back to the program index.
        if nxt is not None and nxt.get("status") != "live" and nxt["day"] not in day_nos:
            nxt = None
        rows = plan_check.day_rows(plan, d["id"]) if plan else {"weekPlanRows": [], "threadRows": [], "ladderRows": [], "dayShape": "", "spoilerRows": []}
        days.append({
            **_day_base(cur, week, d, s),
            "nextHref": f"{nxt['slug']}.html" if nxt else "../../index.html",
            "nextLabel": f"Day {nxt['day']} — {nxt['title']} →" if nxt else "Back to program →",
            **rows,
        })
        if skip_research:
            brief = ROOT / "harness" / "research" / f"{week['dir']}/{d['slug']}.md"
            if not brief.is_file():
                print(f"--skip-research needs an existing brief at {brief}", file=sys.stderr)
                return 2
    # Notes-page template (D-0031): the promoted page named in config.json, else the exemplar.
    exemplar = ROOT / "harness" / "templates" / "day.exemplar.html"
    template = ROOT / config["template"] if config.get("template") else exemplar
    if not template.is_file():
        print(f"config.json template {template} missing; falling back to {exemplar}", file=sys.stderr)
        template = exemplar
    args = {
        **_common(cur, week, ew, today, metrics, config),
        "days": days,
        "skipResearch": skip_research,
        "template": _fwd(template),
        "weekPlan": _fwd(pfile) if plan else None,
        "noPlan": no_plan,
    }
    print(json.dumps(args, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
