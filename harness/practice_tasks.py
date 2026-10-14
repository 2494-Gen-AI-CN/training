#!/usr/bin/env python3
"""Practice tasks as a stage of their own, after a day's page is authored (D-0047, stdlib only).

harness/practice/<week-dir>/<day-slug>.json is the one source of a page's practice tasks. It is written in
three steps, each by a different hand:

  1. suitability  harness/workflows/practice-tasks.js (mode suitability) reads the authored page and writes,
                  per teaching step, whether a task fits and which one (id, title, idea, what each check proves).
  2. approval     the trainer reads the proposal (`show`) and answers; the session records it (`approve`).
                  Nothing is built for a task the trainer has not answered.
  3. build        the same workflow (mode build) fills q, starter and tests for the approved tasks and writes
                  the model answers and the cases to trainer/<rel>/solutions/; `insert` then writes the page.

The page's <section class="practice"> is GENERATED from this file and never edited by hand: `insert` puts it
before the Check yourself step (replacing the old one), so a re-authored page gets its tasks back with one
command, and `check` fails while the two differ.

Usage:
    python harness/practice_tasks.py show <week> [day...]          the proposals, as the trainer should read them
    python harness/practice_tasks.py approve <week> <day> t1 t3    these tasks yes, every other task of the day no
    python harness/practice_tasks.py approve <week> <day> --all | --none
    python harness/practice_tasks.py validate <week> <day>         shape of the file against the page (the agents run it)
    python harness/practice_tasks.py insert <week> <day>           write the built tasks into the page
    python harness/practice_tasks.py verify <week> <day>           one day: file valid, page in sync, starters fail,
                                                                   model answers pass, every case behaves (CPython)
    python harness/practice_tasks.py check                         every day: page section == what the file renders
    python harness/practice_tasks.py extract <week> <day>          one-off: build the file from a hand-written section

A task is BUILT when it is approved and carries q, starter and tests. Only built tasks reach the page.
"""
from __future__ import annotations

import ast
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import notes_check as nc  # noqa: E402

ROOT = bi.ROOT
PRACTICE = ROOT / "harness" / "practice"
VERDICTS = ("full", "partial", "none")   # every teaching step carries a task / some do / none does
TOP_KEYS = ("day", "page", "assessed", "verdict", "summary", "steps", "tasks")
STEP_KEYS = ("step", "title", "suitable", "reason", "task")
TASK_KEYS = ("id", "title", "step", "idea", "checks", "approved", "q", "starter", "tests")
BUILT_KEYS = ("q", "starter", "tests")

SECTION_RE = re.compile(r'^[ \t]*<section class="practice"[^>]*>.*?^[ \t]*</section>[ \t]*\n', re.S | re.M)
STEP_RE = re.compile(r'^([ \t]*)<section class="step"', re.M)
TASK_RE = re.compile(
    r'<div class="ix-task" data-id="([^"]*)" data-title="([^"]*)" data-q="([^"]*)">\s*'
    r'<pre class="task-starter"><code>(.*?)</code></pre>\s*'
    r'<pre class="task-tests" hidden><code>(.*?)</code></pre>\s*</div>', re.S)


# ---------------------------------------------------------------- files
def locate(week_no: int, day_no: int) -> tuple[dict, dict, str]:
    week = next((w for w in bi.load_curriculum()["weeks"] if w["week"] == week_no), None)
    day = next((d for d in (week or {}).get("days", []) if d["day"] == day_no), None)
    if day is None or day.get("kind") == "holiday":
        raise SystemExit(f"week {week_no} has no teaching day {day_no}")
    return week, day, f"{week['dir']}/{day['slug']}"


def path_for(rel: str) -> Path:
    return PRACTICE / f"{rel}.json"


def page_for(rel: str) -> Path:
    return ROOT / "docs" / "weeks" / f"{rel}.html"


def read_text(p: Path) -> str:
    return p.read_bytes().decode("utf-8")   # bytes in, bytes out: a page keeps its line endings


def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))


def load(rel: str) -> dict | None:
    p = path_for(rel)
    return json.loads(read_text(p)) if p.is_file() else None


def save(rel: str, doc: dict) -> None:
    write_text(path_for(rel), json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def is_built(task: dict) -> bool:
    return task.get("approved") is True and all((task.get(k) or "").strip() for k in BUILT_KEYS)


def built(doc: dict | None) -> list[dict]:
    return [t for t in (doc or {}).get("tasks", []) if is_built(t)]


def teaching_steps(page_text: str) -> list[dict]:
    """The page's teaching steps (every section.step but the last, which is Check yourself), in order."""
    steps = nc.parse_html(page_text).find_all("section", "step")[:-1]
    return [{"step": int(s.attrs.get("data-step", i)), "title": " ".join((s.find("h2").text() if s.find("h2") else "").split())}
            for i, s in enumerate(steps)]


# ---------------------------------------------------------------- the page section
def render(tasks: list[dict], indent: str = "      ") -> str:
    """The practice section exactly as it stands on a page (no trailing newline)."""
    inner = indent + "  "
    attr = lambda s: html.escape(s, quote=True)                      # noqa: E731
    code = lambda s: html.escape(s.strip("\n"), quote=False)         # noqa: E731
    out = [f'{indent}<section class="practice" id="practice" hidden>', f'{inner}<div class="tag">Practice</div>', f'{inner}<h2>Practice</h2>']
    for t in tasks:
        out += [f'{inner}<div class="ix-task" data-id="{attr(t["id"])}" data-title="{attr(t["title"])}" data-q="{attr(t["q"])}">',
                f'<pre class="task-starter"><code>{code(t["starter"])}</code></pre>',
                f'<pre class="task-tests" hidden><code>{code(t["tests"])}</code></pre>',
                f'{inner}</div>']
    out.append(f"{indent}</section>")
    return "\n".join(out)


def put_section(text: str, tasks: list[dict]) -> str:
    """The page with its practice section replaced by these tasks (removed when there are none). The section
    goes directly before the last section.step, which is Check yourself, at that step's indentation."""
    m = SECTION_RE.search(text)
    if m:
        end = m.end() + (1 if text[m.end():m.end() + 1] == "\n" else 0)   # the blank line that followed it
        text = text[:m.start()] + text[end:]
    if not tasks:
        return text
    steps = list(STEP_RE.finditer(text))
    if not steps:
        raise ValueError("the page has no section.step to put the practice section before")
    last = steps[-1]
    return text[:last.start()] + render(tasks, last.group(1)) + "\n\n" + text[last.start():]


def page_tasks(text: str) -> list[dict]:
    """The tasks a page carries, read back from its markup."""
    m = SECTION_RE.search(text)
    return [{"id": html.unescape(i), "title": html.unescape(t), "q": html.unescape(q), "starter": html.unescape(s), "tests": html.unescape(c)}
            for i, t, q, s, c in TASK_RE.findall(m.group(0) if m else "")]


def in_sync(rel: str) -> str | None:
    """None when the page's practice section is what the day's file renders, else what is wrong."""
    page, doc = page_for(rel), load(rel)
    if not page.is_file():
        return None if doc is None or not built(doc) else f"{rel}: the file has built tasks and the page is missing"
    text = read_text(page)
    if doc is None:
        return f"{rel}: the page carries practice tasks and harness/practice/{rel}.json is missing (run extract)" if 'class="ix-task"' in text else None
    try:
        same = put_section(text, built(doc)) == text
    except ValueError as exc:
        return f"{rel}: {exc}"
    return None if same else (f"{rel}: the page's practice section differs from harness/practice/{rel}.json; "
                              f"run: python harness/practice_tasks.py insert <week> <day>")


# ---------------------------------------------------------------- the file's shape
def problems(doc: dict, rel: str, page_text: str | None = None, bounds: dict | None = None) -> list[str]:
    """What is wrong with a day's file. With the page text, the steps are held against the page's own."""
    p: list[str] = []
    for k in TOP_KEYS:
        if k not in doc:
            p.append(f"missing key {k!r}")
    if p:
        return p
    if doc["verdict"] not in VERDICTS:
        p.append(f"verdict must be one of {VERDICTS}, got {doc['verdict']!r}")
    if doc["page"] != f"docs/weeks/{rel}.html":
        p.append(f"page must be docs/weeks/{rel}.html")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(doc["assessed"])):
        p.append("assessed must be a YYYY-MM-DD date")
    if not str(doc["summary"]).strip():
        p.append("summary is empty")
    steps, tasks = doc["steps"], doc["tasks"]
    ids = [t.get("id") for t in tasks]
    if len(ids) != len(set(ids)):
        p.append("duplicate task id")
    for s in steps:
        miss = [k for k in STEP_KEYS if k not in s]
        if miss:
            p.append(f"step {s.get('step')!r}: missing {miss}")
            continue
        if not str(s["reason"]).strip():
            p.append(f"step {s['step']}: reason is empty (say why a task fits here, or why none does)")
        if s["suitable"] and s["task"] not in ids:
            p.append(f"step {s['step']}: suitable, so task must name one of the tasks, got {s['task']!r}")
        if not s["suitable"] and s["task"] is not None:
            p.append(f"step {s['step']}: not suitable, so task must be null")
    by_step = {s.get("step"): s for s in steps}
    for t in tasks:
        tid = t.get("id")
        miss = [k for k in TASK_KEYS if k not in t]
        if miss:
            p.append(f"task {tid!r}: missing {miss}")
            continue
        if not re.fullmatch(r"t\d+", str(tid)):
            p.append(f"task {tid!r}: id must look like t1, t2, ...")
        if not str(t["title"]).strip():
            p.append(f"task {tid}: title is empty")
        if t["approved"] not in (True, False, None):
            p.append(f"task {tid}: approved must be true, false or null (null = the trainer has not answered)")
        if t["step"] is not None and steps and (by_step.get(t["step"], {}).get("task") != tid):
            p.append(f"task {tid}: step {t['step']} does not name it back")
        filled = [k for k in BUILT_KEYS if (t[k] or "").strip()]
        if filled and len(filled) != len(BUILT_KEYS):
            p.append(f"task {tid}: q, starter and tests are written together, got only {filled}")
        if filled and t["approved"] is not True:
            p.append(f"task {tid}: carries q, starter and tests without the trainer's approval")
        if not filled and (not str(t["idea"]).strip() or not t["checks"]):
            p.append(f"task {tid}: a proposal needs an idea and the list of what its checks prove")
        if len(filled) == len(BUILT_KEYS):
            p += [f"task {tid}: {x}" for x in _built_problems(t, bounds or {})]
    if steps:
        fit = [s for s in steps if s.get("suitable")]
        want = "none" if not fit else "full" if len(fit) == len(steps) else "partial"
        if doc["verdict"] != want:
            p.append(f"verdict is {doc['verdict']!r} and the steps say {want!r}")
    elif (doc["verdict"] == "none") != (not tasks):
        p.append("verdict 'none' means no tasks, and no tasks means verdict 'none'")
    if page_text is not None and steps:
        have, want = [(s.get("step"), s.get("title")) for s in steps], [(s["step"], s["title"]) for s in teaching_steps(page_text)]
        if have != want:
            p.append(f"steps must list the page's teaching steps in order with their h2 text: expected {want}, got {have}")
    return p


def _built_problems(t: dict, bounds: dict) -> list[str]:
    p: list[str] = []
    try:
        compile(t["starter"].strip("\n") + "\n", "starter", "exec")
        body = ast.parse(t["tests"]).body
    except SyntaxError as exc:
        return [f"does not parse: {exc}"]
    asserts = [n for n in body if isinstance(n, ast.Assert)]
    if not all(isinstance(n.msg, ast.Constant) and isinstance(n.msg.value, str) for n in asserts):
        p.append("every assert carries a message: it is the label the reader sees")
    lo, hi = bounds.get("checksPerTaskMin", 1), bounds.get("checksPerTaskMax", 99)
    if not lo <= len(asserts) <= hi:
        p.append(f"{len(asserts)} checks, expected {lo} to {hi}")
    labels = [n.msg.value for n in asserts if isinstance(n.msg, ast.Constant)]
    if len(labels) != len(set(labels)):
        p.append("two checks share a label")
    if re.search(r"<(?!/?code>)", t["q"]):
        p.append("q may hold <code> and nothing else as markup")
    return p


def bounds() -> dict:
    return json.loads(read_text(ROOT / "harness" / "metrics.json")).get("practice", {})


# ---------------------------------------------------------------- commands
def cmd_show(week_no: int, day_nos: list[int]) -> int:
    week = next(w for w in bi.load_curriculum()["weeks"] if w["week"] == week_no)
    shown = 0
    for d in bi.teaching_days(week):
        if day_nos and d["day"] not in day_nos:
            continue
        rel = f"{week['dir']}/{d['slug']}"
        doc = load(rel)
        if doc is None:
            if day_nos:
                print(f"{d['id']}  {d['title']}: no proposal yet")
            continue
        shown += 1
        print(f"{d['id']}  {d['title']}: {doc['verdict']} ({len(doc['tasks'])} task(s), assessed {doc['assessed']})")
        print(f"  {doc['summary']}")
        for s in doc["steps"]:
            print(f"  step {s['step'] + 1}  {s['title']}")
            print(f"      {'fits' if s['suitable'] else 'no task'}: {s['reason']}")
        for t in doc["tasks"]:
            answer = {True: "approved", False: "declined", None: "NOT ANSWERED"}[t["approved"]]
            state = "built" if is_built(t) else answer
            where = "" if t["step"] is None else f" (step {t['step'] + 1})"
            print(f"  {t['id']}  {t['title']}{where}  [{state}]")
            if t["idea"]:
                print(f"      {t['idea']}")
            for c in t["checks"]:
                print(f"      - {c}")
    if not shown and not day_nos:
        print(f"week {week_no}: no day has a proposal yet")
    return 0


def cmd_approve(week_no: int, day_no: int, picks: list[str]) -> int:
    _w, _d, rel = locate(week_no, day_no)
    doc = load(rel)
    if doc is None:
        raise SystemExit(f"no proposal at {path_for(rel)}; run the suitability pass first")
    ids = [t["id"] for t in doc["tasks"]]
    if picks == ["--all"]:
        yes = set(ids)
    elif picks == ["--none"]:
        yes = set()
    else:
        yes = set(picks)
        if not yes or yes - set(ids):
            raise SystemExit(f"name tasks of this day ({' '.join(ids) or 'it has none'}), or --all, or --none; got {picks}")
    dropped = [t["id"] for t in doc["tasks"] if is_built(t) and t["id"] not in yes]
    for t in doc["tasks"]:
        t["approved"] = t["id"] in yes
    save(rel, doc)
    print(f"{rel}: approved {' '.join(i for i in ids if i in yes) or 'none'}; declined {' '.join(i for i in ids if i not in yes) or 'none'}")
    if dropped:
        print(f"NOTE: {' '.join(dropped)} was on the page. Run insert, and take it out of practice.py and practice_cases.py in the trainer repo.")
    return 0


def cmd_validate(week_no: int, day_no: int) -> int:
    _w, _d, rel = locate(week_no, day_no)
    doc = load(rel)
    if doc is None:
        print(f"FAIL: {path_for(rel)} does not exist")
        return 1
    page = page_for(rel)
    found = problems(doc, rel, read_text(page) if page.is_file() else None, bounds())
    for x in found:
        print("  " + x)
    print(f"{'FAIL' if found else 'OK'}: {path_for(rel).relative_to(ROOT).as_posix()}"
          f" ({doc.get('verdict')}, {len(doc.get('tasks', []))} task(s), {len(built(doc))} built)")
    return 1 if found else 0


def cmd_insert(week_no: int, day_no: int) -> int:
    _w, _d, rel = locate(week_no, day_no)
    doc, page = load(rel), page_for(rel)
    if doc is None:
        print(f"{rel}: no practice file, nothing to insert")
        return 0
    if not page.is_file():
        raise SystemExit(f"{page} does not exist: practice tasks come after the page is authored")
    tasks = built(doc)
    text = read_text(page)
    new = put_section(text, tasks)
    if new != text:
        write_text(page, new)
    print(f"{rel}: {len(tasks)} task(s) on the page ({'written' if new != text else 'already in sync'})")
    return 0


def cmd_check() -> int:
    bad = []
    cur = bi.load_curriculum()
    for w in cur["weeks"]:
        for d in bi.teaching_days(w):
            rel = f"{w['dir']}/{d['slug']}"
            msg = in_sync(rel)
            if msg:
                bad.append(msg)
    for x in bad:
        print("  " + x)
    print("FAIL: practice sections out of sync" if bad else "OK: every practice section matches its file")
    return 1 if bad else 0


def cmd_verify(week_no: int, day_no: int) -> int:
    """Everything the contract tests ask of one day's tasks, without the other days in the way."""
    import practice_browser   # noqa: E402  (needs trainer/; imported here so the other commands do not)
    _w, _d, rel = locate(week_no, day_no)
    if cmd_validate(week_no, day_no):
        return 1
    msg = in_sync(rel)
    if msg:
        print("FAIL: " + msg)
        return 1
    doc = load(rel)
    if not built(doc):
        print(f"OK: {rel} has no built task")
        return 0
    data, bad = practice_browser.expected(rel)
    b = bounds()
    for tid, line in data["expected"].items():
        print("  " + line)
        if len(data["cases"][tid]["accept"]) < b.get("acceptMin", 0):
            bad.append(f"{tid}: practice_cases.py needs at least {b['acceptMin']} other right answer(s)")
    extra = set(data["cases"]) - set(data["expected"])
    if extra:
        bad.append(f"practice_cases.py has entries for tasks the page does not carry: {sorted(extra)}")
    for x in bad:
        print("  PROBLEM " + x)
    print(f"{'FAIL' if bad else 'OK'}: {rel}, {len(data['expected'])} task(s) under CPython"
          + ("" if bad else "; the browser pass (harness/practice_browser.py) is still owed"))
    return 1 if bad else 0


def cmd_extract(week_no: int, day_no: int, today: str) -> int:
    _w, d, rel = locate(week_no, day_no)
    if load(rel) is not None:
        raise SystemExit(f"{path_for(rel)} exists; extract is for a page whose tasks were written by hand before D-0047")
    text = read_text(page_for(rel))
    found = page_tasks(text)
    if not found:
        raise SystemExit(f"{rel}: the page has no practice tasks")
    steps = teaching_steps(text)
    paired = len(steps) == len(found)   # one task per teaching step, in order: the D-0043 shape
    doc = {
        "day": d["id"], "page": f"docs/weeks/{rel}.html", "assessed": today,
        "verdict": "full" if paired else "partial",
        "summary": "Extracted from the page: these tasks were written by hand before the practice stage existed.",
        "steps": [{**s, "suitable": True, "reason": "carries a task since before D-0047", "task": found[i]["id"]} for i, s in enumerate(steps)] if paired else [],
        "tasks": [{"id": t["id"], "title": t["title"], "step": steps[i]["step"] if paired else None, "idea": "", "checks": [],
                   "approved": True, "q": t["q"], "starter": t["starter"], "tests": t["tests"]} for i, t in enumerate(found)],
    }
    if put_section(text, doc["tasks"]) != text:
        raise SystemExit(f"{rel}: the section on the page is not in the generated shape; rendering it back would change the page. Nothing written.")
    save(rel, doc)
    print(f"{rel}: {len(found)} task(s) extracted to {path_for(rel).relative_to(ROOT).as_posix()}; the page renders back byte for byte")
    return 0


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
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "check" and not rest:
            return cmd_check()
        if cmd == "show" and rest:
            return cmd_show(int(rest[0]), [int(x) for x in rest[1:]])
        if cmd == "approve" and len(rest) >= 3:
            return cmd_approve(int(rest[0]), int(rest[1]), rest[2:])
        if cmd in ("validate", "insert", "verify") and len(rest) == 2:
            return {"validate": cmd_validate, "insert": cmd_insert, "verify": cmd_verify}[cmd](int(rest[0]), int(rest[1]))
        if cmd == "extract" and len(rest) == 2:
            if not today:
                raise SystemExit("extract needs --today YYYY-MM-DD (the harness never reads the clock for a recorded date)")
            return cmd_extract(int(rest[0]), int(rest[1]), today)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
