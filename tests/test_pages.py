"""Notes-page contract for every authored or live day (D-0052) (and the exemplar's structure)."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

from helpers import DOCS, FORBIDDEN_RE, HARNESS, PAGE_SCRIPT_ORDER, ROOT, ParsedPage, authored_days, load_json, metrics, node_exe

sys.path.insert(0, str(HARNESS))
import build_index  # noqa: E402
import notes_check  # noqa: E402

EXEMPLAR = HARNESS / "templates" / "day.exemplar.html"
DEMO_REPO_URL = load_json(HARNESS / "config.json")["demoRepo"]["url"]


def _structure_checks(tc: unittest.TestCase, page: ParsedPage, day_id: str | None):
    r = page.root
    tc.assertIn("tc-day", page.meta)
    if day_id:
        tc.assertEqual(day_id, page.meta["tc-day"])
    tc.assertIsNotNone(r.find("nav", "toc"))
    tc.assertIsNotNone(r.find("article", "reading-col"))
    tc.assertIsNotNone(r.find("aside", "side"))
    tc.assertIsNotNone(r.find("div", "lede"))
    steps = r.find_all("section", "step")
    tc.assertEqual([str(i) for i in range(len(steps))], [s.attrs.get("data-step") for s in steps])
    for s in steps:
        tc.assertIsNotNone(s.find("h2"))
        tc.assertIsNotNone(s.find(class_name="tag"))
    # reference-depth shape (D-0040): a closing "Check yourself" step, an interview callout, a sources stamp
    tc.assertTrue(steps, "a page needs steps")
    tc.assertEqual("check yourself", steps[-1].find(class_name="tag").text().strip().lower(), "the last step is Check yourself (D-0040)")
    tc.assertTrue(steps[-1].find_all("details", "check"), "Check yourself needs details.check blocks")
    tc.assertTrue(r.find_all("div", "interview"), "at least one .callout.interview (D-0040)")
    tc.assertIn("Sources checked", r.find(class_name="meta").text())
    tc.assertIsNotNone(r.find("section", "reading-sources"))
    tc.assertIsNotNone(r.find("svg", id="diagram"))
    tc.assertIsNotNone(r.find(class_name="stage-caption"))
    # D-0055: demos are disconnected from the site: no demo card, no demo list, no code popup; one Demos link to the demo repo
    tc.assertIsNone(r.find(class_name="demo-card"), "no demo card on a notes page (D-0055)")
    tc.assertNotIn("data-demo", page.raw)
    tc.assertEqual([], r.find_all("button", "code-cta"), "no code popups (D-0055)")
    tc.assertNotIn("Demos today", page.raw)
    demos_links = [a for a in r.find_all("a", "topnav") if a.text().strip() == "Demos"]
    tc.assertEqual(1, len(demos_links))
    tc.assertEqual(DEMO_REPO_URL, demos_links[0].attrs.get("href"), "the topnav Demos link points at the public demo repo")
    tc.assertIsNotNone(r.find("button", "activity-card", data_modal="quiz-modal"))
    tc.assertIsNotNone(r.find("a", "snav-next"))
    tc.assertIsNotNone(r.find("div", id="quiz-modal"))
    tc.assertIsNotNone(r.find("section", id="quiz"))
    tc.assertIsNotNone(r.find("div", id="goals-modal"))
    goals = r.find("ul", "goals-list")
    tc.assertIsNotNone(goals)
    # scripts
    srcs = page.script_srcs
    tc.assertEqual("theme.js", srcs[0])
    tc.assertEqual(PAGE_SCRIPT_ORDER, srcs[1:])   # D-0061: no survey.js, on any day
    tc.assertIsNone(FORBIDDEN_RE.search(page.raw), FORBIDDEN_RE.search(page.raw))


class ExemplarTests(unittest.TestCase):
    def test_configured_template_exists(self):
        """config.json template (D-0031) names a real page under docs/weeks/ or harness/templates/."""
        cfg = json.loads((HARNESS / "config.json").read_text(encoding="utf-8"))
        tpl = cfg.get("template")
        if not tpl:
            return
        path = ROOT / tpl
        self.assertTrue(path.is_file(), f"config.json template {tpl} missing")
        self.assertTrue(tpl.startswith("docs/weeks/") or tpl.startswith("harness/templates/"), tpl)
        _structure_checks(self, ParsedPage(path), None)

    def test_exemplar_structure(self):
        self.assertTrue(EXEMPLAR.exists())
        page = ParsedPage(EXEMPLAR)
        _structure_checks(self, page, None)
        c = notes_check.counts(page.raw)
        M = metrics()["notes"]
        self.assertTrue(c["lastIsCheck"])
        self.assertTrue(all(n >= M["h3PerStepMin"] for n in c["h3"]), c["h3"])
        self.assertTrue(all(n == M["interviewPerStep"] for n in c["interview"]), c["interview"])
        self.assertTrue(all(n >= M["citationsPerStepMin"] for n in c["citations"]), c["citations"])
        self.assertEqual([], notes_check.citation_findings(notes_check.citation_report(page.raw, None)))
        self.assertEqual([], notes_check.phrase_hits(page.raw, M["deliveryPhrases"]))
        self.assertEqual([], notes_check.phrase_hits(page.raw, M["assumptionPhrases"]))  # D-0048
        if node_exe():
            p = page.probe()
            self.assertEqual(p["captions"], len(page.root.find_all("section", "step")))
            self.assertEqual(M["quizQuestions"], p["questions"])


class AuthoredPageTests(unittest.TestCase):
    def test_every_authored_page(self):
        """Every authored or live day's page (D-0052)."""
        M = metrics()["notes"]
        for w, d, rel in authored_days():
            path = DOCS / "weeks" / f"{rel}.html"
            with self.subTest(rel=rel):
                page = ParsedPage(path)
                _structure_checks(self, page, d["id"])
                steps = page.root.find_all("section", "step")
                self.assertTrue(M["stepsMin"] <= len(steps) <= M["stepsMax"], len(steps))
                words = page.prose_words()
                self.assertTrue(M["wordMin"] - M["wordTolerance"] <= words <= M["wordMax"] + M["wordTolerance"], f"{words} words")
                mins = re.search(r"~(\d+) min", page.raw)
                self.assertIsNotNone(mins, "meta line needs ~N min")
                self.assertAlmostEqual(round(words / M["readingWpm"]), int(mins.group(1)), delta=1)
                # reference-depth bars (D-0040): one checker for the author, the critic and this test
                rep = notes_check.check_page(path, {"counts", "phrases", "stamps", "citations", "style"}, M, tolerance=M["wordTolerance"])
                self.assertEqual([], rep["findings"], "\n".join(rep["findings"]))
                self.assertEqual(words, rep["counts"]["words"], "helpers.prose_words and notes_check.counts must agree")
                goals = page.root.find("ul", "goals-list").find_all("li")
                self.assertTrue(M["goalsMin"] <= len(goals) <= M["goalsMax"])
                src_links = [a for a in page.root.find("section", "reading-sources").find_all("a") if a.attrs.get("href", "").startswith("http")]
                self.assertGreaterEqual(len(src_links), M["sourcesMin"])
                # goals modal links to exercise README
                goal_hrefs = " ".join(a.attrs.get("href", "") for a in page.root.find("div", id="goals-modal").find_all("a"))
                self.assertIn(f"exercises/{rel}", goal_hrefs)
                # relative links resolve
                for href in page.hrefs():
                    if href.startswith(("http", "#", "mailto:")):
                        continue
                    target = (path.parent / href.split("?")[0].split("#")[0]).resolve()
                    self.assertTrue(target.exists(), f"broken relative link {href}")
                if node_exe():
                    p = page.probe()
                    self.assertEqual(len(steps), p["captions"])
                    self.assertTrue(p["nodesOk"] and p["edgesOk"])
                    self.assertEqual(M["quizQuestions"], p["questions"])
                    t = p["types"]
                    self.assertGreaterEqual(t.count("scq"), M["quizTypeMix"]["scq"])
                    self.assertGreaterEqual(t.count("tf"), M["quizTypeMix"]["tf"])
                    self.assertGreaterEqual(t.count("mcq") + t.count("match"), M["quizTypeMix"]["mcqOrMatch"])
                    self.assertLessEqual(t.count("open"), M["quizTypeMix"]["openMax"])
                    self.assertTrue(p["answersOk"] and p["explainsOk"])
                    self.assertTrue(p["next"])
                    nxt = (path.parent / p["next"]).resolve()
                    self.assertTrue(nxt.exists(), f"NEXT target missing: {p['next']}")


if __name__ == "__main__":
    unittest.main()
