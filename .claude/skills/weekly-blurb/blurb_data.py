"""Print the facts for one week's standup blurb: ratings by color band, notes, QC, and the week's days.

Run with the Python that has openpyxl (on the trainer machine that is `python`, 3.12; `py` 3.15 has none):
    python .claude/skills/weekly-blurb/blurb_data.py <week> [--repo <2494-Gen-AI-CN root>]
Read-only. Prints to stdout; never writes anywhere.
"""
import argparse
import json
from pathlib import Path

import openpyxl

DEFAULT_REPO = Path(__file__).resolve().parents[3]  # .claude/skills/weekly-blurb/ -> repo root

# QC rating scale (trainer/qc-rating-scale.png): score out of 5 as a percent, 5 = 100%.
BANDS = [("Blue", 4.5), ("Green", 4.0), ("Lime", 3.5), ("Yellow", 3.0), ("Red", float("-inf"))]
LETTER = {"Blue": "B", "Green": "G", "Lime": "L", "Yellow": "Y", "Red": "R"}


def band(score):
    return next(name for name, floor in BANDS if score >= floor)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("week", type=int)
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    args = ap.parse_args()

    wb = openpyxl.load_workbook(args.repo / "trainer" / "Trainer-Notes.xlsx", read_only=True)
    ws = wb[f"Week {args.week}"]
    rows = [r for r in ws.iter_rows(min_row=3, min_col=2, max_col=6, values_only=True) if r[0]]

    by_band = {name: [] for name, _ in BANDS}
    unrated, notes, qc = [], [], []
    for first, last, qc_rating, trainer_rating, note in rows:
        name = f"{first} {last}"
        if isinstance(trainer_rating, (int, float)):
            by_band[band(trainer_rating)].append((name, trainer_rating))
        else:
            unrated.append(name)
        if note:
            notes.append(f"{name}: {note}")
        if qc_rating is not None:
            qc.append(f"{name}: {qc_rating}" + (f" ({band(qc_rating)})" if isinstance(qc_rating, (int, float)) else ""))

    counts = ", ".join(f"{len(v)} - {LETTER[k]}" for k, v in by_band.items() if v)
    print(f"Trainer Ratings: Technical: {counts}")
    for name, members in by_band.items():
        if members:
            print(f"\n{len(members)} {name} below:")
            for i, (person, score) in enumerate(members, 1):
                print(f"{i}. {person}    [{score}]")
    print("\nUnrated (no numeric trainer rating):", ", ".join(unrated) or "none")
    print("\nNotes:\n" + ("\n".join(notes) or "none"))
    print("\nQC this week:\n" + ("\n".join(qc) or "none"))

    cur = json.loads((args.repo / "harness" / "curriculum.json").read_text(encoding="utf-8"))
    weeks = cur.get("weeks", cur)
    week = next((w for w in weeks if w.get("week") == args.week), None)
    print("\nWeek days (title | taught | subtopics):")
    for d in (week or {}).get("days", []):
        subs = [s if isinstance(s, str) else s.get("title", "") for s in d.get("subtopics", [])]
        print(f"- {d.get('title')} | taught: {d.get('taught') or 'not yet'} | {', '.join(subs)}")


if __name__ == "__main__":
    main()
