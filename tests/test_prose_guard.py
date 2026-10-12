"""harness/prose_guard.py (D-0039): a humanizer pass on a demo script or a runbook may change prose only."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import HARNESS, ROOT

sys.path.insert(0, str(HARNESS))
import prose_guard  # noqa: E402

SCRIPT = (
    "# 01 — Demo\n\nWeek 1 · Day 3\n\n"
    "- Objective: do a thing\n- Time: 20 min\n- Thread: standalone\n- Starts from: cold\n\n"
    "## Step 1 — set (10 min)\n\ncwd: `s/`\n\n```python\nx = 1\n```\n\n"
    "Talking points while typing:\n- `x` is a name bound to an object; say it once, do not dwell.\n- Run it 2 times.\n\n"
    "## Common pitfalls\n\n| Symptom | Fix |\n|---|---|\n| `NameError` on `x` | Type the line; then run again. |\n\n"
    "## What we did NOT cover (intentional)\n\n- Lists: deferred to Thursday. The ticket stays flat.\n"
)
RUNBOOK = (
    "# w01d3 runbook — Python basics\n\nWeek 1 · Day 3 · Wed Oct 14, 2026\n"
    "Notes page: [page](https://example.org/a.html) · Solutions: [solutions/](solutions/)\n\n"
    "## Day at a glance\n\n| Block | Minutes | Artifact |\n|---|---|---|\n| Demo 1 | 30 | script |\n\n"
    "## Demo 1: 01_demo.md\n\n**Script:** demos/01_demo.md · **Time:** 30 min\n"
    "**Stop point if long:** after Step 3; the talking points move to the PM, and the commit waits.\n"
    "- Q: Is the limit 79? A: Yes, the team's contract; set the ruler at column 79.\n"
)


class CompareTests(unittest.TestCase):
    def test_prose_edits_pass(self):
        new = SCRIPT.replace("say it once, do not dwell.", "say it once and move on.").replace("Type the line; then run again.", "Type the line. Then run again.")
        self.assertEqual(([], []), prose_guard.compare(SCRIPT, new, script=True))
        new = RUNBOOK.replace("after Step 3; the talking points move to the PM, and the commit waits.", "after Step 3. The talking points move to the PM, and the commit waits.")
        new = new.replace("Yes, the team's contract; set the ruler", "Yes, it is the team's contract. Set the ruler")
        self.assertEqual(([], []), prose_guard.compare(RUNBOOK, new, script=False))

    def test_line_endings_are_not_a_change(self):
        self.assertEqual(([], []), prose_guard.compare(SCRIPT, SCRIPT.replace("\n", "\r\n"), script=True))

    def _names(self, old: str, new: str, script: bool) -> list[str]:
        return [f.split(":")[0] for f in prose_guard.compare(old, new, script)[0]]

    def test_script_frozen_content_fails(self):
        for label, new, expect in [
            ("code", SCRIPT.replace("x = 1", "x = 2"), "fenced blocks"),
            ("heading", SCRIPT.replace("## Step 1 — set (10 min)", "## Step 1 — set a name (10 min)"), "headings"),
            ("header bullet", SCRIPT.replace("- Objective: do a thing", "- Objective: do one thing"), "header block"),
            ("cwd", SCRIPT.replace("cwd: `s/`", "cwd: `s/` (the scratch folder)"), "cwd lines"),
            ("inline code", SCRIPT.replace("`NameError`", "`TypeError`"), "inline code"),
            ("table header", SCRIPT.replace("| Symptom | Fix |", "| What you see | Fix |"), "table rows"),
            ("added bullet", SCRIPT.replace("- Run it 2 times.", "- Run it 2 times.\n- Then stop."), "bullet count"),
            ("moved block", SCRIPT.replace("```python\nx = 1\n```\n\n", "").replace("## Common pitfalls\n\n", "## Common pitfalls\n\n```python\nx = 1\n```\n\n"), "fence sections"),
        ]:
            with self.subTest(change=label):
                self.assertIn(expect, self._names(SCRIPT, new, True))

    def test_runbook_frozen_content_fails(self):
        for label, new, expect in [
            ("glance row", RUNBOOK.replace("| Demo 1 | 30 | script |", "| Demo 1 | 35 | script |"), "table rows"),
            ("bold label", RUNBOOK.replace("**Stop point if long:**", "Stop point if long:"), "bold labels"),
            ("url", RUNBOOK.replace("https://example.org/a.html", "https://example.org/b.html"), "urls"),
            ("links line", RUNBOOK.replace("Notes page: [page]", "Notes page: [the page]"), "header block"),
        ]:
            with self.subTest(change=label):
                self.assertIn(expect, self._names(RUNBOOK, new, False))

    def test_a_changed_number_is_a_warning(self):
        findings, warnings = prose_guard.compare(SCRIPT, SCRIPT.replace("Run it 2 times.", "Run it 3 times."), script=True)
        self.assertEqual([], findings)
        self.assertEqual(1, len(warnings))
        self.assertIn("numbers", warnings[0])

    def test_script_or_runbook_is_read_from_the_path(self):
        self.assertTrue(prose_guard.is_script("trainer/week-01/day-3-python-basics/demos/01_ticket_record.md"))
        self.assertFalse(prose_guard.is_script("trainer/week-01/day-3-python-basics/runbook.md"))


class SnapshotCliTests(unittest.TestCase):
    def _run(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(HARNESS / "prose_guard.py"), *argv], capture_output=True, text=True, cwd=ROOT)

    def test_snapshot_then_check(self):
        with tempfile.TemporaryDirectory() as t:
            demos = Path(t) / "demos"
            demos.mkdir()
            script, runbook = demos / "01_demo.md", Path(t) / "runbook.md"
            script.write_text(SCRIPT, encoding="utf-8")
            runbook.write_text(RUNBOOK, encoding="utf-8")
            snap = self._run("snapshot", str(script), str(runbook))
            self.assertEqual(0, snap.returncode, snap.stderr)
            snap_dir = snap.stdout.strip()
            try:
                same = self._run("check", snap_dir, str(script), str(runbook))
                self.assertEqual(0, same.returncode, same.stdout)
                self.assertEqual(2, same.stdout.count("UNCHANGED"))
                script.write_text(SCRIPT.replace("say it once, do not dwell.", "say it once and move on."), encoding="utf-8")
                ok = self._run("check", snap_dir, str(script))
                self.assertEqual(0, ok.returncode, ok.stdout)
                self.assertIn("OK ", ok.stdout)
                script.write_text(SCRIPT.replace("x = 1", "x = 2"), encoding="utf-8")
                bad = self._run("check", snap_dir, str(script))
                self.assertEqual(1, bad.returncode, bad.stdout)
                self.assertIn("FAIL ", bad.stdout)
                self.assertIn("fenced blocks", bad.stdout)
            finally:
                for p in Path(snap_dir).glob("*"):
                    p.unlink()
                Path(snap_dir).rmdir()

    def test_usage_without_arguments(self):
        self.assertEqual(2, self._run().returncode)


class WorkflowWiringTests(unittest.TestCase):
    """Static: day-fanout.js humanizes the demo scripts and the runbook between author and critic (D-0039)."""

    def setUp(self):
        self.src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")

    def test_humanize_runs_after_each_author_and_before_its_critic(self):
        src = self.src
        self.assertEqual(1, src.count("const humanizeTrainer = "))
        self.assertEqual(2, src.count("humanizeTrainer("), "one call for the scripts, one for the runbook")
        demos = src[src.index("async function demosStage"):src.index("const humanize = ")]
        self.assertLess(demos.index("You are the DEMO author"), demos.index("humanizeTrainer(d, 'demos'"))
        self.assertLess(demos.index("humanizeTrainer(d, 'demos'"), demos.index("DEMOS CRITIC"))
        runbook = src[src.index("const runbook = () =>"):src.index("// notes + exercise first")]
        self.assertLess(runbook.index("You are the RUNBOOK author"), runbook.index("humanizeTrainer(d, 'runbook'"))
        self.assertLess(runbook.index("humanizeTrainer(d, 'runbook'"), runbook.index("RUNBOOK CRITIC"))

    def test_the_pass_is_guarded_and_on_the_humanize_tier(self):
        body = self.src[self.src.index("const humanizeTrainer = "):self.src.index("async function materialsStage")]
        for needle in ("humanizer:humanizer", "prose_guard.py snapshot", "prose_guard.py check", "demo_check.py", "...tier('humanize')", "-humanize`"):
            self.assertIn(needle, body)
        self.assertRegex(body, r"contrast that corrects what the room really assumes", "the prompt keeps real spoken contrasts")

    def test_authors_are_told_the_wording_rule(self):
        self.assertEqual(2, self.src.count("Wording (D-0039)"), "the demo author and the runbook author both carry the wording line")
        template = (HARNESS / "templates" / "demo-script.md").read_text(encoding="utf-8")
        self.assertIn("Wording (D-0039)", template)
        self.assertNotRegex(template, r"^- <topic[^\n]*—", "the not-covered bullet in the template has no dash")


if __name__ == "__main__":
    unittest.main()
