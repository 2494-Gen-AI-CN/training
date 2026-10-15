"""Runbook + solutions contract. Skipped entirely when trainer/ (private repo) is absent."""

from __future__ import annotations

import re
import unittest

import sys

from helpers import HARNESS, ROOT, TRAINER, authored_days, load_json, metrics, week_demos

sys.path.insert(0, str(HARNESS))
import plan_check  # noqa: E402

CONFIG = load_json(HARNESS / "config.json")
REQUIRED = ["## Day at a glance", "## Objectives", "## Setup check", "## Notes page handoff",
            "## Exercise briefing", "## Common questions", "## If running long / short"]


@unittest.skipUnless(TRAINER.exists(), "trainer/ private repo not cloned here")
class TrainerTests(unittest.TestCase):
    def test_every_authored_runbook(self):
        M = metrics()["runbook"]
        for w, d, rel in authored_days():  # D-0052: authored or live
            rb = TRAINER / rel / "runbook.md"
            with self.subTest(rel=rel):
                self.assertTrue(rb.exists(), f"missing {rb}")
                text = rb.read_text(encoding="utf-8")
                self.assertTrue(text.startswith(f"# {d['id']} runbook"), "first line must be '# <id> runbook'")
                for h in REQUIRED:
                    self.assertIn(h, text, f"missing heading {h}")
                # D-0027: header links every public artifact absolutely (trainer repo is separate) and solutions/ relatively
                head = "\n".join(text.splitlines()[:4])
                self.assertIn(f"{CONFIG['siteUrl']}weeks/{rel}.html", head, "runbook header must link the notes page on the site")
                if week_demos(w["dir"]).is_dir():
                    self.assertIn("](../demos/)", head, "runbook header must link the week's walkthrough folder (D-0055)")
                self.assertIn("](solutions/)", head, "runbook header must link solutions/")
                if d.get("feedback"):
                    self.assertIn("## Feedback form", text)
                if d["kind"] == "review":
                    self.assertIn("## Review agenda", text)
                # D-0055: one "## Demo: <walkthrough>.md" per block of the day in the week plan; concept days facilitate
                if d["demoFormat"] == "none":
                    self.assertNotRegex(text, re.compile(r"^## Demo", re.M), "demoFormat none: no Demo sections")
                    self.assertRegex(text, re.compile(r"^## Facilitation \d+: .+\(\d+ min\)", re.M), "demoFormat none day needs timed Facilitation sections")
                elif week_demos(w["dir"]).is_dir():
                    plan_file = HARNESS / "plans" / f"week-{w['week']:02d}.md"
                    blocks = plan_check.day_rows(plan_check.load_plan(plan_file), d["id"])["blockRows"] if plan_file.is_file() else []
                    self.assertTrue(blocks, f"{d['id']} has no block in the week plan")
                    for b in blocks:
                        self.assertRegex(text, re.compile(rf"^## Demo: {re.escape(b['name'])}\.md", re.M), f"no section for walkthrough {b['name']}.md")
                        self.assertTrue((week_demos(w["dir"]) / f"{b['name']}.md").is_file(), f"walkthrough {b['name']}.md missing on disk")
                # minutes table sums into the day band
                glance = text.split("## Day at a glance", 1)[1].split("\n## ", 1)[0]
                mins = [int(m) for m in re.findall(r"^\|[^|]*\|\s*(\d+)\s*\|", glance, re.M)]
                total = sum(mins[:-1]) if len(mins) > 1 and mins[-1] == sum(mins[:-1]) else sum(mins)
                self.assertTrue(M["dayMinutesMin"] <= total <= M["dayMinutesMax"], f"day sums to {total} min")
                if d.get("exerciseKind", "pytest") == "rubric":
                    self.assertTrue((TRAINER / rel / "solutions" / "RUBRIC.md").exists(), "rubric day needs solutions/RUBRIC.md (D-0025)")
                    continue
                sols = list((TRAINER / rel / "solutions").glob("*.py"))
                self.assertTrue(sols, "solutions/ must contain the module")
                starters = [p.stem for p in (ROOT / "exercises" / rel / "starter").glob("*.py")]
                self.assertTrue(any(s.stem in starters for s in sols), "solution module name must match starter module")


if __name__ == "__main__":
    unittest.main()
