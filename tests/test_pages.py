"""Notes-page contract for every live day (and the exemplar's structure)."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

from helpers import DOCS, FORBIDDEN_RE, HARNESS, PAGE_SCRIPT_ORDER, ROOT, ParsedPage, live_days, metrics, node_exe

sys.path.insert(0, str(HARNESS))
import build_index  # noqa: E402

EXEMPLAR = HARNESS / "templates" / "day.exemplar.html"


def _structure_checks(tc: unittest.TestCase, page: ParsedPage, day_id: str | None, feedback: bool):
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
    tc.assertIsNotNone(r.find("section", "reading-sources"))
    tc.assertIsNotNone(r.find("svg", id="diagram"))
    tc.assertIsNotNone(r.find(class_name="stage-caption"))
    tc.assertIsNotNone(r.find(class_name="demo-card"))
    tc.assertIsNotNone(r.find("button", "activity-card", data_modal="quiz-modal"))
    tc.assertIsNotNone(r.find("a", "snav-next"))
    tc.assertIsNotNone(r.find("div", id="quiz-modal"))
    tc.assertIsNotNone(r.find("section", id="quiz"))
    tc.assertIsNotNone(r.find("div", id="goals-modal"))
    goals = r.find("ul", "goals-list")
    tc.assertIsNotNone(goals)
    # code popups: every code-cta has a matching modal with a .cv[data-file]
    for btn in r.find_all("button", "code-cta"):
        target = btn.attrs.get("data-modal")
        modal = r.find("div", id=target)
        tc.assertIsNotNone(modal, f"missing modal {target}")
        cv = modal.find("div", "cv")
        tc.assertIsNotNone(cv)
        tc.assertTrue(cv.attrs.get("data-file"))
    # scripts
    srcs = page.script_srcs
    tc.assertEqual("theme.js", srcs[0])
    expected = PAGE_SCRIPT_ORDER + (["survey.js"] if feedback else [])
    tc.assertEqual(expected, srcs[1:])
    tc.assertIsNone(FORBIDDEN_RE.search(page.raw), FORBIDDEN_RE.search(page.raw))


class ExemplarTests(unittest.TestCase):
    def test_exemplar_structure(self):
        self.assertTrue(EXEMPLAR.exists())
        page = ParsedPage(EXEMPLAR)
        _structure_checks(self, page, None, feedback=False)
        if node_exe():
            p = page.probe()
            self.assertEqual(p["captions"], len(page.root.find_all("section", "step")))
            self.assertEqual(6, p["questions"])


class LivePageTests(unittest.TestCase):
    def test_every_live_page(self):
        M = metrics()["notes"]
        for w, d, rel in live_days():
            path = DOCS / "weeks" / f"{rel}.html"
            with self.subTest(rel=rel):
                page = ParsedPage(path)
                _structure_checks(self, page, d["id"], build_index.is_feedback(w, d))
                steps = page.root.find_all("section", "step")
                self.assertTrue(M["stepsMin"] <= len(steps) <= M["stepsMax"], len(steps))
                words = page.prose_words()
                self.assertTrue(M["wordMin"] - M["wordTolerance"] <= words <= M["wordMax"] + M["wordTolerance"], f"{words} words")
                mins = re.search(r"~(\d+) min", page.raw)
                self.assertIsNotNone(mins, "meta line needs ~N min")
                self.assertAlmostEqual(round(words / M["readingWpm"]), int(mins.group(1)), delta=1)
                goals = page.root.find("ul", "goals-list").find_all("li")
                self.assertTrue(M["goalsMin"] <= len(goals) <= M["goalsMax"])
                src_links = [a for a in page.root.find("section", "reading-sources").find_all("a") if a.attrs.get("href", "").startswith("http")]
                self.assertGreaterEqual(len(src_links), M["sourcesMin"])
                popups = page.root.find_all("button", "code-cta")
                self.assertTrue(M["codePopupsMin"] <= len(popups) <= M["codePopupsMax"])
                demo_dir = ROOT / "demos" / rel
                for btn in popups:
                    modal = page.root.find("div", id=btn.attrs["data-modal"])
                    f = modal.find("div", "cv").attrs["data-file"]
                    self.assertTrue((demo_dir / f).exists(), f"popup names missing demo file {f}")
                # demo card links name real files
                demo_links = [a.attrs["href"] for a in page.root.find(class_name="demo-card").find_all("a")]
                self.assertTrue(demo_links)
                for href in demo_links:
                    name = href.rstrip("/").rsplit("/", 1)[-1]
                    self.assertTrue((demo_dir / name).exists() or name == rel.rsplit("/", 1)[-1], f"demo link {href} not on disk")
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
