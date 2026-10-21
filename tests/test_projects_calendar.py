"""The index calendar side of the Projects section (D-0065): SPRINTS, flag pills, links and hooks.

The generator itself (harness/build_projects.py) is tested in tests/test_projects.py. Here only
what build_index.render() and docs/index.html do with its calendar_marks() contract.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import DOCS, HARNESS, ParsedPage, curriculum

sys.path.insert(0, str(HARNESS))
import build_index  # noqa: E402

HAVE_PROJECTS = importlib.util.find_spec("build_projects") is not None
LANDED = "harness/build_projects.py lands with the projects generator lane"

SPRINT_MD = """---
kind: sprint
title: Ticket desk data sprint
assigned: 2026-10-21
due: 2026-10-26
mode: pairs
handIn: week-02/hackathon/
status: open
tools: NumPy, pandas, Matplotlib
---
Load the ticket desk data, summarise it and chart it.
"""

OFFICIAL_MD = """---
kind: official
project: P0
title: Ticket desk
status: {status}
handIn: projects/P0/
checkpoints:
  - w05d5 Showcase
---
A small command-line ticket desk built over the first five weeks.

## Goal
Build a working ticket desk in Python.

## Scope
Python, files, tests and SQL from weeks 1 to 4.

## Requirements
- R-01 Load tickets from a file.
- R-02 Report open tickets by priority.

## Deliverable
A repository folder with the code and a short read-me.

## Checkpoints
A showcase at the end of week 5.

## Rubric
Working code, tests that pass, a clear read-me.

## Presentation
Five minutes per pair, demo then questions.
"""

BROKEN_MD = """kind: sprint
title: No fences at all
"""


def _entries(block: str) -> dict:
    """Day id -> its WEEKS entry, parsed from the generated block (one JSON object per line)."""
    out = {}
    for ln in block.splitlines():
        ln = ln.strip().rstrip(",")
        if ln.startswith("{") and '"id": "' in ln:
            entry = json.loads(ln)
            out[entry["id"]] = entry
    return out


def _sprints(block: str) -> list:
    for ln in block.splitlines():
        if ln.startswith("window.SPRINTS = "):
            return json.loads(ln[len("window.SPRINTS = "):].rstrip(";"))
    raise AssertionError("no window.SPRINTS line in the block")


class RenderTests(unittest.TestCase):
    def test_render_always_emits_sprints_after_projects(self):
        block = build_index.render()
        self.assertIn("window.SPRINTS", block)
        lines = block.splitlines()
        i = next(n for n, ln in enumerate(lines) if ln.startswith("window.PROJECTS = "))
        self.assertTrue(lines[i + 1].startswith("window.SPRINTS = "), "SPRINTS right after PROJECTS")
        self.assertIsInstance(_sprints(block), list)

    def test_render_without_the_generator_has_no_marks(self):
        """args_for.py / close_day.py import build_index: a checkout without the generator still renders."""
        with mock.patch.dict(sys.modules, {"build_projects": None}):
            block = build_index.render(json.loads(json.dumps(curriculum())))
        self.assertEqual([], _sprints(block))
        for entry in _entries(block).values():
            self.assertNotIn("due", entry)
            self.assertNotIn("cp", entry)


@unittest.skipUnless(HAVE_PROJECTS, LANDED)
class CalendarMarkTests(unittest.TestCase):
    """Fixture specs in a temp root (like test_render_hides_a_day_flipped_to_authored, on a copy of the curriculum)."""

    def setUp(self):
        import build_projects
        self.bp = build_projects
        self.cur = json.loads(json.dumps(curriculum()))
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.specs = self.root / "projects"
        (self.specs / "sprints").mkdir(parents=True)
        (self.specs / "official").mkdir(parents=True)
        real_load = build_projects.load_specs

        def load_specs(root=None, cur=None, strict=True):
            return real_load(root=self.root if root is None or root == build_projects.ROOT else root, cur=cur, strict=strict)

        for p in (mock.patch.object(build_projects, "SPECS", self.specs),
                  mock.patch.object(build_projects, "load_specs", load_specs)):
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self._tmp.cleanup)

    def _write(self, rel: str, text: str) -> None:
        (self.specs / rel).write_text(text, encoding="utf-8", newline="\n")

    def _render(self) -> tuple[str, str]:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            block = build_index.render(self.cur)
        return block, err.getvalue()

    def test_sprint_marks_its_due_day_and_spans_one_bar(self):
        self._write("sprints/2026-10-21-ticket-desk-data.md", SPRINT_MD)
        self.assertEqual([], self.bp.validate(self.root, self.cur), "fixture is a valid sprint")
        block, _ = self._render()
        entries = {e["date"]: e for e in _entries(block).values()}
        due = entries["2026-10-26"].get("due")
        self.assertEqual(1, len(due or []), "the due day carries one flag")
        self.assertEqual("ticket-desk-data", due[0]["slug"])
        self.assertEqual("Ticket desk data sprint", due[0]["title"])
        for date, e in entries.items():
            if date != "2026-10-26":
                self.assertNotIn("due", e, date)
            self.assertNotIn("cp", e, date)
        sprints = _sprints(block)
        self.assertEqual(1, len(sprints))
        self.assertEqual({"slug": "ticket-desk-data", "start": "2026-10-21", "end": "2026-10-26"},
                         {k: sprints[0][k] for k in ("slug", "start", "end")})

    def test_published_official_marks_its_checkpoint_day(self):
        self._write("official/P0-ticket-desk.md", OFFICIAL_MD.format(status="published"))
        self.assertEqual([], self.bp.validate(self.root, self.cur), "fixture is a valid official spec")
        block, _ = self._render()
        e = _entries(block)["w05d5"]
        self.assertEqual(1, len(e.get("cp", [])))
        self.assertEqual("Showcase", e["cp"][0]["label"])
        self.assertEqual("P0-ticket-desk", e["cp"][0]["slug"])  # slug = file stem
        self.assertEqual([], _sprints(block), "an official spec draws no sprint bar")

    def test_draft_official_yields_no_mark(self):
        self._write("official/P0-ticket-desk.md", OFFICIAL_MD.format(status="draft"))
        self.assertEqual([], self.bp.validate(self.root, self.cur), "fixture is a valid draft")
        block, _ = self._render()
        for entry in _entries(block).values():
            self.assertNotIn("cp", entry, entry["id"])
            self.assertNotIn("due", entry, entry["id"])
        self.assertEqual([], _sprints(block))

    def test_broken_spec_is_skipped_and_render_still_returns(self):
        self._write("sprints/2026-10-21-ticket-desk-data.md", SPRINT_MD)
        self._write("sprints/2026-10-22-broken.md", BROKEN_MD)
        self.assertNotEqual([], self.bp.validate(self.root, self.cur), "the broken file is a validation problem")
        block, err = self._render()
        self.assertTrue(block.startswith(build_index.BEGIN) and block.endswith(build_index.END))
        self.assertTrue(err.strip(), "the skipped file is reported on stderr")
        self.assertEqual(["ticket-desk-data"], [s["slug"] for s in _sprints(block)], "the good spec still marks")


class IndexPageTests(unittest.TestCase):
    def setUp(self):
        self.page = ParsedPage(DOCS / "index.html")

    def test_topnav_links_projects_once(self):
        nav = [a for a in self.page.root.find_all("a", "topnav") if a.text().strip() == "Projects"]
        self.assertEqual(1, len(nav))
        self.assertEqual("projects/index.html", nav[0].attrs.get("href"))

    def test_rail_links_projects_once(self):
        rail = [a for a in self.page.root.find("div", "friday-rituals").find_all("a", "fr-btn")
                if a.attrs.get("href") == "projects/index.html"]
        self.assertEqual(1, len(rail))
        self.assertIn("Projects", rail[0].text())

    def test_legend_explains_the_flag(self):
        foot = self.page.root.find("div", "cal-foot")
        self.assertIn("🏁 Sprint due / project checkpoint", [s.text().strip() for s in foot.find_all("span")])

    def test_page_js_draws_flags_and_bars(self):
        js = self.page.embedded_js
        for needle in ('class="mk flag"', "day.due", "day.cp", "window.SPRINTS", '"sprint-row"', 'class="sprint-bar"', "Sprint due: ", "Checkpoint: "):
            self.assertTrue(needle in js, f"index page JS lacks {needle}")
        css = "\n".join(s.text() for s in self.page.root.find_all("style"))
        for rule in (".sprint-row", ".sprint-bar", ".cal-cell .mk.flag"):
            self.assertIn(rule, css, rule)


class HookTests(unittest.TestCase):
    def test_build_index_checks_and_rebuilds_the_projects_pages(self):
        src = (HARNESS / "build_index.py").read_text(encoding="utf-8")
        self.assertIn("build_projects.check(", src)
        self.assertIn("build_projects.build(", src)
        self.assertIn("strict=False", src, "render() skips a broken spec instead of failing")


if __name__ == "__main__":
    unittest.main()
