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
        self.assertEqual([2, 2, 2, 3, 2], c["h3"])   # step 3 gained a "Side by side" table subsection (D-0060)
        self.assertEqual([1] * 5, c["interview"])
        self.assertEqual(5, c["checkDetails"])
        self.assertGreaterEqual(c["codeBlocks"], 6)
        self.assertTrue(all(n >= 2 for n in c["citations"]), c["citations"])
        self.assertEqual(6, c["quizQ"])
        self.assertEqual(6, c["sources"])
        self.assertEqual("2026-01-01", c["sourcesChecked"])
        self.assertEqual(35, c["declaredMinutes"])

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
                                 ("steps", 11, "steps")]:
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

    def test_assumption_phrases(self):  # D-0048
        phrases = metrics()["notes"]["assumptionPhrases"]
        self.assertEqual([], notes_check.phrase_hits(self.text, phrases))
        hit = self.text.replace("<h3>First subtopic as an h3</h3>", "<h3>First subtopic as an h3</h3>\n<p>You already write Python. A list already knows its length.</p>", 1)
        self.assertEqual(["you already"], [h["phrase"] for h in notes_check.phrase_hits(hit, phrases)])
        rep = notes_check.check_page(EXEMPLAR, {"phrases"}, dict(metrics()["notes"], assumptionPhrases=["first subtopic"]))
        self.assertTrue(any(f.startswith("assumption phrase 'first subtopic'") for f in rep["findings"]), rep["findings"])

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


class StyleTests(unittest.TestCase):
    """--style (D-0060): the readability bar of the teaching steps."""

    def setUp(self):
        self.text = EXEMPLAR.read_text(encoding="utf-8")
        self.mp = metrics()["notes"]["prose"]

    def _findings(self, text: str) -> list[str]:
        return notes_check.style_findings(notes_check.style(text), self.mp)

    def test_exemplar_is_clean(self):
        self.assertEqual([], self._findings(self.text))
        s = notes_check.style_summary(notes_check.style(self.text), self.mp)
        self.assertEqual(5, s["recaps"])
        self.assertGreaterEqual(s["structuredBlocks"], self.mp["structuredBlocksMin"])
        self.assertEqual(0, s["codeNoOutput"])

    def test_sentences_split_on_blocks_not_line_wraps(self):
        marked = ("First sentence runs\n        over a wrap. Second one, e.g. with an abbreviation and 3.5 inside, ends here."
                  + notes_check.BLOCK_MARK + "A list item without a stop" + notes_check.BLOCK_MARK)
        s = notes_check.sentences(marked)
        self.assertEqual(["First sentence runs over a wrap.", "Second one, e.g. with an abbreviation and 3.5 inside, ends here.", "A list item without a stop"],
                         [x["text"] for x in s])
        code = f"Call {notes_check.CODE_MARK} then {notes_check.CODE_MARK} twice."
        self.assertEqual([(3, 2)], [(x["words"], x["codeSpans"]) for x in notes_check.sentences(code)])   # Call, then, twice.

    def test_each_cap_is_named(self):
        anchor = "<h3>First subtopic as an h3</h3>"
        cases = {
            "paragraph of": anchor + "<p>" + "word " * 81 + "</p>",
            "sentence of": anchor + "<p>" + "word " * 41 + ".</p>",
            "code spans": anchor + "<p>" + "<code>x</code> and " * 6 + "done.</p>",
            "<pre> followed by": anchor + "<pre><code>print(1)</code></pre><h3>Bare</h3>",
        }
        for needle, insert in cases.items():
            with self.subTest(cap=needle):
                f = self._findings(self.text.replace(anchor, insert, 1))
                self.assertTrue(any(needle in x and x.startswith("style:") for x in f), f)
        import re
        no_blocks = re.sub(r"<table>.*?</table>", "<p>The table, as prose.</p>", self.text, flags=re.S)
        no_blocks = re.sub(r"<ul>\s*<li>the first thing.*?</ul>", "<p>The list, as prose.</p>", no_blocks, flags=re.S)
        no_blocks = re.sub(r"<ul>\s*<li>The first subtopic.*?</ul>", "<p>The list, as prose.</p>", no_blocks, flags=re.S)
        self.assertEqual(0, notes_check.style(no_blocks)["structuredBlocks"])
        for needle, bad in {
            "structured blocks": no_blocks,
            "div.recap, expected": self.text.replace('<div class="recap">', '<div class="recap-x">', 1),
            "recap label": self.text.replace('<div class="k">Takeaways</div>', '<div class="k">Recap</div>', 1),
            "recap has": self.text.replace("<li>A second line: the trade-off or limit this step named.</li>\n            <li>A third line, optional: how to recognise the thing in someone else's code.</li>", "", 1),
            "recap item": self.text.replace("<li>A second line: the trade-off or limit this step named.</li>", "<li>" + "word " * 21 + "</li>", 1),
        }.items():
            with self.subTest(cap=needle):
                f = self._findings(bad)
                self.assertTrue(any(needle in x for x in f), f)

    def test_callouts_and_check_answers_are_exempt(self):
        long = "word " * 45 + "."
        t = self.text.replace('<p>A spoken answer to "how does this work under the hood?" in two or three sentences.</p>', f"<p>{long}</p>", 1)
        t = t.replace("<p>The answer in one to four sentences, correct against the brief.</p>", f"<p>{long}</p>", 1)
        self.assertEqual([], self._findings(t))

    def test_output_block_counts_as_output_not_code(self):
        c = notes_check.counts(self.text)
        self.assertEqual(c["codeBlocks"], self.text.count("<pre><code>"))
        self.assertIn('<pre class="out">', self.text)
        t = self.text.replace('<pre><code>print("option a")</code></pre>\n        <p>Prints <code>option a</code>. What it buys and what it costs.</p>',
                              '<pre><code>print("option a")</code></pre>\n<pre class="out">option a</pre>\n        <p>What it buys and what it costs.</p>', 1)
        self.assertEqual([], self._findings(t))

    def test_style_is_a_default_phase_and_in_the_json(self):
        self.assertIn("style", notes_check.DEFAULT_PHASES)
        r = subprocess.run([sys.executable, str(HARNESS / "notes_check.py"), str(EXEMPLAR), "--style", "--json"], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        data = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn("style", data["pages"][0])
        self.assertEqual(5, data["pages"][0]["style"]["recaps"])


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
        page = json.loads(r.stdout)["pages"][0]
        self.assertIsInstance(page["findings"], list)
        self.assertTrue(page["findings"], "the exemplar fails the word band")
        self.assertTrue(all(isinstance(f, str) for f in page["findings"]))
        self.assertEqual(len(page["findings"]), page["findingCount"])


class PageSelectionTests(unittest.TestCase):
    """--all-live sweeps live days only; --all-authored (D-0052) sweeps authored and live days."""
    CUR = {"weeks": [{"dir": "week-01", "days": [
        {"kind": "holiday"},
        {"kind": "lesson", "slug": "day-2-a", "status": "live"},
        {"kind": "lesson", "slug": "day-3-b", "status": "authored"},
        {"kind": "lesson", "slug": "day-4-c", "status": "planned"}]}]}

    def names(self, statuses):
        return [p.name for p in notes_check.pages_with_status(statuses, cur=self.CUR, root=ROOT)]

    def test_live_only(self):
        self.assertEqual(["day-2-a.html"], self.names(("live",)))

    def test_authored_and_live(self):
        self.assertEqual(["day-2-a.html", "day-3-b.html"], self.names(("authored", "live")))

    def test_helpers_use_the_right_statuses(self):
        cur = json.loads((HARNESS / "curriculum.json").read_text(encoding="utf-8"))
        days = [(w["dir"], d) for w in cur["weeks"] for d in w["days"] if d.get("kind") != "holiday"]
        live = [ROOT / "docs" / "weeks" / wd / f"{d['slug']}.html" for wd, d in days if d.get("status") == "live"]
        both = [ROOT / "docs" / "weeks" / wd / f"{d['slug']}.html" for wd, d in days if d.get("status") in ("authored", "live")]
        self.assertEqual(live, notes_check.live_pages())
        self.assertEqual(both, notes_check.authored_pages())


if __name__ == "__main__":
    unittest.main()
