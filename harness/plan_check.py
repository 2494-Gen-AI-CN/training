#!/usr/bin/env python3
"""Parse and check one week plan (harness/plans/week-WW.md, template harness/templates/week-plan.md; D-0034, D-0055).

The plan is written once per week by harness/workflows/week-plan.js before any day of the week is authored.
args_for.py reads it (through load_plan) to gate day args, to pass each day's rows into day-fanout.js and to
pass the week's blocks into demo-series.js; harness/series_readme.py renders trainer/week-WW/demos/README.md
from it; the week-plan critic and tests/test_plans.py call check_plan.

Checks (stdlib only):
  headings  - the template's sections, in order; one "### <id> — ..." per teaching day under Per-day shape
              with "- AM:" and "- PM:" lines
  threads   - "### <thread-id>" blocks with a block table: blocks 1..n, Day in this week, Slot AM|PM,
              Walkthrough = NN-<slug>, Starts from = cold (first block of the thread's scope, or the previous
              week's last block) or exactly the previous block's Walkthrough; Adds / End state / Commit message
  standalone- Day, Slot, Walkthrough well formed, a reason
  ladder    - every block and standalone walkthrough once, numbered 1..n in teaching order; Minutes within
              metrics.demos.minutesPerBlockMin..Max; blocks per day within blocksPerDayMin..Max and one per
              (day, slot); walkthroughs numbered 01.. contiguously ACROSS THE WEEK in ladder order; Must follow
              cites earlier rows and includes the previous block of the same thread
  series    - Stop points (one row per walkthrough), Squeeze priorities (Cut first + Never cut lists),
              Hard-stop rule (prose), Scaffold bundle (two tables), Run prerequisites (bullets)
  conventions - the rules a day or demo author could not infer from the block table (D-0057): a table with
              Convention / Kind / Applies from / Rule / Why; Kind in CONVENTION_KINDS, at least one tally and
              one git row, Applies from = all or a walkthrough of the ladder, no empty Rule; the rows travel
              into every day's args (day_rows) and the week's demo args
  coverage  - every curriculum subtopic of every teaching day of the week appears once, with its own day,
              Demo = a walkthrough of that day | facilitation | notes, Notes step a positive integer
  authored/live days - once trainer/week-WW/demos/ exists, the walkthroughs on disk equal the plan's for every
              authored or live day (name, Time, thread, Starts from, commit message) (D-0052)

Usage:
    python harness/plan_check.py harness/plans/week-02.md
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
SECTIONS = ["## Weekly Epic", "## Assumes from the previous week", "## Threads", "## Conventions", "## Standalone demos", "## Demo ladder",
            "## Per-day shape", "## Stop points", "## Squeeze priorities", "## Hard-stop rule", "## Scaffold bundle",
            "## Run prerequisites", "## Anti-spoiler ledger", "## Real-world framing and deliberate deviations", "## Coverage map"]
BLOCK_COLS = ["Block", "Day", "Slot", "Walkthrough", "Starts from", "Adds", "End state", "Commit message"]
CONVENTION_COLS = ["Convention", "Kind", "Applies from", "Rule", "Why"]
# D-0057: the fixed vocabulary of the Kind column. tally = how typed lines are counted; lint = linter rules and what
# they force into the typed lines; schema = record keys / columns later blocks select; git = branch, merge and push
# cadence; config = ordering rules (a basicConfig before the first log call); tooling = container, venv and CLI
# conventions; carried-lines = which earlier lines a rewriting block replaces.
CONVENTION_KINDS = ("tally", "lint", "schema", "git", "config", "tooling", "carried-lines")
STANDALONE_COLS = ["Day", "Slot", "Walkthrough", "Minutes", "Why it fits no thread"]
LADDER_COLS = ["#", "Day", "Walkthrough", "Minutes", "Must follow", "Guarantees"]
STOP_COLS = ["Walkthrough", "Clean stop point", "Resume at"]
SCAFFOLD_COLS = ["Day", "Hand-out", "Pre-provided", "Why rote"]
NEVER_COLS = ["Never pre-provide", "Walkthrough"]
COVERAGE_COLS = ["Subtopic", "Day", "Demo", "Notes step"]
SPOILER_COLS = ["Day", "Defers", "To", "Why"]
DEVIATION_COLS = ["Deviation", "Workplace reality", "Pedagogical reason"]
WALK_RE = re.compile(r"^(\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
SLOTS = ("AM", "PM")
DAY_HEAD_RE = re.compile(r"^### (w\d{2}d\d) — ", re.M)
THREAD_HEAD_RE = re.compile(r"^### ([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", re.M)


def _cell(s: str) -> str:
    """Cell text; a cell that is ONE code span (`02-x`) is unwrapped, any other backtick is content."""
    s = s.strip()
    if len(s) >= 2 and s.startswith("`") and s.endswith("`") and s.count("`") == 2:
        return s[1:-1].strip()
    return s


def _tables(text: str) -> list[tuple[list[str], list[dict[str, str]]]]:
    """Every markdown table in `text` as (header, rows) with rows keyed by header cell."""
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


def _bullets(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^\s*(?:[-*]|\d+\.)\s+(.*)$", body, re.M)]


def _prose(body: str) -> str:
    """Body with tables, comments and bullets removed: the paragraphs."""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    return "\n".join(ln for ln in body.splitlines() if ln.strip() and not ln.lstrip().startswith(("|", "- ", "* ")) and not re.match(r"^\s*\d+\.\s", ln))


def _list_after(body: str, label: str) -> list[str]:
    """Bullets of the list that follows a '**Label**' or 'Label:' line in a section body."""
    m = re.search(rf"^\**{re.escape(label)}\**[^\n]*$", body, re.M | re.I)
    if not m:
        return []
    rest = body[m.end():]
    nxt = re.search(r"^\**(Cut first|Never cut)\**", rest, re.M | re.I)
    return _bullets(rest[:nxt.start()] if nxt else rest)


def load_plan(path: Path) -> dict:
    """Structured view of a plan. Raises ValueError when the file is not a plan at all."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"# Week (\d{2}) plan", text)
    if not m:
        raise ValueError(f"{path.name}: first line must read '# Week WW plan — <theme>'")
    week = int(m.group(1))
    cur = bi.load_curriculum()
    wk = next((w for w in cur["weeks"] if w["week"] == week), None)
    if wk is None:
        raise ValueError(f"{path.name}: week {week} is not in the curriculum")
    threads = []
    tbody = _section(text, "## Threads")
    heads = list(THREAD_HEAD_RE.finditer(tbody))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(tbody)
        block = tbody[h.end():end]
        meta = {k.strip(): v.strip() for k, v in re.findall(r"^- ([A-Za-z ]+?):\s*(.*)$", block, re.M)}
        blocks = [{k: r[k] for k in BLOCK_COLS} for r in (_table_with(block, BLOCK_COLS) or [])]
        threads.append({"id": h.group(1), "domain": meta.get("Domain", ""), "scope": meta.get("Scope", ""),
                        "startState": meta.get("Start state this week", ""), "endState": meta.get("End state this week", ""),
                        "blocks": blocks})
    conventions = [{k: r[k] for k in CONVENTION_COLS} for r in (_table_with(_section(text, "## Conventions"), CONVENTION_COLS) or [])]
    standalone = [{k: r[k] for k in STANDALONE_COLS} for r in (_table_with(_section(text, "## Standalone demos"), STANDALONE_COLS) or [])]
    ladder = [{k: r[k] for k in LADDER_COLS} for r in (_table_with(_section(text, "## Demo ladder"), LADDER_COLS) or [])]
    coverage = [{k: r[k] for k in COVERAGE_COLS} for r in (_table_with(_section(text, "## Coverage map"), COVERAGE_COLS) or [])]
    spoilers = [{k: r[k] for k in SPOILER_COLS} for r in (_table_with(_section(text, "## Anti-spoiler ledger"), SPOILER_COLS) or [])]
    framing_body = _section(text, "## Real-world framing and deliberate deviations")
    deviations = [{k: r[k] for k in DEVIATION_COLS} for r in (_table_with(framing_body, DEVIATION_COLS) or [])]
    stops = [{k: r[k] for k in STOP_COLS} for r in (_table_with(_section(text, "## Stop points"), STOP_COLS) or [])]
    squeeze_body = _section(text, "## Squeeze priorities")
    scaffold_body = _section(text, "## Scaffold bundle")
    shape_body = _section(text, "## Per-day shape")
    day_shape = {}
    dh = list(DAY_HEAD_RE.finditer(shape_body))
    for i, h in enumerate(dh):
        end = dh[i + 1].start() if i + 1 < len(dh) else len(shape_body)
        day_shape[h.group(1)] = shape_body[h.start():end].strip()
    return {"path": str(path), "week": week, "weekDir": wk["dir"], "threads": threads, "conventions": conventions, "standalone": standalone,
            "ladder": ladder, "coverage": coverage, "spoilers": spoilers, "deviations": deviations, "dayShape": day_shape,
            "epic": _section(text, "## Weekly Epic").strip(),
            "assumes": _bullets(_section(text, "## Assumes from the previous week")),
            "stopPoints": stops,
            "squeeze": {"cutFirst": _list_after(squeeze_body, "Cut first"), "neverCut": _list_after(squeeze_body, "Never cut")},
            "hardStop": _prose(_section(text, "## Hard-stop rule")).strip(),
            "scaffold": {"handouts": [{k: r[k] for k in SCAFFOLD_COLS} for r in (_table_with(scaffold_body, SCAFFOLD_COLS) or [])],
                         "never": [{k: r[k] for k in NEVER_COLS} for r in (_table_with(scaffold_body, NEVER_COLS) or [])],
                         "intro": _prose(scaffold_body).strip()},
            "prereqs": _bullets(_section(text, "## Run prerequisites")),
            "framing": _prose(framing_body).strip()}


def week_blocks(plan: dict) -> list[dict]:
    """Every walkthrough of the week in ladder order, with its thread row and ladder minutes merged."""
    by_name: dict[str, dict] = {}
    for t in plan["threads"]:
        for r in t["blocks"]:
            by_name[r["Walkthrough"]] = {"thread": t["id"], "block": r["Block"], "name": r["Walkthrough"], "day": r["Day"], "slot": r["Slot"],
                                         "startsFrom": r["Starts from"], "adds": r["Adds"], "endState": r["End state"],
                                         "commitMessage": r["Commit message"]}
    for s in plan["standalone"]:
        by_name[s["Walkthrough"]] = {"thread": "standalone", "block": "", "name": s["Walkthrough"], "day": s["Day"], "slot": s["Slot"],
                                     "startsFrom": "cold", "adds": s["Why it fits no thread"], "endState": "", "commitMessage": ""}
    stops = {s["Walkthrough"]: s for s in plan["stopPoints"]}
    out = []
    for i, r in enumerate(plan["ladder"]):
        b = dict(by_name.get(r["Walkthrough"], {"thread": "", "block": "", "name": r["Walkthrough"], "day": r["Day"], "slot": "",
                                                "startsFrom": "", "adds": "", "endState": "", "commitMessage": ""}))
        mins = int(r["Minutes"]) if r["Minutes"].isdigit() else None
        st = stops.get(r["Walkthrough"], {})
        b.update({"n": i + 1, "minutes": mins, "mustFollow": r["Must follow"], "guarantees": r["Guarantees"],
                  "stopPoint": st.get("Clean stop point", ""), "resumeAt": st.get("Resume at", "")})
        out.append(b)
    return out


def day_rows(plan: dict, day_id: str) -> dict:
    """The rows of one day, as args_for.py passes them into the day workflow."""
    return {
        "weekPlanRows": [r for r in plan["coverage"] if r["Day"] == day_id],
        "blockRows": [b for b in week_blocks(plan) if b["day"] == day_id],
        "conventions": plan["conventions"],
        "ladderRows": [r for r in plan["ladder"] if r["Day"] == day_id],
        "dayShape": plan["dayShape"].get(day_id, ""),
        "spoilerRows": [r for r in plan["spoilers"] if r["Day"] == day_id or r["To"] == day_id],
        "cutFirst": plan["squeeze"]["cutFirst"],
        "neverCut": plan["squeeze"]["neverCut"],
    }


def previous_last_block(week: int, root: Path = ROOT) -> dict[str, str]:
    """{thread id: last walkthrough name} of the previous week's plan, when it exists and parses."""
    prev = root / "harness" / "plans" / f"week-{week - 1:02d}.md"
    out: dict[str, str] = {}
    if prev.is_file():
        try:
            for t in load_plan(prev)["threads"]:
                if t["blocks"]:
                    out[t["id"]] = t["blocks"][-1]["Walkthrough"]
        except ValueError:
            pass
    return out


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
        for need in ("- AM:", "- PM:"):
            if need not in body:
                p.append(f"{name}: Per-day shape {did} lacks '{need}'")
    # threads
    if not plan["threads"]:
        p.append(f"{name}: Threads section has no '### <thread-id>' block")
    expected: dict[str, tuple[str, str]] = {}  # walkthrough -> (thread, starts from)
    prev_last = previous_last_block(plan["week"], root)
    for t in plan["threads"]:
        tid = t["id"]
        if not t["domain"] or not t["scope"]:
            p.append(f"{name}: thread {tid} needs '- Domain:' and '- Scope:' lines")
        if not t["blocks"]:
            p.append(f"{name}: thread {tid} has no block table with columns {BLOCK_COLS}")
        prev_name = None
        for i, r in enumerate(t["blocks"]):
            tag = f"thread {tid} block {r['Block'] or '?'}"
            if r["Block"] != str(i + 1):
                p.append(f"{name}: {tag}: blocks must be numbered 1..n in order")
            if r["Day"] not in ids:
                p.append(f"{name}: {tag}: Day '{r['Day']}' is not a teaching day of week {plan['week']}")
            if r["Slot"] not in SLOTS:
                p.append(f"{name}: {tag}: Slot must be AM or PM, got '{r['Slot']}'")
            if not WALK_RE.match(r["Walkthrough"]):
                p.append(f"{name}: {tag}: Walkthrough must read NN-<slug>, got '{r['Walkthrough']}'")
            s = r["Starts from"]
            if i == 0:
                if s != "cold" and not WALK_RE.match(s):
                    p.append(f"{name}: {tag}: first block must start cold or from the previous week's last walkthrough (NN-<slug>), got '{s}'")
                elif s != "cold" and tid in prev_last and prev_last[tid] != s:
                    p.append(f"{name}: {tag}: the previous week's last walkthrough of {tid} is '{prev_last[tid]}', not '{s}'")
            elif s != prev_name:
                p.append(f"{name}: {tag}: Starts from must be the previous block's walkthrough '{prev_name}', got '{s}'")
            for col in ("Adds", "End state", "Commit message"):
                if not r[col]:
                    p.append(f"{name}: {tag}: '{col}' is empty")
            if r["Walkthrough"] in expected:
                p.append(f"{name}: {tag}: walkthrough '{r['Walkthrough']}' listed twice")
            expected[r["Walkthrough"]] = (tid, s)
            prev_name = r["Walkthrough"]
    for s in plan["standalone"]:
        tag = f"standalone {s['Walkthrough']}"
        if s["Day"] not in ids:
            p.append(f"{name}: {tag}: Day '{s['Day']}' is not a teaching day of week {plan['week']}")
        if s["Slot"] not in SLOTS:
            p.append(f"{name}: {tag}: Slot must be AM or PM")
        if not WALK_RE.match(s["Walkthrough"]):
            p.append(f"{name}: {tag}: Walkthrough must read NN-<slug>")
        if not s["Why it fits no thread"]:
            p.append(f"{name}: {tag}: say why it fits no thread (A23)")
        if s["Walkthrough"] in expected:
            p.append(f"{name}: {tag}: walkthrough listed twice")
        expected[s["Walkthrough"]] = ("standalone", "cold")
    day_of = {w: next((r["Day"] for t in plan["threads"] for r in t["blocks"] if r["Walkthrough"] == w), None)
              or next((r["Day"] for r in plan["standalone"] if r["Walkthrough"] == w), None) for w in expected}
    slot_of = {w: next((r["Slot"] for t in plan["threads"] for r in t["blocks"] if r["Walkthrough"] == w), None)
               or next((r["Slot"] for r in plan["standalone"] if r["Walkthrough"] == w), None) for w in expected}
    # ladder
    lo, hi = metrics.get("minutesPerBlockMin", 0), metrics.get("minutesPerBlockMax", 10**6)
    ladder = plan["ladder"]
    if not ladder:
        p.append(f"{name}: Demo ladder table missing (columns {LADDER_COLS})")
    seen: set[str] = set()
    minutes_by: dict[str, int] = {}
    order_by_day: dict[str, list[str]] = {}
    row_no: dict[str, int] = {}
    cites_by: dict[int, set[int]] = {}
    for i, r in enumerate(ladder):
        tag = f"ladder #{r['#'] or '?'}"
        w = r["Walkthrough"]
        if r["#"] != str(i + 1):
            p.append(f"{name}: {tag}: rows must be numbered 1..n in order")
        if w in seen:
            p.append(f"{name}: {tag}: {w} listed twice")
        seen.add(w)
        row_no[w] = i + 1
        if w not in expected:
            p.append(f"{name}: {tag}: {w} is neither a thread block nor a standalone walkthrough")
        elif day_of.get(w) != r["Day"]:
            p.append(f"{name}: {tag}: {w} is on {day_of.get(w)} in Threads/Standalone, {r['Day']} here")
        try:
            mins = int(r["Minutes"])
            minutes_by[w] = mins
            if not lo <= mins <= hi:
                p.append(f"{name}: {tag}: {mins} min outside {lo}..{hi}")
        except ValueError:
            p.append(f"{name}: {tag}: Minutes must be an integer, got '{r['Minutes']}'")
        order_by_day.setdefault(r["Day"], []).append(w)
        mf = r["Must follow"]
        cites = set()
        if mf not in ("—", "-", "", "none"):
            for tok in re.split(r"[,\s]+", mf.strip()):
                if not tok.isdigit() or not 1 <= int(tok) < i + 1:
                    p.append(f"{name}: {tag}: Must follow '{mf}' must cite earlier ladder numbers only")
                else:
                    cites.add(int(tok))
        cites_by[i + 1] = cites
        prev_day = ladder[i - 1]["Day"] if i > 0 else None
        if prev_day in ids and r["Day"] in ids and ids.index(r["Day"]) < ids.index(prev_day):
            p.append(f"{name}: {tag}: ladder is not in teaching order ({prev_day} before {r['Day']})")
        m = WALK_RE.match(w)
        if m and int(m.group(1)) != i + 1:
            p.append(f"{name}: {tag}: walkthroughs are numbered 01.. across the week in ladder order; expected {i + 1:02d}-..., got {w}")
    for w in expected:
        if w not in seen:
            p.append(f"{name}: {w} is in Threads/Standalone but not in the Demo ladder")
    for t in plan["threads"]:
        for a, b in zip(t["blocks"], t["blocks"][1:]):
            wa, wb = a["Walkthrough"], b["Walkthrough"]
            if wa in row_no and wb in row_no and row_no[wa] not in cites_by.get(row_no[wb], set()):
                p.append(f"{name}: ladder #{row_no[wb]} ({wb}) must cite #{row_no[wa]} ({wa}), the previous block of {t['id']}")
    bmin, bmax = metrics.get("blocksPerDayMin", 0), metrics.get("blocksPerDayMax", 99)
    for did in ids:
        d = next(x for x in teaching if x["id"] == did)
        ws = order_by_day.get(did, [])
        if d.get("demoFormat") == "none":
            if ws:
                p.append(f"{name}: {did} is demoFormat none but the ladder lists {ws}")
            continue
        if not bmin <= len(ws) <= bmax:
            p.append(f"{name}: {did} has {len(ws)} walkthroughs in the ladder, band is {bmin}..{bmax}")
        slots = [slot_of.get(w) for w in ws]
        if len(set(slots)) != len(slots):
            p.append(f"{name}: {did} has two walkthroughs in the same slot {slots}; one block per AM/PM slot")
        if slots != sorted(slots, key=lambda s: SLOTS.index(s) if s in SLOTS else 9):
            p.append(f"{name}: {did}: the AM block comes before the PM block in the ladder, got {slots}")
    # series sections
    stop_names = [s["Walkthrough"] for s in plan["stopPoints"]]
    for w in seen:
        if w not in stop_names:
            p.append(f"{name}: Stop points has no row for {w} (columns {STOP_COLS})")
    for s in plan["stopPoints"]:
        if s["Walkthrough"] not in seen:
            p.append(f"{name}: Stop points row '{s['Walkthrough']}' is not a walkthrough of the ladder")
        if not s["Clean stop point"] or not s["Resume at"]:
            p.append(f"{name}: Stop points row '{s['Walkthrough']}' needs a clean stop point and a resume point")
    if not plan["squeeze"]["cutFirst"]:
        p.append(f"{name}: Squeeze priorities needs a 'Cut first' list (numbered, cut in this order)")
    if not plan["squeeze"]["neverCut"]:
        p.append(f"{name}: Squeeze priorities needs a 'Never cut' list")
    if len(plan["hardStop"].split()) < 20:
        p.append(f"{name}: Hard-stop rule must be a short paragraph (>= 20 words)")
    if not plan["scaffold"]["handouts"]:
        p.append(f"{name}: Scaffold bundle needs the hand-out table (columns {SCAFFOLD_COLS}; one row per day, 'none' when nothing is pre-provided)")
    for r in plan["scaffold"]["handouts"]:
        if r["Day"] not in ids:
            p.append(f"{name}: Scaffold bundle row Day '{r['Day']}' is not a teaching day of this week")
    if not plan["scaffold"]["never"]:
        p.append(f"{name}: Scaffold bundle needs the never-pre-provide table (columns {NEVER_COLS})")
    for r in plan["scaffold"]["never"]:
        for w in re.split(r"[,\s]+", r["Walkthrough"].strip()):
            if w and w not in seen and w != "all":
                p.append(f"{name}: Scaffold bundle never-pre-provide row names '{w}', not a walkthrough of the ladder")
    if not plan["prereqs"]:
        p.append(f"{name}: Run prerequisites needs at least one bullet (the demo repo branch, containers, keys, tools)")
    # conventions (D-0057): the rules a day or demo author could not infer from the block table
    conv = plan["conventions"]
    if not conv:
        p.append(f"{name}: Conventions needs a table (columns {CONVENTION_COLS}) with at least a tally and a git row")
    kinds = {r["Kind"] for r in conv}
    for need in ("tally", "git"):
        if conv and need not in kinds:
            p.append(f"{name}: Conventions needs a row of kind '{need}' (every week counts typed lines and commits)")
    for r in conv:
        tag = f"Conventions row '{r['Convention'] or '?'}'"
        if r["Kind"] not in CONVENTION_KINDS:
            p.append(f"{name}: {tag}: Kind must be one of {', '.join(CONVENTION_KINDS)}, got '{r['Kind']}'")
        if r["Applies from"] != "all" and r["Applies from"] not in seen:
            p.append(f"{name}: {tag}: Applies from must be 'all' or a walkthrough of the ladder, got '{r['Applies from']}'")
        if not r["Rule"]:
            p.append(f"{name}: {tag}: Rule is empty")
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
            p.append(f"{name}: coverage row '{r['Subtopic']}': Demo '{demo}' is not a walkthrough of {r['Day']} in the ladder, nor 'facilitation' / 'notes'")
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
    # authored/live days: the walkthroughs on disk equal the plan's rows (D-0052, D-0055)
    ddir = root / "trainer" / wk["dir"] / "demos"
    if ddir.is_dir():
        recorded = {d["id"] for d in teaching if d.get("status") in ("authored", "live")}
        on_disk = {f.stem: demo_check.header_facts(f) for f in demo_check.walkthroughs(ddir)}
        for w in on_disk:
            if w not in seen:
                p.append(f"{name}: {ddir.name}/{w}.md is on disk but not in the plan's ladder")
        for w in seen:
            did = day_of.get(w)
            if did not in recorded:
                continue
            f = on_disk.get(w)
            if f is None:
                p.append(f"{name}: authored/live day {did}: walkthrough {w} is in the plan but not on disk under {ddir}")
                continue
            if minutes_by.get(w) != f["time"]:
                p.append(f"{name}: authored/live day {did} {w}: ladder says {minutes_by.get(w)} min, the walkthrough's Time says {f['time']}")
            tid, s = expected.get(w, ("", ""))
            if (tid, s) != (f["thread"], f["startsFrom"]):
                p.append(f"{name}: authored/live day {did} {w}: plan says thread '{tid}' starts from '{s}', the walkthrough says '{f['thread']}' / '{f['startsFrom']}'")
            msg = next((b["Commit message"] for t in plan["threads"] for b in t["blocks"] if b["Walkthrough"] == w), "")
            if tid != "standalone" and msg != f["commit"]:
                p.append(f"{name}: authored/live day {did} {w}: plan commit message '{msg}' but the walkthrough commits '{f['commit']}'")
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
