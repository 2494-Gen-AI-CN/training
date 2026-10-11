"""Runbook + solutions contract. Skipped entirely when trainer/ (private repo) is absent."""

from __future__ import annotations

import re
import unittest

from helpers import HARNESS, ROOT, TRAINER, live_days, load_json, metrics, trainer_demos

CONFIG = load_json(HARNESS / "config.json")
REQUIRED = ["## Day at a glance", "## Objectives", "## Setup check", "## Notes page handoff",
            "## Exercise briefing", "## Common questions", "## If running long / short"]


@unittest.skipUnless(TRAINER.exists(), "trainer/ private repo not cloned here")
class TrainerTests(unittest.TestCase):
    def test_every_live_runbook(self):
        M = metrics()["runbook"]
        for w, d, rel in live_days():
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
                self.assertIn(f"{CONFIG['repoUrl']}/tree/main/demos/{rel}", head, "runbook header must link the demos folder")
                self.assertIn("](solutions/)", head, "runbook header must link solutions/")
                if d.get("feedback"):
                    self.assertIn("## Feedback form", text)
                if d["kind"] == "review":
                    self.assertIn("## Review agenda", text)
                # D-0030: one "## Demo N: <script>" per walkthrough script in trainer/<rel>/demos/; concept days facilitate
                if d["demoFormat"] == "none":
                    self.assertNotRegex(text, re.compile(r"^## Demo \d+:", re.M), "demoFormat none: no Demo sections")
                    self.assertRegex(text, re.compile(r"^## Facilitation \d+: .+\(\d+ min\)", re.M), "demoFormat none day needs timed Facilitation sections")
                else:
                    scripts = sorted(p.name for p in trainer_demos(rel).glob("*.md") if re.match(r"^\d{2}_", p.name))
                    self.assertTrue(scripts, f"no demo scripts in {trainer_demos(rel)}")
                    for f in scripts:
                        self.assertRegex(text, re.compile(rf"^## Demo \d+: {re.escape(f)}", re.M), f"no section for demo script {f}")
                    self.assertNotRegex(text, re.compile(r"^## Demo \d+: \d{2}_\S+\.py", re.M), "Demo sections name the script (.md), not the answer key")
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
