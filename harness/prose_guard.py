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

HTML --restructure (D-0060, the readability pass on a live page): as html mode, but inside a section.step's own
  prose (not section.practice, callouts, details, widgets or <pre>) plain <p>/<ul>/<ol>/<li>/<table> rows and
  cells may be added, removed, split or reordered and a <div class="recap"> (label "Takeaways") may be added;
  inline elements, inline <code> text and citation markers must survive per step as the same multiset; numbers in
  step prose are a hard finding; each step keeps -8%..+15% (or +90) of its prose words and the page stays inside
  metrics.notes wordMin..wordMax; the "~N min" meta span may change. A citation that changed order is a warning.

Usage (from the repo root):
  python harness/prose_guard.py snapshot <file> [<file> ...]         copy the files aside, print the snapshot dir
  python harness/prose_guard.py check [--restructure] <snapshot dir> <file> [...]     compare with that snapshot
  python harness/prose_guard.py git [--restructure] <file> [...]      compare with the committed version (HEAD of
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
BULLET_RE = re.compile(r"^\s*(?:> )?(- |\d+\. )")
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


# Restructure mode (D-0060): inside a teaching step's own prose these tags may be added, removed, split or
# reordered (a paragraph split in two, an enumeration turned into a list or table, a Takeaways recap added).
RELAX_TAGS = {"p", "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td", "br"}
RELAX_INLINE = {"code", "sup", "a", "em", "strong", "b", "i", "span", "kbd"}
RECAP_LABEL_RE = re.compile(r"~\d+ min")
RECAP_LABEL = "Takeaways"           # metrics.notes.prose.recapLabel; notes_check.py --style checks the same string


def parts_html(text: str, mode: str = "html") -> tuple[dict[str, list[str]], list[str]]:
    """mode "html": everything but prose is frozen, in order. mode "restructure": the same, except that inside a
    section.step (not inside section.practice, a callout, a details block, a widget or a <pre>) the RELAX_TAGS
    without attributes and div.recap may change, inline elements and citation markers are compared per step as a
    multiset, inline <code> text is compared per step as a multiset, numbers in step prose are a hard finding, the
    "~N min" meta span is masked (recaps add words), and "step words" / "page words" carry the word deltas."""
    import notes_check as nc  # local import: harness/ is on sys.path when run as a script or from the tests

    relax = mode == "restructure"
    root = nc.parse_html(_norm(text))
    skeleton: list[str] = []
    code: list[str] = []
    headings: list[str] = []
    labels: list[str] = []
    cites: list[str] = []
    cite_order: list[str] = []
    scripts: list[str] = []
    step_inline: list[str] = []
    inline_code: list[str] = []
    step_words: list[str] = []
    step_nums: list[str] = []
    recap_labels: list[str] = []      # restructure mode: recap labels that are NOT the expected one (any is a finding)

    def walk(el: nc.Element, parent_classes: set[str], step: str | None, frozen: bool) -> None:
        for c in el.children:
            if not isinstance(c, nc.Element):
                continue
            cls = c.classes()
            attrs = " ".join(f'{k}="{v}"' for k, v in c.attrs.items())
            open_tag = f"<{c.tag}{(' ' + attrs) if attrs else ''}>"
            c_step = step
            if c.tag == "section" and "step" in cls:
                c_step = c.attrs.get("data-step") or "?"
                step_words.append(f"{c_step}:{len(nc.prose_text(c).split())}")
                step_nums.extend(f"{c_step}:{n}" for n in NUM_RE.findall(nc.prose_text(c)))
            check_step = c.tag == "section" and "step" in cls and (c.find(class_name="tag").text().strip().lower() == nc.CHECK_TAG if c.find(class_name="tag") else False)
            c_frozen = frozen or check_step or (c.tag == "section" and "practice" in cls) or "callout" in cls or c.tag in ("details", "pre", "script") \
                or any(k.startswith("ix-") for k in cls)
            relaxed = relax and c_step is not None and not c_frozen
            is_recap = c.tag == "div" and c.attrs == {"class": "recap"}
            is_recap_k = c.tag == "div" and c.attrs == {"class": "k"} and "recap" in parent_classes
            dropped = False
            if relaxed and ((c.tag in RELAX_TAGS and not c.attrs) or is_recap or is_recap_k):
                dropped = True
            elif relaxed and c.tag in RELAX_INLINE:
                step_inline.append(f"{c_step}:{open_tag}")
                dropped = True
            else:
                skeleton.append(open_tag)
            if c.tag == "pre":
                code.append(c.text())
            elif c.tag == "code":
                (inline_code if relaxed else code).append(f"{c_step}:{c.text()}" if relaxed else c.text())
            if c.tag in ("h1", "h2", "h3", "h4", "title"):
                headings.append(f"{c.tag}: {c.text().strip()}")
            if relaxed and is_recap_k:
                # a recap may be ADDED by the pass, so its label is not frozen; it must still read exactly RECAP_LABEL
                if c.text().strip() != RECAP_LABEL:
                    recap_labels.append(c.text().strip())
            elif "tag" in cls or ("k" in cls and ("callout" in parent_classes or "recap" in parent_classes)) or (c.tag == "span" and "meta" in parent_classes):
                txt = c.text().strip()
                if relax and "meta" in parent_classes:
                    txt = RECAP_LABEL_RE.sub("~N min", txt)
                labels.append(txt)
            if c.tag == "sup" and "cite" in cls:
                txt = c.text().strip()
                cites.append(f"{c_step}:{txt}" if relaxed else txt)
                cite_order.append(txt)
            if c.tag == "script" and not c.attrs.get("src"):
                scripts.append(_mask_js_prose(c.text()))
            walk(c, cls, c_step, c_frozen)
            if not dropped and c.tag not in nc.VOID_TAGS:
                skeleton.append(f"</{c.tag}>")

    walk(root, set(), None, False)
    all_nums = NUM_RE.findall(RECAP_LABEL_RE.sub("~N min", nc.prose_text(root)) if relax else nc.prose_text(root))
    parts: dict[str, list[str]] = {
        "tag skeleton": skeleton,
        "code blocks": code,
        "headings": headings,
        "labels": labels,
        "citations": cites,
        "scripts": scripts,
        "urls": URL_RE.findall(_norm(text)),
    }
    if not relax:
        return parts, all_nums
    in_steps = Counter(n.split(":", 1)[1] for n in step_nums)
    outside = list((Counter(all_nums) - in_steps).elements())
    parts.update({
        "step inline": step_inline,
        "inline code": inline_code,
        "numbers in steps": step_nums,
        "recap labels": recap_labels,
        "citation order": cite_order,
        "step words": step_words,
        "page words": [str(len(nc.prose_text(root).split()))],
    })
    return parts, outside


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


STEP_WORDS_SHRINK = 0.92        # restructure mode: a step may lose at most 8% of its prose words ...
STEP_WORDS_GROW = 0.15          # ... and gain at most 15% or 90 words, whichever is more (the recap)
STEP_WORDS_GROW_MIN = 90
UNORDERED_RESTRUCTURE = {"step inline", "inline code", "numbers in steps", "citations", "recap labels"}


def _word_deltas(before: list[str], after: list[str], band: tuple[int, int] | None, page_before: list[str], page_after: list[str]) -> list[str]:
    old = dict(s.split(":", 1) for s in before)
    new = dict(s.split(":", 1) for s in after)
    f = []
    for step, ow in old.items():
        ow_i, nw_i = int(ow), int(new.get(step, 0))
        lo, hi = int(ow_i * STEP_WORDS_SHRINK), ow_i + max(int(ow_i * STEP_WORDS_GROW), STEP_WORDS_GROW_MIN)
        if not (lo <= nw_i <= hi):
            f.append(f"step {step} words: {ow_i} -> {nw_i}, allowed {lo}..{hi} (at most -8%, at most +15% or +90)")
    if band and page_after:
        total = int(page_after[0])
        if not (band[0] <= total <= band[1]):
            f.append(f"page words: {page_before[0]} -> {total}, outside {band[0]}..{band[1]}")
    return f


def compare(old: str, new: str, script: bool, html: bool = False, mode: str = "html", band: tuple[int, int] | None = None) -> tuple[list[str], list[str]]:
    """Return (hard findings, warnings) for one file. mode applies to HTML only ("html" | "restructure", D-0060);
    band = (wordMin, wordMax) keeps a restructured page inside the notes word band (None skips it)."""
    warnings: list[str] = []
    if html:
        try:
            (old_parts, old_nums), (new_parts, new_nums) = parts_html(old, mode), parts_html(new, mode)
        except ValueError as exc:
            return [f"page does not parse: {exc}"], []
        ordered = set(old_parts) - (UNORDERED_RESTRUCTURE if mode == "restructure" else set())
        if mode == "restructure":
            sw_old, sw_new = old_parts.pop("step words"), new_parts.pop("step words")
            pw_old, pw_new = old_parts.pop("page words"), new_parts.pop("page words")
            co_old, co_new = old_parts.pop("citation order"), new_parts.pop("citation order")
            if co_old != co_new and Counter(co_old) == Counter(co_new):
                warnings.append("citation order changed inside a step: read the moved sentences by hand")
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
    if html and mode == "restructure":
        findings += _word_deltas(sw_old, sw_new, band, pw_old, pw_new)
    gone, added = _diff(old_nums, new_nums)
    if gone or added:
        warnings.append(f"numbers outside code changed: removed {gone[:12]} added {added[:12]}")
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


def word_band() -> tuple[int, int] | None:
    """metrics.notes wordMin..wordMax for the restructure mode's page total (None when metrics.json is absent)."""
    try:
        import notes_check as nc
        m = nc.metrics()
        return (m["wordMin"], m["wordMax"])
    except (OSError, KeyError, ValueError):
        return None


def report(files: list[str], baseline, mode: str = "html") -> int:
    bad = False
    band = word_band() if mode == "restructure" else None
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
        findings, warnings = compare(old, new, is_script(path), is_html(path), mode, band)
        print(("FAIL " if findings else "OK ") + f)
        for line in findings:
            print("  " + line)
        for line in warnings:
            print("  WARN " + line)
        bad = bad or bool(findings)
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    flags = {a for a in argv if a.startswith("--")}
    argv = [a for a in argv if not a.startswith("--")]
    mode = "restructure" if "--restructure" in flags else "html"
    if len(argv) >= 2 and argv[0] == "snapshot":
        print(snapshot(argv[1:]).as_posix())
        return 0
    if len(argv) >= 3 and argv[0] == "check":
        snap = Path(argv[1])
        manifest = json.loads((snap / MANIFEST).read_text(encoding="utf-8"))
        return report(argv[2:], lambda p: (snap / manifest[p.resolve().as_posix()]).read_text(encoding="utf-8"), mode)
    if len(argv) >= 2 and argv[0] == "git":
        return report(argv[1:], head_text, mode)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
