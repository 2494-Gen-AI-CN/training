#!/usr/bin/env python3
"""Publish a taught day's demo answer keys (D-0030: trainer-only until taught).

Authors write demo scripts and answer keys to trainer/<week>/<day>/demos/ (private repo).
Once the delivery-day close sets `taught: "YYYY-MM-DD"` on the day in curriculum.json, this
script mirrors trainer/<rel>/demos/key/ into the public demos/<rel>/ and flips the notes
page's demo card from "Published after class" (data-demo="pending") to the file links
(data-demo="published"). Without `taught` it publishes nothing. Idempotent; the Wire step
and the delivery close both run it.

Usage:
    python harness/publish_demos.py <week> <day>            # publish if taught, else no-op
    python harness/publish_demos.py <week> <day> --check    # report drift, write nothing (exit 1 on drift)
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

ROOT = bi.ROOT
TRAINER = ROOT / "trainer"
SKIP = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
CARD_PENDING = '<div class="activity-card demo-card" data-demo="pending">'
CARD_PUBLISHED = '<div class="activity-card demo-card" data-demo="published">'
PENDING_TEXT = '<div class="ac-t">Published after class</div>'
PUBLISHED_META = '<div class="ac-meta">answer keys from the session · README has the run order</div>'
META_RE = re.compile(r'<div class="ac-meta">.*?</div>', re.S)
KEY_FILE_RE = re.compile(r"^\d{2}_")


def key_files(key_dir: Path) -> list[Path]:
    return sorted(f for f in key_dir.iterdir() if f.is_file() and KEY_FILE_RE.match(f.name)) if key_dir.is_dir() else []


def publishable(key_dir: Path) -> list[Path]:
    """Everything under key/ that gets mirrored (answer keys, README, requirements, .env.example ...)."""
    return sorted(f for f in key_dir.rglob("*") if f.is_file() and not (set(f.relative_to(key_dir).parts) & SKIP))


def card_links(repo_url: str, branch: str, rel: str, names: list[str]) -> str:
    base = f"{repo_url.rstrip('/')}/tree/{branch}/demos/{rel}"
    links = [f'<a href="{base}/{n}" target="_blank" rel="noopener">{n}</a>' for n in names]
    return '<div class="ac-t">\n            ' + " ·\n            ".join(links) + "\n          </div>"


def flip_card(html: str, repo_url: str, branch: str, rel: str, names: list[str]) -> str:
    """Turn the pending demo card into the published one. Raises if the page does not carry the pending card."""
    if CARD_PENDING not in html:
        raise ValueError("page has no pending demo card (data-demo=\"pending\")")
    start = html.index(CARD_PENDING)
    head, rest = html[:start], html[start:]
    rest = rest.replace(CARD_PENDING, CARD_PUBLISHED, 1)
    if PENDING_TEXT not in rest:
        raise ValueError("pending demo card lacks the 'Published after class' line")
    rest = rest.replace(PENDING_TEXT, card_links(repo_url, branch, rel, names), 1)
    m = META_RE.search(rest)  # the first .ac-meta after the card opener is the card's own
    if m:
        rest = rest[:m.start()] + PUBLISHED_META + rest[m.end():]
    return head + rest


def _locate(week_no: int, day_no: int):
    cur = bi.load_curriculum()
    cfg = json.loads((ROOT / "harness" / "config.json").read_text(encoding="utf-8"))
    week = next(w for w in cur["weeks"] if w["week"] == week_no)
    day = next(d for d in week["days"] if d["day"] == day_no)
    if day.get("kind") == "holiday":
        raise SystemExit(f"week {week_no} day {day_no} is a holiday")
    rel = f"{week['dir']}/{day['slug']}"
    return cfg, day, rel


def check(day: dict, rel: str, cfg: dict) -> list[str]:
    """Problems with the public state of one day's demos. Empty list = consistent."""
    p: list[str] = []
    pub = ROOT / "demos" / rel
    page = ROOT / "docs" / "weeks" / f"{rel}.html"
    key_dir = TRAINER / rel / "demos" / "key"
    html = re.sub(r"<!--.*?-->", "", page.read_text(encoding="utf-8"), flags=re.S) if page.exists() else ""
    if day.get("demoFormat") == "none":
        if pub.exists() and any(KEY_FILE_RE.match(f.name) for f in pub.iterdir()):
            p.append(f"demos/{rel}: demoFormat none but answer-key files are published")
        if html and 'class="activity-card demo-card"' in html:
            p.append(f"{page.name}: demoFormat none but the page carries a demo card")
        return p
    if not day.get("taught"):
        if pub.exists() and any(KEY_FILE_RE.match(f.name) for f in pub.iterdir()):
            p.append(f"demos/{rel}: published before the day was taught (no `taught` date in curriculum.json)")
        if html and CARD_PENDING not in html:
            p.append(f"{page.name}: demo card must be data-demo=\"pending\" until the day is taught")
        return p
    # taught: public mirror must exist and match key/ when the private repo is present
    if not (pub / "README.md").exists():
        p.append(f"demos/{rel}/README.md missing: run python harness/publish_demos.py")
    pub_names = sorted(f.name for f in pub.iterdir() if f.is_file() and KEY_FILE_RE.match(f.name)) if pub.exists() else []
    if not pub_names:
        p.append(f"demos/{rel}: no answer-key files published")
    if key_dir.is_dir():
        for f in publishable(key_dir):
            tgt = pub / f.relative_to(key_dir)
            if not tgt.exists():
                p.append(f"demos/{rel}/{f.relative_to(key_dir)}: missing (not published)")
            elif tgt.read_bytes() != f.read_bytes():
                p.append(f"demos/{rel}/{f.relative_to(key_dir)}: differs from trainer key/")
        want = [f.name for f in key_files(key_dir)]
        extra = sorted(set(pub_names) - set(want))
        for n in extra:
            p.append(f"demos/{rel}/{n}: not in trainer key/ (stale)")
    if html:
        if CARD_PUBLISHED not in html:
            p.append(f"{page.name}: demo card must be data-demo=\"published\" once taught")
        for n in pub_names:
            if f"/demos/{rel}/{n}\"" not in html:
                p.append(f"{page.name}: demo card does not link {n}")
    return p


def publish(week_no: int, day_no: int, dry: bool = False) -> list[str]:
    cfg, day, rel = _locate(week_no, day_no)
    if dry:
        return check(day, rel, cfg)
    if day.get("demoFormat") == "none":
        return [f"{rel}: demoFormat none, nothing to publish"]
    if not day.get("taught"):
        return [f"{rel}: not taught yet (no `taught` date in curriculum.json); nothing published"]
    key_dir = TRAINER / rel / "demos" / "key"
    if not key_dir.is_dir():
        raise SystemExit(f"{key_dir} missing: author the demos first (trainer repo present?)")
    pub = ROOT / "demos" / rel
    pub.mkdir(parents=True, exist_ok=True)
    out = []
    for f in publishable(key_dir):
        tgt = pub / f.relative_to(key_dir)
        tgt.parent.mkdir(parents=True, exist_ok=True)
        if not tgt.exists() or tgt.read_bytes() != f.read_bytes():
            shutil.copyfile(f, tgt)
            out.append(f"copied {f.relative_to(key_dir)}")
    want = {f.name for f in key_files(key_dir)}
    for f in pub.iterdir():
        if f.is_file() and KEY_FILE_RE.match(f.name) and f.name not in want:
            f.unlink()
            out.append(f"removed stale {f.name}")
    page = ROOT / "docs" / "weeks" / f"{rel}.html"
    if page.exists():
        html = page.read_text(encoding="utf-8")
        if CARD_PENDING in html:
            html = flip_card(html, cfg["repoUrl"], cfg.get("repoBranch", "main"), rel, sorted(want))
            page.write_text(html, encoding="utf-8")
            out.append(f"flipped demo card on {page.name}")
    return out or [f"{rel}: already published, nothing changed"]


def main(argv: list[str]) -> int:
    dry = "--check" in argv
    nums = [int(a) for a in argv if a != "--check"]
    if len(nums) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    msgs = publish(nums[0], nums[1], dry=dry)
    for m in msgs:
        print(m)
    if not dry:
        # Publishing changes what the work tracker shows for the day (D-0035).
        import build_tracker
        if build_tracker.build(quiet=True):
            print("tracker.html updated")
    return 1 if (dry and msgs) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
