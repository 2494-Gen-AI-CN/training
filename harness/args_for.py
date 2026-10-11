#!/usr/bin/env python3
"""Print the Workflow `args` JSON for one or more curriculum days.

Workflow scripts cannot read files or call Date(), so everything the day-fanout
script needs — day metadata, calendar date, metrics, config, today's date —
travels in args. Dates come from build_index.slot_date (D-0013); holiday slots
are refused (D-0014).

Usage:
    python harness/args_for.py 1 2            # week 1, day 2 (slot 2 = Tue)
    python harness/args_for.py 1 2 3          # week 1, days 2 and 3 (pipelined)
    python harness/args_for.py 1 2 --today 2026-10-13
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

ROOT = bi.ROOT


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
    nums = [int(a) for a in argv]
    if len(nums) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    week_no, day_nos = nums[0], nums[1:]
    cur = bi.load_curriculum()
    metrics = json.loads((ROOT / "harness" / "metrics.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "harness" / "config.json").read_text(encoding="utf-8"))
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
    teaching = bi.teaching_days(week)
    days = []
    for d in teaching:
        if d["day"] not in day_nos:
            continue
        s = by_slot[d["day"]]
        idx = teaching.index(d)
        nxt = teaching[idx + 1] if idx + 1 < len(teaching) else None
        days.append({
            **{k: d[k] for k in ("day", "slug", "id", "kind", "gate", "demoFormat", "title", "subtitle", "subtopics")},
            "date": s["date"].isoformat(),
            "weekday": s["weekday"],
            "dateLabel": bi.date_label(s["date"], year=True),
            "feedback": bi.is_feedback(week, d),
            "rel": f"{week['dir']}/{d['slug']}",
            "nextHref": f"{nxt['slug']}.html" if nxt else "../../index.html",
            "nextLabel": f"Day {nxt['day']} — {nxt['title']} →" if nxt else "Back to program →",
        })
    llm = config["llm"]["byWeek"].get(str(week_no), config["llm"]["default"])
    args = {
        "root": str(ROOT).replace("\\", "/"),
        "today": today or dt.date.today().isoformat(),
        "timezone": cur["timezone"],
        "week": week_no, "weekDir": week["dir"], "theme": week["theme"], "phase": week["phase"], "project": week["project"],
        "weekStart": ew["start"].isoformat(), "weekEnd": ew["end"].isoformat(),
        "weekNotes": week.get("notes", ""),
        "days": days,
        "metrics": metrics,
        "llm": llm,
        "config": {k: config[k] for k in ("cohort", "siteTitle", "brand", "repoUrl", "repoBranch", "feedbackFormUrl", "python")},
    }
    print(json.dumps(args, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
