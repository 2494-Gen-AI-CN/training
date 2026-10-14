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
    python harness/args_for.py 2 --plan --cold --today 2026-10-14   # D-0050: previousEndState {} + coldRestart, every
                                                     # thread starts cold (the previous week's ladder was not delivered)
    python harness/args_for.py 1 2 3 --notes-only    # D-0040: research depth + notes page only; the brief, demo
                                                     # scripts and keys must already be on disk (a demoFormat loose
                                                     # day, D-0050, needs neither: no key README only warns);
                                                     # exercise and runbook are untouched
    python harness/args_for.py 1 2 --notes-only --template harness/templates/day.exemplar.html
                                                     # override the config template (pilot of a new page shape)
    python harness/args_for.py 2 --practice          # D-0047: practice-tasks.js, suitability pass over the week's
                                                     # authored pages (name day slots to narrow it)
    python harness/args_for.py 2 --practice-build    # D-0047: practice-tasks.js, build the tasks the trainer approved
                                                     # (refused while a proposed task has no answer)
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
import practice_tasks as pt  # noqa: E402

ROOT = bi.ROOT
CONFIG_KEYS = ("cohort", "siteTitle", "brand", "repoUrl", "repoBranch", "siteUrl", "feedbackFormUrl", "python", "audience", "learnerRepo", "demoRepo")


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


def plan_args(cur: dict, week: dict, today: str | None, metrics: dict, config: dict, cold: bool = False) -> dict:
    """Args for harness/workflows/week-plan.js: every teaching day of the week, the thread policy for this week,
    the previous week's plan and end state, and the model tiers exactly as day args carry them.
    cold (--cold, after loose days D-0050): previousEndState is empty and coldRestart is set, so every thread's
    first rung starts cold."""
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
    cold_args = {}
    if cold:
        prev_end = {}
        cold_args = {"coldRestart": "the previous week's ladder was not delivered (loose days); every thread starts cold this week"}
    return {
        **_common(cur, week, ew, today, metrics, config),
        **cold_args,
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


def practice_args(cur: dict, week: dict, day_nos: list[int], build: bool, today: str | None, metrics: dict, config: dict) -> tuple[dict | None, list[str]]:
    """Args for harness/workflows/practice-tasks.js (D-0047), or None with the reasons on the second value.

    Suitability (build False): the week's days whose notes page is authored and that carry no built task yet;
    named days must qualify, unnamed ones are skipped with a note. Build: the days whose proposal has approved
    tasks still to build. It is refused while any task of a chosen day has no answer from the trainer."""
    ew = bi.expand_week(cur, week)
    by_slot = {s["slot"]: s for s in ew["slots"]}
    week_no = week["week"]
    notes: list[str] = []
    plan = None
    if plan_path(week_no).is_file():
        try:
            plan = plan_check.load_plan(plan_path(week_no))
        except ValueError:
            notes.append(f"week {week_no} plan does not parse; no anti-spoiler rows passed")
    teaching = bi.teaching_days(week)
    unknown = [n for n in day_nos if n not in {d["day"] for d in teaching}]
    if unknown:
        return None, [f"week {week_no} has no teaching day {unknown}"]
    days, refused, exemplar = [], [], None
    for w in cur["weeks"]:   # the accepted shape to copy: the first day in the course with built tasks
        for d in bi.teaching_days(w):
            rel = f"{w['dir']}/{d['slug']}"
            if exemplar is None and pt.built(pt.load(rel)):
                exemplar = {"day": d["id"], "page": f"docs/weeks/{rel}.html", "file": _fwd(pt.path_for(rel)),
                            "answers": f"trainer/{rel}/solutions/practice.py", "cases": f"trainer/{rel}/solutions/practice_cases.py"}
    for d in teaching:
        named = d["day"] in day_nos
        if day_nos and not named:
            continue
        rel = f"{week['dir']}/{d['slug']}"
        doc = pt.load(rel)
        why = None
        if not pt.page_for(rel).is_file() or d.get("status") != "live":
            why = "its notes page is not authored yet (practice tasks come after the day's other content)"
        elif not build and pt.built(doc):
            why = "it already carries built tasks (to change them, edit its file under harness/practice/ and run insert)"
        elif build and doc is None:
            why = "it has no proposal (run the suitability pass first)"
        elif build and any(t["approved"] is None for t in doc["tasks"]):
            why = f"BLOCKED: the trainer has not answered every proposed task (python harness/practice_tasks.py show {week_no} {d['day']}, then approve)"
            named = True   # an unanswered proposal stops the build; it is never skipped silently
        elif build and not any(t["approved"] for t in doc["tasks"]):
            why = "no task of it was approved"
        elif build and not named and all(pt.is_built(t) for t in doc["tasks"] if t["approved"]):
            why = "every approved task is built (name the day to rebuild it)"
        if why:
            (refused if named else notes).append(f"{d['id']}: {why}")
            continue
        brief = ROOT / "harness" / "research" / f"{rel}.md"
        readme = ROOT / "exercises" / rel / "README.md"
        day = {
            **_day_base(cur, week, d, by_slot[d["day"]]),
            "pageFile": _fwd(pt.page_for(rel)), "pageRel": f"docs/weeks/{rel}.html",
            "practiceFile": _fwd(pt.path_for(rel)), "practiceRel": f"harness/practice/{rel}.json",
            "researchBrief": _fwd(brief) if brief.is_file() else None,
            "exerciseReadme": _fwd(readme) if readme.is_file() else None,
            "solutionsDir": f"trainer/{rel}/solutions",
            "spoilerRows": plan_check.day_rows(plan, d["id"]).get("spoilerRows", []) if plan else [],
        }
        if build:
            day["tasks"] = [{k: t[k] for k in ("id", "title", "step", "idea", "checks")} | {"built": pt.is_built(t)} for t in doc["tasks"] if t["approved"]]
        days.append(day)
    if refused:
        return None, refused + notes
    if not days:
        return None, notes + [f"week {week_no}: no day to {'build' if build else 'assess'}"]
    worker = (ROOT / "docs" / "assets" / "js" / "pyworker.js").read_text(encoding="utf-8")
    pyodide = re.search(r"pyodide@(\d+\.\d+\.\d+)", worker)
    return {
        **_common(cur, week, ew, today, metrics, config),
        "mode": "build" if build else "suitability",
        "days": days,
        "threads": {tid: t for tid, t in (config.get("threads") or {}).items()
                    if isinstance(t, dict) and (not t.get("weeks") or t["weeks"][0] <= week_no <= t["weeks"][1])},
        "critic": _fwd(ROOT / "harness" / "critics" / "practice.md"),
        "exemplar": exemplar,
        "runtime": {"pyodide": pyodide.group(1) if pyodide else None, "worker": "docs/assets/js/pyworker.js", "widgets": "docs/assets/js/widgets.js"},
    }, notes


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
    template_override = None
    if "--template" in argv:
        i = argv.index("--template")
        template_override = argv[i + 1]
        del argv[i:i + 2]
    flags = {f: f in argv for f in ("--skip-research", "--plan", "--no-plan", "--notes-only", "--practice", "--practice-build", "--cold")}
    argv = [a for a in argv if a not in flags]
    skip_research, plan_mode, no_plan, notes_only = flags["--skip-research"], flags["--plan"], flags["--no-plan"], flags["--notes-only"]
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
        print(json.dumps(plan_args(cur, week, today, metrics, config, cold=flags["--cold"]), indent=2, ensure_ascii=False))
        return 0
    if flags["--practice"] or flags["--practice-build"]:
        week = next((w for w in cur["weeks"] if w["week"] == nums[0]), None) if nums else None
        if week is None or (flags["--practice"] and flags["--practice-build"]):
            print("--practice and --practice-build take a week number and optional day slots, one mode at a time", file=sys.stderr)
            return 2
        out, notes = practice_args(cur, week, nums[1:], flags["--practice-build"], today, metrics, config)
        for n in notes:
            print(("" if out is None else "note: ") + n, file=sys.stderr)
        if out is None:
            return 2
        print(json.dumps(out, indent=2, ensure_ascii=False))
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
        rel = f"{week['dir']}/{d['slug']}"
        day_args = {
            **_day_base(cur, week, d, s),
            "nextHref": f"{nxt['slug']}.html" if nxt else "../../index.html",
            "nextLabel": f"Day {nxt['day']} — {nxt['title']} →" if nxt else "Back to program →",
            **rows,
        }
        brief = ROOT / "harness" / "research" / f"{rel}.md"
        if (skip_research or notes_only) and not brief.is_file():
            print(f"{'--notes-only' if notes_only else '--skip-research'} needs an existing brief at {brief}", file=sys.stderr)
            return 2
        if notes_only:
            # D-0040: the notes page is re-authored on top of the day's existing demo scripts and keys.
            scripts = _existing_scripts(rel)
            fmt = d.get("demoFormat")
            has_readme = (ROOT / "trainer" / rel / "demos" / "key" / "README.md").is_file()
            if fmt == "loose":
                # D-0050: loose days may have no scripts at all; fallback scripts without a key README only warn.
                if scripts and not has_readme:
                    print(f"WARNING: loose day {rel} has fallback scripts but no key/README.md under trainer/{rel}/demos/; continuing", file=sys.stderr)
            elif fmt != "none" and (not scripts or not has_readme):
                print(f"--notes-only needs the day's demo scripts and key/README.md on disk under trainer/{rel}/demos/", file=sys.stderr)
                return 2
            day_args["existingScripts"] = scripts
        days.append(day_args)
    # Notes-page template (D-0031): the promoted page named in config.json, else the exemplar; --template overrides.
    exemplar = ROOT / "harness" / "templates" / "day.exemplar.html"
    if template_override:
        template = Path(template_override)
        if not template.is_absolute():
            template = ROOT / template
        if not template.is_file():
            print(f"--template {template_override} is not a file", file=sys.stderr)
            return 2
    else:
        template = ROOT / config["template"] if config.get("template") else exemplar
        if not template.is_file():
            print(f"config.json template {template} missing; falling back to {exemplar}", file=sys.stderr)
            template = exemplar
    args = {
        **_common(cur, week, ew, today, metrics, config),
        "days": days,
        "skipResearch": skip_research,
        "notesOnly": notes_only,
        "template": _fwd(template),
        "weekPlan": _fwd(pfile) if plan else None,
        "noPlan": no_plan,
    }
    print(json.dumps(args, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
