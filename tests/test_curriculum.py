"""curriculum.json contract + index.html sync."""

from __future__ import annotations

import re
import subprocess
import sys
import unittest

from helpers import DOCS, HARNESS, ROOT, all_days, curriculum, load_json

sys.path.insert(0, str(HARNESS))
import build_index  # noqa: E402

SLUG_RE = re.compile(r"^day-[1-5]-[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RE = re.compile(r"^w\d{2}d[1-5]$")


class CurriculumTests(unittest.TestCase):
    def setUp(self):
        self.cur = curriculum()

    def test_eleven_weeks_of_five_days(self):
        self.assertEqual(11, len(self.cur["weeks"]))
        for w in self.cur["weeks"]:
            self.assertEqual(5, len(w["days"]), w["dir"])
            self.assertEqual(f"week-{w['week']:02d}", w["dir"])
            self.assertEqual([1, 2, 3, 4, 5], [d["day"] for d in w["days"]])

    def test_day_fields_and_enums(self):
        for w, d, rel in all_days():
            with self.subTest(rel=rel):
                for k in ("day", "slug", "id", "kind", "gate", "demoFormat", "status", "title", "subtitle", "subtopics"):
                    self.assertIn(k, d)
                self.assertRegex(d["slug"], SLUG_RE)
                self.assertTrue(d["slug"].startswith(f"day-{d['day']}-"))
                self.assertEqual(f"w{w['week']:02d}d{d['day']}", d["id"])
                self.assertIn(d["kind"], ("lesson", "review"))
                self.assertIn(d["gate"], ("full", "light"))
                self.assertIn(d["demoFormat"], ("py", "nb"))
                self.assertIn(d["status"], ("planned", "live"))
                self.assertTrue(d["subtopics"])
                self.assertIn(w["phase"], self.cur["phases"])
                self.assertIn(w["project"], self.cur["projects"])

    def test_slugs_and_ids_unique(self):
        rels = [rel for _, _, rel in all_days()]
        ids = [d["id"] for _, d, _ in all_days()]
        self.assertEqual(len(rels), len(set(rels)))
        self.assertEqual(len(ids), len(set(ids)))

    def test_gate_tiers_match_decision(self):
        full = {5, 8, 9, 10, 11}
        for w, d, rel in all_days():
            self.assertEqual("full" if w["week"] in full else "light", d["gate"], rel)

    def test_index_weeks_block_in_sync(self):
        html = (DOCS / "index.html").read_text(encoding="utf-8")
        self.assertIn(build_index.BEGIN, html)
        self.assertIn(build_index.END, html)
        self.assertEqual(build_index.splice(html, build_index.render()), html,
                         "docs/index.html WEEKS block is stale — run: python harness/build_index.py")

    def test_args_for_runs_for_every_day(self):
        for w in self.cur["weeks"]:
            res = subprocess.run([sys.executable, str(HARNESS / "args_for.py"), str(w["week"]), "1", "2", "3", "4", "5", "--today", "2026-01-01"],
                                 capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(0, res.returncode, res.stderr)
            self.assertIn('"days"', res.stdout)

    def test_live_days_have_all_public_artifacts(self):
        for w, d, rel in all_days():
            if d["status"] != "live":
                continue
            with self.subTest(rel=rel):
                self.assertTrue((DOCS / "weeks" / f"{rel}.html").exists())
                self.assertTrue((ROOT / "demos" / rel / "README.md").exists())
                self.assertTrue((ROOT / "exercises" / rel / "README.md").exists())
                self.assertTrue((HARNESS / "research" / f"{rel}.md").exists())


if __name__ == "__main__":
    unittest.main()
