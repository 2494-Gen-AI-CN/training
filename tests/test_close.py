"""harness/close_day.py, the delivery-day close of a walkthrough day (D-0050, D-0055).

Pure helpers only: nothing here touches curriculum.json, trainer/ or the demo-repo clone.
The git tests build a throwaway repository in a temp directory and skip when git is missing.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import HARNESS, all_days

sys.path.insert(0, str(HARNESS))
import close_day  # noqa: E402

CFG = {"demoRepo": {"url": "https://github.com/2494-Gen-AI-CN/demos", "prepBranch": "prep/week-{WW}"}}
DAY = {"id": "w02d1", "title": "Modules"}
SHA = "0123456789abcdef0123456789abcdef01234567"
BLOCKS = [{"name": "01-desk-modules", "slot": "AM", "commitMessage": "Restart the ticket desk"},
          {"name": "02-pip-and-module-split", "slot": "PM", "commitMessage": "Split the desk into a module"}]


@unittest.skipUnless(shutil.which("git"), "git not installed")
class GitTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str, when: str | None = None) -> None:
        env = dict(os.environ)
        if when:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)

    def _repo(self, t: str) -> Path:
        repo = Path(t)
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "Test")
        self._git(repo, "config", "user.email", "test@example.com")
        (repo / "ticket-desk").mkdir()
        (repo / "README.md").write_text("# demos\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "Initial commit", when="2026-10-10T10:00:00")
        return repo

    def _commit(self, repo: Path, msg: str, when: str, content: str) -> str:
        (repo / "ticket-desk").mkdir(exist_ok=True)   # git drops the empty folder on a branch switch
        (repo / "ticket-desk" / "ticket_desk.py").write_text(content, encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", msg, when=when)
        return close_day.head_sha(repo)

    def test_blocks_are_matched_by_message_and_classified_against_prep(self):
        with tempfile.TemporaryDirectory() as t:
            repo = self._repo(t)
            # prep branch: both blocks, authored before the day
            self._git(repo, "switch", "-q", "-c", "prep/week-02")
            prep1 = self._commit(repo, "Restart the ticket desk", "2026-10-15T10:00:00", "x = 1\n")
            prep2 = self._commit(repo, "Split the desk into a module", "2026-10-15T11:00:00", "x = 1\ny = 2\n")
            # live: the room reached block 1 exactly, block 2 diverged
            self._git(repo, "switch", "-q", "main")
            live1 = self._commit(repo, "Restart the ticket desk", "2026-10-19T10:00:00", "x = 1\n")
            live2 = self._commit(repo, "Split the desk into a module", "2026-10-19T14:00:00", "x = 1\ny = 3\n")
            self.assertTrue(close_day.branch_exists(repo, "prep/week-02"))
            self.assertFalse(close_day.branch_exists(repo, "prep/week-03"))
            prep = close_day.commits_on(repo, "prep/week-02")
            self.assertEqual([prep2, prep1], [s for s, _ in prep][:2])
            live = close_day.commits_dated(repo, "2026-10-19")
            self.assertEqual({live1, live2}, {s for s, _ in live})
            self.assertEqual([], close_day.commits_dated(repo, "2026-10-20"))
            matched = close_day.match_blocks(BLOCKS, prep, live, {}, repo, "ticket-desk")
            self.assertEqual(["reached", "diverged"], [b["state"] for b in matched])
            self.assertEqual((prep1, live1, ""), (matched[0]["prepSha"], matched[0]["liveSha"], matched[0]["diffstat"]))
            self.assertEqual((prep2, live2), (matched[1]["prepSha"], matched[1]["liveSha"]))
            self.assertIn("ticket_desk.py", matched[1]["diffstat"])
            # a block the room never reached; a --match override picks the live commit by hand
            third = [{"name": "03-x", "slot": "AM", "commitMessage": "Never typed"}]
            self.assertEqual("not reached", close_day.match_blocks(third, prep, live, {}, repo, "ticket-desk")[0]["state"])
            forced = close_day.match_blocks(third, prep, live, {"03-x": live2}, repo, "ticket-desk")[0]
            self.assertEqual(("reached", live2, None), (forced["state"], forced["liveSha"], forced["prepSha"]))
            self.assertEqual(live2, close_day.last_commit_by(repo, "2026-10-19"))
            self.assertEqual(live2, close_day.last_commit_by(repo, "2026-10-25"))
            self.assertEqual(prep2, close_day.last_commit_by(repo, "2026-10-16"), "the last commit on any branch by that date")


class ClassifyTests(unittest.TestCase):
    def test_states(self):
        self.assertEqual("not reached", close_day.classify("a", None, ""))
        self.assertEqual("reached", close_day.classify("a", "b", ""))
        self.assertEqual("reached", close_day.classify(None, "b", ""), "no prep commit: the live commit stands")
        self.assertEqual("diverged", close_day.classify("a", "b", " 1 file changed"))
        self.assertEqual({"a": "sha1", "b": "sha2"}, close_day.parse_matches(["a=sha1", " b = sha2 "]))
        with self.assertRaises(SystemExit):
            close_day.parse_matches(["nope"])


class LocateTests(unittest.TestCase):
    def test_none_day_is_refused(self):
        found = next(((w, d) for w, d, _ in all_days() if d["demoFormat"] == "none"), None)
        if found is None:
            self.skipTest("no demoFormat none day in the curriculum")
        week, day = found
        with self.assertRaises(SystemExit) as cm:
            close_day.locate(week["week"], day["day"])
        self.assertIn("nothing to close", str(cm.exception.code))

    def test_unreleased_day_is_refused(self):
        """D-0052: an authored or planned day is refused (dry run and --apply both go through plan -> locate)."""
        for status in ("authored", "planned"):
            day = {"id": "w02d1", "day": 1, "slug": "day-1-x", "demoFormat": "walkthrough", "status": status, "kind": "lesson"}
            week = {"week": 2, "dir": "week-02", "days": [day]}
            with self.subTest(status=status), mock.patch.object(close_day.bi, "load_curriculum", return_value={"weeks": [week]}):
                with self.assertRaises(SystemExit) as cm:
                    close_day.plan(2, 1, pull=False)
                msg = str(cm.exception.code)
                self.assertIn(f"w02d1 is '{status}', not live", msg)
                self.assertIn("python harness/release_week.py 2 --today", msg)
                self.assertNotIn("taught", day)


class RecordTests(unittest.TestCase):
    MATCHED = [{"name": "01-desk-modules", "slot": "AM", "commitMessage": "Restart the ticket desk", "prepSha": SHA, "liveSha": SHA, "state": "reached", "diffstat": ""},
               {"name": "02-pip-and-module-split", "slot": "PM", "commitMessage": "Split the desk into a module", "prepSha": SHA, "liveSha": "89abcdef" + SHA[8:], "state": "diverged", "diffstat": " ticket-desk/desk.py | 2 +-\n 1 file changed, 1 insertion(+), 1 deletion(-)"}]

    def test_delivery_record_key_order(self):
        rec = close_day.delivery_record(DAY, "2026-10-19", self.MATCHED, CFG, SHA, None)
        self.assertEqual(["day", "date", "format", "blocks", "demoRepo", "demoRepoSha", "notes"], list(rec))
        self.assertEqual("w02d1", rec["day"])
        self.assertEqual("walkthrough", rec["format"])
        self.assertEqual(["name", "slot", "commitMessage", "prepSha", "liveSha", "state", "diffstat"], list(rec["blocks"][0]))
        self.assertEqual(CFG["demoRepo"]["url"], rec["demoRepo"])
        self.assertEqual("", rec["notes"])
        self.assertEqual("prep/week-02", close_day.prep_branch(CFG, 2))

    def test_walkthrough_record_inserts_before_the_cheat_sheet_once(self):
        rec = close_day.walkthrough_record("2026-10-19", self.MATCHED[1], "ran 10 min long")
        self.assertTrue(rec.startswith("> **DELIVERY RECORD (2026-10-19)** DIVERGED."))
        self.assertIn("> ```", rec)
        self.assertIn("> Notes: ran 10 min long", rec)
        self.assertTrue(all(ln.startswith(">") for ln in rec.strip().splitlines()), "the record is one blockquote")
        with tempfile.TemporaryDirectory() as t:
            wt = Path(t) / "02-pip-and-module-split.md"
            wt.write_text("# Demo: X (`p0` -> `02-pip-and-module-split`)\n\n> **Objective:** o\n> **Time:** 75 min\n\n---\n\n## Presenter cheat-sheet\n\n| # |\n", encoding="utf-8")
            self.assertTrue(close_day.append_walkthrough(wt, rec, "2026-10-19"))
            self.assertFalse(close_day.append_walkthrough(wt, rec, "2026-10-19"))
            text = wt.read_text(encoding="utf-8")
            self.assertEqual(1, text.count("DELIVERY RECORD (2026-10-19)"))
            self.assertLess(text.index("DELIVERY RECORD"), text.index("## Presenter cheat-sheet"))
            self.assertLess(text.index("**Time:**"), text.index("DELIVERY RECORD"))
            import demo_check
            hdr = demo_check._header(text)
            self.assertEqual("75 min", hdr["Time"], "the record never breaks the header parse")
            self.assertEqual(["2026-10-19"], demo_check.delivery_dates(text))

    def test_runbook_section_appends_once(self):
        section = close_day.runbook_section("2026-10-19", self.MATCHED, CFG["demoRepo"]["url"], SHA, None)
        self.assertIn("## Delivery record (2026-10-19)", section)
        self.assertIn("- 01-desk-modules: reached", section)
        self.assertIn("- 02-pip-and-module-split: diverged", section)
        self.assertIn(f"/commit/{SHA}", section)
        self.assertIn("- Notes: none", section)
        self.assertIn("no walkthrough block", close_day.runbook_section("2026-10-19", [], "u", SHA, "x"))
        with tempfile.TemporaryDirectory() as t:
            rb = Path(t) / "runbook.md"
            rb.write_text("# w02d1 runbook\n\n## Day at a glance\n", encoding="utf-8")
            self.assertTrue(close_day.append_runbook(rb, section, "2026-10-19"))
            self.assertFalse(close_day.append_runbook(rb, section, "2026-10-19"))
            text = rb.read_text(encoding="utf-8")
            self.assertEqual(1, text.count("## Delivery record (2026-10-19)"))
            self.assertIn("## Day at a glance\n\n## Delivery record", text)


if __name__ == "__main__":
    unittest.main()
