"""curriculum.json contract + calendar derivation + index.html sync."""

from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
import unittest

from helpers import DOCS, HARNESS, ROOT, all_days, all_slots, curriculum, load_json

sys.path.insert(0, str(HARNESS))
import build_index  # noqa: E402

SLUG_RE = re.compile(r"^day-[1-5]-[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RE = re.compile(r"^w\d{2}d[1-5]$")
HOLIDAY_SLOT_KEYS = {"day", "kind"}


class CurriculumTests(unittest.TestCase):
    def setUp(self):
        self.cur = curriculum()

    def test_eleven_weeks_of_five_weekday_slots(self):
        """Each week has exactly slots 1..5; each slot is a teaching day or a holiday (D-0014)."""
        self.assertEqual(11, len(self.cur["weeks"]))
        for w in self.cur["weeks"]:
            self.assertEqual(5, len(w["days"]), w["dir"])
            self.assertEqual(f"week-{w['week']:02d}", w["dir"])
            self.assertEqual([1, 2, 3, 4, 5], [d["day"] for d in w["days"]])
            self.assertTrue(build_index.teaching_days(w), f"{w['dir']} has no teaching day")
            for d in w["days"]:
                if d.get("kind") == "holiday":
                    self.assertEqual(HOLIDAY_SLOT_KEYS, set(d), f"{w['dir']} holiday slot {d['day']} carries extra keys {set(d) - HOLIDAY_SLOT_KEYS}")

    def test_teaching_day_counts_match_decision(self):
        """D-0013: week 1 = 4 days, week 7 = 3, week 11 = 4, everything else 5."""
        expected = {1: 4, 7: 3, 11: 4}
        for w in self.cur["weeks"]:
            self.assertEqual(expected.get(w["week"], 5), len(build_index.teaching_days(w)), w["dir"])
        self.assertEqual(55 - len(self.cur["holidays"]), sum(1 for _ in all_days()))

    def test_day_fields_and_enums(self):
        for w, d, rel in all_days():
            with self.subTest(rel=rel):
                for k in ("day", "slug", "id", "kind", "gate", "demoFormat", "status", "title", "subtitle", "subtopics"):
                    self.assertIn(k, d)
                self.assertNotIn("feedback", d, "feedback is derived (last teaching day); never hand-set")
                self.assertNotIn("date", d, "dates are derived from startDate; never hand-typed")
                self.assertRegex(d["slug"], SLUG_RE)
                self.assertTrue(d["slug"].startswith(f"day-{d['day']}-"))
                self.assertEqual(f"w{w['week']:02d}d{d['day']}", d["id"])
                self.assertIn(d["kind"], ("lesson", "review"))
                self.assertIn(d["gate"], ("full", "light"))
                self.assertIn(d["demoFormat"], ("py", "nb", "none"))
                self.assertIn(d["status"], ("planned", "live"))
                if "taught" in d:  # D-0030: set by the delivery-day close, after the session
                    self.assertRegex(d["taught"], r"^20\d\d-\d\d-\d\d$")
                    self.assertEqual("live", d["status"], "a taught day must be live")
                    slot = build_index.slot_date(self.cur, w["week"], d["day"])
                    self.assertGreaterEqual(dt.date.fromisoformat(d["taught"]), slot, "taught before its calendar date")
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

    # ---------------------------------------------------------------- calendar (D-0013, D-0014)
    def test_calendar_top_level_fields(self):
        for k in ("startDate", "endDate", "timezone", "holidays"):
            self.assertIn(k, self.cur)
        start, end = dt.date.fromisoformat(self.cur["startDate"]), dt.date.fromisoformat(self.cur["endDate"])
        self.assertLess(start, end)
        self.assertLess(start.weekday(), 5, "startDate must be a weekday")
        self.assertLess(end.weekday(), 5, "endDate must be a weekday")
        self.assertRegex(self.cur["timezone"], r"^[A-Za-z_]+/[A-Za-z_]+$")

    def test_holidays_are_weekdays_inside_the_grid_and_unique(self):
        grid_start = build_index.grid_start(self.cur)
        grid_end = build_index.slot_date(self.cur, len(self.cur["weeks"]), 5)
        dates = []
        for h in self.cur["holidays"]:
            with self.subTest(h=h):
                for k in ("date", "label", "scope"):
                    self.assertIn(k, h)
                self.assertIn(h["scope"], ("ca", "us", "trainer"))
                d = dt.date.fromisoformat(h["date"])
                self.assertLess(d.weekday(), 5, f"holiday {h['date']} is on a weekend")
                self.assertTrue(grid_start <= d <= grid_end, f"holiday {h['date']} outside the training grid {grid_start}..{grid_end}")
                dates.append(d)
        self.assertEqual(len(dates), len(set(dates)), "duplicate holiday date")

    def test_holiday_slots_match_holiday_dates(self):
        hols = set(build_index.holiday_map(self.cur))
        seen = set()
        for w, d in all_slots():
            date = build_index.slot_date(self.cur, w["week"], d["day"])
            self.assertEqual(d.get("kind") == "holiday", date in hols, f"{w['dir']} day {d['day']} ({date})")
            if date in hols:
                seen.add(date)
        self.assertEqual(hols, seen, "every holiday must land on exactly one grid slot")
        for w in self.cur["weeks"]:
            build_index.expand_week(self.cur, w)  # must not raise

    def test_derived_dates_increase_and_bracket_start_end(self):
        dates = [build_index.slot_date(self.cur, w["week"], d["day"]) for w, d in all_slots()]
        self.assertEqual(sorted(dates), dates, "derived dates must be strictly increasing")
        self.assertEqual(len(dates), len(set(dates)), "two slots share a date")
        for a, b in zip(dates, dates[1:]):
            self.assertLess(a, b)
        first_week, last_week = self.cur["weeks"][0], self.cur["weeks"][-1]
        first = build_index.teaching_days(first_week)[0]
        last = build_index.last_teaching_day(last_week)
        self.assertEqual(self.cur["startDate"], build_index.slot_date(self.cur, first_week["week"], first["day"]).isoformat(),
                         "week 1's first teaching day must be startDate")
        self.assertEqual(self.cur["endDate"], build_index.slot_date(self.cur, last_week["week"], last["day"]).isoformat(),
                         "the last teaching day must be endDate")

    def test_feedback_is_last_teaching_day(self):
        for w in self.cur["weeks"]:
            flagged = [d["day"] for d in w["days"] if build_index.is_feedback(w, d)]
            self.assertEqual([build_index.last_teaching_day(w)["day"]], flagged, w["dir"])

    def test_readme_lists_dates_and_holidays(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(self.cur["startDate"], readme)
        self.assertIn(self.cur["endDate"], readme)
        for h in self.cur["holidays"]:
            self.assertIn(h["date"], readme, f"README must list holiday {h['date']}")

    # ---------------------------------------------------------------- generated index block
    def test_index_weeks_block_in_sync(self):
        html = (DOCS / "index.html").read_text(encoding="utf-8")
        self.assertIn(build_index.BEGIN, html)
        self.assertIn(build_index.END, html)
        self.assertEqual(build_index.splice(html, build_index.render()), html,
                         "docs/index.html WEEKS block is stale — run: python harness/build_index.py")

    def test_index_block_is_generated_and_carries_dates(self):
        block = build_index.render()
        self.assertIn(build_index.GENERATED_MARK, block)
        self.assertIn("window.CAL = ", block)
        self.assertEqual(55 + len(self.cur["holidays"]), block.count('"date": "'), "one date per weekday slot plus the CAL holiday list")
        self.assertEqual(len(self.cur["holidays"]), block.count('"kind": "holiday"'))
        for h in self.cur["holidays"]:
            self.assertIn(h["label"], block)
        # the page must never contain a hand-typed date outside the generated block
        html = (DOCS / "index.html").read_text(encoding="utf-8")
        outside = html[:html.index(build_index.BEGIN)] + html[html.index(build_index.END) + len(build_index.END):]
        self.assertIsNone(re.search(r"\b20\d\d-\d\d-\d\d\b", outside), "hand-typed ISO date outside the generated block")

    def test_args_for_runs_for_every_teaching_day_and_refuses_holidays(self):
        for w in self.cur["weeks"]:
            slots = [str(d["day"]) for d in build_index.teaching_days(w)]
            res = subprocess.run([sys.executable, str(HARNESS / "args_for.py"), str(w["week"]), *slots, "--today", "2026-01-01"],
                                 capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(0, res.returncode, res.stderr)
            self.assertIn('"days"', res.stdout)
            self.assertIn('"date"', res.stdout)
            self.assertIn('"dateLabel"', res.stdout)
            for d in w["days"]:
                if d.get("kind") == "holiday":
                    res = subprocess.run([sys.executable, str(HARNESS / "args_for.py"), str(w["week"]), str(d["day"])],
                                         capture_output=True, text=True, encoding="utf-8")
                    self.assertEqual(2, res.returncode, f"{w['dir']} day {d['day']} should be refused")
                    self.assertIn("holiday", res.stderr)

    def test_live_days_have_all_public_artifacts(self):
        for w, d, rel in all_days():
            if d["status"] != "live":
                continue
            with self.subTest(rel=rel):
                self.assertTrue((DOCS / "weeks" / f"{rel}.html").exists())
                # D-0030: answer keys are public only once taught; demoFormat none days never have a demos/ folder
                if d.get("taught") and d["demoFormat"] != "none":
                    self.assertTrue((ROOT / "demos" / rel / "README.md").exists())
                else:
                    self.assertFalse((ROOT / "demos" / rel).exists(), f"demos/{rel} must not exist before the day is taught")
                self.assertTrue((ROOT / "exercises" / rel / "README.md").exists())
                self.assertTrue((HARNESS / "research" / f"{rel}.md").exists())


if __name__ == "__main__":
    unittest.main()
