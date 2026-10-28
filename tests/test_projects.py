"""The projects section (D-0065): spec grammar, generated pages in sync, page shape, and the two-way
decoupling from the day pipeline (no project page links a day or exit page; no day-pipeline file names
projects/)."""

from __future__ import annotations

import contextlib
import copy
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import DOCS, FORBIDDEN_RE, HARNESS, ROOT, ParsedPage, curriculum

sys.path.insert(0, str(HARNESS))
import build_index  # noqa: E402
import build_projects as bp  # noqa: E402
import drift_check  # noqa: E402
import site_pages  # noqa: E402

OUT = DOCS / "projects"
ISO_RE = re.compile(r"20\d\d-\d\d-\d\d")
BUILD_INDEX_SRC = (HARNESS / "build_index.py").read_text(encoding="utf-8")


# ---------------------------------------------------------------- fixtures
def sprint(**kw) -> str:
    meta = {"kind": "sprint", "title": "Fixture sprint", "assigned": "2026-10-21", "due": "2026-10-26",
            "mode": "pairs", "handIn": "week-02/hackathon/", "status": "open", "tools": "Python, pandas"}
    meta.update(kw)
    head = "".join(f"{k}: {v}\n" for k, v in meta.items() if v is not None)
    return f"---\n{head}---\n\nOne paragraph of intro.\n\n## Rules\n\n- One rule.\n"


def official(project="P1", status="published", checkpoints=("w08d5 Showcase",), sections=("Build", "Rules", "Hand-in"),
             reqs=None, body_extra="", **kw) -> str:
    """A free-form official spec (D-0073); `reqs` adds a `## Requirements` section holding that text."""
    meta = {"kind": "official", "project": project, "title": "Fixture project", "status": status,
            "handIn": f"projects/{project}/"}
    meta.update(kw)
    head = "".join(f"{k}: {v}\n" for k, v in meta.items() if v is not None)
    head += "checkpoints:\n" + "".join(f"- {c}\n" for c in checkpoints)
    body = ["Intro paragraph."]
    for s in sections:
        body.append(f"## {s}\n\nText for {s.lower()}.\n")
    if reqs is not None:
        body.append(f"## Requirements\n\n{reqs}")
    return f"---\n{head}---\n\n" + "\n".join(body) + body_extra


class _TempRoot(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.cur = copy.deepcopy(curriculum())

    def tearDown(self):
        self._tmp.cleanup()

    def put(self, rel: str, text: str) -> Path:
        p = self.root / "projects" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def problems(self) -> list[str]:
        return bp.validate(self.root, self.cur)

    def assertProblem(self, needle: str, rel: str | None = None):
        ps = self.problems()
        hits = [p for p in ps if needle in p and (rel is None or p.startswith(f"projects/{rel}: "))]
        self.assertTrue(hits, f"no problem containing {needle!r} in {ps}")

    def set_status(self, day_id: str, status: str):
        for w in self.cur["weeks"]:
            for d in w["days"]:
                if d.get("id") == day_id:
                    d["status"] = status
                    return
        raise AssertionError(day_id)


# ---------------------------------------------------------------- parser / validation
class ParserTests(_TempRoot):
    def test_valid_fixtures_pass(self):
        self.put("sprints/2026-10-21-fixture.md", sprint())
        self.put("official/P1-fixture.md", official())
        self.assertEqual([], self.problems())

    def test_no_drop_zone_is_clean(self):
        self.assertEqual([], self.problems())
        self.assertEqual([], bp.load_specs(self.root, self.cur))

    def test_parse_frontmatter(self):
        meta, body = bp.parse_frontmatter(official())
        self.assertEqual("P1", meta["project"])
        self.assertEqual([("w08d5", "Showcase")], meta["checkpoints"])
        self.assertTrue(body.startswith("Intro paragraph."))
        meta, _ = bp.parse_frontmatter("---\ntitle: Project 0: the desk\n---\n")
        self.assertEqual("Project 0: the desk", meta["title"], "the value is the rest of the line")

    def test_parse_errors_raise_spec_error(self):
        with self.assertRaises(bp.SpecError):
            bp.parse_frontmatter("no fence\n")

    # frontmatter grammar
    def test_missing_opening_fence(self):
        self.put("sprints/2026-10-21-fixture.md", "kind: sprint\n")
        self.assertProblem("line 1: the frontmatter must open with '---'")

    def test_missing_closing_fence(self):
        self.put("sprints/2026-10-21-fixture.md", "---\nkind: sprint\ntitle: x\n")
        self.assertProblem("the frontmatter has no closing '---'")

    def test_not_a_key_value_line(self):
        self.put("sprints/2026-10-21-fixture.md", "---\nthis is: [not closed\n")
        self.assertProblem("line 2: not a 'key: value' line", "sprints/2026-10-21-fixture.md")

    def test_duplicate_key(self):
        self.put("sprints/2026-10-21-fixture.md", sprint().replace("mode: pairs\n", "mode: pairs\ntitle: Again\n"))
        self.assertProblem("duplicate key 'title'")

    def test_list_line_outside_checkpoints(self):
        self.put("sprints/2026-10-21-fixture.md", sprint().replace("mode: pairs\n", "mode: pairs\n- w02d3 Kickoff\n"))
        self.assertProblem("only allowed under 'checkpoints:'")

    def test_bad_checkpoint_line(self):
        self.put("official/P1-fixture.md", official(checkpoints=("day5 Showcase",)))
        self.assertProblem("a checkpoint line reads '- wNNdN Label'")

    def test_checkpoints_key_takes_no_value(self):
        self.put("official/P1-fixture.md", official().replace("checkpoints:\n", "checkpoints: w08d5\n"))
        self.assertProblem("'checkpoints:' takes no value")

    def test_unknown_key(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(colour="blue"))
        self.assertProblem("unknown key 'colour'")

    def test_tools_is_sprint_only(self):
        self.put("official/P1-fixture.md", official(tools="Python"))
        self.assertProblem("unknown key 'tools' (official specs take")

    def test_missing_key(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(mode=None))
        self.assertProblem("missing key 'mode'")

    def test_bad_kind(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(kind="hackathon"))
        self.assertProblem("kind must be official or sprint")

    def test_kind_in_the_wrong_folder(self):
        self.put("official/2026-10-21-fixture.md", sprint())
        self.assertProblem("does not belong in projects/official/")

    def test_empty_title(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(title=""))
        self.assertProblem("title is empty")

    def test_empty_hand_in(self):
        self.put("official/P1-fixture.md", official(handIn=""))
        self.assertProblem("handIn is empty")

    # statuses and modes
    def test_bad_sprint_status(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(status="draft"))
        self.assertProblem("status must be open | closed")

    def test_bad_official_status(self):
        self.put("official/P1-fixture.md", official(status="open"))
        self.assertProblem("status must be draft | published | closed")

    def test_bad_mode(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(mode="pair"))
        self.assertProblem("mode must be pairs | solo | teams")

    # dates
    def test_bad_iso_date(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(due="26/10/2026"))
        self.assertProblem("due '26/10/2026' is not an ISO date")

    def test_date_outside_the_course(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(due="2027-01-04"))
        self.assertProblem("due 2027-01-04 is outside the course")

    def test_weekend_is_not_a_teaching_day(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(due="2026-10-24"))
        self.assertProblem("due 2026-10-24 is not a teaching day")

    def test_holiday_is_not_a_teaching_day(self):
        self.put("sprints/2026-11-23-fixture.md", sprint(assigned="2026-11-23", due="2026-11-26", handIn="week-07/hackathon/"))
        self.assertProblem("due 2026-11-26 is not a teaching day")

    def test_due_before_assigned(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(due="2026-10-20"))
        self.assertProblem("due is before assigned")

    # hand-in (sprint == the week's hackathon)
    def test_hand_in_must_be_the_hackathon_folder(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(handIn="week-02/sprint/"))
        self.assertProblem("must read week-NN/hackathon/")

    def test_hand_in_week_follows_assigned(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(handIn="week-03/hackathon/"))
        self.assertProblem("is not in the week of assigned (week-02/hackathon/)")

    def test_second_sprint_in_a_week_hands_in_under_a_subfolder(self):
        self.put("sprints/2026-10-21-fixture.md", sprint())
        self.put("sprints/2026-10-22-second.md", sprint(assigned="2026-10-22"))
        self.assertProblem("handIn 'week-02/hackathon/' is already used by projects/sprints/2026-10-21-fixture.md")
        self.put("sprints/2026-10-22-second.md", sprint(assigned="2026-10-22", handIn="week-02/hackathon/second/"))
        self.assertEqual([], self.problems())

    def test_one_spec_per_official_project(self):
        self.put("official/P1-fixture.md", official())
        self.put("official/P1-second.md", official())
        self.assertProblem("project P1 already has a spec, projects/official/P1-fixture.md")

    # filenames and slugs
    def test_sprint_filename_pattern(self):
        self.put("sprints/fixture.md", sprint())
        self.assertProblem("the filename must be YYYY-MM-DD-<slug>.md")

    def test_sprint_filename_date_matches_assigned(self):
        self.put("sprints/2026-10-22-fixture.md", sprint())
        self.assertProblem("the filename date 2026-10-22 does not match assigned 2026-10-21")

    def test_official_filename_pattern(self):
        self.put("official/fixture.md", official())
        self.assertProblem("the filename must be P<n>-<slug>.md")

    def test_official_filename_prefix_matches_project(self):
        self.put("official/P2-fixture.md", official())
        self.assertProblem("the filename prefix P2 does not match project P1")

    def test_reserved_slug(self):
        self.put("sprints/2026-10-21-index.md", sprint())
        self.assertProblem("the slug 'index' is reserved")

    def test_duplicate_slug_across_folders(self):
        self.put("official/P1-fixture.md", official())
        self.put("sprints/2026-10-21-p1-fixture.md", sprint())
        self.assertProblem("slug 'p1-fixture' is already used by projects/official/P1-fixture.md",
                           "sprints/2026-10-21-p1-fixture.md")

    def test_duplicate_slug_within_sprints(self):
        self.put("sprints/2026-10-21-fixture.md", sprint())
        self.put("sprints/2026-10-22-fixture.md", sprint(assigned="2026-10-22", handIn="week-02/hackathon/fixture/"))
        self.assertProblem("slug 'fixture' is already used by projects/sprints/2026-10-21-fixture.md")

    # officials
    def test_unknown_project(self):
        self.put("official/P9-fixture.md", official(project="P9"))
        self.assertProblem("unknown project 'P9'")

    def test_unknown_day_id(self):
        self.put("official/P1-fixture.md", official(checkpoints=("w08d9 Showcase",)))
        self.assertProblem("checkpoint w08d9 is not a day id")

    def test_holiday_slot(self):
        self.put("official/P1-fixture.md", official(checkpoints=("w07d4 Showcase",)))
        self.assertProblem("checkpoint w07d4 is a holiday slot")

    def test_checkpoint_inside_the_project_weeks(self):
        self.put("official/P1-fixture.md", official(checkpoints=("w03d1 Kickoff",)))
        self.assertProblem("checkpoint w03d1 is outside P1's weeks 6–8")

    def test_at_least_one_checkpoint(self):
        self.put("official/P1-fixture.md", official(checkpoints=()))
        self.assertProblem("checkpoints needs at least one")

    def test_draft_with_a_live_checkpoint(self):
        self.set_status("w08d5", "live")
        self.put("official/P1-fixture.md", official(status="draft"))
        self.assertProblem("draft spec has a checkpoint on a live day (w08d5)")
        self.put("official/P1-fixture.md", official(status="published"))
        self.assertEqual([], self.problems())

    # sections (free-form since D-0073)
    def test_any_sections_in_any_order(self):
        self.put("official/P1-fixture.md", official(sections=("Presentation", "Dataset", "Build", "Build")))
        self.assertEqual([], self.problems())

    def test_no_sections_at_all(self):
        self.put("official/P1-fixture.md", official(sections=()))
        self.assertEqual([], self.problems())

    def test_requirements_section_is_optional(self):
        self.put("official/P1-fixture.md", official(reqs=None))
        self.assertEqual([], self.problems())
        self.put("official/P1-fixture.md", official(reqs="- R-01 One.\n- R-02 Two.\n"))
        self.assertEqual([], self.problems())

    def test_heading_inside_fenced_code_is_not_a_section(self):
        self.put("official/P1-fixture.md", official(body_extra="\n```\n## Requirements\n```\n"))
        self.assertEqual([], self.problems())

    def test_requirements_numbered_from_r01(self):
        self.put("official/P1-fixture.md", official(reqs="- R-01 One.\n- R-03 Three.\n"))
        self.assertProblem("requirements are not numbered R-01, R-02, ... in order (got R-01, R-03)")
        self.put("official/P1-fixture.md", official(reqs="- R-02 Two.\n"))
        self.assertProblem("(got R-02)")

    def test_requirements_need_a_bullet(self):
        self.put("official/P1-fixture.md", official(reqs="Some prose, no bullets.\n"))
        self.assertProblem("'## Requirements' has no '- R-01 ...' bullet")

    # prose rules
    def test_body_never_names_the_day_pipeline(self):
        self.put("sprints/2026-10-21-fixture.md", sprint() + "\nSee [the notes](../weeks/week-02/day-1.html).\n")
        self.assertProblem("project specs never link day or exit-criteria pages")

    def test_no_iso_date_in_prose(self):
        self.put("sprints/2026-10-21-fixture.md", sprint() + "\nPresent on 2026-10-26.\n")
        self.assertProblem("an ISO date (YYYY-MM-DD) appears in the prose")

    def test_curriculum_without_a_calendar(self):
        self.put("sprints/2026-10-21-fixture.md", sprint())
        self.cur = {"weeks": []}
        self.assertProblem("no usable calendar")

    # load_specs
    def test_strict_raises(self):
        self.put("sprints/2026-10-21-fixture.md", sprint(mode="pair"))
        with self.assertRaises(bp.SpecError) as cm:
            bp.load_specs(self.root, self.cur)
        self.assertIn("projects/sprints/2026-10-21-fixture.md: mode must be", str(cm.exception))

    def test_non_strict_skips_and_warns_once_per_file(self):
        self.put("sprints/2026-10-21-fixture.md", sprint())
        self.put("sprints/2026-10-22-broken.md", sprint(assigned="2026-10-22", mode="pair", status="later",
                                                         handIn="week-02/hackathon/broken/"))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            specs = bp.load_specs(self.root, self.cur, strict=False)
        self.assertEqual(["fixture"], [s["slug"] for s in specs])
        lines = [ln for ln in err.getvalue().splitlines() if ln.strip()]
        self.assertEqual(1, len(lines), lines)
        self.assertIn("projects/sprints/2026-10-22-broken.md", lines[0])
        self.assertIn("2 problems", lines[0])

    def test_spec_fields_and_order(self):
        self.put("sprints/2026-10-21-fixture.md", sprint())
        self.put("sprints/2026-10-28-later.md", sprint(assigned="2026-10-28", due="2026-10-30", handIn="week-03/hackathon/"))
        self.put("official/P1-fixture.md", official())
        specs = bp.load_specs(self.root, self.cur)
        self.assertEqual(["P1-fixture", "later", "fixture"], [s["slug"] for s in specs], "officials, then sprints newest first")
        s = specs[2]
        self.assertEqual(("sprint", "pairs", ["Python", "pandas"], True), (s["kind"], s["mode"], s["tools"], s["visible"]))
        self.assertEqual("2026-10-26", s["due"].isoformat())
        o = specs[0]
        self.assertEqual("P1", o["project"])
        self.assertEqual([{"dayId": "w08d5", "label": "Showcase", "date": build_index.slot_date(self.cur, 8, 5),
                           "week": 8, "slot": 5}], o["checkpoints"])

    def test_calendar_marks(self):
        self.put("sprints/2026-10-21-fixture.md", sprint())
        self.put("sprints/2026-10-28-done.md", sprint(assigned="2026-10-28", due="2026-10-30", handIn="week-03/hackathon/",
                                                      status="closed", title="Done sprint"))
        self.put("official/P1-fixture.md", official())
        self.put("official/P2-hidden.md", official(project="P2", status="draft", checkpoints=("w11d4 Showcase",)))
        marks = bp.calendar_marks(bp.load_specs(self.root, self.cur), self.cur)
        self.assertEqual({"2026-10-26": [{"slug": "fixture", "title": "Fixture sprint"}],
                          "2026-10-30": [{"slug": "done", "title": "Done sprint"}]}, marks["due"])
        cp_day = build_index.slot_date(self.cur, 8, 5).isoformat()
        self.assertEqual({cp_day: [{"slug": "P1-fixture", "title": "Fixture project", "label": "Showcase"}]}, marks["cp"],
                         "the draft P2 spec carries no mark")
        self.assertEqual([{"slug": "fixture", "title": "Fixture sprint", "start": "2026-10-21", "end": "2026-10-26"},
                          {"slug": "done", "title": "Done sprint", "start": "2026-10-28", "end": "2026-10-30"}], marks["sprints"])


# ---------------------------------------------------------------- sync
class SyncTests(unittest.TestCase):
    def test_pages_are_in_sync_with_the_builder(self):
        self.assertEqual([], bp.check())

    def test_specs_are_valid(self):
        self.assertEqual([], bp.validate())

    def test_expected_files_are_the_files_on_disk(self):
        want = {p.name for p in bp.expected()}
        self.assertIn("index.html", want)
        self.assertEqual(want, {p.name for p in OUT.glob("*.html")})

    def test_drift_check_runs_the_projects_check(self):
        self.assertIn("build_projects", (HARNESS / "drift_check.py").read_text(encoding="utf-8"))
        self.assertIn("projects", drift_check.MD_SCAN_DIRS)

    def test_markdown_is_a_dev_requirement_imported_lazily(self):
        self.assertRegex((ROOT / "requirements-dev.txt").read_text(encoding="utf-8"), r"(?m)^markdown>=")
        src = (HARNESS / "build_projects.py").read_text(encoding="utf-8")
        self.assertNotRegex(src, r"(?m)^(import markdown|from markdown)", "markdown is imported inside the renderer only")
        self.assertNotRegex(BUILD_INDEX_SRC, r"(?m)^\s*(import markdown|from markdown)")

    @unittest.skipUnless("build_projects.check(" in BUILD_INDEX_SRC, "landed by lane C")
    def test_build_index_check_runs_the_projects_check(self):
        self.assertIn("build_projects.check(", BUILD_INDEX_SRC)

    @unittest.skipUnless("build_projects.build(" in BUILD_INDEX_SRC, "landed by lane C")
    def test_build_index_rebuilds_the_projects_pages(self):
        self.assertIn("build_projects.build(", BUILD_INDEX_SRC)


# ---------------------------------------------------------------- pages
def _index_version() -> str:
    return re.search(r'style\.css\?v=([^"]+)', (DOCS / "index.html").read_text(encoding="utf-8")).group(1)


def _sibling_section_indexes() -> set[str]:
    return {f"../{d}/index.html" for key, _label, d in site_pages.SECTIONS if key != "projects"}


def _common_checks(tc: unittest.TestCase, page: ParsedPage):
    r = page.root
    tc.assertEqual(["theme.js"], page.script_srcs, "theme.js is the only script src")
    js_v = re.search(r'theme\.js\?v=([^"]+)', (DOCS / "index.html").read_text(encoding="utf-8")).group(1)
    for s in r.find_all("script"):
        if s.attrs.get("src"):
            tc.assertEqual(f"../assets/js/theme.js?v={js_v}", s.attrs["src"])
    tc.assertIsNotNone(r.find(class_name="topbar-right"))
    tc.assertIsNone(r.find(class_name="reading2col"), "no .reading2col: theme.js would inject the view switch")
    nav = [a for a in r.find_all("a", "topnav") if a.text().strip() == "Projects"]
    tc.assertEqual(1, len(nav))
    tc.assertEqual("index.html", nav[0].attrs.get("href"))
    nav = [a for a in r.find_all("a", "topnav") if a.text().strip() == "Exit criteria"]
    tc.assertEqual(1, len(nav))
    tc.assertEqual("../exit-criteria/index.html", nav[0].attrs.get("href"))
    tc.assertIsNone(FORBIDDEN_RE.search(page.raw), FORBIDDEN_RE.search(page.raw))
    tc.assertNotRegex(page.raw, r"<html[^>]*\bdata-view")
    tc.assertNotRegex(page.raw, r"<html[^>]*\bdata-theme")
    tc.assertIsNone(ISO_RE.search(page.raw), "no ISO date on a generated page")
    tc.assertNotRegex(page.raw, r"<time\b")
    tc.assertEqual(_index_version(), re.search(r'style\.css\?v=([^"]+)', page.raw).group(1))
    tc.assertIsNotNone(r.find("main", id="reading-main"))
    tc.assertIsNotNone(r.find("a", "skip-link"))
    for word in ("TBD", "OWED"):
        tc.assertNotRegex(page.raw, rf"\b{word}\b")
    tc.assertNotRegex(page.raw, r"(?i)\bpending\b|blocked until")
    for href in page.hrefs():
        if href.startswith(("http", "#", "mailto:")):
            continue
        tc.assertFalse(href.startswith("//"), href)
        target = (page.path.parent / href.split("?")[0].split("#")[0]).resolve()
        if href in _sibling_section_indexes() and not target.parent.is_dir():
            continue
        tc.assertTrue(target.is_file(), f"broken relative link {href}")
    for href in page.hrefs():
        if href.startswith("http"):
            tc.assertTrue(href.startswith("https://github.com/"), f"no external origin but GitHub: {href}")


class PageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cur = curriculum()
        cls.specs = bp.load_specs(cur=cls.cur)

    def test_every_page_parses(self):
        pages = sorted(OUT.glob("*.html"))
        self.assertGreaterEqual(len(pages), 1)
        for p in pages:
            with self.subTest(page=p.name):
                ParsedPage(p)

    def test_index(self):
        page = ParsedPage(OUT / "index.html")
        _common_checks(self, page)
        r = page.root
        self.assertEqual("Projects", r.find("h1").text().strip())
        cards = {c.attrs.get("data-slug"): c for c in r.find_all("div", "pj-card")}
        visible = [s for s in self.specs if s["visible"]]
        self.assertEqual({s["slug"] for s in visible}, set(cards))
        for s in visible:
            card = cards[s["slug"]]
            self.assertEqual(s["title"], card.find("h2").text().strip())
            self.assertEqual(f'{s["slug"]}.html', card.find("a", "fr-btn").attrs.get("href"))
            self.assertEqual(s["status"] == "closed", "pj-closed" in card.classes(), s["slug"])
        for s in self.specs:
            self.assertTrue((OUT / f'{s["slug"]}.html').is_file(), f"{s['slug']}: every spec has a page, drafts too")
        if not [s for s in visible if s["kind"] == "sprint"]:
            self.assertIn("No sprint published yet.", page.raw)
        # every official project of the curriculum is listed: a card once published, a placeholder before
        slots = {c.attrs.get("data-project") for c in r.find_all("div", "pj-slot")}
        published = {s["project"] for s in visible if s["kind"] == "official"}
        self.assertEqual(set(curriculum()["projects"]) - published, slots)
        for c in r.find_all("div", "pj-slot"):
            self.assertIn("Not published yet", c.text())
            self.assertEqual([], c.find_all("a"))

    def test_drafts_have_a_page_but_no_card(self):
        drafts = [s for s in self.specs if not s["visible"]]
        index = (OUT / "index.html").read_text(encoding="utf-8")
        for s in drafts:
            self.assertTrue((OUT / f'{s["slug"]}.html').is_file())
            self.assertNotIn(f'data-slug="{s["slug"]}"', index)
            self.assertNotIn(f'href="{s["slug"]}.html"', index)

    def _render_fixture_index(self, files: dict[str, str]) -> ParsedPage:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for rel, text in files.items():
                p = root / "projects" / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text, encoding="utf-8")
            specs = bp.load_specs(root, copy.deepcopy(self.cur))
            html = bp.render_index(specs, site_pages.load_config(), site_pages.version())
            out = root / "index.html"
            out.write_text(html, encoding="utf-8")
            return ParsedPage(out)

    def test_closed_cards_are_marked_and_drafts_listed_nowhere(self):
        page = self._render_fixture_index({
            "sprints/2026-10-21-fixture.md": sprint(),
            "sprints/2026-10-28-done.md": sprint(assigned="2026-10-28", due="2026-10-30", handIn="week-03/hackathon/", status="closed"),
            "official/P1-fixture.md": official(status="draft"),
        })
        cards = {c.attrs.get("data-slug"): c for c in page.root.find_all("div", "pj-card")}
        self.assertEqual({"fixture", "done"}, set(cards))
        self.assertIn("pj-closed", cards["done"].classes())
        self.assertNotIn("pj-closed", cards["fixture"].classes())
        self.assertNotIn("No sprint published yet.", page.raw)

    def test_empty_index_says_so(self):
        page = self._render_fixture_index({"official/P1-fixture.md": official(status="draft")})
        self.assertEqual([], page.root.find_all("div", "pj-card"))
        self.assertIn("No sprint published yet.", page.raw)
        # the official projects of the curriculum are still listed, as placeholders
        self.assertEqual(len(curriculum()["projects"]), len(page.root.find_all("div", "pj-slot")))

    def test_spec_pages(self):
        self.assertTrue(self.specs, "the drop zone holds at least one spec")
        for s in self.specs:
            with self.subTest(spec=s["slug"]):
                page = ParsedPage(OUT / f'{s["slug"]}.html')
                _common_checks(self, page)
                r = page.root
                self.assertEqual(s["title"], r.find("h1").text().strip())
                facts = {tr.find("th").text().strip(): tr.find("td") for tr in r.find("table", "pj-facts").find_all("tr")}
                self.assertEqual(s["handIn"], facts["Hand-in"].find("code").text())
                if s["kind"] == "official":
                    ul = facts["Checkpoints"].find("ul", "pj-checkpoints")
                    self.assertEqual([bp.checkpoint_text(c) for c in s["checkpoints"]],
                                     [li.text().strip() for li in ul.find_all("li")])
                    self.assertEqual([], ul.find_all("a"), "checkpoints are plain text, never a link")
                    self.assertIn("Week ", bp.checkpoint_text(s["checkpoints"][0]))
                    self.assertEqual(s["projectLabel"], self.cur["projects"][s["project"]]["label"])
                    self.assertIn(s["projectLabel"], facts["Project"].text())
                    self.assertEqual(bp.LABELS[s["status"]], facts["Status"].text().strip())
                    self.assertEqual(s["status"] == "draft", r.find("p", "pj-draft") is not None)
                else:
                    self.assertEqual(bp.LABELS[s["mode"]], facts["Mode"].text().strip())
                    self.assertEqual(build_index.date_label(s["assigned"], year=True), facts["Assigned"].text().strip())
                    self.assertEqual(build_index.date_label(s["due"], year=True), facts["Due"].text().strip())
                    if s["tools"]:
                        self.assertEqual(", ".join(s["tools"]), facts["Tools"].text().strip())
                    self.assertEqual(bp.LABELS[s["status"]], facts["Status"].text().strip())

    def test_checkpoint_text_shape(self):
        c = {"week": 5, "slot": 5, "date": build_index.slot_date(self.cur, 5, 5), "label": "Showcase"}
        self.assertEqual("Week 5 · Day 5 — Fri Nov 13, 2026 — Showcase", bp.checkpoint_text(c))


# ---------------------------------------------------------------- decoupling (two-way)
PROJECTS_RE = re.compile(r"(^|[^a-z])projects/", re.M)


class DecouplingTests(unittest.TestCase):
    def test_project_pages_never_link_day_or_exit_pages(self):
        for p in sorted(OUT.glob("*.html")):
            page = ParsedPage(p)
            for a in page.root.find_all("a"):
                if "topnav" in a.classes():
                    continue
                href = a.attrs.get("href", "")
                self.assertFalse(href.startswith(("../weeks/", "../exit-criteria/")) or "weeks/" in href
                                 or "exit-criteria/" in href, f"{p.name}: {href}")

    def test_specs_never_name_day_or_exit_pages(self):
        for p in sorted((ROOT / "projects").rglob("*.md")):
            text = p.read_text(encoding="utf-8")
            self.assertNotIn("weeks/", text, p.relative_to(ROOT).as_posix())
            self.assertNotIn("exit-criteria/", text, p.relative_to(ROOT).as_posix())

    def test_day_pipeline_never_names_projects(self):
        files = sorted((DOCS / "weeks").rglob("*.html"))
        files += [HARNESS / "templates" / "day.exemplar.html", HARNESS / "plan_check.py", HARNESS / "args_for.py"]
        files += sorted((HARNESS / "workflows").glob("*.js")) + sorted((HARNESS / "critics").glob("*.md"))
        self.assertGreater(len(files), 5)
        for p in files:
            m = PROJECTS_RE.search(p.read_text(encoding="utf-8"))
            self.assertIsNone(m, f"{p.relative_to(ROOT).as_posix()} names projects/")

    def test_exit_pages_link_projects_only_from_the_topnav(self):
        pages = sorted((DOCS / "exit-criteria").glob("*.html"))
        self.assertTrue(pages)
        for p in pages:
            page = ParsedPage(p)
            links = [a for a in page.root.find_all("a") if "projects/" in a.attrs.get("href", "")]
            self.assertEqual(1, len(links), p.name)
            self.assertIn("topnav", links[0].classes())
            self.assertEqual(1, len(PROJECTS_RE.findall(page.raw)), p.name)


if __name__ == "__main__":
    unittest.main()
