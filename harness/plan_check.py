#!/usr/bin/env python3
"""Parse and check one week plan (harness/plans/week-WW.md, template harness/templates/week-plan.md; D-0034).

The plan is written once per week by harness/workflows/week-plan.js before any day of the week is authored.
args_for.py reads it (through load_plan) to gate day args and to pass each day's rows into the day workflow;
the week-plan critic and tests/test_plans.py call check_plan.

Checks (stdlib only):
  headings  - the template's sections, in order; one "### <id> — ..." per teaching day under Per-day shape
  threads   - "### <thread-id>" blocks with a rung table: rungs 1..n, Day in this week, Key = Demo + ext,
              Starts from = cold (first rung) or exactly the previous rung's key path (or an existing key on
              disk for the first rung of a later week); .py start keys exist when the rung's day is authored/live
  standalone- Day in this week, Demo/Key well formed
  ladder    - every thread rung and standalone demo appears exactly once, numbered 1..n in teaching order;
              Minutes within metrics.demos.minutesPerScriptMin..Max; scripts per day within scriptsMin..Max;
              a day's demos are numbered 01.. contiguously in ladder order; Must follow cites earlier rows and
              includes the previous rung of the same thread
  coverage  - every curriculum subtopic of every teaching day of the week appears once, with its own day,
              Demo = a demo of that day | facilitation | notes, Notes step a positive integer
  authored/live days - an authored or live day is recorded as-is: its rows equal its scripts on disk
              (name, Time, Thread, Starts from) (D-0052)

Usage:
    python harness/plan_check.py harness/plans/week-01.md
Exit 1 with one problem per line when anything fails; exit 0 and "OK" otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import demo_check  # noqa: E402

ROOT = bi.ROOT
METRICS = ROOT / "harness" / "metrics.json"
SECTIONS = ["## Weekly Epic", "## Assumes from the previous week", "## Threads", "## Standalone demos", "## Demo ladder",
            "## Per-day shape", "## Anti-spoiler ledger", "## Real-world framing and deliberate deviations", "## Coverage map"]
RUNG_COLS = ["Rung", "Day", "Demo", "Key", "Starts from", "Adds", "End state", "Commit message"]
STANDALONE_COLS = ["Day", "Demo", "Key", "Minutes", "Why it fits no thread"]
LADDER_COLS = ["#", "Day", "Demo", "Minutes", "Must follow", "Guarantees"]
COVERAGE_COLS = ["Subtopic", "Day", "Demo", "Notes step"]
SPOILER_COLS = ["Day", "Defers", "To", "Why"]
DEVIATION_COLS = ["Deviation", "Workplace reality", "Pedagogical reason"]
DEMO_RE = re.compile(r"^(\d{2})_([a-z0-9]+(?:[-_][a-z0-9]+)*)$")
KEY_RE = re.compile(r"^(\d{2})_([a-z0-9]+(?:[-_][a-z0-9]+)*)\.(py|md|ipynb)$")
DAY_HEAD_RE = re.compile(r"^### (w\d{2}d\d) — ", re.M)
THREAD_HEAD_RE = re.compile(r"^### ([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", re.M)


def _cell(s: str) -> str:
    """Cell text; a cell that is ONE code span (`02_x.py`) is unwrapped, any other backtick is content."""
    s = s.strip()
    if len(s) >= 2 and s.startswith("`") and s.endswith("`") and s.count("`") == 2:
        return s[1:-1].strip()
    return s


def _tables(text: str) -> list[list[dict[str, str]]]:
    """Every markdown table in `text` as a list of row dicts keyed by header cell."""
    out, cur, header = [], [], None
    for ln in text.splitlines() + [""]:
        if ln.lstrip().startswith("|"):
            cells = [_cell(c) for c in ln.strip().strip("|").split("|")]
            if header is None:
                header = cells
            elif all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            else:
                cur.append(dict(zip(header, cells + [""] * (len(header) - len(cells)))))
        else:
            if header is not None:
                out.append((header, cur))
            cur, header = [], None
    return out


def _section(text: str, heading: str) -> str:
    """Body of a '## heading' up to the next '## ' heading ('' when absent)."""
    m = re.search(rf"^{re.escape(heading)}\s*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"^## ", rest, re.M)
    return rest[:n.start()] if n else rest


def _table_with(body: str, cols: list[str]) -> list[dict[str, str]] | None:
    for header, rows in _tables(body):
        if header == cols:
            return rows
    return None


def load_plan(path: Path) -> dict:
    """Structured view of a plan: week, threads (with rungs and resolved key paths), standalone, ladder, coverage,
    dayShape (id -> text). Raises ValueError when the file is not a plan at all."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"# Week (\d{2}) plan", text)
    if not m:
        raise ValueError(f"{path.name}: first line must read '# Week WW plan — <theme>'")
    week = int(m.group(1))
    cur = bi.load_curriculum()
    wk = next((w for w in cur["weeks"] if w["week"] == week), None)
    if wk is None:
        raise ValueError(f"{path.name}: week {week} is not in the curriculum")
    slug_by_id = {d["id"]: d["slug"] for d in wk["days"] if d.get("kind") != "holiday"}
    threads = []
    tbody = _section(text, "## Threads")
    heads = list(THREAD_HEAD_RE.finditer(tbody))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(tbody)
        block = tbody[h.end():end]
        meta = {k.strip(): v.strip() for k, v in re.findall(r"^- ([A-Za-z ]+?):\s*(.*)$", block, re.M)}
        rungs = []
        for r in (_table_with(block, RUNG_COLS) or []):
            slug = slug_by_id.get(r["Day"])
            rungs.append({**{k: r[k] for k in RUNG_COLS},
                          "keyPath": f"trainer/{wk['dir']}/{slug}/demos/key/{r['Key']}" if slug else None})
        threads.append({"id": h.group(1), "domain": meta.get("Domain", ""), "scope": meta.get("Scope", ""),
                        "startState": meta.get("Start state this week", ""), "endState": meta.get("End state this week", ""),
                        "rungs": rungs})
    standalone = []
    for r in (_table_with(_section(text, "## Standalone demos"), STANDALONE_COLS) or []):
        slug = slug_by_id.get(r["Day"])
        standalone.append({**{k: r[k] for k in STANDALONE_COLS},
                           "keyPath": f"trainer/{wk['dir']}/{slug}/demos/key/{r['Key']}" if slug else None})
    ladder = [{k: r[k] for k in LADDER_COLS} for r in (_table_with(_section(text, "## Demo ladder"), LADDER_COLS) or [])]
    coverage = [{k: r[k] for k in COVERAGE_COLS} for r in (_table_with(_section(text, "## Coverage map"), COVERAGE_COLS) or [])]
    spoilers = [{k: r[k] for k in SPOILER_COLS} for r in (_table_with(_section(text, "## Anti-spoiler ledger"), SPOILER_COLS) or [])]
    deviations = [{k: r[k] for k in DEVIATION_COLS} for r in (_table_with(_section(text, "## Real-world framing and deliberate deviations"), DEVIATION_COLS) or [])]
    shape_body = _section(text, "## Per-day shape")
    day_shape = {}
    dh = list(DAY_HEAD_RE.finditer(shape_body))
    for i, h in enumerate(dh):
        end = dh[i + 1].start() if i + 1 < len(dh) else len(shape_body)
        day_shape[h.group(1)] = shape_body[h.start():end].strip()
    return {"path": str(path), "week": week, "weekDir": wk["dir"], "threads": threads, "standalone": standalone,
            "ladder": ladder, "coverage": coverage, "spoilers": spoilers, "deviations": deviations, "dayShape": day_shape,
            "epic": _section(text, "## Weekly Epic").strip()}


def day_rows(plan: dict, day_id: str) -> dict:
    """The rows of one day, as args_for.py passes them into the day workflow."""
    thread_rows = []
    for t in plan["threads"]:
        for r in t["rungs"]:
            if r["Day"] == day_id:
                thread_rows.append({"thread": t["id"], "rung": r["Rung"], "demo": r["Demo"], "key": r["Key"],
                                    "startsFrom": r["Starts from"], "adds": r["Adds"], "endState": r["End state"],
                                    "commitMessage": r["Commit message"], "keyPath": r["keyPath"]})
    for s in plan["standalone"]:
        if s["Day"] == day_id:
            thread_rows.append({"thread": "standalone", "rung": "", "demo": s["Demo"], "key": s["Key"], "startsFrom": "cold",
                                "adds": s["Why it fits no thread"], "endState": "", "commitMessage": "", "keyPath": s["keyPath"]})
    return {
        "weekPlanRows": [r for r in plan["coverage"] if r["Day"] == day_id],
        "threadRows": thread_rows,
        "ladderRows": [r for r in plan["ladder"] if r["Day"] == day_id],
        "dayShape": plan["dayShape"].get(day_id, ""),
        "spoilerRows": [r for r in plan["spoilers"] if r["Day"] == day_id or r["To"] == day_id],
    }


def check_plan(path: Path, metrics: dict | None = None, root: Path = ROOT) -> list[str]:
    """All problems with one plan file. Empty list = OK."""
    if metrics is None:
        metrics = json.loads(METRICS.read_text(encoding="utf-8"))["demos"]
    p: list[str] = []
    if not path.is_file():
        return [f"{path}: missing"]
    text = path.read_text(encoding="utf-8")
    try:
        plan = load_plan(path)
    except ValueError as e:
        return [str(e)]
    name = path.name
    cur = bi.load_curriculum()
    wk = next(w for w in cur["weeks"] if w["week"] == plan["week"])
    teaching = bi.teaching_days(wk)
    ids = [d["id"] for d in teaching]
    recorded = {d["id"] for d in teaching if d.get("status") in ("authored", "live")}  # D-0052
    # headings in order
    pos = -1
    for s in SECTIONS:
        m = re.search(rf"^{re.escape(s)}\s*$", text, re.M)
        if not m:
            p.append(f"{name}: missing section '{s}'")
        elif m.start() < pos:
            p.append(f"{name}: section '{s}' out of template order")
        else:
            pos = m.start()
    if not plan["epic"] or len(plan["epic"].split()) < 40:
        p.append(f"{name}: Weekly Epic must be a real paragraph (>= 40 words)")
    for did in ids:
        if did not in plan["dayShape"]:
            p.append(f"{name}: Per-day shape has no '### {did} — ...' heading")
    for did, body in plan["dayShape"].items():
        if did not in ids:
            p.append(f"{name}: Per-day shape names {did}, not a teaching day of week {plan['week']}")
        for need in ("- AM:", "- PM:", "- Stop points:", "- Cut first:", "- Never cut:"):
            if need not in body:
                p.append(f"{name}: Per-day shape {did} lacks '{need}'")
    # threads
    if not plan["threads"]:
        p.append(f"{name}: Threads section has no '### <thread-id>' block")
    demos_by_day: dict[str, list[tuple[str, str]]] = {}  # day -> [(demo, origin)]
    expected_start: dict[str, str] = {}  # (day, demo) -> Starts from
    for t in plan["threads"]:
        tid = t["id"]
        if not t["domain"] or not t["scope"]:
            p.append(f"{name}: thread {tid} needs '- Domain:' and '- Scope:' lines")
        if not t["rungs"]:
            p.append(f"{name}: thread {tid} has no rung table with columns {RUNG_COLS}")
        prev_key = None
        for i, r in enumerate(t["rungs"]):
            tag = f"thread {tid} rung {r['Rung'] or '?'}"
            if r["Rung"] != str(i + 1):
                p.append(f"{name}: {tag}: rungs must be numbered 1..n in order")
            if r["Day"] not in ids:
                p.append(f"{name}: {tag}: Day '{r['Day']}' is not a teaching day of week {plan['week']}")
            if not DEMO_RE.match(r["Demo"]):
                p.append(f"{name}: {tag}: Demo must read NN_<slug>, got '{r['Demo']}'")
            if not KEY_RE.match(r["Key"]) or r["Key"].rsplit(".", 1)[0] != r["Demo"]:
                p.append(f"{name}: {tag}: Key must be Demo + .py|.md|.ipynb, got '{r['Key']}'")
            s = r["Starts from"]
            if i == 0:
                if s != "cold" and not (demo_check.STARTS_RE.match(s) and (root / s).is_file()):
                    p.append(f"{name}: {tag}: first rung must start cold or from an existing key (previous week's last rung), got '{s}'")
            elif s != prev_key:
                p.append(f"{name}: {tag}: Starts from must be the previous rung's key '{prev_key}', got '{s}'")
            if r["Day"] in recorded and s != "cold" and not (root / s).is_file():
                p.append(f"{name}: {tag}: authored/live day but Starts from key {s} is not on disk")
            for col in ("Adds", "End state", "Commit message"):
                if not r[col]:
                    p.append(f"{name}: {tag}: '{col}' is empty")
            prev_key = r["keyPath"]
            demos_by_day.setdefault(r["Day"], []).append((r["Demo"], tag))
            expected_start[(r["Day"], r["Demo"])] = (tid, s)
    for s in plan["standalone"]:
        tag = f"standalone {s['Demo']}"
        if s["Day"] not in ids:
            p.append(f"{name}: {tag}: Day '{s['Day']}' is not a teaching day of week {plan['week']}")
        if not DEMO_RE.match(s["Demo"]):
            p.append(f"{name}: {tag}: Demo must read NN_<slug>")
        if not KEY_RE.match(s["Key"]) or s["Key"].rsplit(".", 1)[0] != s["Demo"]:
            p.append(f"{name}: {tag}: Key must be Demo + .py|.md|.ipynb, got '{s['Key']}'")
        if not s["Why it fits no thread"]:
            p.append(f"{name}: {tag}: say why it fits no thread (A23)")
        demos_by_day.setdefault(s["Day"], []).append((s["Demo"], tag))
        expected_start[(s["Day"], s["Demo"])] = ("standalone", "cold")
    # ladder
    lo, hi = metrics.get("minutesPerScriptMin", 0), metrics.get("minutesPerScriptMax", 10**6)
    ladder = plan["ladder"]
    if not ladder:
        p.append(f"{name}: Demo ladder table missing (columns {LADDER_COLS})")
    seen: set[tuple[str, str]] = set()
    minutes_by: dict[tuple[str, str], int] = {}
    order_by_day: dict[str, list[str]] = {}
    row_no: dict[tuple[str, str], int] = {}
    for i, r in enumerate(ladder):
        tag = f"ladder #{r['#'] or '?'}"
        if r["#"] != str(i + 1):
            p.append(f"{name}: {tag}: rows must be numbered 1..n in order")
        key = (r["Day"], r["Demo"])
        if key in seen:
            p.append(f"{name}: {tag}: {r['Day']} {r['Demo']} listed twice")
        seen.add(key)
        row_no[key] = i + 1
        if key not in expected_start:
            p.append(f"{name}: {tag}: {r['Day']} {r['Demo']} is neither a thread rung nor a standalone demo")
        try:
            mins = int(r["Minutes"])
            minutes_by[key] = mins
            if not lo <= mins <= hi:
                p.append(f"{name}: {tag}: {mins} min outside {lo}..{hi}")
        except ValueError:
            p.append(f"{name}: {tag}: Minutes must be an integer, got '{r['Minutes']}'")
        order_by_day.setdefault(r["Day"], []).append(r["Demo"])
        mf = r["Must follow"]
        cites = set()
        if mf not in ("—", "-", "", "none"):
            for tok in re.split(r"[,\s]+", mf.strip()):
                if not tok.isdigit() or not 1 <= int(tok) < i + 1:
                    p.append(f"{name}: {tag}: Must follow '{mf}' must cite earlier ladder numbers only")
                else:
                    cites.add(int(tok))
        r["_cites"] = cites
        prev_day = ladder[i - 1]["Day"] if i > 0 else None
        if prev_day in ids and r["Day"] in ids and ids.index(r["Day"]) < ids.index(prev_day):
            p.append(f"{name}: {tag}: ladder is not in teaching order ({prev_day} before {r['Day']})")
    for key in expected_start:
        if key not in seen:
            p.append(f"{name}: {key[0]} {key[1]} is in Threads/Standalone but not in the Demo ladder")
    # the previous rung of a thread must be cited in Must follow
    for t in plan["threads"]:
        for a, b in zip(t["rungs"], t["rungs"][1:]):
            ka, kb = (a["Day"], a["Demo"]), (b["Day"], b["Demo"])
            if ka in row_no and kb in row_no:
                rb = ladder[row_no[kb] - 1]
                if row_no[ka] not in rb.get("_cites", set()):
                    p.append(f"{name}: ladder #{row_no[kb]} ({b['Demo']}) must cite #{row_no[ka]} ({a['Demo']}), the previous rung of {t['id']}")
    smin, smax = metrics.get("scriptsMin", 1), metrics.get("scriptsMax", 99)
    for did in ids:
        d = next(x for x in teaching if x["id"] == did)
        demos = order_by_day.get(did, [])
        if d.get("demoFormat") == "none":
            if demos:
                p.append(f"{name}: {did} is demoFormat none but the ladder lists {demos}")
            continue
        if not smin <= len(demos) <= smax:
            p.append(f"{name}: {did} has {len(demos)} demos in the ladder, band is {smin}..{smax}")
        nums = [int(x[:2]) for x in demos if DEMO_RE.match(x)]
        if nums != list(range(1, len(nums) + 1)):
            p.append(f"{name}: {did} demos must be numbered 01.. in ladder order, got {nums}")
    # coverage map
    cov = plan["coverage"]
    if not cov:
        p.append(f"{name}: Coverage map table missing (columns {COVERAGE_COLS})")
    want = {(d["id"], st.strip().lower()): st for d in teaching for st in d["subtopics"]}
    got: dict[tuple[str, str], int] = {}
    for r in cov:
        key = (r["Day"], r["Subtopic"].strip().lower())
        got[key] = got.get(key, 0) + 1
        if key not in want:
            p.append(f"{name}: coverage row '{r['Subtopic']}' / {r['Day']} is not a curriculum subtopic of that day (spell it exactly as curriculum.json does)")
        demo = r["Demo"]
        if demo not in ("facilitation", "notes") and demo not in order_by_day.get(r["Day"], []):
            p.append(f"{name}: coverage row '{r['Subtopic']}': Demo '{demo}' is not a demo of {r['Day']} in the ladder, nor 'facilitation' / 'notes'")
        if not r["Notes step"].isdigit() or int(r["Notes step"]) < 1:
            p.append(f"{name}: coverage row '{r['Subtopic']}': Notes step must be a positive integer, got '{r['Notes step']}'")
    for key, st in want.items():
        n = got.get(key, 0)
        if n == 0:
            p.append(f"{name}: coverage map lacks subtopic '{st}' of {key[0]} (COVERAGE DEFECT)")
        elif n > 1:
            p.append(f"{name}: coverage map lists '{st}' of {key[0]} {n} times")
    # ledgers
    if not plan["spoilers"]:
        p.append(f"{name}: Anti-spoiler ledger table missing or empty (columns {SPOILER_COLS})")
    for r in plan["spoilers"]:
        if r["Day"] not in ids:
            p.append(f"{name}: anti-spoiler row Day '{r['Day']}' is not a teaching day of this week")
        if not (r["To"] in ids or re.fullmatch(r"week \d{1,2}", r["To"]) or r["To"].startswith("w")):
            p.append(f"{name}: anti-spoiler row '{r['Defers']}': To must be a day id or 'week WW', got '{r['To']}'")
    if not plan["deviations"]:
        p.append(f"{name}: deviation ledger table missing or empty (columns {DEVIATION_COLS})")
    # authored/live days: rows equal the scripts on disk (D-0052)
    trainer = root / "trainer"
    for d in teaching:
        if d.get("status") not in ("authored", "live") or d.get("demoFormat") == "none" or not trainer.exists():
            continue
        ddir = trainer / wk["dir"] / d["slug"] / "demos"
        if d.get("demoFormat") == "loose" and not ddir.is_dir():
            continue  # D-0050: a loose authored/live day without fallback scripts has nothing to compare to the ladder
        on_disk = {}
        for s in sorted(ddir.glob("*.md")):
            if re.match(r"^\d{2}_", s.name):
                hdr = demo_check._header(s.read_text(encoding="utf-8"))
                tm = re.fullmatch(r"(\d+)\s*min", hdr.get("Time", ""))
                on_disk[s.stem] = (int(tm.group(1)) if tm else None, hdr.get("Thread", ""), hdr.get("Starts from", ""), Path(hdr.get("Answer key", "")).name)
        planned = order_by_day.get(d["id"], [])
        if sorted(on_disk) != sorted(planned):
            p.append(f"{name}: authored/live day {d['id']}: plan lists {planned} but disk has {sorted(on_disk)} (an authored or live day is recorded as-is)")
            continue
        for demo, (mins, thread, starts, keyname) in on_disk.items():
            key = (d["id"], demo)
            if minutes_by.get(key) != mins:
                p.append(f"{name}: authored/live day {d['id']} {demo}: ladder says {minutes_by.get(key)} min, script header says {mins}")
            tid, s = expected_start.get(key, ("", ""))
            if (tid, s) != (thread, starts):
                p.append(f"{name}: authored/live day {d['id']} {demo}: plan says thread '{tid}' starts from '{s}', script header says '{thread}' / '{starts}'")
            row_key = next((r["Key"] for t in plan["threads"] for r in t["rungs"] if (r["Day"], r["Demo"]) == key), None) \
                or next((r["Key"] for r in plan["standalone"] if (r["Day"], r["Demo"]) == key), None)
            if row_key != keyname:
                p.append(f"{name}: authored/live day {d['id']} {demo}: plan Key '{row_key}' but script's Answer key is '{keyname}'")
    return p


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    problems = check_plan(Path(argv[0]))
    for pr in problems:
        print(pr)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
