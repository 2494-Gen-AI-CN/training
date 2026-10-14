"""harness/close_day.py, the delivery-day close of a loose day (D-0050).

Pure helpers only: nothing here touches curriculum.json, demos/, trainer/ or the demo-repo clone.
The git test builds a throwaway repository in a temp directory and skips when git is missing.
"""

from __future__ import annotations

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

REL = "week-01/day-3-python-basics"
CFG = {"demoRepo": {"url": "https://github.com/2494-Gen-AI-CN/demos"}}
DAY = {"id": "w01d3", "title": "Python Basics"}
SHA = "0123456789abcdef0123456789abcdef01234567"


@unittest.skipUnless(shutil.which("git"), "git not installed")
class FilesForTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str, when: str | None = None) -> None:
        env = dict(os.environ)
        if when:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)

    def test_only_that_dates_surviving_files(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            self._git(repo, "init", "-q")
            self._git(repo, "config", "user.name", "Test")
            self._git(repo, "config", "user.email", "test@example.com")
            day = repo / REL
            day.mkdir(parents=True)
            (day / "hello.py").write_text("print('hi')\n", encoding="utf-8")
            self._git(repo, "add", "-A")
            self._git(repo, "commit", "-q", "-m", "hello", when="2026-10-14T10:00:00")
            (day / "later.py").write_text("x = 1\n", encoding="utf-8")
            self._git(repo, "add", "-A")
            self._git(repo, "commit", "-q", "-m", "later", when="2026-10-15T10:00:00")
            (day / "later.py").unlink()
            self._git(repo, "add", "-A")
            self._git(repo, "commit", "-q", "-m", "drop later", when="2026-10-15T11:00:00")
            self.assertEqual(["hello.py"], close_day.files_for(repo, REL, "2026-10-14"))
            self.assertEqual([], close_day.files_for(repo, REL, "2026-10-15"), "a file deleted the same day is not published")
            self.assertEqual([], close_day.files_for(repo, REL, "2026-10-16"))
            self.assertEqual(40, len(close_day.head_sha(repo)))

    def _repo(self, t: str) -> Path:
        repo = Path(t)
        self._git(repo, "init", "-q")
        self._git(repo, "config", "user.name", "Test")
        self._git(repo, "config", "user.email", "test@example.com")
        (repo / REL).mkdir(parents=True)
        return repo

    def _commit(self, repo: Path, msg: str, when: str) -> str:
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", msg, when=when)
        return close_day.head_sha(repo)

    def test_content_and_sha_are_as_of_the_date_not_head(self):
        with tempfile.TemporaryDirectory() as t:
            repo = self._repo(t)
            hello = repo / REL / "hello.py"
            hello.write_bytes(b"print('typed on the 14th')\n")
            sha14 = self._commit(repo, "hello", "2026-10-14T10:00:00")
            hello.write_bytes(b"print('changed on the 15th')\n")
            sha15 = self._commit(repo, "edit", "2026-10-15T10:00:00")
            self.assertNotEqual(sha14, sha15)
            self.assertEqual(sha14, close_day.day_sha(repo, REL, "2026-10-14"))
            self.assertEqual(sha15, close_day.day_sha(repo, REL, "2026-10-15"))
            self.assertEqual(sha15, close_day.day_sha(repo, REL, "2026-10-16"), "a day with no commit pins the last one before it")
            self.assertEqual(["hello.py"], close_day.files_for(repo, REL, "2026-10-14"))
            self.assertEqual(b"print('typed on the 14th')\n", close_day.show_bytes(repo, sha14, f"{REL}/hello.py"))
            self.assertEqual(b"print('changed on the 15th')\n", hello.read_bytes(), "the working tree is HEAD, which must not be published")
            rec = close_day.delivery_record(DAY, "2026-10-14", ["hello.py"], CFG, close_day.day_sha(repo, REL, "2026-10-14"), None)
            self.assertEqual(sha14, rec["demoRepoSha"])

    def test_trainer_readme_is_not_published_and_warned(self):
        with tempfile.TemporaryDirectory() as t:
            repo = self._repo(t)
            (repo / REL / "README.md").write_text("# mine\n", encoding="utf-8")
            (repo / REL / "a.py").write_text("x = 1\n", encoding="utf-8")
            sha = self._commit(repo, "day", "2026-10-14T10:00:00")
            self.assertEqual(["a.py"], close_day.files_for(repo, REL, "2026-10-14"))
            present = close_day.tree_at(repo, sha, REL)
            self.assertEqual({"README.md", "a.py"}, present)
            warn = close_day.readme_warning(present, REL, {"demoRepo": {"localDir": "demo-repo"}})
            self.assertIn(f"demo-repo {REL}/README.md is not published", warn)
            self.assertIsNone(close_day.readme_warning({"a.py"}, REL, {"demoRepo": {"localDir": "demo-repo"}}))


class SafeNamesTests(unittest.TestCase):
    def test_files_stay_inside_the_day_folder(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            self.assertEqual(["a.py", "sub/b.py"], close_day.safe_names(repo, REL, ["a.py", "sub\\b.py", "./a.py"]))
            for bad in ("../x.py", "sub/../../x.py", "..\\x.py", "/etc/passwd", "C:/x.py", "C:x.py", "\\\\server\\share\\x.py", ""):
                with self.subTest(bad=bad), self.assertRaises(SystemExit):
                    close_day.safe_names(repo, REL, [bad])


class CardPlanTests(unittest.TestCase):
    CFG = {"repoUrl": "https://github.com/2494-Gen-AI-CN/training", "repoBranch": "main"}

    def test_validated_before_any_write(self):
        pend = close_day.pd.CARD_PENDING
        good = (f"<p>x</p>\n{pend}\n  <div class=\"ac-k\">k</div>\n  {close_day.pd.PENDING_TEXT}\n"
                "  <div class=\"ac-meta\">m</div>\n</div>\n")
        action, new = close_day.card_plan(good, ["hello.py"], self.CFG, REL)
        self.assertEqual("flip to links", action)
        self.assertIn(f"/demos/{REL}/hello.py", new)
        action, new = close_day.card_plan(good, [], self.CFG, REL)
        self.assertEqual("flip to none", action)
        self.assertIn(close_day.pd.CARD_NONE, new)
        broken = good.replace(close_day.pd.PENDING_TEXT, "<div class=\"ac-t\">edited</div>")
        with self.assertRaises(SystemExit) as cm:
            close_day.card_plan(broken, ["hello.py"], self.CFG, REL)
        self.assertIn("Nothing was written", str(cm.exception.code))
        self.assertEqual(("already flipped", None), close_day.card_plan(new, [], self.CFG, REL))
        self.assertEqual(("no demo card", None), close_day.card_plan("<p>no card</p>", [], self.CFG, REL))
        commented = f"<!-- {close_day.pd.CARD_PUBLISHED} -->\n<p>x</p>"
        self.assertEqual(("no demo card", None), close_day.card_plan(commented, [], self.CFG, REL))
        self.assertEqual(("no notes page", None), close_day.card_plan(None, [], self.CFG, REL))


class ReadmeTests(unittest.TestCase):
    def test_lists_each_file_once(self):
        files = ["hello.py", "notes/scratch.py"]
        text = close_day.render_readme(DAY, REL, "2026-10-14", files, CFG["demoRepo"]["url"])
        self.assertTrue(text.startswith("# Python Basics — files typed live"), text)
        self.assertTrue(text.endswith("\n"))
        for f in files:
            self.assertEqual(1, text.count(f"`{f}`"), f"{f} should appear once")
        self.assertIn("| # | File |", text)
        self.assertIn("Typed live on 2026-10-14", text)
        self.assertIn(f"https://github.com/2494-Gen-AI-CN/demos/tree/main/{REL}", text)
        self.assertNotIn("No code demo this day", text)

    def test_no_files(self):
        text = close_day.render_readme(DAY, REL, "2026-10-14", [], CFG["demoRepo"]["url"])
        self.assertIn("No code demo this day", text)
        self.assertNotIn("| # | File |", text)
        self.assertIn("Typed live on 2026-10-14", text)


class LocateTests(unittest.TestCase):
    def test_thread_day_is_refused(self):
        week, day = next((w, d) for w, d, _ in all_days() if d["demoFormat"] in ("py", "nb"))
        with self.assertRaises(SystemExit) as cm:
            close_day.locate(week["week"], day["day"])
        self.assertIn("not built yet", str(cm.exception.code))

    def test_unreleased_day_is_refused(self):
        """D-0052: an authored or planned loose day is refused (dry run and --apply both go through plan -> locate)."""
        week = {"week": 2, "dir": "week-02", "days": []}
        for status in ("authored", "planned"):
            day = {"id": "w02d1", "day": 1, "slug": "day-1-x", "demoFormat": "loose", "status": status}
            fixture = ({"demoRepo": CFG["demoRepo"]}, day, "week-02/day-1-x", {"weeks": [week]}, week)
            with self.subTest(status=status), mock.patch.object(close_day.pd, "_locate", return_value=fixture):
                with self.assertRaises(SystemExit) as cm:
                    close_day.plan(2, 1, pull=False)
                msg = str(cm.exception.code)
                self.assertIn(f"w02d1 is '{status}', not live", msg)
                self.assertIn("python harness/release_week.py 2 --today", msg)
                self.assertNotIn("taught", day)


class RecordTests(unittest.TestCase):
    def test_delivery_record_key_order(self):
        rec = close_day.delivery_record(DAY, "2026-10-14", ["hello.py"], CFG, SHA, None)
        self.assertEqual(["day", "date", "format", "files", "demoRepo", "demoRepoSha", "notes"], list(rec))
        self.assertEqual("w01d3", rec["day"])
        self.assertEqual("loose", rec["format"])
        self.assertEqual(CFG["demoRepo"]["url"], rec["demoRepo"])
        self.assertEqual("", rec["notes"])

    def test_runbook_section_appends_once(self):
        section = close_day.runbook_section("2026-10-14", ["hello.py", "b.py"], CFG["demoRepo"]["url"], SHA, REL, None)
        self.assertIn("## Delivery record (2026-10-14)", section)
        self.assertIn("(2)", section)
        self.assertIn(f"/tree/{SHA}/{REL}", section)
        self.assertIn("- Notes: none", section)
        self.assertIn("- Files typed live: none", close_day.runbook_section("2026-10-14", [], "u", SHA, REL, "x"))
        with tempfile.TemporaryDirectory() as t:
            rb = Path(t) / "runbook.md"
            rb.write_text("# w01d3 runbook\n\n## Day at a glance\n", encoding="utf-8")
            self.assertTrue(close_day.append_runbook(rb, section, "2026-10-14"))
            self.assertFalse(close_day.append_runbook(rb, section, "2026-10-14"))
            text = rb.read_text(encoding="utf-8")
            self.assertEqual(1, text.count("## Delivery record (2026-10-14)"))
            self.assertIn("## Day at a glance\n\n## Delivery record", text)


if __name__ == "__main__":
    unittest.main()
