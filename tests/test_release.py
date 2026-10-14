"""harness/release_week.py, the Friday gate (D-0052): authored -> live only when the week is ready.

Every fixture lives in a temporary tree (a copy of the curriculum, fake last-tests.json, delivery.json files,
pages and exercise READMEs); the real harness/curriculum.json is never written. The plan check is patched to pass,
since plan_check reads the real curriculum and a fixture plan would only re-test plan_check.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import HARNESS, ROOT, curriculum

sys.path.insert(0, str(HARNESS))
import build_index  # noqa: E402
import release_week  # noqa: E402

TODAY = "2026-10-16"  # a Friday of week 1 in the fixture calendar (week 1 Monday 2026-10-12)
WEEK1_MONDAY = "2026-10-12"
WEEK2_MONDAY = "2026-10-19"
PAGE_DAY = "2026-10-15"  # fixture pages' mtime date: before the fixture last-tests date


class ReleaseWeekTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "harness").mkdir()
        self.cur = curriculum()
        self.assertEqual(WEEK1_MONDAY, build_index.grid_start(self.cur).isoformat(), "fixture dates assume this calendar")
        self.w1 = next(w for w in self.cur["weeks"] if w["week"] == 1)
        self.w2 = next(w for w in self.cur["weeks"] if w["week"] == 2)
        for d in build_index.teaching_days(self.w2):
            d["status"] = "authored"
            d.pop("taught", None)
        self._write_cur()
        self._last_tests(ok=True)
        for d in build_index.teaching_days(self.w2):
            rel = self._rel(self.w2, d)
            self._set_mtime(self._touch(f"docs/weeks/{rel}.html", "<!doctype html>\n"), PAGE_DAY)
            self._touch(f"exercises/{rel}/README.md", "# exercise\n")
        # week 1 days dated before the fixture Friday are closed
        for d in build_index.teaching_days(self.w1):
            if build_index.slot_date(self.cur, 1, d["day"]) < dt.date.fromisoformat(TODAY):
                self._delivery(d)
        self._touch("docs/index.html", f"<html>\n{build_index.BEGIN}\n{build_index.END}\n</html>\n")
        self.plan = mock.patch.object(release_week, "plan_problems", return_value=[]).start()
        self.notes = mock.patch.object(release_week, "notes_findings", return_value=[]).start()
        self.addCleanup(mock.patch.stopall)
        self.addCleanup(self._tmp.cleanup)

    # ------------------------------------------------------------ fixture helpers
    @staticmethod
    def _rel(week: dict, day: dict) -> str:
        return f"{week['dir']}/{day['slug']}"

    def _touch(self, rel_path: str, text: str) -> Path:
        p = self.root / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        return p

    @staticmethod
    def _set_mtime(path: Path, day: str, hour: int = 12) -> None:
        ts = dt.datetime.combine(dt.date.fromisoformat(day), dt.time(hour)).timestamp()  # local time
        os.utime(path, (ts, ts))

    def _write_cur(self) -> None:
        with open(self.root / "harness" / "curriculum.json", "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(self.cur, indent=2, ensure_ascii=False) + "\n")

    def _cur_bytes(self) -> bytes:
        return (self.root / "harness" / "curriculum.json").read_bytes()

    def _last_tests(self, ok: bool, date: str = TODAY, at: str | None = None) -> None:
        rec = {"date": date, **({"at": at} if at else {}), "ran": 10, "ok": ok, "failures": 0 if ok else 2,
               "errors": 0, "skipped": 0}
        self._touch("harness/last-tests.json", json.dumps(rec) + "\n")

    def _delivery(self, day: dict) -> Path:
        return self._touch(f"trainer/{self._rel(self.w1, day)}/delivery.json", json.dumps({"day": day["id"]}) + "\n")

    def _run(self, *extra: str, today: str = TODAY) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = release_week.main(["2", "--today", today, *extra], root=self.root)
        return code, buf.getvalue()

    def _w2(self, day_no: int) -> dict:
        return next(d for d in self.w2["days"] if d["day"] == day_no)

    # ------------------------------------------------------------ tests
    def test_refuses_while_a_day_is_planned(self):
        self._w2(1)["status"] = "planned"
        self._write_cur()
        before = self._cur_bytes()
        code, out = self._run()
        self.assertEqual(1, code, out)
        self.assertIn("w02d1 is planned (not authored)", out)
        self.assertEqual(before, self._cur_bytes(), "a refused release writes nothing")

    def test_flips_authored_to_live_byte_exact(self):
        code, out = self._run()
        self.assertEqual(0, code, out)
        ids = [d["id"] for d in build_index.teaching_days(self.w2)]
        for d in build_index.teaching_days(self.w2):
            d["status"] = "live"
        raw = self._cur_bytes()
        self.assertEqual((json.dumps(self.cur, indent=2, ensure_ascii=False) + "\n").encode("utf-8"), raw)
        self.assertNotIn(b"\r\n", raw)
        self.assertIn(f"release_week W2: {','.join(ids)} authored -> live", out)
        index = (self.root / "docs" / "index.html").read_text(encoding="utf-8")
        for d in build_index.teaching_days(self.w2):
            self.assertIn(f"weeks/{self._rel(self.w2, d)}.html", index, "the released week is linked")
        # a second run has nothing left to do
        code, out = self._run()
        self.assertEqual(0, code, out)
        self.assertIn("nothing to release: every day of week 2 is live", out)

    def test_refuses_on_red_tests(self):
        self._last_tests(ok=False)
        before = self._cur_bytes()
        code, out = self._run()
        self.assertEqual(1, code, out)
        self.assertIn("last contract test run is red (2 failure(s)", out)
        self.assertEqual(before, self._cur_bytes())

    def test_refuses_on_missing_page_or_exercise(self):
        d = self._w2(3)
        (self.root / "docs" / "weeks" / f"{self._rel(self.w2, d)}.html").unlink()
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        self.assertIn(f"w02d3 is authored but docs/weeks/{self._rel(self.w2, d)}.html is missing", out)

    def test_current_week_day_must_be_closed(self):
        """Every current-week day dated strictly before --today needs delivery.json; --today itself is not closed yet."""
        last = max((d for d in build_index.teaching_days(self.w1)
                    if build_index.slot_date(self.cur, 1, d["day"]) < dt.date.fromisoformat(TODAY)), key=lambda d: d["day"])
        rec = self.root / "trainer" / self._rel(self.w1, last) / "delivery.json"
        rec.unlink()
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        self.assertIn(f"{last['id']} (", out)
        self.assertIn("delivery.json is missing", out)
        self._delivery(last)
        code, out = self._run("--check")
        self.assertEqual(0, code, out)
        self.assertIn("OK: week 2 ready to release", out)

    def test_tests_at_is_compared_with_the_page_mtime(self):
        """With `at` (log_run.py tests), a page edited later the same day refuses; earlier passes."""
        page = f"docs/weeks/{self._rel(self.w2, self._w2(2))}.html"
        self._last_tests(ok=True, date=PAGE_DAY, at=f"{PAGE_DAY}T13:00:00")
        code, out = self._run("--check")  # pages at noon, tests at 13:00
        self.assertEqual(0, code, out)
        self._set_mtime(self.root / page, PAGE_DAY, hour=14)
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        self.assertIn(f"last-tests.json ({PAGE_DAY}T13:00:00) predates the newest authored page ({page}, {PAGE_DAY}T14:00:00)", out)

    def test_past_unclosable_day_does_not_block(self):
        """close_day.py closes loose days only (O-18 adds py / nb): a past py day without delivery.json is no reason."""
        d = next(x for x in build_index.teaching_days(self.w1)
                 if build_index.slot_date(self.cur, 1, x["day"]) < dt.date.fromisoformat(TODAY))
        d["demoFormat"] = "py"
        self._write_cur()
        (self.root / "trainer" / self._rel(self.w1, d) / "delivery.json").unlink()
        code, out = self._run("--check")
        self.assertEqual(0, code, out)
        self.assertNotIn(d["id"], out)

    def test_index_without_markers_writes_nothing(self):
        self._touch("docs/index.html", "<html>no markers</html>\n")
        before = self._cur_bytes()
        with self.assertRaises(SystemExit) as cm:
            self._run()
        self.assertIn("markers missing", str(cm.exception.code))
        self.assertEqual(before, self._cur_bytes())

    def test_notes_finding_refuses(self):
        page = f"docs/weeks/{self._rel(self.w2, self._w2(1))}.html"
        self.notes.side_effect = lambda p: ["prose words 900 outside 4300..7200"] if p.as_posix().endswith(page) else []
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        self.assertIn(f"notes_check {page}: prose words 900 outside 4300..7200", out)
        self.assertEqual(len(build_index.teaching_days(self.w2)), self.notes.call_count, "one notes_check per authored page")

    def test_refuses_when_tests_predate_the_newest_page(self):
        """Without `at` (an older last-tests.json) the dates are compared: a page touched on a later day refuses."""
        d = self._w2(4)
        page = f"docs/weeks/{self._rel(self.w2, d)}.html"
        self._set_mtime(self.root / page, "2026-10-17")
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        self.assertIn(f"last-tests.json ({TODAY}) predates the newest authored page ({page}, 2026-10-17)", out)
        self._set_mtime(self.root / page, TODAY)  # same day as the run: fine
        code, out = self._run("--check")
        self.assertEqual(0, code, out)

    def test_release_after_friday_still_checks_last_week(self):
        """On week 2's Monday no week-2 day is due, but last week's unclosed Friday still blocks the release."""
        fri = max(build_index.teaching_days(self.w1), key=lambda d: d["day"])
        self.assertFalse((self.root / "trainer" / self._rel(self.w1, fri) / "delivery.json").exists())
        code, out = self._run("--check", today=WEEK2_MONDAY)
        self.assertEqual(1, code, out)
        self.assertIn(f"{fri['id']} (", out)
        self.assertIn("is not closed", out)
        self._delivery(fri)
        code, out = self._run("--check", today=WEEK2_MONDAY)
        self.assertEqual(0, code, out)

    def test_rejected_run_record_writes_nothing(self):
        import log_run
        before = self._cur_bytes()
        with mock.patch.object(log_run, "validate", return_value=["boom"]):
            with self.assertRaises(SystemExit) as cm:
                self._run()
        self.assertIn("nothing was written", str(cm.exception.code))
        self.assertEqual(before, self._cur_bytes())
        self.assertFalse((self.root / "harness" / "run-report.tmp.json").exists())

    def test_plan_check_runs_once_per_gate(self):
        self._run("--check")
        self.assertEqual(1, self.plan.call_count)
        self.plan.return_value = ["week-02.md: something"]
        (self.root / "harness" / "plans").mkdir()
        self._touch("harness/plans/week-02.md", "# Week 02 plan\n")
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        self.assertIn("harness/plans/week-02.md fails plan_check (1 problem(s))", out)
        self.assertEqual(2, self.plan.call_count)

    def test_check_writes_nothing(self):
        before = self._cur_bytes()
        code, out = self._run("--check")
        self.assertEqual(0, code, out)
        self.assertIn(f"OK: week 2 ready to release ({len(build_index.teaching_days(self.w2))} days authored)", out)
        self.assertEqual(before, self._cur_bytes())

    def test_every_day_live_is_nothing_to_release(self):
        for d in build_index.teaching_days(self.w2):
            d["status"] = "live"
        self._write_cur()
        for extra in ((), ("--check",)):
            code, out = self._run(*extra)
            self.assertEqual(0, code, out)
            self.assertIn("nothing to release: every day of week 2 is live", out)


class ReleaseWeekRealRepoTests(unittest.TestCase):
    def test_week2_check_refuses_on_the_real_repo(self):
        cur_path = HARNESS / "curriculum.json"
        before = cur_path.read_bytes()
        res = subprocess.run([sys.executable, str(HARNESS / "release_week.py"), "2", "--check", "--today", TODAY],
                             capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        self.assertEqual(before, cur_path.read_bytes(), "--check must never write")
        cur = json.loads(before.decode("utf-8"))
        w2 = next(w for w in cur["weeks"] if w["week"] == 2)
        if next(d for d in w2["days"] if d["day"] == 1).get("status") != "planned":
            self.skipTest("w02d1 is no longer planned; the fixture tests above cover the gate")
        self.assertNotEqual(0, res.returncode, res.stdout + res.stderr)
        self.assertIn("w02d1 is planned (not authored)", res.stdout)


if __name__ == "__main__":
    unittest.main()
