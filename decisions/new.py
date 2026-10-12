#!/usr/bin/env python3
"""Mint a new decision-log entry (stdlib only).

Usage:
    python decisions/new.py "One-line decision" --why "Reason" --affects "harness/curriculum.json, week 1"
        [--supersedes D-0003] [--status proposed|accepted] [--date YYYY-MM-DD] [--notes "Free text"]

Creates decisions/D-NNNN-<slug>.md (next sequential ID), prepends a row to the
newest-first table in decisions/README.md, and, with --supersedes, flips the
old entry to Status: superseded / Superseded-by: D-NNNN. Prints the new ID so
it can go in the commit message.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE / "README.md"
ID_RE = re.compile(r"^D-(\d{4})$")
ENTRY_RE = re.compile(r"^D-(\d{4})-[a-z0-9-]+\.md$")
SEP_RE = re.compile(r"^\|---\|.*$", re.M)  # table separator; new rows go right after it
NONE = "—"


def entries() -> dict[str, Path]:
    return {f"D-{m.group(1)}": p for p in HERE.glob("D-*.md") if (m := ENTRY_RE.match(p.name))}


def next_id() -> str:
    nums = [int(k[2:]) for k in entries()]
    return f"D-{(max(nums) + 1) if nums else 1:04d}"


def slugify(text: str, limit: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(s) > limit:
        s = s[:limit].rsplit("-", 1)[0]  # cut at a word boundary
    return s or "entry"


def render_entry(eid: str, a: argparse.Namespace) -> str:
    lines = [
        f"# {eid} — {a.decision}",
        "",
        f"- Date: {a.date}",
        f"- Status: {a.status}",
        f"- Decision: {a.decision}",
        f"- Why: {a.why}",
        f"- Affects: {a.affects}",
        f"- Supersedes: {a.supersedes or NONE}",
        f"- Superseded-by: {NONE}",
        "",
    ]
    if a.notes:
        lines += ["## Notes", "", a.notes.strip(), ""]
    return "\n".join(lines)


def set_field(path: Path, field: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(rf"^- {re.escape(field)}: .*$", f"- {field}: {value}", text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"{path.name}: field '{field}' not found")
    path.write_text(new, encoding="utf-8", newline="\n")


def add_row(eid: str, a: argparse.Namespace) -> None:
    text = INDEX.read_text(encoding="utf-8")
    m = SEP_RE.search(text)
    if not m:
        sys.exit(f"{INDEX.name}: table separator row not found")
    cell = lambda s: s.replace("|", "\\|")
    row = f"| {eid} | {a.date} | {a.status} | {cell(a.decision)} | {cell(a.affects)} | {a.supersedes or NONE} |"
    INDEX.write_text(text[:m.end()] + "\n" + row + text[m.end():], encoding="utf-8", newline="\n")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("decision", help="one-line decision (becomes the title)")
    ap.add_argument("--why", required=True)
    ap.add_argument("--affects", required=True, help="files / weeks / days, comma-separated")
    ap.add_argument("--supersedes", default="", help="ID of the entry this replaces")
    ap.add_argument("--status", default="accepted", choices=["proposed", "accepted"])
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--notes", default="")
    a = ap.parse_args(argv)
    dt.date.fromisoformat(a.date)
    if a.supersedes:
        if not ID_RE.match(a.supersedes):
            sys.exit(f"bad --supersedes {a.supersedes!r}; expected D-NNNN")
        if a.supersedes not in entries():
            sys.exit(f"{a.supersedes} does not exist")
    eid = next_id()
    path = HERE / f"{eid}-{slugify(a.decision)}.md"
    path.write_text(render_entry(eid, a), encoding="utf-8", newline="\n")
    add_row(eid, a)
    if a.supersedes:
        old = entries()[a.supersedes]
        set_field(old, "Status", "superseded")
        set_field(old, "Superseded-by", eid)
        # keep the index row in step with the entry file
        text = INDEX.read_text(encoding="utf-8")
        text = re.sub(rf"^(\| {a.supersedes} \| [^|]* \| )(proposed|accepted)( \|)", r"\1superseded\3", text, count=1, flags=re.M)
        INDEX.write_text(text, encoding="utf-8", newline="\n")
    print(eid)
    rebuild_tracker()
    return 0


def rebuild_tracker() -> None:
    """The work tracker lists the decisions (D-0035). Rebuild the local, gitignored tracker.html (D-0036);
    the entry is minted either way. Messages go to stderr so stdout stays the bare ID. Only the real repo
    is touched (tests run this module against a temp folder, which has no tracker template)."""
    root = HERE.parent
    if not (root / "harness" / "templates" / "tracker.html").is_file():
        return
    try:
        sys.path.insert(0, str(root / "harness"))
        import build_tracker
        if build_tracker.ROOT.resolve() == root.resolve() and build_tracker.build(quiet=True):
            print("tracker.html updated", file=sys.stderr)
    except Exception as e:  # noqa: BLE001 - never fail a decision over the tracker
        print(f"tracker.html not rebuilt: {e}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
