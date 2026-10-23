"""Demo contract (D-0055): one walkthrough per demo block under trainer/week-WW/demos/, format-checked by
harness/demo_check.py; the answer key is the demo repo at the block's commit on the week's prep branch, so
nothing here reads keys. Weeks whose trainer folder does not exist (week 1, taught before D-0055) are skipped."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from helpers import HARNESS, SECRET_RE, TRAINER, authored_weeks, metrics, week_demos

sys.path.insert(0, str(HARNESS))
import demo_check  # noqa: E402


class DemoScriptTests(unittest.TestCase):
    """Every authored or live week with a demos folder passes the format check and carries no secret."""

    def test_every_authored_week(self):
        if not TRAINER.exists():
            self.skipTest("trainer/ private repo not cloned here")
        for w in authored_weeks():
            ddir = week_demos(w["dir"])
            with self.subTest(week=w["dir"]):
                if not ddir.is_dir():
                    continue  # pre-D-0055 week (per-day demo folders) or a week with no code demo at all
                problems = demo_check.check_dir(ddir, metrics()["demos"])
                self.assertEqual([], problems, "\n".join(problems))
                for p in sorted(ddir.glob("*.md")):
                    self.assertIsNone(SECRET_RE.search(p.read_text(encoding="utf-8")), f"secret-looking string in {p.name}")

    def test_blocks_chain_in_order(self):
        """Every non-cold block starts from an earlier walkthrough: one of this week's folder before it, or any block of
        an earlier week (a week's first block starts from the previous week's last one, D-0034)."""
        if not TRAINER.exists():
            self.skipTest("trainer/ private repo not cloned here")
        earlier: list[str] = []
        for w in sorted(authored_weeks(), key=lambda w: w["dir"]):
            ddir = week_demos(w["dir"])
            if not ddir.is_dir():
                continue
            names = [f.stem for f in demo_check.walkthroughs(ddir)]
            for i, f in enumerate(demo_check.walkthroughs(ddir)):
                facts = demo_check.header_facts(f)
                with self.subTest(file=f"{w['dir']}/{f.name}"):
                    self.assertIsNotNone(facts["thread"], "Thread line malformed")
                    if facts["startsFrom"] != "cold":
                        self.assertIn(facts["startsFrom"], earlier + names[:i],
                                      f"starts from {facts['startsFrom']}, which is not an earlier walkthrough of this or an earlier week")
            earlier += names


class DemoCheckSelfTests(unittest.TestCase):
    """harness/demo_check.py itself: the template passes once filled; each rule fails once."""

    M = {"blocksPerDayMin": 0, "blocksPerDayMax": 2, "minutesPerBlockMin": 20, "minutesPerBlockMax": 180,
         "stepsPerBlockMin": 2, "stepsPerBlockMax": 12, "maxTypedLinesPerBlock": 250}

    HEAD = ("# Demo: A thing (`p0-demo` -> `01-thing`)\n\n"
            "> **Objective:** do a thing\n> that spans two lines.\n>\n> **Time:** 20 min (AM block)\n"
            "> **Audience:** grads\n> **Prerequisite reading:** none\n"
            "> **Thread:** `p0-demo` — commit `Add the thing`, starts cold\n\n"
            "Extends nothing.\n\n### Stub manifest\n- None.\n\n---\n\n")
    CHEAT = "## Presenter cheat-sheet\n\n| # | Step | File touched |\n|---|---|---|\n| 1 | set | `x.py` |\n| 2 | commit | Terminal |\n\n"
    STEPS = ("## Step 1 — set (10 min)\n\ncwd: `s/`\n\n```python\nx = 1\n```\n\n### Talking points while typing\n\n- x\n\n"
             "## Step 2 — commit (10 min)\n\ncwd: `s/`\n\n```bash\ngit add .\ngit commit -m \"Add the thing\"\n```\n\n")
    TAIL = ("## Common pitfalls (call these out proactively)\n\n1. **a.** b\n\n## What we did NOT cover (intentional)\n\n"
            "- x: deferred to later. It is not needed today.\n\n## End-of-demo wrap-up\n\n1. q\n\n## Sequence pointer\n\nnext\n")

    def _write(self, tmp: Path, text: str, name: str = "01-thing.md") -> Path:
        (tmp / "README.md").write_text("# index\n", encoding="utf-8")
        f = tmp / name
        f.write_text(text, encoding="utf-8")
        return f

    def test_good_walkthrough_passes(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            self._write(tmp, self.HEAD + self.CHEAT + self.STEPS + self.TAIL)
            self.assertEqual([], demo_check.check_dir(tmp, self.M))
            facts = demo_check.header_facts(tmp / "01-thing.md")
            self.assertEqual(("01-thing", 20, "p0-demo", "Add the thing", "cold", 2),
                             (facts["name"], facts["time"], facts["thread"], facts["commit"], facts["startsFrom"], facts["steps"]))
            self.assertEqual("do a thing that spans two lines.", facts["objective"])

    def test_each_rule_fails_once(self):
        cases = {
            "title": (self.HEAD.replace("`01-thing`", "`02-thing`"), "title names"),
            "field": (self.HEAD.replace("> **Audience:** grads\n", ""), "'> **Audience:**' missing"),
            "time": (self.HEAD.replace("20 min (AM block)", "about 20 minutes"), "must start with 'N min'"),
            "band": (self.HEAD.replace("20 min (AM block)", "10 min"), "outside 20..180"),
            "sum": (self.HEAD.replace("20 min (AM block)", "30 min"), "step minutes sum to 20"),
            "thread": (self.HEAD.replace("`p0-demo` — commit `Add the thing`, starts cold", "p0-demo, cold"), "Thread must read"),
            "title-thread": (self.HEAD.replace("(`p0-demo` ->", "(`other` ->"), "differs from the Thread field"),
            "commit": (self.HEAD.replace("commit `Add the thing`", "commit `Other message`"), "git commit -m \"Other message\""),
        }
        for label, (head, needle) in cases.items():
            with self.subTest(rule=label), tempfile.TemporaryDirectory() as t:
                tmp = Path(t)
                self._write(tmp, head + self.CHEAT + self.STEPS + self.TAIL)
                probs = demo_check.check_dir(tmp, self.M)
                self.assertTrue(any(needle in p for p in probs), f"{label}: {probs}")
        body_cases = {
            "cheat-rows": (self.CHEAT.replace("| 2 | commit | Terminal |\n", ""), self.STEPS, "cheat-sheet rows"),
            "cheat-missing": ("", self.STEPS, "missing section '## Presenter cheat-sheet'"),
            "numbering": (self.CHEAT, self.STEPS.replace("## Step 2", "## Step 3"), "numbered 1..n"),
            "cwd": (self.CHEAT, self.STEPS.replace("cwd: `s/`\n\n```python", "```python"), "no 'cwd:' line"),
            "steps-band": (self.CHEAT.replace("| 2 | commit | Terminal |\n", ""), self.STEPS.split("## Step 2")[0].replace("(10 min)", "(20 min)"), "band is 2..12"),
            "no-code-step": (self.CHEAT, self.STEPS.replace("## Step 1 — set (10 min)", "## Step 1 — set (10 min, no code)"), None),
        }
        for label, (cheat, steps, needle) in body_cases.items():
            with self.subTest(rule=label), tempfile.TemporaryDirectory() as t:
                tmp = Path(t)
                self._write(tmp, self.HEAD + cheat + steps + self.TAIL)
                probs = demo_check.check_dir(tmp, self.M)
                if needle is None:
                    self.assertEqual([], probs, probs)
                else:
                    self.assertTrue(any(needle in p for p in probs), f"{label}: {probs}")
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            self._write(tmp, self.HEAD + self.CHEAT + self.STEPS + self.TAIL.replace("## End-of-demo wrap-up", "## Wrap-up questions"))
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any("missing section '## End-of-demo wrap-up'" in p for p in probs), probs)
            self._write(tmp, self.HEAD + self.CHEAT + self.STEPS + self.TAIL.replace("- x: deferred to later.", "- x — deferred to later;"))
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any("NOT cover" in p for p in probs), probs)
            probs = demo_check.check_dir(tmp, {**self.M, "maxTypedLinesPerBlock": 1})
            self.assertTrue(any("maxTypedLinesPerBlock" in p for p in probs), probs)
            (tmp / "README.md").unlink()
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any("README.md missing" in p for p in probs), probs)

    def test_folder_numbering_and_standalone(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            self._write(tmp, self.HEAD + self.CHEAT + self.STEPS + self.TAIL)
            second = (self.HEAD.replace("`01-thing`", "`03-other`").replace("(`p0-demo` ->", "(`standalone` ->")
                      .replace("> **Thread:** `p0-demo` — commit `Add the thing`, starts cold", "> **Thread:** standalone — starts cold"))
            steps = self.STEPS.replace("## Step 2 — commit (10 min)\n\ncwd: `s/`\n\n```bash\ngit add .\ngit commit -m \"Add the thing\"\n```\n\n",
                                       "## Step 2 — talk (10 min, no code)\n\nwords\n\n")
            self._write(tmp, second + self.CHEAT + steps + self.TAIL, name="03-other.md")
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any("numbered 01..NN" in p for p in probs), probs)
            self.assertFalse(any("03-other.md" in p for p in probs), f"a standalone block owes no commit: {probs}")
            self.assertEqual(("standalone", "", "cold"), demo_check.thread_info(demo_check._header((tmp / "03-other.md").read_text(encoding="utf-8"))))

    def test_delivery_record_is_ignored_by_the_header_parser(self):
        text = self.HEAD.replace("Extends nothing.", "> **DELIVERY RECORD (2026-10-19)** Taught in full; classroom commit abc1234.\n> Steps 1-2 taught.\n\nExtends nothing.")
        hdr = demo_check._header(text)
        self.assertEqual("grads", hdr["Audience"])
        self.assertNotIn("DELIVERY RECORD (2026-10-19)", hdr)
        self.assertEqual(["2026-10-19"], demo_check.delivery_dates(text))
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            self._write(tmp, text + self.CHEAT + self.STEPS + self.TAIL)
            self.assertEqual([], demo_check.check_dir(tmp, self.M))

    def test_template_is_well_formed(self):
        text = (HARNESS / "templates" / "demo-script.md").read_text(encoding="utf-8")
        hdr = demo_check._header(text)
        for f in demo_check.HEADER_FIELDS:
            self.assertIn(f, hdr)
        for s in [demo_check.CHEAT_HEAD] + demo_check.REQUIRED_SECTIONS:
            self.assertIn(s, text)
        steps = demo_check._steps(text)
        self.assertEqual([1, 2, 3, 4, 5], [s[0] for s in steps])
        self.assertEqual(demo_check.time_minutes(hdr), sum(s[1] for s in steps))
        self.assertEqual([1, 2, 3, 4, 5], demo_check.cheat_rows(text))
        self.assertEqual([], demo_check.not_covered_problems(text), "the template's own bullet follows the one format")

    def test_not_covered_bullets_take_one_format(self):
        """D-0039: '- <topic>: <where it goes>. <reason>.' on every script, no dash between topic and note."""
        head = "## What we did NOT cover (intentional)\n\n"
        tail = "\n\n## End-of-demo wrap-up\n\n- not a bullet of that section — ignored\n"
        good = [
            "- Lists and tuples: deferred to Thursday (w01d4). The ticket stays six flat variables.",
            '- `if __name__ == "__main__":` around the script body: deferred to week 2 day 1, when the file splits into modules.',
            "- `for` over `ticket.items()`: deferred to Friday. The items print as a list here.",
        ]
        self.assertEqual([], demo_check.not_covered_problems(head + "\n".join(good) + tail))
        for bad in (
            "- Lists and tuples — deferred to Thursday (w01d4); the ticket stays flat.",
            "- Lists and tuples are deferred to Thursday (w01d4); the ticket stays flat.",
            "- Lists and tuples. Deferred to Thursday (w01d4); the ticket stays flat.",
            "- `datetime` for `hours_open` -- deferred to Demo 4.",
        ):
            with self.subTest(bullet=bad):
                self.assertEqual([bad], demo_check.not_covered_problems(head + bad + tail))


if __name__ == "__main__":
    unittest.main()
