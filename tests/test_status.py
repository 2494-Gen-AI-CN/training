"""STATUS.md shape. The file is hand-written and stays the source for milestones and open items; the work
tracker (D-0035) parses its Phase line and two tables, so a malformed row must fail here instead of
silently vanishing from tracker.html.
"""

from __future__ import annotations

import re
import sys
import unittest

from helpers import HARNESS, ROOT

sys.path.insert(0, str(HARNESS))
import build_tracker as bt  # noqa: E402

STATUS = ROOT / "STATUS.md"


class StatusShapeTests(unittest.TestCase):
    def setUp(self):
        self.text = STATUS.read_text(encoding="utf-8")

    def test_phase_and_last_updated(self):
        self.assertRegex(self.text, re.compile(r"^\*\*Phase:\*\* \S", re.M), "STATUS.md needs a '**Phase:** ...' line")
        self.assertRegex(self.text, re.compile(r"^\*\*Last updated:\*\* \d{4}-\d{2}-\d{2}\s*$", re.M),
                         "STATUS.md needs '**Last updated:** YYYY-MM-DD'")

    def test_phase_is_a_summary_with_next_steps(self):
        """One short paragraph (where things stand, then 'Next, in order:' steps split by ';'); history goes in the Log."""
        phase = re.search(r"^\*\*Phase:\*\* (.*)$", self.text, re.M).group(1)
        self.assertLess(len(phase), 1600, "the Phase line is a summary; move history to the Log section")
        m = re.search(r"Next, in order:\s*(.+)$", phase)
        self.assertIsNotNone(m, "the Phase line ends with 'Next, in order: step; step; ...'")
        steps = [s.strip() for s in m.group(1).rstrip(". ").split(";") if s.strip()]
        self.assertGreaterEqual(len(steps), 2, "list the next steps separated by semicolons")

    def test_milestones_table(self):
        self.assertIn(bt.MILESTONE_HEADER, self.text.splitlines(), "Milestones table header changed")
        rows = bt._table(self.text, bt.MILESTONE_HEADER)
        self.assertTrue(rows)
        for r in rows:
            self.assertEqual(4, len(r), f"milestone row needs 4 columns: {r}")
        self.assertEqual([str(i) for i in range(1, len(rows) + 1)], [r[0] for r in rows], "milestones are numbered 1..n in order")
        for r in rows:
            self.assertTrue(r[2] == "—" or bt.ISO_RE.search(r[2]), f"milestone {r[0]}: Done is '—' or carries a YYYY-MM-DD date, got '{r[2]}'")

    def test_open_items_table(self):
        self.assertIn(bt.OPEN_HEADER, self.text.splitlines(), "Open items table header changed")
        rows = bt._table(self.text, bt.OPEN_HEADER)
        self.assertTrue(rows)
        ids = [r[0] for r in rows]
        for r in rows:
            self.assertEqual(5, len(r), f"open-item row needs 5 columns (no ' | ' inside a cell): {r[:2]}")
            self.assertRegex(r[0], r"^O-\d+$")
            self.assertTrue(r[1].strip("~ "), f"{r[0]}: empty item")
        self.assertEqual(len(ids), len(set(ids)), "open-item IDs are unique")
        nums = sorted(int(i[2:]) for i in ids)
        self.assertEqual(list(range(1, len(nums) + 1)), nums, "open-item IDs run O-1..O-n with no gap")

    def test_log_section(self):
        self.assertRegex(self.text, re.compile(r"^## Log\s*$", re.M))
        log = self.text.split("## Log", 1)[1]
        self.assertRegex(log, re.compile(r"^- \d{4}-\d{2}-\d{2} ", re.M), "log lines start with '- YYYY-MM-DD'")


if __name__ == "__main__":
    unittest.main()
