#!/usr/bin/env python3
"""Prose-only guard for the trainer's delivery files (demo scripts, runbooks; D-0039) and for notes pages
(D-0040). Stdlib only.

A humanizer pass may reword what the trainer reads and says, or what a learner reads. It must not change what a
demo types, what the checkers parse or what the tests read. This script compares a file with an earlier version
of itself and fails when anything other than prose moved.

Markdown (demo script, runbook): fenced blocks (content, order, and the section each one sits in), heading
  lines, the header block (a script's title and header bullets; a runbook's title, date line and links line),
  cwd: lines, tables (a runbook's rows; a script's header and separator rows and its row count), bold labels,
  inline code spans, URLs, and the number of bullets and numbered items.
HTML (a notes page, .html): the tag skeleton (every tag with its attributes, in order: ids, classes, hrefs,
  data-*), every <pre>/<code> content, headings (h1-h4, title), the .tag / .callout .k / .meta labels,
  citation markers (sup.cite), URLs, and the inline scripts with their prose string literals masked (quiz
  stem/options/explain/hint/model, diagram captions and node detail may be reworded; answers, pairs, types,
  labels, ids, NEXT may not).

Numbers that changed outside code are printed as a warning to read by hand.

Usage (from the repo root):
  python harness/prose_guard.py snapshot <file> [<file> ...]         copy the files aside, print the snapshot dir
  python harness/prose_guard.py check <snapshot dir> <file> [...]     compare with that snapshot
  python harness/prose_guard.py git <file> [...]                      compare with the committed version (HEAD of
                                                                      the repository that holds the file)
Exit 1 on a hard finding.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

FENCE_RE = re.compile(r"^```[^\n`]*\n.*?^```\s*$", re.M | re.S)
CODE_RE = re.compile(r"`[^`\n]+`")
BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
BULLET_RE = re.compile(r"^\s*(- |\d+\. )")
RUNBOOK_HEAD_RE = re.compile(r"^(# |Week \d|Notes page:)")
MANIFEST = "manifest.json"
ORDERED = ("fenced blocks", "fence sections", "headings", "header block", "cwd lines")


def is_script(path: Path | str) -> bool:
    """A demo script lives in a demos/ folder; everything else is treated as a runbook."""
    return "/demos/" in Path(path).as_posix()


def is_html(path: Path | str) -> bool:
    """A notes page (D-0040) is judged by its tag skeleton, not by Markdown rules."""
    return Path(path).suffix.lower() in (".html", ".htm")


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n")


# ---------------------------------------------------------------- HTML (notes pages, D-0040)
JS_STR = r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''
JS_PROSE_KEYS = ("stem", "explain", "hint", "model", "detail")
JS_PROSE_ARRAYS = ("options", "captions")


def _mask_js_prose(js: str) -> str:
    """Replace the prose string literals of window.QUIZ / window.DIAGRAM with "<P>" so a reword is not a change
    while their count, order and every other literal (answers, pairs, labels, ids, NEXT) stay frozen."""
    out = re.sub(r"\b(" + "|".join(JS_PROSE_KEYS) + r")\s*:\s*(" + JS_STR + ")", r'\1:"<P>"', js)
    for key in JS_PROSE_ARRAYS:
        out = re.sub(r"\b" + key + r"\s*:\s*\[(.*?)\]", lambda m, k=key: k + ":[" + re.sub(JS_STR, '"<P>"', m.group(1)) + "]", out, flags=re.S)
    return out


def parts_html(text: str) -> tuple[dict[str, list[str]], list[str]]:
    import notes_check as nc  # local import: harness/ is on sys.path when run as a script or from the tests

    root = nc.parse_html(_norm(text))
    skeleton: list[str] = []
    code: list[str] = []
    headings: list[str] = []
    labels: list[str] = []
    cites: list[str] = []
    scripts: list[str] = []

    def walk(el: nc.Element, parent_classes: set[str]) -> None:
        for c in el.children:
            if not isinstance(c, nc.Element):
                continue
            attrs = " ".join(f'{k}="{v}"' for k, v in c.attrs.items())
            skeleton.append(f"<{c.tag}{(' ' + attrs) if attrs else ''}>")
            cls = c.classes()
            if c.tag in ("pre", "code"):
                code.append(c.text())
            if c.tag in ("h1", "h2", "h3", "h4", "title"):
                headings.append(f"{c.tag}: {c.text().strip()}")
            if "tag" in cls or ("k" in cls and "callout" in parent_classes) or (c.tag == "span" and "meta" in parent_classes):
                labels.append(c.text().strip())
            if c.tag == "sup" and "cite" in cls:
                cites.append(c.text().strip())
            if c.tag == "script" and not c.attrs.get("src"):
                scripts.append(_mask_js_prose(c.text()))
            walk(c, cls)
            if c.tag not in nc.VOID_TAGS:
                skeleton.append(f"</{c.tag}>")

    walk(root, set())
    return {
        "tag skeleton": skeleton,
        "code blocks": code,
        "headings": headings,
        "labels": labels,
        "citations": cites,
        "scripts": scripts,
        "urls": URL_RE.findall(_norm(text)),
    }, NUM_RE.findall(nc.prose_text(root))


def parts(text: str, script: bool) -> tuple[dict[str, list[str]], list[str]]:
    text = _norm(text)
    fences = FENCE_RE.findall(text)
    bare = FENCE_RE.sub("\n<<FENCE>>\n", text)
    lines = bare.split("\n")
    first_section = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), len(lines))
    tables = [ln for ln in lines if ln.startswith("|")]
    seps = [i for i, ln in enumerate(lines) if ln.startswith("|") and set(ln) <= set("|-: ")]
    frozen_rows = tables if not script else [lines[j] for i in seps for j in (i - 1, i) if j >= 0 and lines[j].startswith("|")]
    return {
        "fenced blocks": fences,
        "fence sections": [str(sum(1 for ln in lines[:i] if ln.startswith("## "))) for i, ln in enumerate(lines) if ln == "<<FENCE>>"],
        "headings": [ln for ln in lines if ln.startswith("#")],
        "header block": lines[:first_section] if script else [ln for ln in lines[:first_section] if RUNBOOK_HEAD_RE.match(ln)],
        "cwd lines": [ln for ln in lines if ln.startswith("cwd:")],
        "table rows": frozen_rows,
        "table row count": [str(len(tables))],
        "bold labels": BOLD_RE.findall(bare),
        "inline code": CODE_RE.findall(bare),
        "urls": URL_RE.findall(bare),
        "bullet count": [str(sum(1 for ln in lines if BULLET_RE.match(ln)))],
    }, NUM_RE.findall(CODE_RE.sub("", bare))


def _diff(before: list[str], after: list[str]) -> tuple[list[str], list[str]]:
    b, a = Counter(before), Counter(after)
    return sorted((b - a).elements()), sorted((a - b).elements())


def compare(old: str, new: str, script: bool, html: bool = False) -> tuple[list[str], list[str]]:
    """Return (hard findings, warnings) for one file."""
    if html:
        try:
            (old_parts, old_nums), (new_parts, new_nums) = parts_html(old), parts_html(new)
        except ValueError as exc:
            return [f"page does not parse: {exc}"], []
        ordered = set(old_parts)   # every HTML part is order-sensitive
    else:
        (old_parts, old_nums), (new_parts, new_nums) = parts(old, script), parts(new, script)
        ordered = set(ORDERED)
    findings: list[str] = []
    for name, before in old_parts.items():
        after = new_parts[name]
        if name in ordered and before == after:
            continue
        gone, added = _diff(before, after)
        if name in ordered and not gone and not added:
            findings.append(f"{name}: same items in a different order")
        elif gone or added:
            findings.append(f"{name}: removed {[g[:90] for g in gone][:6]} added {[x[:90] for x in added][:6]}")
    gone, added = _diff(old_nums, new_nums)
    warnings = [f"numbers outside code changed: removed {gone[:12]} added {added[:12]}"] if gone or added else []
    return findings, warnings


def head_text(path: Path) -> str:
    top = subprocess.run(["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
    rel = path.resolve().relative_to(Path(top).resolve()).as_posix()
    return subprocess.run(["git", "-C", top, "show", f"HEAD:{rel}"], capture_output=True, check=True).stdout.decode("utf-8")


def snapshot(files: list[str]) -> Path:
    snap = Path(tempfile.mkdtemp(prefix="prose-guard-"))
    manifest = {}
    for i, f in enumerate(files):
        src = Path(f).resolve()
        copy = f"{i:03d}_{src.name}"
        shutil.copyfile(src, snap / copy)
        manifest[src.as_posix()] = copy
    (snap / MANIFEST).write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return snap


def report(files: list[str], baseline) -> int:
    bad = False
    for f in files:
        path = Path(f)
        new = path.read_text(encoding="utf-8")
        try:
            old = baseline(path)
        except (KeyError, OSError, subprocess.CalledProcessError) as exc:
            bad = True
            print(f"FAIL {f}\n  no earlier version to compare with ({exc.__class__.__name__})")
            continue
        if _norm(old) == _norm(new):
            print(f"UNCHANGED {f}")
            continue
        findings, warnings = compare(old, new, is_script(path), is_html(path))
        print(("FAIL " if findings else "OK ") + f)
        for line in findings:
            print("  " + line)
        for line in warnings:
            print("  WARN " + line)
        bad = bad or bool(findings)
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "snapshot":
        print(snapshot(argv[1:]).as_posix())
        return 0
    if len(argv) >= 3 and argv[0] == "check":
        snap = Path(argv[1])
        manifest = json.loads((snap / MANIFEST).read_text(encoding="utf-8"))
        return report(argv[2:], lambda p: (snap / manifest[p.resolve().as_posix()]).read_text(encoding="utf-8"))
    if len(argv) >= 2 and argv[0] == "git":
        return report(argv[1:], head_text)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
