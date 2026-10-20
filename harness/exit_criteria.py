#!/usr/bin/env python3
"""Revature exit criteria as a harness input (D-0063).

The source of truth is the markdown drop zone `curriculum.json exitCriteria.sourceDir` (Curricula/Exit-Criteria):
one file per group, `qc-N-<slug>.md`, a `# QC - N` title and one `## <Section>` table per section. Two row
shapes are accepted, two-column (`| Required | text |`) and the broken one-column export (`| Required text |`).
Nothing is hand-maintained here: this module parses the files at runtime and numbers the rows positionally,
`<group>.<section slug>.<tier letter><row within tier within section>` (`qc2.sql.R07`), so a published file is
append-only. The registry (`fromWeek`, `sourceDir`, `groups` with `id, label, weeks, source`) lives in
`harness/curriculum.json`.

Consumers: plan_check.py (registry, group_for_week, normalise), args_for.py (week_args), build_exit_pages.py
(load_groups, load_group). plan_check imports this module, so plan_check is imported lazily inside audit() only.

Usage:
    python harness/exit_criteria.py show <qc2|3>   # markdown table of a group's rows (copy-paste source for plan rows)
    python harness/exit_criteria.py json [key]     # one Group, or every group, as JSON
    python harness/exit_criteria.py check          # registry + every present source parses; exit 1 on problems
    python harness/exit_criteria.py audit <week>   # the week plan's exit map against the group's rows
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

ROOT = bi.ROOT
PLANS = ROOT / "harness" / "plans"
TIERS = ("Required", "Preferred", "Stretch")
TIER_LETTER = {"Required": "R", "Preferred": "P", "Stretch": "S"}
ID_RE = re.compile(r"^(qc\d)\.([a-z0-9]+(?:-[a-z0-9]+)*)\.([RPS])(\d{2})$")
SOURCE_NAME_RE = re.compile(r"^qc-\d-[a-z0-9-]+\.md$")
NORMALISE = {"‘": "'", "’": "'", "“": '"', "”": '"', "‑": "-", " ": " "}
_ONE_COL_RE = re.compile(r"^(Required|Preferred|Stretch)\s+(.+)$")
_SEPARATOR_RE = re.compile(r"[\s|:-]+")
_DEFERRED_RE = re.compile(r"^week (\d+)$")

_CACHE: dict[tuple[str, float], dict] = {}   # (path, mtime) -> parse_source() result


# ---------------------------------------------------------------- text
def normalise(s: str) -> str:
    """Curly quotes, non-breaking hyphens and spaces to ASCII; whitespace runs to one space; stripped."""
    for src, dst in NORMALISE.items():
        s = s.replace(src, dst)
    return re.sub(r"\s+", " ", s).strip()


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ---------------------------------------------------------------- parsing
def parse_source(text: str, name: str = "") -> dict:
    """{"title", "sections": [{"name", "slug", "rows": [(tier, text), ...]}]}; ValueError on a row without a tier."""
    lines = text.splitlines()
    title = ""
    for ln in lines:
        if ln.startswith("# "):
            title = normalise(ln[2:])
            break
    sections: list[dict] = []
    current: dict | None = None
    seen_header = False
    for lineno, ln in enumerate(lines, 1):
        m = re.match(r"^## (.+)$", ln)
        if m:
            sec_name = normalise(m.group(1))
            current = {"name": sec_name, "slug": slug(sec_name), "rows": []}
            sections.append(current)
            seen_header = False
            continue
        if current is None or not ln.lstrip().startswith("|"):
            continue
        if not seen_header:
            seen_header = True
            continue
        if _SEPARATOR_RE.fullmatch(ln):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and cells[0] in TIERS:
            tier, body = cells[0], " | ".join(cells[1:])
        elif len(cells) == 1 and (om := _ONE_COL_RE.match(cells[0])):
            tier, body = om.group(1), om.group(2)
        else:
            raise ValueError(f"{name}:{lineno}: row has no tier: {ln[:60]}")
        body = normalise(body)
        if not body:
            raise ValueError(f"{name}:{lineno}: row has no text: {ln[:60]}")
        current["rows"].append((tier, body))
    return {"title": title, "sections": sections}


def number(gid: str, parsed: dict) -> list[dict]:
    """Positional ids: per section, per tier, 01.. in row order."""
    out = []
    for sec in parsed["sections"]:
        counters = {t: 0 for t in TIERS}
        for tier, text in sec["rows"]:
            counters[tier] += 1
            n = counters[tier]
            letter = TIER_LETTER[tier]
            out.append({"id": f"{gid}.{sec['slug']}.{letter}{n:02d}", "group": gid, "section": sec["name"],
                        "sectionSlug": sec["slug"], "tier": tier, "letter": letter, "n": n, "text": text})
    return out


# ---------------------------------------------------------------- registry
def registry(cur: dict | None = None) -> dict:
    """The curriculum's exitCriteria block, shape-checked (ValueError when malformed)."""
    cur = cur or bi.load_curriculum()
    reg = cur.get("exitCriteria")
    if not isinstance(reg, dict):
        raise ValueError("curriculum.json has no exitCriteria block")
    if not isinstance(reg.get("fromWeek"), int) or isinstance(reg.get("fromWeek"), bool):
        raise ValueError("exitCriteria.fromWeek must be an int")
    if not isinstance(reg.get("sourceDir"), str) or not reg["sourceDir"]:
        raise ValueError("exitCriteria.sourceDir must be a non-empty string")
    groups = reg.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ValueError("exitCriteria.groups must be a non-empty list")
    for i, g in enumerate(groups):
        if not isinstance(g, dict):
            raise ValueError(f"exitCriteria.groups[{i}] is not an object")
        for key, typ in (("id", str), ("label", str), ("source", str)):
            if not isinstance(g.get(key), typ) or not g[key]:
                raise ValueError(f"exitCriteria.groups[{i}].{key} must be a non-empty string")
        weeks = g.get("weeks")
        if not isinstance(weeks, list) or not weeks or not all(isinstance(w, int) and not isinstance(w, bool) for w in weeks):
            raise ValueError(f"exitCriteria.groups[{i}].weeks must be a non-empty list of ints")
    return reg


def _source_path(reg: dict, group: dict) -> Path:
    return ROOT / reg["sourceDir"] / group["source"]


def _parsed_file(path: Path, name: str) -> dict:
    key = (str(path), path.stat().st_mtime)
    hit = _CACHE.get(key)
    if hit is None:
        hit = parse_source(path.read_text(encoding="utf-8"), name)
        _CACHE.clear()  # one live entry per path is enough; drop stale mtimes
        _CACHE[key] = hit
    return hit


def _find_group(reg: dict, key) -> dict | None:
    if isinstance(key, int) and not isinstance(key, bool):
        return next((g for g in reg["groups"] if key in g["weeks"]), None)
    key = str(key).strip()
    if key.isdigit():
        return next((g for g in reg["groups"] if int(key) in g["weeks"]), None)
    return next((g for g in reg["groups"] if g["id"] == key), None)


def _build_group(reg: dict, g: dict) -> dict:
    path = _source_path(reg, g)
    stem = Path(g["source"]).stem
    out = {"id": g["id"], "label": g["label"], "weeks": list(g["weeks"]), "lastWeek": max(g["weeks"]), "source": g["source"],
           "sourceFile": path.as_posix(), "page": f"exit-criteria/{stem}.html", "exists": path.is_file(),
           "title": "", "sections": [], "criteria": [], "byId": {}}
    if not out["exists"]:
        return out
    parsed = _parsed_file(path, g["source"])
    criteria = number(g["id"], parsed)
    out["title"] = parsed["title"]
    out["criteria"] = criteria
    out["byId"] = {c["id"]: c for c in criteria}
    out["sections"] = [{"name": s["name"], "slug": s["slug"], "criteria": [c for c in criteria if c["sectionSlug"] == s["slug"]]}
                       for s in parsed["sections"]]
    return out


def load_group(key, cur: dict | None = None) -> dict | None:
    """Group by id ("qc2") or week number (int or digit string); None when the key matches no group."""
    reg = registry(cur)
    g = _find_group(reg, key)
    return _build_group(reg, g) if g else None


def load_groups(cur: dict | None = None) -> list[dict]:
    reg = registry(cur)
    return [_build_group(reg, g) for g in reg["groups"]]


def group_for_week(week_no: int, cur: dict | None = None) -> dict | None:
    return load_group(int(week_no), cur)


def week_args(cur: dict, week_no: int) -> dict:
    """What args_for.py passes into the week-plan and day workflows."""
    reg = registry(cur)
    from_week = reg["fromWeek"]
    group = group_for_week(week_no, cur)
    gid = group["id"] if group else None
    if week_no < from_week:
        return {"fromWeek": from_week, "active": False, "id": gid, "reason": "week before fromWeek"}
    if group is None:
        return {"fromWeek": from_week, "active": False, "id": None, "reason": "week in no group"}
    if not group["exists"]:
        return {"fromWeek": from_week, "active": False, "id": gid, "reason": "source not published"}
    stem = Path(group["source"]).stem
    return {"fromWeek": from_week, "active": True, "id": gid, "label": group["label"], "weeks": group["weeks"],
            "lastWeek": group["lastWeek"], "source": group["source"], "sourceFile": group["sourceFile"],
            "pageRel": f"../../exit-criteria/{stem}.html",
            "criteria": [{"id": c["id"], "section": c["section"], "tier": c["tier"], "text": c["text"]} for c in group["criteria"]]}


# ---------------------------------------------------------------- checks
def check_sources(cur: dict | None = None) -> list[str]:
    """Registry and source problems, one per line; [] when everything is in order."""
    cur = cur or bi.load_curriculum()
    try:
        reg = registry(cur)
    except ValueError as e:
        return [str(e)]
    problems: list[str] = []
    week_nos = [w["week"] for w in cur["weeks"]]
    if reg["fromWeek"] not in week_nos:
        problems.append(f"exitCriteria.fromWeek {reg['fromWeek']} is not a curriculum week ({week_nos[0]}..{week_nos[-1]})")
    owners: dict[int, list[str]] = {}
    seen_ids: set[str] = set()
    for g in reg["groups"]:
        if g["id"] in seen_ids:
            problems.append(f"{g['id']}: duplicate group id")
        seen_ids.add(g["id"])
        if not SOURCE_NAME_RE.match(g["source"]):
            problems.append(f"{g['id']}: source {g['source']!r} does not match qc-N-<slug>.md")
        weeks = g["weeks"]
        if weeks != list(range(weeks[0], weeks[0] + len(weeks))):
            problems.append(f"{g['id']}: weeks {weeks} are not contiguous ascending")
        for w in weeks:
            owners.setdefault(w, []).append(g["id"])
        path = _source_path(reg, g)
        if path.is_file():
            try:
                parsed = _parsed_file(path, g["source"])
            except ValueError as e:
                problems.append(str(e))
                continue
            ids = [c["id"] for c in number(g["id"], parsed)]
            dupes = sorted({i for i in ids if ids.count(i) > 1})
            if dupes:
                problems.append(f"{g['id']}: duplicate criterion ids {dupes}")
            if not ids:
                problems.append(f"{g['id']}: {g['source']} has no criteria rows")
    for w in week_nos:
        who = owners.get(w, [])
        if len(who) != 1:
            problems.append(f"week {w} is in {len(who)} groups ({', '.join(who) or 'none'}); expected exactly one")
    for w in sorted(set(owners) - set(week_nos)):
        problems.append(f"week {w} ({', '.join(owners[w])}) is not a curriculum week")
    return problems


def _plan_rows(path: Path) -> list[dict] | None:
    """The exit map rows of one plan (None when the plan is absent or not a plan)."""
    import plan_check  # lazy: plan_check imports this module
    if not path.is_file():
        return None
    try:
        plan = plan_check.load_plan(path)
    except ValueError:
        return None
    return list(plan.get("exitMap", []))


def _split_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    mapped, deferred = [], []
    for r in rows:
        cid = (r.get("ID") or "").strip()
        day = (r.get("Day") or "").strip()
        m = _DEFERRED_RE.match(day)
        if m:
            deferred.append({"id": cid, "week": int(m.group(1))})
        else:
            mapped.append({"id": cid, "day": day, "where": (r.get("Where") or "").strip(), "notesStep": (r.get("Notes step") or "").strip()})
    return mapped, deferred


def audit(week_no: int, cur: dict | None = None) -> dict:
    """The week plan's '## Exit criteria map' against the group's rows, plus the union across the group's plans."""
    cur = cur or bi.load_curriculum()
    reg = registry(cur)
    group = group_for_week(week_no, cur)
    gid = group["id"] if group else None
    active = bool(group and group["exists"] and week_no >= reg["fromWeek"])
    group_ids = list(group["byId"]) if group else []
    rows = _plan_rows(PLANS / f"week-{week_no:02d}.md")
    plan_exists = rows is not None
    mapped, week_rows = _split_rows(rows or [])
    # A `week NN` Day is a forward deferral when NN is later than this week and a taught-earlier pointer when earlier
    # (plan_check validates the latter against that week's plan).
    deferred = [d for d in week_rows if d["week"] > week_no]
    taught_earlier = [d for d in week_rows if d["week"] < week_no]
    in_plan = {r["id"] for r in mapped} | {r["id"] for r in week_rows}
    missing = [i for i in group_ids if i not in in_plan]
    unknown = sorted(i for i in in_plan if i not in group["byId"]) if group else sorted(in_plan)
    anywhere: set[str] = set()
    for w in (group["weeks"] if group else []):
        wrows = _plan_rows(PLANS / f"week-{w:02d}.md")
        if wrows:
            m2, _ = _split_rows(wrows)
            anywhere.update(r["id"] for r in m2)
    return {"week": week_no, "group": gid, "active": active, "planExists": plan_exists, "mapped": mapped, "deferred": deferred,
            "taughtEarlier": taught_earlier, "missing": missing, "unknown": unknown,
            "groupUnion": {"mappedAnywhere": [i for i in group_ids if i in anywhere],
                           "missingEverywhere": [i for i in group_ids if i not in anywhere]}}


# ---------------------------------------------------------------- cli
USAGE = "usage: python harness/exit_criteria.py show <qc2|3> | json [key] | check | audit <week>"


def _cmd_show(key: str) -> int:
    group = load_group(key)
    if group is None:
        print(f"unknown group or week: {key}", file=sys.stderr)
        return 2
    if not group["exists"]:
        print(f"{group['id']}: source not published ({group['source']} is absent)", file=sys.stderr)
        return 2
    print("| ID | Tier | Section | Criterion |")
    print("|---|---|---|---|")
    for c in group["criteria"]:
        print(f"| {c['id']} | {c['tier']} | {c['section']} | {c['text'].replace('|', '\\|')} |")
    return 0


def _cmd_json(key: str | None) -> int:
    if key is None:
        data = load_groups()
    else:
        data = load_group(key)
        if data is None:
            print(f"unknown group or week: {key}", file=sys.stderr)
            return 2
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def _cmd_check() -> int:
    problems = check_sources()
    if problems:
        print("\n".join(problems))
        return 1
    groups = load_groups()
    published = [g for g in groups if g["exists"]]
    print(f"OK: {len(groups)} groups registered, {len(published)} published, {sum(len(g['criteria']) for g in published)} criteria")
    return 0


def _cmd_audit(week: str) -> int:
    try:
        week_no = int(week)
    except ValueError:
        print(f"week must be a number, got {week!r}", file=sys.stderr)
        return 2
    a = audit(week_no)
    state = "active" if a["active"] else "inactive"
    print(f"week {week_no}: group {a['group'] or '-'} ({state}); plan {'found' if a['planExists'] else 'absent'}")
    print(f"mapped {len(a['mapped'])}, deferred {len(a['deferred'])}, taught earlier {len(a['taughtEarlier'])}, missing {len(a['missing'])}, unknown {len(a['unknown'])}")
    if a["missing"]:
        print("missing: " + ", ".join(a["missing"]))
    if a["unknown"]:
        print("unknown: " + ", ".join(a["unknown"]))
    u = a["groupUnion"]
    print(f"group union: {len(u['mappedAnywhere'])} mapped in some plan, {len(u['missingEverywhere'])} missing everywhere")
    if a["active"] and (a["missing"] or a["unknown"] or not a["planExists"]):
        return 1
    return 0


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
        except Exception:
            pass
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "show" and len(rest) == 1:
        return _cmd_show(rest[0])
    if cmd == "json" and len(rest) <= 1:
        return _cmd_json(rest[0] if rest else None)
    if cmd == "check" and not rest:
        return _cmd_check()
    if cmd == "audit" and len(rest) == 1:
        return _cmd_audit(rest[0])
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
