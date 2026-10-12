#!/usr/bin/env python3
"""Mechanical checks for one day's demo scripts and answer keys (D-0030).

A demo is a walkthrough SCRIPT the trainer types in front of the room
(trainer/<week>/<day>/demos/NN_<slug>.md, format harness/templates/demo-script.md).
The committed code is the ANSWER KEY (trainer/<week>/<day>/demos/key/NN_<slug>.py
or .md transcript), published to demos/<week>/<day>/ only after the day is taught.

Checks (stdlib only; the demos critic and tests/test_demos.py both call this):
  header   - the eleven header bullets, Time = sum of step minutes, Delivery mode enum, Answer key path,
             Thread (thread id or "standalone"), Starts from ("cold" or the previous rung's key path)
  steps    - "## Step n ... (M min)" numbered 1..n, >= 2, every step with a key block states its cwd
  sections - Common pitfalls / What we did NOT cover (intentional) / Wrap-up questions / Sequence pointer
  key      - exists, same NN + slug; .py compiles and fits the line cap (maxLinesPerFile for a standalone
             demo, maxLinesPerThreadKey for a thread rung, whose key is the thread's whole end state);
             key/README.md names every key file
  both-ways- .py key: every ```python line is in the key; every key line is typed in a ```python block OR
             carried from the `Starts from` key (A5, A12); a carried line this rung deletes or rewrites is
             shown in a ```python replaced block; a carried line that is neither replaced nor in the key fails
             (so re-authoring an earlier rung breaks the later ones loudly).
             .md key: the ```bash command sequence equals the transcript's "$ " command sequence, in order.
             A transcript's end state is a repository, not a file: a .py rung that starts from one carries nothing.
  typed cap- python lines + bash commands typed in one rung <= maxTypedLinesPerRung
  bands    - scripts per day and minutes per script within harness/metrics.json demos

Usage:
    python harness/demo_check.py trainer/week-01/day-2-orientation-agile-and-git/demos
Exit 1 with one problem per line when anything fails; exit 0 and "OK" otherwise.
"""
from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "harness" / "metrics.json"

SCRIPT_RE = re.compile(r"^(\d{2})_([a-z0-9]+(?:[-_][a-z0-9]+)*)\.md$")
KEY_RE = re.compile(r"^(\d{2})_([a-z0-9]+(?:[-_][a-z0-9]+)*)\.(py|md|ipynb)$")
HEADER_FIELDS = ["Objective", "Time", "Before the room arrives", "Delivery mode", "Audience",
                 "Prerequisite reading", "Answer key", "Hand-typed files", "Tool-generated files",
                 "Thread", "Starts from"]
DELIVERY_MODES = ("typed", "lecture-over-file")
THREAD_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STARTS_RE = re.compile(r"^trainer/week-\d{2}/day-\d-[a-z0-9-]+/demos/key/\d{2}_[a-z0-9]+(?:[-_][a-z0-9]+)*\.(py|md|ipynb)$")
STEP_RE = re.compile(r"^## Step (\d+)\b.*\((\d+) min\)\s*$", re.M)
REQUIRED_SECTIONS = ["## Common pitfalls", "## What we did NOT cover (intentional)", "## Wrap-up questions", "## Sequence pointer"]
FENCE_RE = re.compile(r"^```([^\n`]*)\n(.*?)^```\s*$", re.M | re.S)
CWD_RE = re.compile(r"^cwd:\s*\S", re.M)


def _fences(text: str) -> list[tuple[str, str]]:
    """[(info string, body)] for every fenced block, in order."""
    return [(m.group(1).strip(), m.group(2)) for m in FENCE_RE.finditer(text)]


def _lines(body: str) -> list[str]:
    return [ln.strip() for ln in body.splitlines() if ln.strip()]


def _header(text: str) -> dict[str, str]:
    head = text.split("\n## ", 1)[0]
    out = {}
    for m in re.finditer(r"^- ([A-Za-z][A-Za-z -]*?):\s*(.*)$", head, re.M):
        out[m.group(1).strip()] = m.group(2).strip()
    return out


def _steps(text: str) -> list[tuple[int, int, str]]:
    """[(n, minutes, section body)] for every '## Step n' heading."""
    heads = list(STEP_RE.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[m.end():end]
        body = body.split("\n## ", 1)[0]  # stop at the next non-step heading
        out.append((int(m.group(1)), int(m.group(2)), body))
    return out


def transcript_commands(text: str) -> list[str]:
    """'$ ' command lines inside ```console blocks of a transcript answer key, in order."""
    cmds = []
    for info, body in _fences(text):
        if info.split()[:1] == ["console"]:
            for ln in body.splitlines():
                if ln.startswith("$ "):
                    cmds.append(ln[2:].strip())
    return cmds


def script_commands(text: str) -> list[str]:
    """Command lines of every ```bash block in a script, in order (comments and blanks dropped)."""
    cmds = []
    for info, body in _fences(text):
        if info.split()[:1] == ["bash"]:
            cmds += [ln for ln in _lines(body) if not ln.startswith("#")]
    return cmds


def script_python_lines(text: str) -> tuple[set[str], set[str]]:
    """(lines in ```python blocks, lines in ```python transient blocks). Replaced blocks are excluded from both."""
    keep, transient = set(), set()
    for info, body in _fences(text):
        parts = info.split()
        if parts[:1] != ["python"] or "replaced" in parts[1:]:
            continue
        (transient if "transient" in parts[1:] else keep).update(_lines(body))
    return keep, transient


def script_replaced_lines(text: str) -> set[str]:
    """Lines in ```python replaced blocks: carried lines this rung deletes or rewrites."""
    out: set[str] = set()
    for info, body in _fences(text):
        parts = info.split()
        if parts[:1] == ["python"] and "replaced" in parts[1:]:
            out.update(_lines(body))
    return out


def typed_line_count(text: str) -> int:
    """Lines the trainer types in one rung: python (kept + transient) plus bash commands."""
    n = 0
    for info, body in _fences(text):
        parts = info.split()
        if parts[:1] == ["python"] and "replaced" not in parts[1:]:
            n += len(_lines(body))
        elif parts[:1] == ["bash"]:
            n += len([ln for ln in _lines(body) if not ln.startswith("#")])
    return n


def carried_lines(start: Path | None) -> set[str]:
    """Lines a rung inherits from its `Starts from` key. Only a .py key carries lines; a transcript's end
    state is a repository, so a rung that starts from one types its file from the first line."""
    if start is None or not start.is_file() or start.suffix != ".py":
        return set()
    return set(_lines(start.read_text(encoding="utf-8")))


def check_script(path: Path, key_dir: Path, metrics: dict, root: Path = ROOT) -> list[str]:
    p: list[str] = []
    name = path.name
    m = SCRIPT_RE.match(name)
    if not m:
        return [f"{name}: script must be named NN_<slug>.md"]
    nn, slug = m.group(1), m.group(2)
    text = path.read_text(encoding="utf-8")
    hdr = _header(text)
    for f in HEADER_FIELDS:
        if f not in hdr or not hdr[f]:
            p.append(f"{name}: header bullet '- {f}:' missing or empty")
    mode = hdr.get("Delivery mode", "")
    if mode and mode not in DELIVERY_MODES:
        p.append(f"{name}: Delivery mode must be one of {DELIVERY_MODES} (facilitation scripts live in the runbook), got '{mode}'")
    tm = re.fullmatch(r"(\d+)\s*min", hdr.get("Time", ""))
    total = int(tm.group(1)) if tm else None
    if hdr.get("Time") and not tm:
        p.append(f"{name}: Time must read 'N min'")
    lo, hi = metrics.get("minutesPerScriptMin", 0), metrics.get("minutesPerScriptMax", 10**6)
    if total is not None and not lo <= total <= hi:
        p.append(f"{name}: Time {total} min outside {lo}..{hi}")
    steps = _steps(text)
    if len(steps) < 2:
        p.append(f"{name}: needs >= 2 '## Step n — title (M min)' headings")
    if [s[0] for s in steps] != list(range(1, len(steps) + 1)):
        p.append(f"{name}: steps must be numbered 1..n in order, got {[s[0] for s in steps]}")
    if total is not None and steps and sum(s[1] for s in steps) != total:
        p.append(f"{name}: step minutes sum to {sum(s[1] for s in steps)}, header Time says {total}")
    for n, _mins, body in steps:
        if any(i.split()[:1] in (["python"], ["bash"]) for i, _ in _fences(body)) and not CWD_RE.search(body):
            p.append(f"{name}: Step {n} has a code/command block but no 'cwd:' line")
    for s in REQUIRED_SECTIONS:
        if s not in text:
            p.append(f"{name}: missing section '{s}'")
    # thread + starts from (demo-thread amendment to D-0030)
    thread = hdr.get("Thread", "")
    starts = hdr.get("Starts from", "")
    start_path: Path | None = None
    if thread and thread != "standalone" and not THREAD_RE.match(thread):
        p.append(f"{name}: Thread must be a kebab-case thread id or 'standalone', got '{thread}'")
    if starts and starts != "cold":
        if not STARTS_RE.match(starts):
            p.append(f"{name}: Starts from must be 'cold' or trainer/<week>/<day>/demos/key/NN_<slug>.py|.md, got '{starts}'")
        elif thread == "standalone":
            p.append(f"{name}: a standalone demo must start cold, not from '{starts}'")
        else:
            start_path = root / starts
            if not start_path.is_file():
                p.append(f"{name}: Starts from key {starts} does not exist (author rungs in ladder order)")
                start_path = None
    carried = carried_lines(start_path)
    replaced = script_replaced_lines(text)
    for ln in sorted(replaced - carried):
        p.append(f"{name}: ```python replaced line is not in the Starts from key: {ln}")
    cap_typed = metrics.get("maxTypedLinesPerRung")
    if cap_typed and typed_line_count(text) > cap_typed:
        p.append(f"{name}: {typed_line_count(text)} typed lines > maxTypedLinesPerRung {cap_typed}; split the rung")
    # answer key
    key_field = hdr.get("Answer key", "")
    km = re.fullmatch(r"key/(\d{2})_([a-z0-9]+(?:[-_][a-z0-9]+)*)\.(py|md|ipynb)", key_field)
    if not km:
        p.append(f"{name}: Answer key must read key/NN_<slug>.py|.md|.ipynb, got '{key_field}'")
        return p
    if (km.group(1), km.group(2)) != (nn, slug):
        p.append(f"{name}: Answer key '{key_field}' must carry the same NN and slug as the script")
    key = key_dir / Path(key_field).name
    if not key.exists():
        p.append(f"{name}: answer key {key_field} does not exist")
        return p
    ktext = key.read_text(encoding="utf-8")
    if key.suffix == ".py":
        if thread and thread != "standalone":
            cap_name, cap = "maxLinesPerThreadKey", metrics.get("maxLinesPerThreadKey", metrics.get("maxLinesPerFile", 90))
        else:
            cap_name, cap = "maxLinesPerFile", metrics.get("maxLinesPerFile", 90)
        if len(ktext.splitlines()) > cap:
            p.append(f"{key.name}: {len(ktext.splitlines())} lines > {cap_name} {cap}; split the demo")
        try:
            py_compile.compile(str(key), doraise=True)
        except py_compile.PyCompileError as e:
            p.append(f"{key.name}: does not compile: {e.msg.splitlines()[-1] if e.msg else e}")
        keep, transient = script_python_lines(text)
        klines = set(_lines(ktext))
        if not keep:
            p.append(f"{name}: a .py answer key needs at least one ```python block in the script")
        for ln in sorted(keep - klines):
            p.append(f"{name}: typed line not in the answer key (mark it ```python transient if it is replaced later): {ln}")
        surviving = carried - replaced
        for ln in sorted(klines - keep - transient - surviving):
            p.append(f"{key.name}: answer-key line never typed in the script and not carried from the Starts from key (no elisions, A5): {ln}")
        for ln in sorted(surviving - klines):
            p.append(f"{key.name}: carried line from {starts} missing (show it in a ```python replaced block if this rung removes or rewrites it): {ln}")
    elif key.suffix == ".md":
        want, have = script_commands(text), transcript_commands(ktext)
        if not want:
            p.append(f"{name}: a transcript answer key needs ```bash command blocks in the script")
        if not have:
            p.append(f"{key.name}: transcript needs ```console blocks with '$ ' command lines")
        if want != have:
            k = next((i for i, (a, b) in enumerate(zip(want, have)) if a != b), min(len(want), len(have)))
            w = want[k] if k < len(want) else "<end>"
            h = have[k] if k < len(have) else "<end>"
            p.append(f"{name} vs {key.name}: command sequences differ at #{k + 1}: script '{w}' vs transcript '{h}'")
    return p


def check_dir(demo_dir: Path, metrics: dict | None = None, root: Path = ROOT) -> list[str]:
    """All problems for one trainer demo folder (scripts + key/). Empty list = OK.
    `root` resolves `Starts from` paths (repo root by default; tests pass a scratch root)."""
    if metrics is None:
        metrics = json.loads(METRICS.read_text(encoding="utf-8"))["demos"]
    p: list[str] = []
    if not demo_dir.is_dir():
        return [f"{demo_dir}: missing"]
    key_dir = demo_dir / "key"
    scripts = sorted(f for f in demo_dir.iterdir() if f.is_file() and f.suffix == ".md" and re.match(r"^\d{2}_", f.name))
    lo, hi = metrics.get("scriptsMin", 1), metrics.get("scriptsMax", 99)
    if not lo <= len(scripts) <= hi:
        p.append(f"{demo_dir.name}: {len(scripts)} scripts, band is {lo}..{hi}")
    nums = [int(f.name[:2]) for f in scripts]
    if nums != list(range(1, len(nums) + 1)):
        p.append(f"{demo_dir.name}: scripts must be numbered 01..NN in order, got {nums}")
    if not key_dir.is_dir():
        p.append(f"{demo_dir.name}: key/ folder missing")
        return p
    for s in scripts:
        p += check_script(s, key_dir, metrics, root)
    stems = {s.stem for s in scripts}
    keys = sorted(f for f in key_dir.iterdir() if f.is_file() and KEY_RE.match(f.name))
    for k in keys:
        if k.stem not in stems:
            p.append(f"key/{k.name}: answer key with no script {k.stem}.md")
    readme = key_dir / "README.md"
    if not readme.exists():
        p.append("key/README.md missing (run-order table; template harness/templates/demo-README.md)")
    else:
        rt = readme.read_text(encoding="utf-8")
        for k in keys:
            if k.name not in rt:
                p.append(f"key/README.md does not list {k.name}")
    return p


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    problems = check_dir(Path(argv[0]))
    for pr in problems:
        print(pr)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
