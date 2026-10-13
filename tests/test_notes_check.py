"""harness/notes_check.py (D-0040): the one mechanical checker for reference-depth notes pages."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from helpers import HARNESS, ROOT, metrics

sys.path.insert(0, str(HARNESS))
import notes_check  # noqa: E402

EXEMPLAR = HARNESS / "templates" / "day.exemplar.html"
BRIEF = (
    "# w00d0 — Topic\n\ngate: light\nverified: 2026-01-01\n\nversion-stamps:\n  - python: 3.15 (verified 2026-01-01)\n"
    "  - git: 2.50 (verified 2026-01-01)\n\n## Claims\n\n- A claim — [Tutorial](https://docs.python.org/3/tutorial/)\n\n"
    "## Sources\n\n- Tutorial — https://docs.python.org/3/tutorial/\n- sys — https://docs.python.org/3/library/sys.html\n"
    "- Pro Git — https://git-scm.com/book/en/v2\n- PEP 8 — https://peps.python.org/pep-0008/\n"
    "- Built-ins — https://docs.python.org/3/library/functions.html\n- Reference — https://docs.python.org/3/reference/\n"
)


class CountTests(unittest.TestCase):
    def setUp(self):
        self.text = EXEMPLAR.read_text(encoding="utf-8")
        self.c = notes_check.counts(self.text)

    def test_exemplar_counts(self):
        c = self.c
        self.assertEqual(6, c["steps"])
        self.assertEqual(6, c["captions"])
        self.assertTrue(c["lastIsCheck"])
        self.assertEqual(5, c["teachingSteps"])
        self.assertEqual([2] * 5, c["h3"])
        self.assertEqual([1] * 5, c["interview"])
        self.assertEqual(5, c["checkDetails"])
        self.assertGreaterEqual(c["codeBlocks"], 6)
        self.assertTrue(all(n >= 2 for n in c["citations"]), c["citations"])
        self.assertEqual(6, c["quizQ"])
        self.assertEqual(6, c["sources"])
        self.assertEqual("2026-01-01", c["sourcesChecked"])
        self.assertEqual(35, c["declaredMinutes"])
        self.assertEqual(1, c["popups"])

    def test_words_skip_code_sources_and_citation_markers(self):
        base = self.c["words"]
        more = self.text.replace("<h3>First subtopic as an h3</h3>", "<h3>First subtopic as an h3</h3>\n<p>five more plain words here</p>", 1)
        self.assertEqual(base + 5, notes_check.counts(more)["words"])
        for ignored in ("<pre><code>ignored words here</code></pre>", '<sup class="cite"><a href="#src-1">ignored</a></sup>', "<code>ignored words</code>"):
            with self.subTest(ignored=ignored):
                t = self.text.replace("<h3>First subtopic as an h3</h3>", "<h3>First subtopic as an h3</h3>" + ignored, 1)
                self.assertEqual(base, notes_check.counts(t)["words"])

    def test_findings_name_each_bar(self):
        m = metrics()["notes"]
        f = notes_check.count_findings(self.c, m)
        self.assertTrue(any(x.startswith("prose words") for x in f), f)   # the exemplar is a skeleton, far under the band
        ok = dict(self.c, words=5000, declaredMinutes=33)
        self.assertEqual([], notes_check.count_findings(ok, m))
        self.assertEqual([], notes_check.count_findings(dict(ok, words=4300, declaredMinutes=29), m, tolerance=250))
        self.assertTrue(notes_check.count_findings(dict(ok, words=4300, declaredMinutes=29), m), "the hard band has no tolerance")
        for key, bad, needle in [("captions", 5, "captions"), ("lastIsCheck", False, "Check yourself"), ("h3", [1, 2, 2, 2, 2], "h3"),
                                 ("interview", [0, 1, 1, 1, 1], "callout.interview"), ("checkDetails", 2, "details.check"),
                                 ("codeBlocks", 1, "code blocks"), ("citations", [0, 2, 2, 2, 2], "citations"), ("quizQ", 5, "quiz"),
                                 ("sources", 2, "sources"), ("declaredMinutes", 10, "min"), ("sourcesChecked", None, "Sources checked"),
                                 ("popups", 3, "popups"), ("steps", 11, "steps")]:
            with self.subTest(bar=key):
                self.assertTrue(any(needle in x for x in notes_check.count_findings(dict(ok, **{key: bad}), m)), key)

    def test_truncated_page_is_a_parse_error(self):
        with self.assertRaises(ValueError):
            notes_check.counts(self.text[: len(self.text) // 2])


class PhraseStampCitationTests(unittest.TestCase):
    def setUp(self):
        self.text = EXEMPLAR.read_text(encoding="utf-8")
        self.phrases = metrics()["notes"]["deliveryPhrases"]

    def test_delivery_phrases(self):
        self.assertEqual([], notes_check.phrase_hits(self.text, self.phrases))
        hit = self.text.replace("<h3>First subtopic as an h3</h3>", "<h3>First subtopic as an h3</h3>\n<p>The Trainer types it live. Trainers do.</p>", 1)
        hits = notes_check.phrase_hits(hit, self.phrases)
        self.assertEqual(["the trainer"], [h["phrase"] for h in hits])
        self.assertEqual("prose", hits[0]["where"])
        self.assertIn("types it live", hits[0]["sentence"])
        quiz = self.text.replace('stem: "Second single-choice question?"', 'stem: "What did you see in class?"', 1)
        self.assertEqual([("in class", "inline-js")], [(h["phrase"], h["where"]) for h in notes_check.phrase_hits(quiz, self.phrases)])

    def test_stamps_against_the_brief(self):
        self.assertEqual([], notes_check.stamp_findings(self.text, BRIEF))
        self.assertEqual([], notes_check.stamp_findings(self.text.replace("python 3.15</span>", "python 3.15 · git 2.50</span>"), BRIEF))
        self.assertTrue(notes_check.stamp_findings(self.text.replace("Sources checked 2026-01-01", "Sources checked 2026-02-02"), BRIEF))
        self.assertTrue(notes_check.stamp_findings(self.text.replace("python 3.15</span>", "python 3.15 · numpy 2.0</span>"), BRIEF))
        self.assertTrue(notes_check.stamp_findings(self.text.replace('<span class="verified">Sources checked 2026-01-01 · python 3.15</span>', ""), BRIEF))

    def test_citations_resolve_and_sources_come_from_the_brief(self):
        r = notes_check.citation_report(self.text, BRIEF)
        self.assertEqual(6, r["sourceIds"])
        self.assertEqual([], r["unresolved"])
        self.assertEqual([], r["notInBrief"])
        self.assertEqual([], notes_check.citation_findings(r))
        bad = self.text.replace('href="#src-6"', 'href="#src-9"', 1)
        self.assertEqual(["#src-9"], notes_check.citation_report(bad, BRIEF)["unresolved"])
        foreign = self.text.replace("https://docs.python.org/3/reference/", "https://example.org/blog", 1)
        self.assertEqual(["https://example.org/blog"], notes_check.citation_report(foreign, BRIEF)["notInBrief"])

    def test_page_links_lists_each_http_href_once(self):
        links = notes_check.page_links(self.text)
        self.assertEqual(len(links), len(set(links)))
        self.assertIn("https://peps.python.org/pep-0008/", links)
        self.assertTrue(all(l.startswith("http") for l in links))


class CliTests(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(HARNESS / "notes_check.py"), *args], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)

    def test_usage_without_arguments(self):
        self.assertEqual(2, self._run().returncode)

    def test_counts_on_the_exemplar_prints_json_and_fails_the_band(self):
        r = self._run(str(EXEMPLAR), "--counts", "--phrases")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        last = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertFalse(last["ok"])
        self.assertEqual(6, last["pages"][0]["counts"]["steps"])
        self.assertIn("prose words", r.stdout)

    def test_json_only_output(self):
        r = self._run(str(EXEMPLAR), "--counts", "--json")
        self.assertEqual(1, len(r.stdout.strip().splitlines()))
        json.loads(r.stdout)


if __name__ == "__main__":
    unittest.main()
