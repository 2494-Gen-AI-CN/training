#!/usr/bin/env python3
"""Format check for the demo notebooks of `demoFormat: "notebook"` days (D-0085), and the path rule they live by.

A notebook day's demo is ONE prepared Jupyter notebook in the demo repo (config.json `demoRepo`, cloned at
`demoRepo.localDir`) on `main`, at `notebooks/week-WW/NN_<weekday>_<slug>.ipynb` (NN = the weekday slot 01..05,
weekday lowercase English, slug lowercase words joined by underscores). The trainer runs it live in Google Colab
cell by cell. The style reference is the substitute trainer's demo-repo/notebooks/week-06/02_tuesday_trees_and_clustering.ipynb;
the rules below are derived from it (it passes unchanged) and the style guide is harness/templates/notebook-style.md.

FORMAT check only (the notebook is not run here; Colab is its runtime, not the course Python):
  - valid JSON, nbformat 4
  - the file name matches the path rule (and the folder is notebooks/week-WW/)
  - the first cell is markdown, starts with "# " and carries a numbered agenda (>= 3 "1. ..." lines)
  - the second cell is a code cell (the setup / helpers cell: imports, RANDOM_STATE, plotting helpers)
  - at least 3 "## " sections besides "## Recap"
  - the trailing markdown cell(s) carry "## Recap" and a "Quick check" block with >= 4 numbered questions
  - no code cell has stored outputs or an execution count (nothing run is committed)
  - no "!pip install" / "%pip install" of tensorflow, keras or scikit-learn (Colab ships them)
  - every code cell except the setup cell is at most CODE_LINES_MAX lines

The study layer (D-0105; what lets a learner work through the notebook alone). A notebook declares it by carrying
the line "**Studying on your own**" in its title cell; `--study` fails a notebook that does not declare it. Once
declared, the rules are:
  - the title cell's study block links the day's notes page (a markdown link)
  - every numbered "## N. " section carries at least one "**Predict first:**" question
  - every numbered "## N. " section ends with a "**Before you move on**" checkpoint
  - every <details> block is closed and has a <summary> (same counts per markdown cell)
  - the Quick check is followed by a <details> block with at least one numbered answer per question

Usage:
    python harness/notebook_check.py demo-repo/notebooks/week-06/02_tuesday_trees_and_clustering.ipynb
    python harness/notebook_check.py demo-repo/notebooks/week-06          # every .ipynb in the folder
    python harness/notebook_check.py demo-repo/notebooks/week-07 --study  # and each must carry the study layer
Exit 1 with one problem per line when anything fails; exit 0 and "OK" otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday")
NAME_RE = re.compile(r"^(0[1-5])_(monday|tuesday|wednesday|thursday|friday)_([a-z0-9]+(?:_[a-z0-9]+)*)\.ipynb$")
WEEK_DIR_RE = re.compile(r"^week-\d{2}$")
HEADING_RE = re.compile(r"^(#{1,3}) (.+?)\s*$")
NUMBERED_RE = re.compile(r"^\s*\d+\.\s+\S")
PIP_RE = re.compile(r"^\s*[!%]pip\s+install\b.*\b(tensorflow|keras|scikit-learn|sklearn)\b", re.I)
CODE_LINES_MAX = 40
SECTIONS_MIN = 3
AGENDA_MIN = 3
QUICK_CHECK_MIN = 4
STUDY_MARKER = "**Studying on your own**"
PREDICT_MARK = "**Predict first:**"
CHECKPOINT_MARK = "**Before you move on**"
NUMBERED_SECTION_RE = re.compile(r"^## \d+\. ")
MD_LINK_RE = re.compile(r"\]\(https?://")


# ---------------------------------------------------------------- the path rule
def demo_repo_dir(root: Path = ROOT) -> Path:
    cfg = json.loads((root / "harness" / "config.json").read_text(encoding="utf-8"))
    return root / cfg["demoRepo"]["localDir"]


def day_prefix(day_no: int) -> str:
    """'02_tuesday' for weekday slot 2."""
    return f"{day_no:02d}_{WEEKDAYS[day_no - 1]}"


def default_name(day_no: int, slug: str) -> str:
    """The file name a notebook day gets when none is on disk yet: the day slug without 'day-N-', hyphens -> underscores."""
    stem = re.sub(r"^day-\d+-", "", slug).replace("-", "_")
    return f"{day_prefix(day_no)}_{stem}.ipynb"


def notebook_rel(week_no: int, day_no: int, slug: str, root: Path = ROOT) -> str:
    """The day's notebook path inside the demo repo: the file on disk whose name starts with NN_<weekday>_ (the
    sorted first when several do), else the default name. The slug part is free: W6D2's is the substitute's own."""
    folder = f"notebooks/week-{week_no:02d}"
    d = demo_repo_dir(root) / folder
    hits = sorted(d.glob(f"{day_prefix(day_no)}_*.ipynb")) if d.is_dir() else []
    return f"{folder}/{hits[0].name if hits else default_name(day_no, slug)}"


def outline(path: Path) -> list[str]:
    """The '#', '##' and '###' headings of the notebook's markdown cells, in order (fenced blocks skipped)."""
    nb = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "markdown":
            continue
        fenced = False
        for ln in _src(c).splitlines():
            if ln.lstrip().startswith("```"):
                fenced = not fenced
                continue
            m = None if fenced else HEADING_RE.match(ln)
            if m:
                out.append(f"{m.group(1)} {m.group(2)}")
    return out


def notebook_for(week_no: int, day_no: int, slug: str, root: Path = ROOT) -> dict:
    """What args_for.py passes for a notebook day: {path (inside the demo repo), exists, outline}."""
    rel = notebook_rel(week_no, day_no, slug, root)
    f = demo_repo_dir(root) / rel
    exists = f.is_file()
    try:
        heads = outline(f) if exists else []
    except (ValueError, OSError):
        heads = []
    return {"path": rel, "exists": exists, "outline": heads}


# ---------------------------------------------------------------- the format check
def _src(cell: dict) -> str:
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else str(s)


def _tail_text(cells: list[dict]) -> str:
    """The trailing markdown cell(s), joined."""
    tail = []
    for c in reversed(cells):
        if c.get("cell_type") != "markdown":
            break
        tail.insert(0, _src(c))
    return "\n".join(tail)


def has_study_layer(cells: list[dict]) -> bool:
    """True when the title cell declares the study layer (D-0105)."""
    return bool(cells) and cells[0].get("cell_type") == "markdown" and STUDY_MARKER in _src(cells[0])


def study_problems(name: str, cells: list[dict]) -> list[str]:
    """The study-layer rules (D-0105) for a notebook that declares the layer."""
    p: list[str] = []
    if not MD_LINK_RE.search(_src(cells[0])):
        p.append(f"{name}: the title cell's study block must link the day's notes page")
    sections: list[dict] = []          # one per numbered '## N. ' section, in order
    current = None
    for i, c in enumerate(cells):
        if c.get("cell_type") != "markdown":
            continue
        text = _src(c)
        opened, closed, summaries = text.count("<details"), text.count("</details>"), text.count("<summary")
        if not (opened == closed == summaries):
            p.append(f"{name}: cell {i} has unbalanced <details> blocks ({opened} opened, {closed} closed, {summaries} <summary>)")
        fenced = False
        for ln in text.splitlines():
            if ln.lstrip().startswith("```"):
                fenced = not fenced
                continue
            if fenced:
                continue
            if ln.startswith("## "):
                current = {"head": ln.strip(), "predict": False, "checkpoint": False} if NUMBERED_SECTION_RE.match(ln) else None
                if current:
                    sections.append(current)
                continue
            if current:
                current["predict"] = current["predict"] or PREDICT_MARK in ln
                current["checkpoint"] = current["checkpoint"] or CHECKPOINT_MARK in ln
    for sec in sections:
        if not sec["predict"]:
            p.append(f"{name}: section '{sec['head']}' has no '{PREDICT_MARK}' question")
        if not sec["checkpoint"]:
            p.append(f"{name}: section '{sec['head']}' has no '{CHECKPOINT_MARK}' checkpoint")
    tail_text = _tail_text(cells)
    qc = re.search(r"Quick check", tail_text)
    if qc:
        questions, sep, answers = tail_text[qc.end():].partition("<details")
        n_q = sum(1 for ln in questions.splitlines() if NUMBERED_RE.match(ln))
        n_a = sum(1 for ln in answers.splitlines() if NUMBERED_RE.match(ln))
        if not sep:
            p.append(f"{name}: the Quick check needs its answers in a <details> block after the questions")
        elif n_a < n_q:
            p.append(f"{name}: the Quick check has {n_q} questions and {n_a} numbered answers; one answer per question")
    return p


def check(path: Path, study: bool = False) -> list[str]:
    """Every format problem of one notebook. Empty list = OK. `study` also fails a notebook with no study layer;
    a notebook that declares the layer is always held to its rules."""
    name = path.name
    p: list[str] = []
    m = NAME_RE.match(name)
    if not m:
        p.append(f"{name}: file name must read NN_<weekday>_<slug>.ipynb (NN 01..05, weekday lowercase, slug lowercase_words)")
    elif WEEKDAYS.index(m.group(2)) + 1 != int(m.group(1)):
        p.append(f"{name}: {m.group(1)} is not the slot of {m.group(2)} (01 monday .. 05 friday)")
    if not WEEK_DIR_RE.match(path.parent.name) or path.parent.parent.name != "notebooks":
        p.append(f"{name}: must live in notebooks/week-WW/ of the demo repo, found in {path.parent.as_posix()}")
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        return p + [f"{name}: not valid JSON ({e})"]
    if not isinstance(nb, dict) or nb.get("nbformat") != 4 or not isinstance(nb.get("cells"), list):
        return p + [f"{name}: not an nbformat 4 notebook (nbformat {nb.get('nbformat') if isinstance(nb, dict) else '?'})"]
    cells = nb["cells"]
    if len(cells) < 2:
        return p + [f"{name}: needs at least a title cell and a setup cell"]
    first, second = cells[0], cells[1]
    title = _src(first)
    if first.get("cell_type") != "markdown" or not title.startswith("# "):
        p.append(f"{name}: the first cell must be markdown starting with '# <title>'")
    elif sum(1 for ln in title.splitlines() if NUMBERED_RE.match(ln)) < AGENDA_MIN:
        p.append(f"{name}: the title cell needs a numbered agenda (>= {AGENDA_MIN} '1. ...' lines)")
    if second.get("cell_type") != "code" or not _src(second).strip():
        p.append(f"{name}: the second cell must be the code setup cell (imports, RANDOM_STATE, helpers; run once)")
    heads = []
    for c in cells:
        if c.get("cell_type") == "markdown":
            heads += [ln.strip() for ln in _src(c).splitlines() if ln.startswith("## ")]
    sections = [h for h in heads if h != "## Recap"]
    if len(sections) < SECTIONS_MIN:
        p.append(f"{name}: needs >= {SECTIONS_MIN} '## ' sections besides '## Recap', found {len(sections)}")
    tail_text = _tail_text(cells)
    if not re.search(r"^## Recap\s*$", tail_text, re.M):
        p.append(f"{name}: the last markdown cell(s) need a '## Recap' heading")
    qc = re.search(r"Quick check", tail_text)
    if not qc:
        p.append(f"{name}: the last markdown cell(s) need a 'Quick check' block")
    else:
        qs = sum(1 for ln in tail_text[qc.end():].partition("<details")[0].splitlines() if NUMBERED_RE.match(ln))
        if qs < QUICK_CHECK_MIN:
            p.append(f"{name}: the Quick check needs >= {QUICK_CHECK_MIN} numbered questions, found {qs}")
    for i, c in enumerate(cells):
        if c.get("cell_type") != "code":
            continue
        if c.get("outputs"):
            p.append(f"{name}: cell {i} has stored outputs (clear every output before committing)")
        if c.get("execution_count") is not None:
            p.append(f"{name}: cell {i} has an execution count (clear it before committing)")
        lines = _src(c).splitlines()
        for ln in lines:
            if PIP_RE.match(ln):
                p.append(f"{name}: cell {i} pip-installs a package Colab ships ({ln.strip()})")
        if i != 1 and len(lines) > CODE_LINES_MAX:
            p.append(f"{name}: cell {i} has {len(lines)} lines; split it (at most {CODE_LINES_MAX} outside the setup cell)")
    if has_study_layer(cells):
        p += study_problems(name, cells)
    elif study:
        p.append(f"{name}: no study layer (the title cell needs the '{STUDY_MARKER}' block; D-0105)")
    return p


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    study = "--study" in argv
    argv = [a for a in argv if a != "--study"]
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    target = Path(argv[0])
    files = sorted(target.glob("*.ipynb")) if target.is_dir() else [target]
    if not files or not all(f.is_file() for f in files):
        print(f"{target}: no notebook found", file=sys.stderr)
        return 2
    problems = [x for f in files for x in check(f, study=study)]
    for pr in problems:
        print(pr)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
