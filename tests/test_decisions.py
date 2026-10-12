"""decisions/ log contract: index parses, IDs unique + sequential, fields present, links resolve."""

from __future__ import annotations

import datetime as dt
import re
import unittest

from helpers import DOCS, HARNESS, ROOT

DECISIONS = ROOT / "decisions"
INDEX = DECISIONS / "README.md"
ID_RE = re.compile(r"\bD-\d{4}\b")
ENTRY_FILE_RE = re.compile(r"^(D-\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ROW_RE = re.compile(r"^\| (D-\d{4}) \| (\d{4}-\d{2}-\d{2}) \| (\w+) \| (.*?) \| (.*?) \| (.*?) \|$")
FIELD_RE = re.compile(r"^- (Date|Status|Decision|Why|Affects|Supersedes|Superseded-by): (.*)$", re.M)
REQUIRED = ("Date", "Status", "Decision", "Why", "Affects", "Supersedes", "Superseded-by")
STATUSES = ("proposed", "accepted", "superseded")
NONE = "—"
# Files/dirs where a D-NNNN mention must resolve to a real entry.
CITATION_SCOPES = [HARNESS, DOCS, ROOT / "tests", ROOT / "AGENTS.md", ROOT / "README.md", ROOT / "harness-walkthrough.html"]
TEXT_SUFFIXES = {".md", ".py", ".js", ".json", ".html", ".txt", ".css"}


def entry_files() -> dict[str, "Path"]:
    out = {}
    for p in DECISIONS.glob("D-*.md"):
        m = ENTRY_FILE_RE.match(p.name)
        if m:
            out[m.group(1)] = p
    return out


def parse_entry(path) -> dict:
    text = path.read_text(encoding="utf-8")
    fields = {k: v.strip() for k, v in FIELD_RE.findall(text)}
    fields["_title"] = text.splitlines()[0] if text else ""
    return fields


def index_rows() -> list[tuple]:
    rows = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if m:
            rows.append(m.groups())
    return rows


class DecisionLogTests(unittest.TestCase):
    def setUp(self):
        self.files = entry_files()
        self.rows = index_rows()
        self.entries = {eid: parse_entry(p) for eid, p in self.files.items()}

    def test_index_exists_and_parses(self):
        self.assertTrue(INDEX.exists())
        self.assertTrue(self.rows, "no entry rows found in decisions/README.md")
        self.assertIn("| ID | Date | Status | Decision | Affects | Supersedes |", INDEX.read_text(encoding="utf-8"))

    def test_ids_unique_sequential_and_index_matches_files(self):
        ids_in_index = [r[0] for r in self.rows]
        self.assertEqual(len(ids_in_index), len(set(ids_in_index)), "duplicate ID in index")
        self.assertEqual(set(ids_in_index), set(self.files), "index rows and entry files differ")
        nums = sorted(int(i[2:]) for i in self.files)
        self.assertEqual(list(range(1, len(nums) + 1)), nums, "IDs must be sequential from D-0001")
        self.assertEqual(sorted(ids_in_index, reverse=True), ids_in_index, "index must be newest-first")
        bad = [p.name for p in DECISIONS.glob("D-*.md") if not ENTRY_FILE_RE.match(p.name)]
        self.assertFalse(bad, f"entry file names must be D-NNNN-<slug>.md: {bad}")

    def test_entry_fields(self):
        for eid, f in self.entries.items():
            with self.subTest(eid=eid):
                for k in REQUIRED:
                    self.assertIn(k, f, f"{eid} missing field {k}")
                    self.assertTrue(f[k], f"{eid} field {k} is empty")
                self.assertTrue(f["_title"].startswith(f"# {eid} — "), f"{eid} title line must start with '# {eid} — '")
                dt.date.fromisoformat(f["Date"])
                self.assertIn(f["Status"], STATUSES)
                for k in ("Supersedes", "Superseded-by"):
                    self.assertTrue(f[k] == NONE or ID_RE.fullmatch(f[k]), f"{eid} {k} must be {NONE} or D-NNNN")

    def test_index_rows_match_entries(self):
        for eid, date, status, decision, affects, supersedes in self.rows:
            with self.subTest(eid=eid):
                f = self.entries[eid]
                self.assertEqual(f["Date"], date)
                self.assertEqual(f["Status"], status)
                self.assertEqual(f["Supersedes"], supersedes)
                self.assertEqual(f["Decision"].replace("|", "\\|"), decision)

    def test_supersede_links_resolve_both_ways(self):
        for eid, f in self.entries.items():
            with self.subTest(eid=eid):
                if f["Supersedes"] != NONE:
                    old = f["Supersedes"]
                    self.assertIn(old, self.entries, f"{eid} supersedes unknown {old}")
                    self.assertEqual("superseded", self.entries[old]["Status"], f"{old} must be marked superseded")
                    self.assertEqual(eid, self.entries[old]["Superseded-by"])
                if f["Status"] == "superseded":
                    self.assertNotEqual(NONE, f["Superseded-by"], f"{eid} superseded without Superseded-by")
                    self.assertIn(f["Superseded-by"], self.entries)

    def test_every_cited_id_exists(self):
        cited = {}
        for scope in CITATION_SCOPES:
            paths = [scope] if scope.is_file() else [p for p in scope.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES]
            for p in paths:
                if "__pycache__" in p.parts:
                    continue
                for m in ID_RE.findall(p.read_text(encoding="utf-8", errors="replace")):
                    cited.setdefault(m, set()).add(str(p.relative_to(ROOT)))
        unknown = {k: sorted(v) for k, v in cited.items() if k not in self.entries}
        self.assertFalse(unknown, f"cited decision IDs with no entry: {unknown}")


if __name__ == "__main__":
    unittest.main()
