#!/usr/bin/env python3
"""Print the Workflow `args` JSON for one or more curriculum days.

Workflow scripts cannot read files or call Date(), so everything the day-fanout
script needs — day metadata, metrics, config, today's date — travels in args.

Usage:
    python harness/args_for.py 1 1            # week 1, day 1
    python harness/args_for.py 1 2 3          # week 1, days 2 and 3 (pipelined)
    python harness/args_for.py 1 1 --today 2026-10-13
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
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
    cur = json.loads((ROOT / "harness" / "curriculum.json").read_text(encoding="utf-8"))
    metrics = json.loads((ROOT / "harness" / "metrics.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "harness" / "config.json").read_text(encoding="utf-8"))
    week = next(w for w in cur["weeks"] if w["week"] == week_no)
    days = []
    for d in week["days"]:
        if d["day"] in day_nos:
            nxt = next((x for x in week["days"] if x["day"] == d["day"] + 1), None)
            days.append({
                **{k: d[k] for k in ("day", "slug", "id", "kind", "gate", "demoFormat", "title", "subtitle", "subtopics")},
                "feedback": bool(d.get("feedback")),
                "rel": f"{week['dir']}/{d['slug']}",
                "nextHref": f"{nxt['slug']}.html" if nxt else "../../index.html",
                "nextLabel": f"Day {nxt['day']} — {nxt['title']} →" if nxt else "Back to program →",
            })
    missing = sorted(set(day_nos) - {d["day"] for d in days})
    if missing:
        print(f"week {week_no} has no day(s) {missing}", file=sys.stderr)
        return 2
    llm = config["llm"]["byWeek"].get(str(week_no), config["llm"]["default"])
    args = {
        "root": str(ROOT).replace("\\", "/"),
        "today": today or dt.date.today().isoformat(),
        "week": week_no, "weekDir": week["dir"], "theme": week["theme"], "phase": week["phase"], "project": week["project"],
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
