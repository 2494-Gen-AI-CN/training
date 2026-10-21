#!/usr/bin/env python3
"""Generate the learner-facing project spec pages under docs/projects/ (D-0065).

The specs are hand-authored markdown in the drop zone `projects/` (grammar and templates in
projects/README.md):

    projects/official/P<n>-<slug>.md        one per official project (P0-P2 in curriculum.json `projects`)
    projects/sprints/YYYY-MM-DD-<slug>.md   one per sprint (a sprint is the week's hackathon)

Each spec opens with a frontmatter block (`---` ... `---`, one `key: value` per line; only
`checkpoints:` takes `- wNNdN Label` lines under it). This module parses and validates them (stdlib),
renders one page per spec plus an index (the body markdown goes through the `markdown` package from
requirements-dev.txt, imported lazily inside the renderer so build_index.py and its importers never
need it), and hands the calendar marks to build_index.py.

`draft` official specs render a page but get no card on the index and no calendar mark (hidden, like
`authored` days). Pages carry human dates only (`build_index.date_label(d, year=True)`), never an ISO
date, and never link a day page or an exit-criteria page outside the shared topnav: the projects are
deliberately decoupled from the notes pipeline.

Usage:
    python harness/build_projects.py             # (re)write docs/projects/*.html
    python harness/build_projects.py --check     # exit 1 when a spec is invalid or a page is stale
    python harness/build_projects.py --validate  # grammar, sections and dates only
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import site_pages  # noqa: E402
from site_pages import esc  # noqa: E402

ROOT = bi.ROOT
SPECS = ROOT / "projects"
OUT = ROOT / "docs" / "projects"
REBUILD_CMD = "python harness/build_projects.py"

KINDS = {"official": "official", "sprint": "sprints"}          # kind -> folder under projects/
KEYS = {
    "official": {"required": ["kind", "project", "title", "status", "handIn", "checkpoints"], "optional": []},
    "sprint": {"required": ["kind", "title", "assigned", "due", "mode", "handIn", "status"], "optional": ["tools"]},
}
STATUSES = {"official": ("draft", "published", "closed"), "sprint": ("open", "closed")}
MODES = ("pairs", "solo", "teams")
SECTIONS = ["Goal", "Scope", "Requirements", "Deliverable", "Checkpoints", "Rubric", "Presentation"]
LABELS = {"open": "Open", "closed": "Closed", "draft": "Draft", "published": "Published",
          "pairs": "Pairs", "solo": "Solo", "teams": "Teams"}

KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*):\s*(.*)$")
ITEM_RE = re.compile(r"^\s*-\s+(w\d\dd\d)\s+(.+)$")
LISTISH_RE = re.compile(r"^\s*-(\s|$)")
HEADING_RE = re.compile(r"^##[ \t]+(.+?)[ \t]*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
REQ_RE = re.compile(r"^-\s+R-(\d{2,})\s")
ISO_RE = re.compile(r"^\d{4}-\d\d-\d\d$")
ISO_ANY_RE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
PIPELINE_RE = re.compile(r"(weeks|exit-criteria)/")
DAY_ID_RE = re.compile(r"^w(\d\d)d(\d)$")
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
SPRINT_NAME_RE = re.compile(rf"^(\d{{4}}-\d\d-\d\d)-({SLUG})\.md$")
OFFICIAL_NAME_RE = re.compile(rf"^(P\d+)-({SLUG})\.md$")
HANDIN_SPRINT_RE = re.compile(r"^(week-\d\d)/hackathon(/[a-z0-9-]+)?/$")
RESERVED_SLUGS = {"index"}


class SpecError(ValueError):
    """A spec (or the set of specs) does not follow projects/README.md; the message lists every problem."""


# ---------------------------------------------------------------- parse
def _parse(text: str) -> tuple[dict, str, dict]:
    """(meta, body, key -> line number). Raises SpecError naming the line."""
    lines = text.lstrip("﻿").replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        raise SpecError("line 1: the frontmatter must open with '---'")
    meta: dict = {}
    where: dict = {}
    in_list = False
    for i in range(1, len(lines)):
        ln = lines[i].rstrip()
        n = i + 1
        if ln.strip() == "---":
            return meta, "\n".join(lines[i + 1:]).strip("\n"), where
        if not ln.strip():
            continue
        if LISTISH_RE.match(ln):
            if not in_list:
                raise SpecError(f"line {n}: a '- ' list line is only allowed under 'checkpoints:'")
            m = ITEM_RE.match(ln)
            if not m:
                raise SpecError(f"line {n}: a checkpoint line reads '- wNNdN Label'")
            meta["checkpoints"].append((m.group(1), m.group(2).strip()))
            continue
        m = KEY_RE.match(ln)
        if not m:
            raise SpecError(f"line {n}: not a 'key: value' line")
        key, val = m.group(1), m.group(2).strip()
        if key in meta:
            raise SpecError(f"line {n}: duplicate key '{key}'")
        where[key] = n
        if key == "checkpoints":
            if val:
                raise SpecError(f"line {n}: 'checkpoints:' takes no value; list '- wNNdN Label' lines under it")
            meta[key] = []
            in_list = True
        else:
            meta[key] = val
            in_list = False
    raise SpecError("the frontmatter has no closing '---'")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """(meta, body). Values are stripped strings; `checkpoints` is a list of (dayId, label)."""
    meta, body, _ = _parse(text)
    return meta, body


def _sections(body: str) -> tuple[str, list[tuple[str, str]]]:
    """(preamble, [(heading, text)]) split on level-2 headings outside fenced code."""
    pre: list[str] = []
    secs: list[tuple[str, list[str]]] = []
    fence = None
    for ln in body.split("\n"):
        m = FENCE_RE.match(ln)
        if m:
            fence = None if fence == m.group(1) else (fence or m.group(1))
        h = HEADING_RE.match(ln) if fence is None else None
        if h:
            secs.append((h.group(1), []))
        elif secs:
            secs[-1][1].append(ln)
        else:
            pre.append(ln)
    return "\n".join(pre).strip("\n"), [(h, "\n".join(t).strip("\n")) for h, t in secs]


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "section"


# ---------------------------------------------------------------- calendar
def _load_cur(root: Path, cur: dict | None) -> dict:
    if cur is not None:
        return cur
    p = root / "harness" / "curriculum.json"
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return bi.load_curriculum()


def _calendar(cur: dict) -> dict | None:
    """Teaching days by id and by date, holiday slot ids, course span; None when the curriculum has no calendar."""
    try:
        start = dt.date.fromisoformat(cur["startDate"])
        end = dt.date.fromisoformat(cur["endDate"])
        by_id, by_date, holidays = {}, {}, set()
        for w in cur["weeks"]:
            for d in w["days"]:
                key = f"w{w['week']:02d}d{d['day']}"
                if d.get("kind") == "holiday":
                    holidays.add(key)
                    continue
                info = {"dayId": d.get("id") or key, "week": w["week"], "slot": d["day"], "dir": w["dir"],
                        "date": bi.slot_date(cur, w["week"], d["day"]), "status": d.get("status")}
                by_id[info["dayId"]] = info
                by_date[info["date"]] = info
        return {"start": start, "end": end, "byId": by_id, "byDate": by_date, "holidays": holidays}
    except (KeyError, TypeError, ValueError):
        return None


def _iso(val: str) -> dt.date | None:
    if not ISO_RE.match(val or ""):
        return None
    try:
        return dt.date.fromisoformat(val)
    except ValueError:
        return None


# ---------------------------------------------------------------- validate
def _spec_files(root: Path) -> list[tuple[str, Path]]:
    """(folder, path) for every *.md under projects/official/ and projects/sprints/, sorted."""
    out = []
    for folder in ("official", "sprints"):
        d = root / "projects" / folder
        if d.is_dir():
            out.extend((folder, p) for p in sorted(d.glob("*.md")) if p.is_file())
    return out


def _check_teaching_day(name: str, d: dt.date, cal: dict, problems: list[str]) -> bool:
    if not cal["start"] <= d <= cal["end"]:
        problems.append(f"{name} {d.isoformat()} is outside the course ({cal['start'].isoformat()} to {cal['end'].isoformat()})")
        return False
    if d not in cal["byDate"]:
        problems.append(f"{name} {d.isoformat()} is not a teaching day (weekend or holiday)")
        return False
    return True


def _check_sections(body: str, problems: list[str]) -> None:
    _pre, secs = _sections(body)
    heads = [h for h, _ in secs]
    for name in SECTIONS:
        n = heads.count(name)
        if n == 0:
            problems.append(f"missing section '## {name}'")
        elif n > 1:
            problems.append(f"section '## {name}' appears {n} times (exactly once)")
    seen = [h for h in heads if h in SECTIONS]
    if len(seen) == len(SECTIONS) and seen != SECTIONS:
        problems.append("sections out of order: " + ", ".join(seen) + " (expected " + ", ".join(SECTIONS) + ")")
    if "Presentation" in heads:
        last = max(i for i, h in enumerate(heads) if h == "Presentation")
        for h in heads[:last]:
            if h not in SECTIONS:
                problems.append(f"extra section '## {h}' comes before '## Presentation' (extra sections go after the seven)")
    req = next((t for h, t in secs if h == "Requirements"), None)
    if req is not None:
        nums = [int(m.group(1)) for m in (REQ_RE.match(ln) for ln in req.split("\n")) if m]
        if not nums:
            problems.append("'## Requirements' has no '- R-01 ...' bullet")
        elif nums != list(range(1, len(nums) + 1)):
            got = ", ".join(f"R-{n:02d}" for n in nums)
            problems.append(f"requirements are not numbered R-01, R-02, ... in order (got {got})")


def _check_file(folder: str, path: Path, rel: str, cur: dict, cal: dict | None) -> tuple[dict | None, list[str]]:
    """(spec or None, problems) for one spec file; problems are bare messages (no file prefix)."""
    problems: list[str] = []
    try:
        meta, body, where = _parse(path.read_text(encoding="utf-8"))
    except (SpecError, UnicodeDecodeError, OSError) as e:
        return None, [str(e)]
    kind = meta.get("kind", "")
    if kind not in KINDS:
        return None, [f"kind must be official or sprint (got '{kind}')"]
    if KINDS[kind] != folder:
        problems.append(f"kind '{kind}' does not belong in projects/{folder}/ (it goes in projects/{KINDS[kind]}/)")
    allowed = KEYS[kind]["required"] + KEYS[kind]["optional"]
    for k in meta:
        if k not in allowed:
            problems.append(f"line {where[k]}: unknown key '{k}' ({kind} specs take {', '.join(allowed)})")
    for k in KEYS[kind]["required"]:
        if k not in meta:
            problems.append(f"missing key '{k}'")
    title = meta.get("title", "")
    if "title" in meta and not title:
        problems.append("title is empty")
    status = meta.get("status", "")
    if "status" in meta and status not in STATUSES[kind]:
        problems.append(f"status must be {' | '.join(STATUSES[kind])} (got '{status}')")
    hand_in = meta.get("handIn", "")
    if "handIn" in meta and not hand_in:
        problems.append("handIn is empty")
    texts = [body, title, hand_in, meta.get("tools", "")] + [lbl for _, lbl in meta.get("checkpoints", []) or []]
    if PIPELINE_RE.search(body):
        problems.append("the body names 'weeks/' or 'exit-criteria/': project specs never link day or exit-criteria pages")
    if any(ISO_ANY_RE.search(t) for t in texts):
        problems.append("an ISO date (YYYY-MM-DD) appears in the prose: write dates the way a reader says them")
    if cal is None:
        problems.append("harness/curriculum.json has no usable calendar (startDate, endDate, weeks): dates not checked")
    spec = {"kind": kind, "path": path, "rel": rel, "title": title, "status": status, "handIn": hand_in,
            "body": body, "visible": status != "draft"}

    if kind == "sprint":
        m = SPRINT_NAME_RE.match(path.name)
        spec["slug"] = m.group(2) if m else path.stem
        if not m:
            problems.append("the filename must be YYYY-MM-DD-<slug>.md (lowercase slug, words joined by '-')")
        dates = {}
        for k in ("assigned", "due"):
            if k in meta:
                d = _iso(meta[k])
                if d is None:
                    problems.append(f"{k} '{meta[k]}' is not an ISO date (YYYY-MM-DD)")
                else:
                    dates[k] = d
        if m and "assigned" in meta and m.group(1) != meta["assigned"]:
            problems.append(f"the filename date {m.group(1)} does not match assigned {meta['assigned']}")
        if "assigned" in dates and "due" in dates and dates["due"] < dates["assigned"]:
            problems.append("due is before assigned")
        ok_days = {}
        if cal is not None:
            for k, d in dates.items():
                if _check_teaching_day(k, d, cal, problems):
                    ok_days[k] = cal["byDate"][d]
        mode = meta.get("mode", "")
        if "mode" in meta and mode not in MODES:
            problems.append(f"mode must be {' | '.join(MODES)} (got '{mode}')")
        if "handIn" in meta and hand_in:
            hm = HANDIN_SPRINT_RE.match(hand_in)
            if not hm:
                problems.append(f"handIn '{hand_in}' must read week-NN/hackathon/ (or week-NN/hackathon/<slug>/ for a second sprint in a week)")
            elif "assigned" in ok_days and hm.group(1) != ok_days["assigned"]["dir"]:
                problems.append(f"handIn '{hand_in}' is not in the week of assigned ({ok_days['assigned']['dir']}/hackathon/)")
        spec.update({"assigned": dates.get("assigned"), "due": dates.get("due"), "mode": mode,
                     "tools": [t.strip() for t in meta.get("tools", "").split(",") if t.strip()]})
    else:
        m = OFFICIAL_NAME_RE.match(path.name)
        spec["slug"] = path.stem
        project = meta.get("project", "")
        projects = cur.get("projects", {}) or {}
        if "project" in meta and project not in projects:
            problems.append(f"unknown project '{project}' (curriculum.json projects: {', '.join(projects) or 'none'})")
        if not m:
            problems.append("the filename must be P<n>-<slug>.md (lowercase slug, words joined by '-')")
        elif "project" in meta and m.group(1) != project:
            problems.append(f"the filename prefix {m.group(1)} does not match project {project}")
        pinfo = projects.get(project) or {}
        weeks = pinfo.get("weeks") or []
        cps = []
        if "checkpoints" in meta and not meta["checkpoints"]:
            problems.append("checkpoints needs at least one '- wNNdN Label' line")
        for day_id, label in meta.get("checkpoints", []) or []:
            if cal is None:
                continue
            if day_id in cal["holidays"]:
                problems.append(f"checkpoint {day_id} is a holiday slot")
                continue
            info = cal["byId"].get(day_id)
            if info is None:
                problems.append(f"checkpoint {day_id} is not a day id in curriculum.json")
                continue
            if len(weeks) == 2 and not weeks[0] <= info["week"] <= weeks[1]:
                problems.append(f"checkpoint {day_id} is outside {project}'s weeks {weeks[0]}–{weeks[1]}")
            if status == "draft" and info["status"] == "live":
                problems.append(f"draft spec has a checkpoint on a live day ({day_id}): publish the spec or move the checkpoint")
            cps.append({"dayId": day_id, "label": label, "date": info["date"], "week": info["week"], "slot": info["slot"]})
        _check_sections(body, problems)
        spec.update({"project": project, "projectLabel": pinfo.get("label", project), "weeks": list(weeks),
                     "checkpoints": cps})
    if spec["slug"].lower() in RESERVED_SLUGS:
        problems.append(f"the slug '{spec['slug']}' is reserved (it would overwrite the projects index)")
    return (None if problems else spec), problems


def _scan(root: Path, cur: dict | None) -> list[tuple[str, dict | None, list[str]]]:
    """(rel, spec or None, problems) per spec file, cross-file checks included; rel is under projects/."""
    cur = _load_cur(root, cur)
    cal = _calendar(cur)
    rows = []
    for folder, path in _spec_files(root):
        rel = path.relative_to(root / "projects").as_posix()
        spec, problems = _check_file(folder, path, rel, cur, cal)
        rows.append([rel, spec, problems])
    seen_slug: dict[str, str] = {}
    seen_hand_in: dict[str, str] = {}
    seen_project: dict[str, str] = {}
    for row in rows:
        rel, spec, problems = row
        stem = Path(rel).stem
        m = SPRINT_NAME_RE.match(Path(rel).name)
        slug = (m.group(2) if m and rel.startswith("sprints/") else stem).lower()
        if slug in seen_slug:
            problems.append(f"slug '{slug}' is already used by projects/{seen_slug[slug]} (page names must be unique)")
        else:
            seen_slug[slug] = rel
        if spec and spec["kind"] == "official":
            if spec["project"] in seen_project:
                problems.append(f"project {spec['project']} already has a spec, projects/{seen_project[spec['project']]} "
                                "(one spec per official project)")
            else:
                seen_project[spec["project"]] = rel
        if spec and spec["kind"] == "sprint":
            if spec["handIn"] in seen_hand_in:
                problems.append(f"handIn '{spec['handIn']}' is already used by projects/{seen_hand_in[spec['handIn']]} "
                                f"(a second sprint in a week hands in under <week-dir>/hackathon/<slug>/)")
            else:
                seen_hand_in[spec["handIn"]] = rel
        if problems:
            row[1] = None
    return [tuple(r) for r in rows]


def validate(root: Path = ROOT, cur: dict | None = None) -> list[str]:
    """Every problem with the specs under root/projects/, one line each: 'projects/<rel>: <message>'."""
    return [f"projects/{rel}: {p}" for rel, _spec, problems in _scan(root, cur) for p in problems]


def _order(specs: list[dict], cur: dict) -> list[dict]:
    keys = list((cur.get("projects") or {}).keys())
    officials = sorted((s for s in specs if s["kind"] == "official"),
                       key=lambda s: (keys.index(s["project"]) if s["project"] in keys else len(keys), s["slug"]))
    sprints = sorted((s for s in specs if s["kind"] == "sprint"), key=lambda s: s["slug"])
    sprints.sort(key=lambda s: s["assigned"], reverse=True)
    return officials + sprints


def load_specs(root: Path = ROOT, cur: dict | None = None, strict: bool = True) -> list[dict]:
    """The valid specs, officials first (curriculum order) then sprints newest first.

    strict: raise SpecError listing every problem. strict=False: skip each broken file with one warning
    line on stderr (build_index.py uses this so a typo in a spec never blocks a day release).
    """
    cur = _load_cur(root, cur)
    rows = _scan(root, cur)
    problems = [f"projects/{rel}: {p}" for rel, _s, ps in rows for p in ps]
    if strict and problems:
        raise SpecError("\n".join(problems))
    if not strict:
        for rel, _s, ps in rows:
            if ps:
                print(f"build_projects: skipped projects/{rel} ({len(ps)} problem{'s' if len(ps) != 1 else ''}: {ps[0]}; "
                      f"run: python harness/build_projects.py --validate)", file=sys.stderr)
    return _order([s for _rel, s, ps in rows if s is not None and not ps], cur)


# ---------------------------------------------------------------- calendar marks
def calendar_marks(specs: list[dict], cur: dict) -> dict:
    """{"due": {iso: [{slug,title}]}, "cp": {iso: [{slug,title,label}]}, "sprints": [{slug,title,start,end}]}.

    Visible specs only (drafts carry no mark). Dates are ISO strings, as in window.CAL.
    """
    due: dict[str, list[dict]] = {}
    cp: dict[str, list[dict]] = {}
    sprints = []
    for s in specs:
        if not s.get("visible"):
            continue
        if s["kind"] == "sprint":
            due.setdefault(s["due"].isoformat(), []).append({"slug": s["slug"], "title": s["title"]})
            sprints.append({"slug": s["slug"], "title": s["title"],
                            "start": s["assigned"].isoformat(), "end": s["due"].isoformat()})
        else:
            for c in s["checkpoints"]:
                cp.setdefault(c["date"].isoformat(), []).append({"slug": s["slug"], "title": s["title"], "label": c["label"]})
    sprints.sort(key=lambda x: (x["start"], x["slug"]))
    return {"due": due, "cp": cp, "sprints": sprints}


# ---------------------------------------------------------------- html
CSS = """
  .pj-main { padding-top: 0; }
  .pj-page { max-width: 980px; margin: 0 auto; padding-top: 30px; padding-bottom: 50px; }
  .pj-page .lede { max-width: none; margin: 0 0 10px; }
  .pj-page .lede h1 { font-size: 40px; line-height: 1.1; margin: 0 0 10px; letter-spacing: -.5px; }
  .pj-page .lede .meta { display: flex; gap: 14px 18px; flex-wrap: wrap; align-items: center; color: var(--ink-soft); font-size: 15px; }
  .pj-page .lede .meta b { color: var(--ink); }
  .pj-page .lede p { font-size: 18px; line-height: 1.6; color: var(--ink-soft); margin: 14px 0 0; }
  .pj-page .step { opacity: 1; min-height: 0; justify-content: flex-start; padding: 30px 0 10px; border-left: 0; margin-left: 0; padding-left: 0; }
  .pj-page [id] { scroll-margin-top: 72px; }
  .pj-page .step h2 { font-size: 28px; line-height: 1.15; margin: 6px 0 12px; }
  .pj-page .step h3 { font-size: 19px; line-height: 1.3; margin: 22px 0 6px; }
  .pj-page .step ul, .pj-page .step ol { margin: 0 0 14px; padding-left: 22px; font-size: 16px; line-height: 1.55; }
  .pj-page .step li { margin: 0 0 5px; }
  .pj-page .step p { font-size: 16px; line-height: 1.6; color: var(--ink-soft); margin: 0 0 12px; }
  .pj-page .step code, .pj-facts code { font-family: var(--mono); font-size: .9em; background: var(--code-bg); padding: 1px 5px; border-radius: 4px; }
  .pj-page .step pre { background: var(--code-bg); padding: 12px 14px; border-radius: 8px; overflow-x: auto; font-size: 14px; }
  .pj-page .step pre code { background: none; padding: 0; }
  .pj-page .step table { width: 100%; border-collapse: collapse; font-size: 15.5px; line-height: 1.5; margin: 0 0 18px; }
  .pj-page .step th, .pj-page .step td { border: 1px solid var(--line); padding: 7px 10px; text-align: left; vertical-align: top; }
  .pj-page .step thead th { background: var(--surface-2); font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: var(--ink-soft); }
  .pj-facts th { width: 150px; background: var(--surface-2); font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: var(--ink-soft); }
  .pj-status { display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; padding: 2px 8px; border-radius: 20px; border: 1px solid var(--line); white-space: nowrap; vertical-align: middle; }
  .pj-status.open, .pj-status.published { color: var(--good-ink); border-color: var(--good-line); background: var(--good-soft); }
  .pj-status.draft { color: var(--warn-ink); border-color: var(--warn-line); background: var(--warn-soft); }
  .pj-status.closed { color: var(--dim); }
  .pj-draft { border-left: 3px solid var(--warn-line); padding-left: 12px; }
  .pj-checkpoints li { font-weight: 600; color: var(--ink); }
  .pj-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin: 24px 0 0; }
  .pj-card, .pj-slot { margin: 0; display: flex; flex-direction: column; gap: 6px; }
  .pj-card h2, .pj-slot h2 { font-size: 22px; line-height: 1.2; margin: 0; }
  .pj-card .pj-when { color: var(--ink-soft); font-size: 14px; margin: 0; }
  .pj-card .pj-status { align-self: flex-start; }
  .pj-card .fr-btn { margin-top: auto; align-self: flex-start; }
  .pj-card.pj-closed { opacity: .7; }
  .pj-slot { opacity: .75; }
  .pj-slot .ritual { align-self: flex-start; }
  .pj-intro p, .pj-empty { font-size: 17px; line-height: 1.65; color: var(--ink-soft); margin: 0 0 12px; }
  @media (max-width: 700px) { .pj-page .lede h1 { font-size: 30px; } .pj-facts th { width: auto; } }
"""
CLOSE = "</body>\n</html>\n"


def _md(text: str) -> str:
    import markdown  # lazy: only the page renderer needs it (requirements-dev.txt)
    return markdown.markdown(text, extensions=["tables", "fenced_code"], output_format="html")


def _shell(title: str, body: str, cfg: dict, v: str) -> str:
    return site_pages.shell(title, body, cfg, v, active="projects", extra_css=CSS,
                            main_class="pj-main", article_class="pj-page") + CLOSE


def _status_pill(status: str) -> str:
    return f'<span class="pj-status {esc(status)}">{esc(LABELS.get(status, status))}</span>'


def _weeks_label(weeks: list[int]) -> str:
    if len(weeks) == 2 and weeks[0] != weeks[1]:
        return f"Weeks {weeks[0]}–{weeks[1]}"
    return f"Week {weeks[0]}" if weeks else ""


def checkpoint_text(c: dict) -> str:
    """'Week 5 · Day 5 — Fri Nov 13, 2026 — Showcase' (plain text, never a link)."""
    return f"Week {c['week']} · Day {c['slot']} — {bi.date_label(c['date'], year=True)} — {c['label']}"


def _body_sections(body: str, used: set[str], prepend: dict[str, str] | None = None) -> tuple[str, list[str]]:
    """(preamble html, [section html]) with unique ids; `prepend` maps a heading to html placed under its h2."""
    pre, secs = _sections(body)
    out = []
    for heading, text in secs:
        sid = base = slugify(heading)
        n = 2
        while sid in used:
            sid = f"{base}-{n}"
            n += 1
        used.add(sid)
        extra = (prepend or {}).get(heading, "")
        out.append(f'    <section class="step" id="{esc(sid)}">\n      <h2>{esc(heading)}</h2>\n'
                   f'{extra}{_md(text) if text.strip() else ""}\n    </section>')
    return (_md(pre) if pre.strip() else ""), out


def _facts(rows: list[tuple[str, str]]) -> str:
    trs = "\n".join(f'          <tr><th scope="row">{esc(k)}</th><td>{v}</td></tr>' for k, v in rows)
    return f'      <table class="pj-facts">\n        <tbody>\n{trs}\n        </tbody>\n      </table>\n'


def render_page(spec: dict, cfg: dict, cur: dict, v: str) -> str:
    """One spec page (sprint or official), complete with the closing tags."""
    used = {"reading-main", "at-a-glance"}
    hand_in = f'<code>{esc(spec["handIn"])}</code> in your learner repository'
    if spec["kind"] == "sprint":
        meta = (f'<span>Sprint</span><span><b>{esc(LABELS.get(spec["mode"], spec["mode"]))}</b></span>'
                f'<span>Due <b>{esc(bi.date_label(spec["due"], year=True))}</b></span>{_status_pill(spec["status"])}')
        rows = [("Mode", esc(LABELS.get(spec["mode"], spec["mode"]))),
                ("Assigned", esc(bi.date_label(spec["assigned"], year=True))),
                ("Due", esc(bi.date_label(spec["due"], year=True))),
                ("Hand-in", hand_in)]
        if spec["tools"]:
            rows.append(("Tools", esc(", ".join(spec["tools"]))))
        rows.append(("Status", esc(LABELS.get(spec["status"], spec["status"]))))
        prepend = None
        notice = ""
    else:
        meta = (f'<span><b>{esc(spec["projectLabel"])}</b></span><span>{esc(_weeks_label(spec["weeks"]))}</span>'
                f'{_status_pill(spec["status"])}')
        rows = [("Project", f'{esc(spec["projectLabel"])} ({esc(spec["project"])})'),
                ("Weeks", esc(_weeks_label(spec["weeks"]))),
                ("Hand-in", hand_in),
                ("Status", esc(LABELS.get(spec["status"], spec["status"])))]
        items = "\n".join(f"        <li>{esc(checkpoint_text(c))}</li>" for c in spec["checkpoints"])
        prepend = {"Checkpoints": f'      <ul class="pj-checkpoints">\n{items}\n      </ul>\n'}
        notice = ('      <p class="pj-draft">Draft: this spec is still being written and can change before it is published.</p>\n'
                  if spec["status"] == "draft" else "")
    pre, secs = _body_sections(spec["body"], used, prepend)
    intro = f'      <div class="pj-intro">\n{pre}\n      </div>\n' if pre else ""
    body = (f'    <div class="lede">\n      <h1>{esc(spec["title"])}</h1>\n      <div class="meta">{meta}</div>\n'
            f'{notice}{intro}    </div>\n\n'
            f'    <section class="step" id="at-a-glance">\n      <h2>At a glance</h2>\n{_facts(rows)}    </section>\n\n'
            + "\n\n".join(secs))
    return _shell(spec["title"], body, cfg, v)


def _card(spec: dict) -> str:
    closed = " pj-closed" if spec["status"] == "closed" else ""
    if spec["kind"] == "sprint":
        k = f'Sprint · {LABELS.get(spec["mode"], spec["mode"])}'
        when = [f'Assigned {bi.date_label(spec["assigned"], year=True)} · due {bi.date_label(spec["due"], year=True)}']
    else:
        k = f'{spec["projectLabel"]} · {_weeks_label(spec["weeks"])}'
        when = [f'{c["label"]}: {bi.date_label(c["date"], year=True)}' for c in spec["checkpoints"]]
    lines = [f'      <div class="callout pj-card{closed}" data-slug="{esc(spec["slug"])}">',
             f'        <div class="k">{esc(k)}</div>',
             f'        <h2>{esc(spec["title"])}</h2>']
    lines += [f'        <p class="pj-when">{esc(w)}</p>' for w in when]
    lines += [f'        {_status_pill(spec["status"])}',
              f'        <a class="fr-btn" href="{esc(spec["slug"])}.html">Open the spec</a>',
              '      </div>']
    return "\n".join(lines)


def _slot(pid: str, pinfo: dict) -> str:
    """A placeholder card for an official project with no published spec yet (like the exit-criteria index)."""
    k = _weeks_label(list(pinfo.get("weeks") or []))
    return "\n".join([f'      <div class="callout pj-slot" data-project="{esc(pid)}">',
                      f'        <div class="k">{esc(k)}</div>',
                      f'        <h2>{esc(pinfo.get("label", pid))}</h2>',
                      '        <span class="ritual">Not published yet</span>',
                      '      </div>'])


def render_index(specs: list[dict], cfg: dict, v: str, cur: dict | None = None) -> str:
    """The section index: one card per visible spec (drafts have a page but no card), complete page.
    The official projects of curriculum.json are always listed, as a placeholder until their spec is published."""
    cur = _load_cur(ROOT, cur)
    visible = [s for s in specs if s.get("visible")]
    officials = {s["project"]: s for s in visible if s["kind"] == "official"}
    sprints = [s for s in visible if s["kind"] == "sprint"]
    parts = ["""    <div class="lede">
      <h1>Projects</h1>
      <p>The spec sheets for the course projects and the short sprints. Each one says what to build, how to hand it
      in and when it is due. Due days and checkpoints carry a 🏁 on the <a href="../index.html">course calendar</a>.</p>
    </div>"""]
    slots = [(_card(officials[pid]) if pid in officials else _slot(pid, pinfo))
             for pid, pinfo in (cur.get("projects") or {}).items()]
    if slots:
        parts.append(f"""    <section class="step" id="official">
      <div class="tag">Official projects</div>
      <h2>Projects</h2>
      <p class="pj-empty">Each project runs over several weeks and ends with a showcase.</p>
      <div class="pj-cards">
{chr(10).join(slots)}
      </div>
    </section>""")
    cards = (f'      <div class="pj-cards">\n{chr(10).join(_card(s) for s in sprints)}\n      </div>' if sprints
             else '      <p class="pj-empty">No sprint published yet.</p>')
    parts.append(f"""    <section class="step" id="sprints">
      <div class="tag">Sprints</div>
      <h2>Sprints</h2>
      <p class="pj-empty">A sprint is a few days of work, often in pairs, handed in under the week's
      <code>hackathon/</code> folder of your learner repository.</p>
{cards}
    </section>""")
    return _shell("Projects", "\n\n".join(parts), cfg, v)


# ---------------------------------------------------------------- build / check
def expected(cur: dict | None = None, root: Path = ROOT) -> dict[Path, str]:
    """Every file docs/projects/ should hold, with its content (broken specs are left out, silently)."""
    cur = _load_cur(root, cur)
    specs = _order([s for _rel, s, ps in _scan(root, cur) if s is not None and not ps], cur)
    cfg = site_pages.load_config()
    v = site_pages.version()
    out_dir = root / "docs" / "projects"
    files = {out_dir / "index.html": render_index(specs, cfg, v, cur)}
    for s in specs:
        files[out_dir / f"{s['slug']}.html"] = render_page(s, cfg, cur, v)
    return files


def check(root: Path = ROOT) -> list[str]:
    """Spec problems, then stale, missing or unexpected pages under docs/projects/, one per line."""
    return validate(root) + site_pages.check_dir(expected(root=root), root / "docs" / "projects", root, REBUILD_CMD)


def build(quiet: bool = False, root: Path = ROOT) -> bool:
    """Write the pages; True when anything changed. Raises SpecError when a spec is invalid."""
    problems = validate(root)
    if problems:
        raise SpecError("\n".join(problems))
    return site_pages.build_dir(expected(root=root), root / "docs" / "projects", root, quiet)


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if "--validate" in argv:
        problems = validate()
        for p in problems:
            print(p, file=sys.stderr)
        if problems:
            return 1
        print(f"projects/ valid ({len(_spec_files(ROOT))} specs)")
        return 0
    if "--check" in argv:
        problems = check()
        for p in problems:
            print(f"{p} — run: {REBUILD_CMD}", file=sys.stderr)
        if problems:
            return 1
        print("docs/projects in sync")
        return 0
    try:
        changed = build()
    except SpecError as e:
        print(str(e), file=sys.stderr)
        print("docs/projects not written: fix the specs above (python harness/build_projects.py --validate)", file=sys.stderr)
        return 1
    print("docs/projects updated" if changed else "docs/projects already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
