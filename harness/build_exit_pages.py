#!/usr/bin/env python3
"""Generate the learner-facing exit-criteria pages under docs/exit-criteria/ (D-0063).

One index page plus one checklist page per PUBLISHED group (a group whose source file under
`curriculum.json exitCriteria.sourceDir` exists). Everything is derived at build time:

- the rows come from harness/exit_criteria.py (the markdown drop zone, numbered positionally);
- "where each criterion is taught" comes from the `## Exit criteria map` of each week plan of the
  group (`plan_check.load_plan(...)["exitMap"]`, read defensively: a plan without the section maps
  nothing);
- a day is linked only while its curriculum status is `live` (same rule as docs/index.html);
- the per-criterion tick is localStorage only (`tc_exit_<group id>`), no backend.

The pages are committed. build_index.py, release_week.py and close_day.py rebuild them, so a status flip
(authored -> live) or a plan change reaches the pages without a hand step; `--check` is the sync test.
Like docs/index.html the pages carry no hand-typed date, and their `?v=` cache-buster is copied from
docs/index.html so `docs/bump-css.sh` keeps them in step.

Usage:
    python harness/build_exit_pages.py          # (re)write docs/exit-criteria/*.html
    python harness/build_exit_pages.py --check  # exit 1 when a page is stale or unexpected
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import exit_criteria as ec  # noqa: E402

ROOT = bi.ROOT
OUT = ROOT / "docs" / "exit-criteria"
PLANS = ROOT / "harness" / "plans"
TIER_CLASS = {"Required": "req", "Preferred": "pref", "Stretch": "str"}
_V_RE = re.compile(r'style\.css\?v=([^"]+)')
_VJS_RE = re.compile(r'theme\.js\?v=([^"]+)')


def load_config() -> dict:
    return json.loads((ROOT / "harness" / "config.json").read_text(encoding="utf-8"))


def esc(s) -> str:
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- data
def version() -> str:
    """The `?v=` value docs/index.html uses for style.css (bump-css.sh rewrites every page the same way)."""
    m = _V_RE.search(bi.INDEX.read_text(encoding="utf-8"))
    return m.group(1) if m else "1"


def js_version() -> str:
    """The `?v=` value docs/index.html uses for theme.js (bump-css.sh without --all leaves it alone)."""
    m = _VJS_RE.search(bi.INDEX.read_text(encoding="utf-8"))
    return m.group(1) if m else version()


def _week(cur: dict, week_no: int) -> dict | None:
    return next((w for w in cur["weeks"] if w["week"] == week_no), None)


def group_days(group: dict, cur: dict) -> list[dict]:
    """Every teaching day of the group's weeks in curriculum order: {dayId, week, day, title, rel, live}."""
    out = []
    for wn in group["weeks"]:
        wk = _week(cur, wn)
        if wk is None:
            continue
        for d in bi.teaching_days(wk):
            out.append({"dayId": d["id"], "week": wn, "day": d["day"], "title": d["title"],
                        "rel": bi.day_paths(wk, d)["rel"], "live": d.get("status") == "live"})
    return out


def coverage(group: dict, cur: dict) -> dict[str, list[dict]]:
    """criterion id -> [Cover], from the exit maps of the group's week plans (in-week rows only)."""
    import plan_check  # lazy: plan_check imports exit_criteria, which imports build_index
    days = {d["dayId"]: d for d in group_days(group, cur)}
    cover: dict[str, list[dict]] = {}
    for wn in group["weeks"]:
        path = PLANS / f"week-{wn:02d}.md"
        if not path.is_file():
            continue
        try:
            plan = plan_check.load_plan(path)
        except ValueError:
            continue
        for row in plan.get("exitMap", []) or []:
            cid = (row.get("ID") or "").strip()
            day_id = (row.get("Day") or "").strip()
            d = days.get(day_id)
            if not cid or d is None or d["week"] != wn:
                continue
            c = dict(d)
            c["where"] = (row.get("Where") or "").strip()
            c["notesStep"] = (row.get("Notes step") or "").strip()
            lst = cover.setdefault(cid, [])
            if not any(x["dayId"] == c["dayId"] for x in lst):
                lst.append(c)
    return cover


def _weeks_label(group: dict, long: bool = False) -> str:
    ws = group["weeks"]
    if len(ws) == 1:
        return f"{'Week' if long else 'week'} {ws[0]}"
    return f"{'Weeks' if long else 'weeks'} {ws[0]}–{ws[-1]}"


def _counts(group: dict) -> dict[str, int]:
    return {t: sum(1 for c in group["criteria"] if c["tier"] == t) for t in ec.TIERS}


# ---------------------------------------------------------------- html
CSS = """
  .ec-main { padding-top: 0; }
  .ec-page { max-width: 980px; margin: 0 auto; padding-top: 30px; padding-bottom: 50px; }
  .ec-page .lede { max-width: none; margin: 0 0 10px; }
  .ec-page .lede h1 { font-size: 40px; line-height: 1.1; margin: 0 0 10px; letter-spacing: -.5px; }
  .ec-page .lede .meta { display: flex; gap: 14px 18px; flex-wrap: wrap; align-items: center; color: var(--ink-soft); font-size: 15px; }
  .ec-page .lede .meta b { color: var(--ink); }
  .ec-page .lede p { font-size: 18px; line-height: 1.6; color: var(--ink-soft); margin: 14px 0 0; }
  .ec-page .step { opacity: 1; min-height: 0; justify-content: flex-start; padding: 30px 0 10px; border-left: 0; margin-left: 0; padding-left: 0; }
  .ec-page [id] { scroll-margin-top: 72px; }
  .ec-page .step h2 { font-size: 28px; line-height: 1.15; margin: 6px 0 12px; }
  .ec-page .step h3 { font-size: 19px; line-height: 1.3; margin: 22px 0 6px; scroll-margin-top: 80px; }
  .ec-page .step h3 a { color: inherit; text-decoration: none; border-bottom: 1px solid var(--accent-line); }
  .ec-page .step h3 a:hover { color: var(--accent); }
  .ec-page .step ul { margin: 0 0 14px; padding-left: 22px; font-size: 16px; line-height: 1.55; }
  .ec-page .step li { margin: 0 0 5px; }
  .ec-page .step p { font-size: 16px; line-height: 1.6; color: var(--ink-soft); margin: 0 0 12px; }
  .ec-page .step code, .ec-page .step li a { font-family: var(--mono); font-size: .9em; }
  .ec-page .step li a { background: var(--code-bg); padding: 1px 5px; border-radius: 4px; text-decoration: none; color: var(--accent-ink); }
  .ec-page .step li a:hover { text-decoration: underline; }
  .ec-legend { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin: 16px 0 0; font-size: 14px; color: var(--ink-soft); }
  .ec-tier { display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; padding: 2px 8px; border-radius: 20px; border: 1px solid var(--line); white-space: nowrap; vertical-align: middle; }
  .ec-tier.req { color: var(--good-ink); border-color: var(--good-line); background: var(--good-soft); }
  .ec-tier.pref { color: var(--info); border-color: var(--info-line); background: var(--info-soft); }
  .ec-tier.str { color: var(--warn-ink); border-color: var(--warn-line); background: var(--warn-soft); }
  .ec-table { width: 100%; border-collapse: collapse; font-size: 15.5px; line-height: 1.5; margin: 0 0 18px; }
  .ec-table th, .ec-table td { border: 1px solid var(--line); padding: 7px 10px; text-align: left; vertical-align: top; }
  .ec-table th { background: var(--surface-2); font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: var(--ink-soft); }
  .ec-table td:first-child { text-align: center; width: 44px; }
  .ec-table input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--accent); cursor: pointer; }
  .ec-table tr { scroll-margin-top: 80px; }
  .ec-table tr:target td { background: var(--accent-soft); }
  .ec-table tr.ec-done td { color: var(--dim); }
  .ec-table tr.ec-done td:nth-child(4) { text-decoration: line-through; }
  .ec-table td code { font-family: var(--mono); font-size: .85em; background: var(--code-bg); padding: 1px 5px; border-radius: 4px; white-space: nowrap; }
  .ec-table td a { color: var(--accent); white-space: nowrap; }
  .ec-soon { color: var(--dim); white-space: nowrap; }
  .ec-page .ritual { cursor: pointer; font: inherit; font-size: 12px; font-weight: 600; background: var(--surface); color: var(--ink-soft); }
  .ec-page button.ritual:hover { color: var(--accent); border-color: var(--accent); }
  .ec-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin: 24px 0 0; }
  .ec-card { margin: 0; display: flex; flex-direction: column; gap: 6px; }
  .ec-card h2 { font-size: 22px; line-height: 1.2; margin: 0; }
  .ec-card .ec-counts { color: var(--ink-soft); font-size: 14px; margin: 0; }
  .ec-card .fr-btn { margin-top: auto; align-self: flex-start; }
  .ec-card .ritual { align-self: flex-start; margin-top: auto; }
  .ec-intro p { font-size: 17px; line-height: 1.65; color: var(--ink-soft); margin: 0 0 12px; }
  @media (max-width: 700px) { .ec-page .lede h1 { font-size: 30px; } .ec-table { font-size: 14px; } }
"""


def _shell(title: str, body: str, cfg: dict, v: str) -> str:
    site = cfg.get("siteTitle", "")
    brand = cfg.get("brand", {}) or {}
    repo = (cfg.get("repoUrl") or "").rstrip("/")
    demo = ((cfg.get("demoRepo") or {}).get("url") or "").rstrip("/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | {esc(site)}</title>
<link rel="stylesheet" href="../assets/css/style.css?v={esc(v)}">
<script src="../assets/js/theme.js?v={esc(js_version())}"></script>
<style>{CSS}</style>
</head>
<body>
<a class="skip-link" href="#reading-main">Skip to content</a>

<div class="topbar">
  <div class="topbar-left">
    <span class="brand"><a href="../index.html"><b>{esc(brand.get('bold', ''))}</b>·{esc(brand.get('rest', ''))}</a></span>
    <a class="topnav" href="../index.html">Home</a>
  </div>
  <nav class="topbar-center">
    <a class="topnav" href="{esc(demo)}" target="_blank" rel="noopener">Demos</a>
    <a class="topnav" href="{esc(repo)}/tree/main/exercises" target="_blank" rel="noopener">Exercises</a>
    <a class="topnav" href="index.html">Exit criteria</a>
  </nav>
  <div class="topbar-right"></div>
</div>

<main class="lesson2 ec-main" id="reading-main">
  <article class="reading-col ec-page">
{body}
  </article>
</main>

<footer class="foot">{esc(site)} Developer Training</footer>
"""


def tier_pill(tier: str) -> str:
    return f'<span class="ec-tier {TIER_CLASS.get(tier, "")}">{esc(tier)}</span>'


def render_index(groups: list[dict], cfg: dict, v: str) -> str:
    cards = []
    for g in groups:
        stem = Path(g["source"]).stem
        parts = [f'      <div class="callout ec-card">',
                 f'        <div class="k">{esc(g["id"])} · {esc(_weeks_label(g))}</div>',
                 f'        <h2>{esc(g["label"])}</h2>']
        if g["exists"]:
            n = _counts(g)
            parts.append(f'        <p class="ec-counts">{n["Required"]} required · {n["Preferred"]} preferred · {n["Stretch"]} stretch</p>')
            parts.append(f'        <a class="fr-btn" href="{esc(stem)}.html">Open the checklist</a>')
        else:
            parts.append('        <span class="ritual">Not published yet</span>')
        parts.append('      </div>')
        cards.append("\n".join(parts))
    body = f"""    <div class="lede">
      <h1>Exit criteria</h1>
      <p>Revature publishes, for each technology group of the course, the list of things a learner should be able to do
      or explain when the group ends. Each page below is that list for one group, with a tick box per row and a link to
      the day of notes where it is taught.</p>
    </div>

    <section class="step ec-intro" id="tiers">
      <div class="tag">How to read the tiers</div>
      <h2>Required, Preferred, Stretch</h2>
      <p><b>Required</b> rows are expected of everyone at the group's exit. <b>Preferred</b> rows are what a strong
      learner can also do. <b>Stretch</b> rows go beyond the course: good to know, never assumed.</p>
      <p>The mock interview and the exam at the end of each group draw from these rows, so use the checklist as a
      revision list: open a row's day of notes, work through it, then tick the row. Ticks are saved in this browser only
      (nothing is sent anywhere), so they are yours to clear and redo.</p>
    </section>

    <section class="step" id="groups">
      <div class="tag">Groups</div>
      <h2>One checklist per group</h2>
      <div class="ec-cards">
{chr(10).join(cards)}
      </div>
    </section>"""
    return _shell("Exit criteria", body, cfg, v)


def _day_heading(d: dict) -> str:
    text = f"Week {d['week']} · Day {d['day']} — {esc(d['title'])}"
    if d["live"]:
        return f'<a href="../weeks/{esc(d["rel"])}.html">{text}</a>'
    return text


def _short_day(d: dict) -> str:
    return f"W{d['week']} · D{d['day']}"


def render_group(group: dict, cover: dict[str, list[dict]], cfg: dict, cur: dict, v: str) -> str:
    gid = group["id"]
    total = len(group["criteria"])
    days = group_days(group, cur)
    by_day: dict[str, list[dict]] = {d["dayId"]: [] for d in days}
    for c in group["criteria"]:
        for cv in cover.get(c["id"], []):
            if cv["dayId"] in by_day:
                by_day[cv["dayId"]].append(c)
    out = [f"""    <div class="lede">
      <h1>{esc(group["label"])} exit criteria</h1>
      <div class="meta">
        <span>Group <b>{esc(gid)}</b></span>
        <span>{esc(_weeks_label(group, long=True))}</span>
        <span><b>{total}</b> criteria</span>
        <span id="ec-count">0 of {total} ticked</span>
        <button type="button" id="ec-reset" class="ritual">Clear my ticks</button>
      </div>
      <p>Tick a row once you can do or explain it without notes. Ticks are saved in this browser only. Each row links to
      the day whose notes teach it; a day that is not open yet is named but not linked.</p>
      <div class="ec-legend">
        {tier_pill("Required")} <span>expected of everyone</span>
        {tier_pill("Preferred")} <span>expected of a strong learner</span>
        {tier_pill("Stretch")} <span>beyond the course</span>
      </div>
    </div>

    <section class="step" id="by-day">
      <div class="tag">By day</div>
      <h2>Where each criterion is taught</h2>"""]
    for d in days:
        out.append(f'      <h3 id="{esc(d["dayId"])}">{_day_heading(d)}</h3>')
        rows = by_day[d["dayId"]]
        if rows:
            out.append("      <ul>")
            for c in rows:
                out.append(f'        <li><a href="#{esc(c["id"])}">{esc(c["id"])}</a> {tier_pill(c["tier"])} {esc(c["text"])}</li>')
            out.append("      </ul>")
        else:
            out.append("      <p>No criteria mapped to this day yet.</p>")
    out.append("    </section>")
    for sec in group["sections"]:
        out.append(f"""
    <section class="step" id="{esc(sec["slug"])}">
      <div class="tag">Section</div>
      <h2>{esc(sec["name"])}</h2>
      <table class="ec-table">
        <thead><tr><th>Done</th><th>ID</th><th>Tier</th><th>Criterion</th><th>Covered on</th></tr></thead>
        <tbody>""")
        for c in sec["criteria"]:
            cells = []
            for cv in cover.get(c["id"], []):
                if cv["live"]:
                    cells.append(f'<a href="../weeks/{esc(cv["rel"])}.html">{_short_day(cv)}</a>')
                else:
                    cells.append(f'<span class="ec-soon">{_short_day(cv)}</span>')
            covered = ", ".join(cells) if cells else "—"
            out.append(f'          <tr id="{esc(c["id"])}">'
                       f'<td><input type="checkbox" data-ec="{esc(c["id"])}" aria-label="Done: {esc(c["id"])}"></td>'
                       f'<td><code>{esc(c["id"])}</code></td>'
                       f'<td>{tier_pill(c["tier"])}</td>'
                       f'<td>{esc(c["text"])}</td>'
                       f'<td>{covered}</td></tr>')
        out.append("        </tbody>\n      </table>\n    </section>")
    body = "\n".join(out)
    script = f"""<script>
(function () {{
  var KEY = "tc_exit_{gid}";
  var state = {{}};
  try {{ state = JSON.parse(localStorage.getItem(KEY) || "{{}}") || {{}}; }} catch (e) {{ state = {{}}; }}
  var boxes = Array.prototype.slice.call(document.querySelectorAll("input[data-ec]"));
  function save() {{ try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch (e) {{}} }}
  function paint() {{
    var n = 0;
    boxes.forEach(function (b) {{ var on = !!state[b.getAttribute("data-ec")]; b.checked = on; var tr = b.closest("tr"); if (tr) tr.classList.toggle("ec-done", on); if (on) n++; }});
    var c = document.getElementById("ec-count"); if (c) c.textContent = n + " of " + boxes.length + " ticked";
  }}
  boxes.forEach(function (b) {{ b.addEventListener("change", function () {{ var id = b.getAttribute("data-ec"); if (b.checked) state[id] = 1; else delete state[id]; save(); paint(); }}); }});
  var r = document.getElementById("ec-reset"); if (r) r.addEventListener("click", function () {{ state = {{}}; save(); paint(); }});
  paint();
}})();
</script>
"""
    return _shell(f"{group['label']} exit criteria", body, cfg, v) + script + "</body>\n</html>\n"


# ---------------------------------------------------------------- build / check
def expected(cur: dict | None = None, root: Path = ROOT) -> dict[Path, str]:
    """Every file docs/exit-criteria/ should hold, with its content."""
    cur = cur or bi.load_curriculum()
    cfg = load_config()
    v = version()
    out_dir = root / "docs" / "exit-criteria"
    groups = ec.load_groups(cur)
    files = {out_dir / "index.html": render_index(groups, cfg, v) + "</body>\n</html>\n"}
    for g in groups:
        if g["exists"]:
            files[out_dir / f"{Path(g['source']).stem}.html"] = render_group(g, coverage(g, cur), cfg, cur, v)
    return files


def check(root: Path = ROOT) -> list[str]:
    """Stale or unexpected pages under docs/exit-criteria/, one per line."""
    problems = []
    want = expected(root=root)
    for path, text in want.items():
        rel = path.relative_to(root).as_posix()
        if not path.is_file():
            problems.append(f"{rel} is missing")
        elif path.read_text(encoding="utf-8") != text:
            problems.append(f"{rel} is stale")
    out_dir = root / "docs" / "exit-criteria"
    if out_dir.is_dir():
        for p in sorted(out_dir.glob("*.html")):
            if p not in want:
                problems.append(f"{p.relative_to(root).as_posix()} is not a generated page (delete it)")
    return problems


def build(quiet: bool = False, root: Path = ROOT) -> bool:
    """Write the pages; True when anything changed."""
    changed = False
    want = expected(root=root)
    out_dir = root / "docs" / "exit-criteria"
    out_dir.mkdir(parents=True, exist_ok=True)
    for path, text in want.items():
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        changed = True
        if not quiet:
            print(f"wrote {path.relative_to(root).as_posix()}")
    for p in sorted(out_dir.glob("*.html")):
        if p not in want:
            p.unlink()
            changed = True
            if not quiet:
                print(f"removed {p.relative_to(root).as_posix()}")
    return changed


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if "--check" in argv:
        problems = check()
        for p in problems:
            print(f"{p} — run: python harness/build_exit_pages.py", file=sys.stderr)
        if problems:
            return 1
        print("docs/exit-criteria in sync")
        return 0
    if build():
        print("docs/exit-criteria updated")
    else:
        print("docs/exit-criteria already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
