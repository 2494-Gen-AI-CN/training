"""harness/drift_check.py (D-0052): decisions, markers, curriculum checks on temp trees, CLI exit codes, real-repo smoke."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "harness" / "drift_check.py"
sys.path.insert(0, str(ROOT / "harness"))
import drift_check as dc  # noqa: E402

HEADER = "| ID | Date | Status | Decision | Affects | Supersedes |\n|---|---|---|---|---|---|\n"
REL = "week-01/day-2-demo"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def make_root(tmp: Path, ids=(1, 2, 3), files=None, statuses=None, taught=True, status="live",
              delivery=True, record=True) -> Path:
    files = ids if files is None else files
    statuses = statuses or {}
    rows = "".join(f"| D-{n:04d} | 2026-10-0{min(n, 9)} | {statuses.get(n, 'accepted')} | Decision {n} | x | — |\n"
                   for n in sorted(ids, reverse=True))
    write(tmp / "decisions" / "README.md", "# Decision log\n\n" + HEADER + rows)
    for n in files:
        write(tmp / "decisions" / f"D-{n:04d}-decision-{n}.md", f"# D-{n:04d} — Decision {n}\n")
    day = {"kind": "lesson", "slug": "day-2-demo", "id": "w01d2", "status": status}
    if taught:
        day["taught"] = "2026-10-13"
    cur = {"weeks": [{"week": 1, "dir": "week-01", "days": [{"kind": "holiday"}, day]}]}
    write(tmp / "harness" / "curriculum.json", json.dumps(cur))
    tdir = tmp / "trainer" / REL
    write(tdir / "runbook.md", "# Runbook\n\nSteps.\n" + ("\n## Delivery record (2026-10-13)\n\nDone.\n" if record else ""))
    if delivery:
        write(tdir / "delivery.json", json.dumps({"date": "2026-10-13", "files": []}))
    return tmp


def levels(found, check):
    return [(f["level"], f["detail"]) for f in found if f["check"] == check]


def cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(ROOT))


class DecisionsTests(unittest.TestCase):
    def test_clean_set_passes(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual([], dc.check_decisions(make_root(Path(t))))

    def test_row_without_file_is_hard(self):
        with tempfile.TemporaryDirectory() as t:
            found = dc.check_decisions(make_root(Path(t), ids=(1, 2, 3), files=(1, 2)))
            self.assertTrue(any(f["level"] == "HARD" and "D-0003" in f["detail"] for f in found), found)

    def test_file_without_row_is_hard(self):
        with tempfile.TemporaryDirectory() as t:
            found = dc.check_decisions(make_root(Path(t), ids=(1, 2), files=(1, 2, 3)))
            self.assertTrue(any(f["level"] == "HARD" and "D-0003" in f["detail"] for f in found), found)

    def test_gap_is_hard(self):
        with tempfile.TemporaryDirectory() as t:
            found = dc.check_decisions(make_root(Path(t), ids=(1, 3)))
            self.assertTrue(any(f["level"] == "HARD" and "gap" in f["detail"] and "D-0002" in f["detail"] for f in found), found)

    def test_bad_status_is_hard(self):
        with tempfile.TemporaryDirectory() as t:
            found = dc.check_decisions(make_root(Path(t), statuses={2: "maybe"}))
            self.assertTrue(any(f["level"] == "HARD" and "D-0002" in f["detail"] for f in found), found)


class MarkerTests(unittest.TestCase):
    def scan(self, files: dict[str, str]):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(Path(t))
            for rel, text in files.items():
                write(root / rel, text)
            return dc.check_markers(root)

    def test_tbd_in_prose_is_hard_with_original_line(self):
        found = self.scan({"docs/a.md": "# A\n\nline two\nThis is TBD.\n"})
        self.assertEqual([("HARD", "docs/a.md:4: TBD")], levels(found, "markers"))

    def test_owed_is_hard_and_case_sensitive(self):
        found = self.scan({"notes.md": "OWED here\nowed there, tbd too\n"})
        self.assertEqual([("HARD", "notes.md:1: OWED")], levels(found, "markers"))

    def test_code_span_and_fence_ignored_line_numbers_kept(self):
        text = "Use `TBD` as a value.\n```\nTBD\npending\n```\n~~~python\nOWED = 1\n~~~\nreal TBD\n"
        found = self.scan({"harness/x.md": text})
        self.assertEqual([("HARD", "harness/x.md:9: TBD")], levels(found, "markers"))

    def test_pending_and_blocked_until_are_soft(self):
        found = self.scan({"docs/b.md": "Status: Pending review.\nThis is blocked until Friday.\n"})
        self.assertEqual([("SOFT", "docs/b.md:1: pending"), ("SOFT", "docs/b.md:2: blocked until")], levels(found, "markers"))

    def test_html_attributes_tags_and_code_ignored(self):
        html = ('<html>\n<head><style>.pending{}</style></head>\n<body>\n'
                '<div class="card" data-demo="pending">Demo</div>\n'
                '<!-- TBD later -->\n<pre>TBD\nOWED</pre>\n<p>Use <code>pending</code> here.</p>\n'
                '<script>\nvar TBD = 1;\n</script>\n<p>Still pending.</p>\n</body>\n</html>\n')
        found = self.scan({"docs/weeks/w/p.html": html})
        self.assertEqual([("SOFT", "docs/weeks/w/p.html:12: pending")], levels(found, "markers"))

    def test_excluded_paths(self):
        found = self.scan({"decisions/notes.md": "TBD\n", "docs/process/mined-rules-catalog.md": "TBD\n",
                           "demo-repo/x.md": "TBD\n", "Reference-Example/y.md": "TBD\n",
                           "harness/__pycache__/z.md": "TBD\n", "tests/t.md": "TBD\n"})
        self.assertEqual([], levels(found, "markers"))

    def test_trainer_md_scanned(self):
        found = self.scan({"trainer/week-01/x/runbook.md": "TBD\n"})
        self.assertEqual([("HARD", "trainer/week-01/x/runbook.md:1: TBD")], levels(found, "markers"))


class GitPorcelainTests(unittest.TestCase):
    def test_classification(self):
        cases = {"?? new.md": "untracked", " D gone.md": "deleted", "D  staged.md": "deleted",
                 "MD mod-then-del.md": "deleted", "AD add-then-del.md": "deleted", "RD old -> new.md": "deleted",
                 " M changed.md": None, "M  staged.md": None, "A  added.md": None, "": None}
        for line, want in cases.items():
            with self.subTest(line=line):
                self.assertEqual(want, dc.classify_porcelain(line))


class CurriculumTests(unittest.TestCase):
    def test_clean_taught_day_passes(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual([], dc.check_curriculum(make_root(Path(t))))

    def test_no_delivery_json_is_hard(self):
        with tempfile.TemporaryDirectory() as t:
            found = dc.check_curriculum(make_root(Path(t), delivery=False))
            self.assertTrue(any(f["level"] == "HARD" and "delivery.json" in f["detail"] for f in found), found)

    def test_no_delivery_record_is_hard(self):
        with tempfile.TemporaryDirectory() as t:
            found = dc.check_curriculum(make_root(Path(t), record=False))
            self.assertTrue(any(f["level"] == "HARD" and "Delivery record" in f["detail"] for f in found), found)

    def test_taught_but_authored_is_hard(self):
        with tempfile.TemporaryDirectory() as t:
            found = dc.check_curriculum(make_root(Path(t), status="authored"))
            self.assertTrue(any(f["level"] == "HARD" and "not live" in f["detail"] for f in found), found)

    def test_untaught_day_needs_nothing(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual([], dc.check_curriculum(make_root(Path(t), taught=False, delivery=False, record=False)))

    def test_trainer_absent_is_soft(self):
        import shutil
        with tempfile.TemporaryDirectory() as t:
            root = make_root(Path(t))
            shutil.rmtree(root / "trainer")
            found = dc.check_curriculum(root)
            self.assertEqual(["SOFT"], [f["level"] for f in found])


class NotesParseTests(unittest.TestCase):
    OUT = json.dumps({"ok": False, "pages": [
        {"page": "docs/weeks/w/a.html", "findingCount": 3,
         "findings": ["dead link https://x.example (HTTP 404)", "steps 5 below 6",
                      "delivery phrase 'in class' in step 2: a finding\nthat spans two lines"]},
        {"page": "docs/weeks/w/b.html", "findingCount": 0, "findings": []}]}) + "\n"

    def test_dead_link_soft_unless_strict(self):
        found = dc.parse_notes_output(self.OUT, strict=False)
        self.assertEqual(["SOFT", "HARD", "HARD"], [f["level"] for f in found])
        self.assertIn("docs/weeks/w/a.html: steps 5 below 6", [f["detail"] for f in found])
        self.assertTrue(found[2]["detail"].endswith("that spans two lines"))
        found = dc.parse_notes_output(self.OUT, strict=True)
        self.assertEqual(["HARD", "HARD", "HARD"], [f["level"] for f in found])

    def test_count_only_summary_is_hard(self):
        old = json.dumps({"ok": False, "pages": [{"page": "a.html", "findings": 2}]})
        self.assertEqual(["HARD"], [f["level"] for f in dc.parse_notes_output(old, strict=False)])


class GitRepoPresenceTests(unittest.TestCase):
    def test_absent_and_non_git_repos_are_soft(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(Path(t))  # trainer/ exists without .git, demo-repo/ is absent, root has no .git
            found = dc.check_git(root)
            self.assertEqual(["SOFT", "SOFT", "SOFT"], [f["level"] for f in found])
            details = " ".join(f["detail"] for f in found)
            for name in ("root:", "trainer:", "demo-repo:"):
                self.assertIn(name, details)


class CliTests(unittest.TestCase):
    FLAGS = ("--no-git", "--no-notes", "--no-tracker")

    def test_clean_tree_exits_0(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(Path(t))
            write(root / "docs" / "a.md", "Fine prose, `TBD` in code.\n")
            res = cli("--root", str(root), *self.FLAGS)
            self.assertEqual(0, res.returncode, res.stdout + res.stderr)
            self.assertIn("0 hard", res.stdout)

    def test_soft_only_exits_0(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(Path(t))
            write(root / "docs" / "a.md", "Still pending.\n")
            res = cli("--root", str(root), *self.FLAGS)
            self.assertEqual(0, res.returncode, res.stdout + res.stderr)
            self.assertIn("SOFT markers: docs/a.md:1: pending", res.stdout)

    def test_hard_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(Path(t), delivery=False)
            res = cli("--root", str(root), *self.FLAGS)
            self.assertEqual(1, res.returncode, res.stdout + res.stderr)
            self.assertIn("HARD curriculum:", res.stdout)

    def test_strict_does_not_change_marker_levels(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(Path(t))
            write(root / "docs" / "a.md", "Still pending.\n")
            res = cli("--root", str(root), "--strict", "--json", *self.FLAGS)
            self.assertEqual(0, res.returncode, res.stdout + res.stderr)
            data = json.loads(res.stdout)
            self.assertEqual([("SOFT", "docs/a.md:1: pending")], [(f["level"], f["detail"]) for f in data["findings"]])

    def test_json_output_parses(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(Path(t), ids=(1, 3))
            write(root / "README.md", "TBD\n")
            res = cli("--root", str(root), "--json", *self.FLAGS)
            self.assertEqual(1, res.returncode, res.stdout + res.stderr)
            data = json.loads(res.stdout)
            self.assertFalse(data["ok"])
            self.assertGreaterEqual(data["hard"], 2)
            self.assertTrue(all(set(f) == {"level", "check", "detail"} for f in data["findings"]))


class RealRepoSmokeTests(unittest.TestCase):
    def test_decisions_and_curriculum_consistent(self):
        res = cli("--no-git", "--no-notes", "--no-markers", "--no-tracker")
        self.assertEqual(0, res.returncode, res.stdout + res.stderr)


if __name__ == "__main__":
    unittest.main()
