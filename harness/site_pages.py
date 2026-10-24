#!/usr/bin/env python3
"""Shared page shell for the generated site sections (exit criteria, projects).

Every generated section under docs/<dir>/ shares the same chrome: skip link, topbar with the brand,
Home, Demos and one topnav per section in SECTIONS, an empty .topbar-right, the main/article
wrappers and the footer. The generators (build_exit_pages.py, build_projects.py) hand `shell()` their
body and page-local CSS and append their own script and closing tags.

`check_dir()` / `build_dir()` are the generic sync test and writer for a directory of generated pages:
the generator computes `want` (path -> content) and these compare or write it.

Stdlib only.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

ROOT = bi.ROOT

# (key, label, directory under docs/) — the topnav order on every generated section page.
SECTIONS = [("exit", "Exit criteria", "exit-criteria"), ("projects", "Projects", "projects")]

_V_RE = re.compile(r'style\.css\?v=([^"]+)')
_VJS_RE = re.compile(r'theme\.js\?v=([^"]+)')


def load_config() -> dict:
    return json.loads((ROOT / "harness" / "config.json").read_text(encoding="utf-8"))


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def version() -> str:
    """The `?v=` value docs/index.html uses for style.css (bump-css.sh rewrites every page the same way)."""
    m = _V_RE.search(bi.INDEX.read_text(encoding="utf-8"))
    return m.group(1) if m else "1"


def js_version() -> str:
    """The `?v=` value docs/index.html uses for theme.js (bump-css.sh without --all leaves it alone)."""
    m = _VJS_RE.search(bi.INDEX.read_text(encoding="utf-8"))
    return m.group(1) if m else version()


def _section_nav(active: str) -> str:
    lines = []
    for key, label, d in SECTIONS:
        href = "index.html" if key == active else f"../{d}/index.html"
        lines.append(f'    <a class="topnav" href="{esc(href)}">{esc(label)}</a>')
    return "\n".join(lines)


def shell(title: str, body: str, cfg: dict, v: str, *, active: str, extra_css: str,
          main_class: str, article_class: str) -> str:
    """The page chrome around `body` for a page under docs/<section dir>/.

    `active` is the SECTIONS key of the section the page belongs to (its topnav links "index.html",
    every other section links "../<dir>/index.html"). Does NOT close </body></html>: the caller
    appends its script, then the closing tags.
    """
    site = cfg.get("siteTitle", "")
    brand = cfg.get("brand", {}) or {}
    demo = ((cfg.get("demoRepo") or {}).get("url") or "").rstrip("/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | {esc(site)}</title>
<link rel="stylesheet" href="../assets/css/style.css?v={esc(v)}">
<script src="../assets/js/theme.js?v={esc(js_version())}"></script>
<style>{extra_css}</style>
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
{_section_nav(active)}
  </nav>
  <div class="topbar-right"></div>
</div>

<main class="lesson2 {esc(main_class)}" id="reading-main">
  <article class="reading-col {esc(article_class)}">
{body}
  </article>
</main>

<footer class="foot">{esc(site)} Developer Training</footer>
"""


# ---------------------------------------------------------------- build / check
def check_dir(want: dict[Path, str], out_dir: Path, root: Path, rebuild_cmd: str) -> list[str]:
    """Stale, missing or unexpected *.html under `out_dir`, one problem per line.

    The lines carry no "run: ..." hint: the callers (each generator's main(), build_index.py --check,
    drift_check.py) add their own. `rebuild_cmd` is kept for the callers' hint text only.
    """
    problems = []
    for path, text in want.items():
        rel = path.relative_to(root).as_posix()
        if not path.is_file():
            problems.append(f"{rel} is missing")
        elif path.read_text(encoding="utf-8") != text:
            problems.append(f"{rel} is stale")
    if out_dir.is_dir():
        for p in sorted(out_dir.glob("*.html")):
            if p not in want:
                problems.append(f"{p.relative_to(root).as_posix()} is not a generated page (delete it)")
    return problems


def build_dir(want: dict[Path, str], out_dir: Path, root: Path, quiet: bool = False) -> bool:
    """Write `want` under `out_dir`, remove any other *.html there; True when anything changed."""
    changed = False
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
