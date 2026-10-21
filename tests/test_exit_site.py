"""The learner-facing exit-criteria pages (D-0063): generated, in sync, linked, and link only live days."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

from helpers import DOCS, FORBIDDEN_RE, HARNESS, ParsedPage, curriculum

sys.path.insert(0, str(HARNESS))
import build_exit_pages  # noqa: E402
import build_index  # noqa: E402
import exit_criteria  # noqa: E402
import site_pages  # noqa: E402

OUT = DOCS / "exit-criteria"
ISO_RE = re.compile(r"20\d\d-\d\d-\d\d")


def _groups() -> list[dict]:
    return exit_criteria.load_groups(curriculum())


def _sibling_section_indexes() -> set[str]:
    """The topnav hrefs the shared shell emits for the OTHER generated sections (site_pages.SECTIONS)."""
    return {f"../{d}/index.html" for key, _label, d in site_pages.SECTIONS if key != "exit"}


def _index_version() -> str:
    return re.search(r'style\.css\?v=([^"]+)', (DOCS / "index.html").read_text(encoding="utf-8")).group(1)


def _page_version(page: ParsedPage) -> str:
    m = re.search(r'style\.css\?v=([^"]+)', page.raw)
    return m.group(1) if m else ""


def _common_checks(tc: unittest.TestCase, page: ParsedPage):
    r = page.root
    tc.assertEqual(["theme.js"], page.script_srcs, "theme.js is the only script src")
    for s in r.find_all("script"):
        if s.attrs.get("src"):
            js_v = re.search(r'theme\.js\?v=([^"]+)', (DOCS / "index.html").read_text(encoding="utf-8")).group(1)
            tc.assertEqual(f"../assets/js/theme.js?v={js_v}", s.attrs["src"], "theme.js keeps its own ?v= (bump-css.sh --all)")
    tc.assertIsNotNone(r.find(class_name="topbar-right"))
    tc.assertIsNone(r.find(class_name="reading2col"), "no .reading2col: theme.js would inject the view switch")
    nav = [a for a in r.find_all("a", "topnav") if a.text().strip() == "Exit criteria"]
    tc.assertEqual(1, len(nav))
    tc.assertEqual("index.html", nav[0].attrs.get("href"))
    nav = [a for a in r.find_all("a", "topnav") if a.text().strip() == "Projects"]
    tc.assertEqual(1, len(nav), "the shared shell (site_pages.SECTIONS) links the Projects section once")
    tc.assertEqual("../projects/index.html", nav[0].attrs.get("href"))
    tc.assertIsNone(FORBIDDEN_RE.search(page.raw), FORBIDDEN_RE.search(page.raw))
    tc.assertNotRegex(page.raw, r"<html[^>]*\bdata-view")
    tc.assertNotRegex(page.raw, r"<html[^>]*\bdata-theme")
    tc.assertIsNone(ISO_RE.search(page.raw), "no hand-typed date on a generated page")
    tc.assertEqual(_index_version(), _page_version(page), "the ?v= cache-buster follows docs/index.html (bump-css.sh)")
    tc.assertIsNotNone(r.find("main", id="reading-main"))
    tc.assertIsNotNone(r.find("a", "skip-link"))
    for href in page.hrefs():
        if href.startswith(("http", "#", "mailto:")):
            continue
        tc.assertFalse(href.startswith("//"), href)
        target = (page.path.parent / href.split("?")[0].split("#")[0]).resolve()
        if href in _sibling_section_indexes() and not target.parent.is_dir():
            continue  # another generated section's index: optional only while that section has no pages at all
        tc.assertTrue(target.is_file(), f"broken relative link {href}")
    for href in page.hrefs():
        if href.startswith("http"):
            tc.assertTrue(href.startswith("https://github.com/"), f"no external origin but GitHub: {href}")


class SyncTests(unittest.TestCase):
    def test_pages_are_in_sync_with_the_builder(self):
        self.assertEqual([], build_exit_pages.check())

    def test_expected_files(self):
        want = {p.name for p in build_exit_pages.expected()}
        self.assertIn("index.html", want)
        for g in _groups():
            self.assertEqual(g["exists"], Path(g["source"]).with_suffix(".html").name in want, g["id"])
        self.assertEqual(want, {p.name for p in OUT.glob("*.html")})

    def test_hooks_rebuild_the_pages(self):
        for name in ("build_index.py", "release_week.py", "close_day.py"):
            src = (HARNESS / name).read_text(encoding="utf-8")
            self.assertIn("build_exit_pages.build(", src, name)
        self.assertIn("build_exit_pages.check(", (HARNESS / "build_index.py").read_text(encoding="utf-8"))

    def test_site_index_links_the_pages(self):
        page = ParsedPage(DOCS / "index.html")
        nav = [a for a in page.root.find_all("a", "topnav") if a.text().strip() == "Exit criteria"]
        self.assertEqual(1, len(nav))
        self.assertEqual("exit-criteria/index.html", nav[0].attrs.get("href"))
        rail = [a for a in page.root.find("div", "friday-rituals").find_all("a", "fr-btn") if a.attrs.get("href") == "exit-criteria/index.html"]
        self.assertEqual(1, len(rail))


class IndexPageTests(unittest.TestCase):
    def setUp(self):
        self.page = ParsedPage(OUT / "index.html")

    def test_shape(self):
        _common_checks(self, self.page)
        r = self.page.root
        self.assertEqual("Exit criteria", r.find("h1").text().strip())
        cards = r.find_all("div", "ec-card")
        groups = _groups()
        self.assertEqual(len(groups), len(cards))
        for g, card in zip(groups, cards):
            with self.subTest(group=g["id"]):
                self.assertEqual(g["label"], card.find("h2").text().strip())
                self.assertIn(g["id"], card.find(class_name="k").text())
                link = card.find("a", "fr-btn")
                if g["exists"]:
                    self.assertIsNotNone(link)
                    self.assertEqual(Path(g["source"]).with_suffix(".html").name, link.attrs.get("href"))
                    self.assertNotIn("Not published yet", card.text())
                    n = {t: sum(1 for c in g["criteria"] if c["tier"] == t) for t in exit_criteria.TIERS}
                    self.assertIn(f"{n['Required']} required · {n['Preferred']} preferred · {n['Stretch']} stretch", card.text())
                else:
                    self.assertIsNone(link)
                    self.assertIn("Not published yet", card.text())


class GroupPageTests(unittest.TestCase):
    def test_every_published_group(self):
        cur = curriculum()
        live = {}
        for w in cur["weeks"]:
            for d in build_index.teaching_days(w):
                live[f"{w['dir']}/{d['slug']}"] = (d["id"], d.get("status"))
        for g in _groups():
            if not g["exists"]:
                self.assertFalse((OUT / Path(g["source"]).with_suffix(".html").name).exists(), g["id"])
                continue
            with self.subTest(group=g["id"]):
                path = OUT / Path(g["source"]).with_suffix(".html").name
                page = ParsedPage(path)
                _common_checks(self, page)
                r = page.root
                ids = {c["id"] for c in g["criteria"]}
                boxes = r.find_all("input", type="checkbox")
                self.assertEqual(ids, {b.attrs.get("data-ec") for b in boxes})
                self.assertEqual(len(ids), len(boxes))
                for cid in ids:
                    self.assertIsNotNone(r.find("tr", id=cid), cid)
                h3_ids = {h.attrs.get("id") for h in r.find_all("h3")}
                for day in build_exit_pages.group_days(g, cur):
                    self.assertIn(day["dayId"], h3_ids)
                for a in r.find_all("a"):
                    href = a.attrs.get("href", "")
                    if href.startswith("../weeks/"):
                        rel = href[len("../weeks/"):-len(".html")]
                        self.assertIn(rel, live, href)
                        self.assertEqual("live", live[rel][1], f"{href} links a day that is not live")
                        self.assertTrue((DOCS / "weeks" / f"{rel}.html").is_file(), href)
                for s in r.find_all("span", "ec-soon"):
                    self.assertEqual([], s.find_all("a"))
                js = page.embedded_js
                self.assertIn("localStorage", js)
                self.assertIn("try", js)
                self.assertIn(f'"tc_exit_{g["id"]}"', js)
                self.assertIsNotNone(r.find("button", id="ec-reset"))
                self.assertIsNotNone(r.find(id="ec-count"))
                self.assertIsNotNone(r.find("section", id="by-day"))
                for sec in g["sections"]:
                    self.assertIsNotNone(r.find("section", id=sec["slug"]), sec["slug"])
                for word in ("TBD", "OWED"):
                    self.assertNotRegex(page.raw, rf"\b{word}\b")
                self.assertNotRegex(page.raw, r"(?i)\bpending\b|blocked until")


if __name__ == "__main__":
    unittest.main()
