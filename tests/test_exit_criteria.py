"""Exit criteria as a harness input (D-0063): the registry in curriculum.json, the parser over
Curricula/Exit-Criteria/qc-N-*.md, the week args and the CLI of harness/exit_criteria.py."""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from collections import Counter

from helpers import HARNESS, ROOT, curriculum

sys.path.insert(0, str(HARNESS))
import exit_criteria as ec  # noqa: E402

SOURCE_NAME_RE = re.compile(r"^qc-\d-[a-z0-9-]+\.md$")


def run_cli(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HARNESS / "exit_criteria.py"), *argv], capture_output=True, text=True, encoding="utf-8")


class RegistryTests(unittest.TestCase):
    def test_registry_shape(self):
        cur = curriculum()
        reg = ec.registry(cur)
        self.assertEqual(["qc1", "qc2", "qc3", "qc4", "qc5", "qc6"], [g["id"] for g in reg["groups"]])
        self.assertEqual(3, reg["fromWeek"])
        owners = Counter(w for g in reg["groups"] for w in g["weeks"])
        for wn in range(1, 12):
            self.assertEqual(1, owners[wn], f"week {wn} must be in exactly one group")
        self.assertEqual(set(range(1, 12)), set(owners))
        self.assertTrue((ROOT / reg["sourceDir"]).is_dir(), reg["sourceDir"])
        for g in reg["groups"]:
            self.assertRegex(g["source"], SOURCE_NAME_RE)


class ParserTests(unittest.TestCase):
    def test_every_present_source_parses(self):
        self.assertEqual([], ec.check_sources())
        published = [g for g in ec.load_groups() if g["exists"]]
        self.assertTrue(published, "no published exit-criteria source")
        for g in published:
            with self.subTest(group=g["id"]):
                ids = [c["id"] for c in g["criteria"]]
                self.assertEqual(len(ids), len(set(ids)), "duplicate ids")
                for cid in ids:
                    self.assertRegex(cid, ec.ID_RE)
                per = {}
                for c in g["criteria"]:
                    per.setdefault((c["sectionSlug"], c["tier"]), []).append(c["n"])
                for key, ns in per.items():
                    self.assertEqual(list(range(1, len(ns) + 1)), ns, f"{key}: numbering not contiguous from 01")

    def test_one_and_two_column_rows_and_normalisation(self):
        text = (
            "# QC - X\n\n"
            "## Agile\n\n"
            "| Criteria Difficulty Exit Criteria |\n"
            "|-----------------------------------|\n"
            "| Required Describe   the scrum ceremonies. |\n"
            "| Stretch Can explain Python's “Call by Object Reference” system |\n\n"
            "## Git\n\n"
            "| Criteria Difficulty | Exit Criteria |\n"
            "|---------------------|---------------|\n"
            "| Preferred           | Perform element‑wise operations. |\n"
        )
        parsed = ec.parse_source(text, "fixture.md")
        self.assertEqual("QC - X", parsed["title"])
        self.assertEqual(["Agile", "Git"], [s["name"] for s in parsed["sections"]])
        crit = ec.number("qcx", parsed)
        self.assertEqual(["qcx.agile.R01", "qcx.agile.S01", "qcx.git.P01"], [c["id"] for c in crit])
        self.assertEqual("Describe the scrum ceremonies.", crit[0]["text"])
        self.assertEqual('Can explain Python\'s "Call by Object Reference" system', crit[1]["text"])
        self.assertEqual("Perform element-wise operations.", crit[2]["text"])
        for c in crit:
            self.assertTrue(c["text"].isascii(), c["text"])

    def test_known_rows(self):
        qc2 = ec.load_group("qc2")
        self.assertIsNotNone(qc2)
        self.assertTrue(qc2["exists"])
        self.assertEqual("Describe the difference between DROP, DELETE, and TRUNCATE functionality", qc2["byId"]["qc2.sql.R07"]["text"])
        tiers = Counter(c["tier"] for c in qc2["criteria"])
        self.assertEqual({"Required": 21, "Preferred": 16, "Stretch": 8}, dict(tiers))
        qc1 = ec.load_group("qc1")
        self.assertTrue(qc1["exists"])
        self.assertEqual(["Agile", "Git", "Python"], [s["name"] for s in qc1["sections"]])
        for s in qc1["sections"]:
            with self.subTest(section=s["name"]):
                self.assertTrue(any(c["tier"] == "Required" for c in s["criteria"]), "no Required row")

    def test_malformed_row_raises(self):
        text = "# QC - X\n\n## Git\n\n| A | B |\n|---|---|\n| Required | ok |\n| no tier here |\n"
        with self.assertRaises(ValueError) as cm:
            ec.parse_source(text, "bad.md")
        self.assertIn(":8:", str(cm.exception))
        self.assertIn("bad.md", str(cm.exception))


class WeekArgsTests(unittest.TestCase):
    def test_week_args(self):
        cur = curriculum()
        w3 = ec.week_args(cur, 3)
        self.assertTrue(w3["active"])
        self.assertEqual("qc2", w3["id"])
        self.assertEqual(45, len(w3["criteria"]))
        self.assertEqual("../../exit-criteria/qc-2-sql.html", w3["pageRel"])
        self.assertEqual({"id", "section", "tier", "text"}, set(w3["criteria"][0]))
        w1 = ec.week_args(cur, 1)
        self.assertFalse(w1["active"])
        self.assertEqual("week before fromWeek", w1["reason"])
        self.assertEqual("qc1", w1["id"])
        qc3 = ec.load_group("qc3")
        if not qc3["exists"]:
            w4 = ec.week_args(cur, 4)
            self.assertFalse(w4["active"])
            self.assertEqual("source not published", w4["reason"])
            self.assertEqual("qc3", w4["id"])


class CliTests(unittest.TestCase):
    def test_show_and_check(self):
        show = run_cli("show", "qc2")
        self.assertEqual(0, show.returncode, show.stderr)
        self.assertIn("qc2.sql.R07", show.stdout)
        self.assertIn("| ID | Tier | Section | Criterion |", show.stdout)
        check = run_cli("check")
        self.assertEqual(0, check.returncode, check.stdout + check.stderr)
        self.assertIn("OK", check.stdout)
        bad = run_cli("show", "qc9")
        self.assertEqual(2, bad.returncode)


if __name__ == "__main__":
    unittest.main()
