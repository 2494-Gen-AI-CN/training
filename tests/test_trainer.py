"""Runbook + solutions contract. Skipped entirely when trainer/ (private repo) is absent."""

from __future__ import annotations

import re
import unittest

from helpers import ROOT, TRAINER, live_days, metrics

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
                if d.get("feedback"):
                    self.assertIn("## Feedback form", text)
                if d["kind"] == "review":
                    self.assertIn("## Review agenda", text)
                demo_files = sorted(p.name for p in (ROOT / "demos" / rel).iterdir() if re.match(r"^\d{2}_", p.name))
                for f in demo_files:
                    self.assertRegex(text, rf"^## Demo \d+: {re.escape(f)}", f"no section for demo {f}")
                # minutes table sums into the day band
                glance = text.split("## Day at a glance", 1)[1].split("\n## ", 1)[0]
                mins = [int(m) for m in re.findall(r"^\|[^|]*\|\s*(\d+)\s*\|", glance, re.M)]
                total = sum(mins[:-1]) if len(mins) > 1 and mins[-1] == sum(mins[:-1]) else sum(mins)
                self.assertTrue(M["dayMinutesMin"] <= total <= M["dayMinutesMax"], f"day sums to {total} min")
                sols = list((TRAINER / rel / "solutions").glob("*.py"))
                self.assertTrue(sols, "solutions/ must contain the module")
                starters = [p.stem for p in (ROOT / "exercises" / rel / "starter").glob("*.py")]
                self.assertTrue(any(s.stem in starters for s in sols), "solution module name must match starter module")


if __name__ == "__main__":
    unittest.main()
