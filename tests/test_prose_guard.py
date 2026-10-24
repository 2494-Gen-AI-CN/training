"""harness/prose_guard.py (D-0039): a humanizer pass on a demo script or a runbook may change prose only."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import HARNESS, ROOT

sys.path.insert(0, str(HARNESS))
import prose_guard  # noqa: E402

SCRIPT = (
    "# 01 — Demo\n\nWeek 1 · Day 3\n\n"
    "- Objective: do a thing\n- Time: 20 min\n- Thread: standalone\n- Starts from: cold\n\n"
    "## Step 1 — set (10 min)\n\ncwd: `s/`\n\n```python\nx = 1\n```\n\n"
    "Talking points while typing:\n- `x` is a name bound to an object; say it once, do not dwell.\n- Run it 2 times.\n\n"
    "## Common pitfalls\n\n| Symptom | Fix |\n|---|---|\n| `NameError` on `x` | Type the line; then run again. |\n\n"
    "## What we did NOT cover (intentional)\n\n- Lists: deferred to Thursday. The ticket stays flat.\n"
)
RUNBOOK = (
    "# w01d3 runbook — Python basics\n\nWeek 1 · Day 3 · Wed Oct 14, 2026\n"
    "Notes page: [page](https://example.org/a.html) · Solutions: [solutions/](solutions/)\n\n"
    "## Day at a glance\n\n| Block | Minutes | Artifact |\n|---|---|---|\n| Demo 1 | 30 | script |\n\n"
    "## Demo 1: 01_demo.md\n\n**Script:** demos/01_demo.md · **Time:** 30 min\n"
    "**Stop point if long:** after Step 3; the talking points move to the PM, and the commit waits.\n"
    "- Q: Is the limit 79? A: Yes, the team's contract; set the ruler at column 79.\n"
)


class CompareTests(unittest.TestCase):
    def test_prose_edits_pass(self):
        new = SCRIPT.replace("say it once, do not dwell.", "say it once and move on.").replace("Type the line; then run again.", "Type the line. Then run again.")
        self.assertEqual(([], []), prose_guard.compare(SCRIPT, new, script=True))
        new = RUNBOOK.replace("after Step 3; the talking points move to the PM, and the commit waits.", "after Step 3. The talking points move to the PM, and the commit waits.")
        new = new.replace("Yes, the team's contract; set the ruler", "Yes, it is the team's contract. Set the ruler")
        self.assertEqual(([], []), prose_guard.compare(RUNBOOK, new, script=False))

    def test_line_endings_are_not_a_change(self):
        self.assertEqual(([], []), prose_guard.compare(SCRIPT, SCRIPT.replace("\n", "\r\n"), script=True))

    def _names(self, old: str, new: str, script: bool) -> list[str]:
        return [f.split(":")[0] for f in prose_guard.compare(old, new, script)[0]]

    def test_script_frozen_content_fails(self):
        for label, new, expect in [
            ("code", SCRIPT.replace("x = 1", "x = 2"), "fenced blocks"),
            ("heading", SCRIPT.replace("## Step 1 — set (10 min)", "## Step 1 — set a name (10 min)"), "headings"),
            ("header bullet", SCRIPT.replace("- Objective: do a thing", "- Objective: do one thing"), "header block"),
            ("cwd", SCRIPT.replace("cwd: `s/`", "cwd: `s/` (the scratch folder)"), "cwd lines"),
            ("inline code", SCRIPT.replace("`NameError`", "`TypeError`"), "inline code"),
            ("table header", SCRIPT.replace("| Symptom | Fix |", "| What you see | Fix |"), "table rows"),
            ("added bullet", SCRIPT.replace("- Run it 2 times.", "- Run it 2 times.\n- Then stop."), "bullet count"),
            ("moved block", SCRIPT.replace("```python\nx = 1\n```\n\n", "").replace("## Common pitfalls\n\n", "## Common pitfalls\n\n```python\nx = 1\n```\n\n"), "fence sections"),
        ]:
            with self.subTest(change=label):
                self.assertIn(expect, self._names(SCRIPT, new, True))

    def test_runbook_frozen_content_fails(self):
        for label, new, expect in [
            ("glance row", RUNBOOK.replace("| Demo 1 | 30 | script |", "| Demo 1 | 35 | script |"), "table rows"),
            ("bold label", RUNBOOK.replace("**Stop point if long:**", "Stop point if long:"), "bold labels"),
            ("url", RUNBOOK.replace("https://example.org/a.html", "https://example.org/b.html"), "urls"),
            ("links line", RUNBOOK.replace("Notes page: [page]", "Notes page: [the page]"), "header block"),
        ]:
            with self.subTest(change=label):
                self.assertIn(expect, self._names(RUNBOOK, new, False))

    def test_a_changed_number_is_a_warning(self):
        findings, warnings = prose_guard.compare(SCRIPT, SCRIPT.replace("Run it 2 times.", "Run it 3 times."), script=True)
        self.assertEqual([], findings)
        self.assertEqual(1, len(warnings))
        self.assertIn("numbers", warnings[0])

    def test_script_or_runbook_is_read_from_the_path(self):
        self.assertTrue(prose_guard.is_script("trainer/week-01/day-3-python-basics/demos/01_ticket_record.md"))
        self.assertFalse(prose_guard.is_script("trainer/week-01/day-3-python-basics/runbook.md"))


class SnapshotCliTests(unittest.TestCase):
    def _run(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(HARNESS / "prose_guard.py"), *argv], capture_output=True, text=True, cwd=ROOT)

    def test_snapshot_then_check(self):
        with tempfile.TemporaryDirectory() as t:
            demos = Path(t) / "demos"
            demos.mkdir()
            script, runbook = demos / "01_demo.md", Path(t) / "runbook.md"
            script.write_text(SCRIPT, encoding="utf-8")
            runbook.write_text(RUNBOOK, encoding="utf-8")
            snap = self._run("snapshot", str(script), str(runbook))
            self.assertEqual(0, snap.returncode, snap.stderr)
            snap_dir = snap.stdout.strip()
            try:
                same = self._run("check", snap_dir, str(script), str(runbook))
                self.assertEqual(0, same.returncode, same.stdout)
                self.assertEqual(2, same.stdout.count("UNCHANGED"))
                script.write_text(SCRIPT.replace("say it once, do not dwell.", "say it once and move on."), encoding="utf-8")
                ok = self._run("check", snap_dir, str(script))
                self.assertEqual(0, ok.returncode, ok.stdout)
                self.assertIn("OK ", ok.stdout)
                script.write_text(SCRIPT.replace("x = 1", "x = 2"), encoding="utf-8")
                bad = self._run("check", snap_dir, str(script))
                self.assertEqual(1, bad.returncode, bad.stdout)
                self.assertIn("FAIL ", bad.stdout)
                self.assertIn("fenced blocks", bad.stdout)
            finally:
                for p in Path(snap_dir).glob("*"):
                    p.unlink()
                Path(snap_dir).rmdir()

    def test_usage_without_arguments(self):
        self.assertEqual(2, self._run().returncode)


class HtmlTests(unittest.TestCase):
    """html mode (D-0040): a notes page keeps everything but its prose byte-identical through the humanizer."""

    PAGE = (HARNESS / "templates" / "day.exemplar.html").read_text(encoding="utf-8")

    def _names(self, new: str) -> list[str]:
        return [f.split(":")[0] for f in prose_guard.compare(self.PAGE, new, script=False, html=True)[0]]

    def test_prose_edits_pass(self):
        new = self.PAGE.replace("Explain the mechanism in plain words a graduate can follow.", "Explain the mechanism plainly, so a graduate can follow it.")
        new = new.replace("Step 2 caption: the pitfall and why it bites.", "Step 2 caption: the pitfall, and why it bites.")
        new = new.replace('explain: "Why it is true." }', 'explain: "Why the statement holds." }')
        new = new.replace("<summary>A question that tests the pitfall?</summary><p>The answer.</p>", "<summary>A question about the pitfall?</summary><p>The answer, reworded.</p>")
        self.assertEqual(([], []), prose_guard.compare(self.PAGE, new, script=False, html=True))

    def test_frozen_content_fails(self):
        for label, new, expect in [
            ("code", self.PAGE.replace("git add hello.py", "git add hi.py"), "code blocks"),
            ("inline code", self.PAGE.replace("<code>(3, 12)</code>", "<code>(3, 13)</code>"), "code blocks"),
            ("href", self.PAGE.replace('href="#src-3"', 'href="#src-2"', 1), "tag skeleton"),
            ("dropped tag", self.PAGE.replace('<div class="ix-legend"></div>', ""), "tag skeleton"),
            ("heading", self.PAGE.replace("<h2>How it actually works</h2>", "<h2>How it works</h2>"), "headings"),
            ("h3", self.PAGE.replace("<h3>Option A</h3>", "<h3>Option one</h3>"), "headings"),
            ("tag label", self.PAGE.replace('<div class="tag">Pitfall</div>', '<div class="tag">Pitfalls</div>'), "labels"),
            ("callout label", self.PAGE.replace('<div class="k">Say it in an interview</div>', '<div class="k">Say it</div>', 1), "labels"),
            ("meta span", self.PAGE.replace("Sources checked 2026-01-01", "Sources checked 2026-01-02"), "labels"),
            ("citation marker", self.PAGE.replace('<a href="#src-1">1</a></sup></p>\n        <h3>First', '<a href="#src-1">one</a></sup></p>\n        <h3>First'), "citations"),
            ("quiz answer", self.PAGE.replace("answer: 1,", "answer: 2,", 1), "scripts"),
            ("quiz type", self.PAGE.replace('{ type: "tf",', '{ type: "scq",', 1), "scripts"),
            ("match pair", self.PAGE.replace('r: "Meaning 1"', 'r: "Meaning one"'), "scripts"),
            ("diagram label", self.PAGE.replace('label:"Part A"', 'label:"Part one"'), "scripts"),
            ("next", self.PAGE.replace('href: "day-1-next-topic.html"', 'href: "day-2.html"'), "scripts"),
            ("dropped option", self.PAGE.replace('options: ["Correct option", "Wrong option", "Wrong option"]', 'options: ["Correct option", "Wrong option"]'), "scripts"),
            ("recap label", self.PAGE.replace('<div class="k">Takeaways</div>', '<div class="k">Recap</div>', 1), "labels"),
            ("split paragraph", self.PAGE.replace("day's topic as a section. A later day's topic", "day's topic as a section.</p>\n        <p>A later day's topic", 1), "tag skeleton"),
        ]:
            with self.subTest(change=label):
                self.assertIn(expect, self._names(new))

    def test_truncated_page_fails(self):
        self.assertIn("page does not parse", prose_guard.compare(self.PAGE, self.PAGE[: len(self.PAGE) // 2], script=False, html=True)[0][0])

    def test_changed_number_in_prose_is_a_warning(self):
        new = self.PAGE.replace("Each teaching step is 450–900 prose words", "Each teaching step is 400–900 prose words")
        findings, warnings = prose_guard.compare(self.PAGE, new, script=False, html=True)
        self.assertEqual([], findings)
        self.assertEqual(1, len(warnings))

    def test_cli_dispatches_on_the_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            page.write_text(self.PAGE, encoding="utf-8")
            snap = subprocess.run([sys.executable, str(HARNESS / "prose_guard.py"), "snapshot", str(page)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT).stdout.strip()
            page.write_text(self.PAGE.replace("git add hello.py", "git add hi.py"), encoding="utf-8")
            r = subprocess.run([sys.executable, str(HARNESS / "prose_guard.py"), "check", snap, str(page)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
            self.assertEqual(1, r.returncode)
            self.assertIn("code blocks", r.stdout)


class RestructureTests(unittest.TestCase):
    """--restructure mode (D-0060): inside a teaching step the prose containers may change; everything else may not."""

    PAGE = (HARNESS / "templates" / "day.exemplar.html").read_text(encoding="utf-8")
    SPLIT_AT = "day's topic as a section. A later day's topic"
    SPLIT_TO = "day's topic as a section.</p>\n        <p>A later day's topic"
    RECAP = '<div class="recap">\n          <div class="k">Takeaways</div>\n          <ul>\n            <li>One line the reader can check themselves against, drawn from this step\'s prose.</li>'

    def _cmp(self, new: str, band=None):
        return prose_guard.compare(self.PAGE, new, script=False, html=True, mode="restructure", band=band)

    def _names(self, new: str) -> list[str]:
        return [f.split(":")[0] for f in self._cmp(new)[0]]

    def test_container_changes_pass(self):
        new = self.PAGE.replace(self.SPLIT_AT, self.SPLIT_TO, 1)   # split a paragraph
        new = new.replace('<p>What goes wrong, what the symptom looks like, and the fix.<sup class="cite"><a href="#src-4">4</a></sup></p>',
                          '<ul>\n<li>What goes wrong.</li>\n<li>What the symptom looks like.</li>\n<li>The fix.<sup class="cite"><a href="#src-4">4</a></sup></li>\n</ul>', 1)   # listify
        new = new.replace("<p>When the index really is needed, and what to reach for then.</p>",
                          "<table><thead><tr><th>Case</th><th>Reach for</th></tr></thead><tbody><tr><td>The index really is needed.</td><td>What to reach for then.</td></tr></tbody></table>", 1)   # tabulate
        new = new.replace(self.RECAP, self.RECAP + "\n            <li>A fourth line added by the pass.</li>", 1)   # grow a recap
        new = new.replace("<b>~35 min</b>", "<b>~7 min</b>")   # minutes follow the words
        findings, warnings = self._cmp(new)
        self.assertEqual([], findings)
        self.assertEqual([], warnings)

    def test_moved_citation_is_a_warning_not_a_finding(self):
        a = '<p>Prose that walks the mechanism. The diagram on the right reveals one more piece per step.<sup class="cite"><a href="#src-2">2</a></sup></p>'
        b = '<p>State the output of each command and what changed on disk.<sup class="cite"><a href="#src-3">3</a></sup></p>'
        self.assertIn(a, self.PAGE)
        self.assertIn(b, self.PAGE)
        new = self.PAGE.replace(a, "\x00").replace(b, a).replace("\x00", b)   # swap two cited paragraphs inside step 1 (across its h3)
        findings, warnings = self._cmp(new)
        self.assertEqual([], findings, findings)   # same multiset of cites per step; the h3 anchors are untouched
        self.assertTrue(any("citation order" in w for w in warnings), warnings)

    def test_frozen_content_fails(self):
        for label, new, expect in [
            ("dropped code block", self.PAGE.replace("<pre><code>for item in items:\n    print(item)</code></pre>\n", "", 1), "tag skeleton"),
            ("code text", self.PAGE.replace("git add hello.py", "git add hi.py"), "code blocks"),
            ("inline code text", self.PAGE.replace("<code>(3, 12)</code>", "<code>(3, 13)</code>"), "inline code"),
            ("heading", self.PAGE.replace("<h3>Option A</h3>", "<h3>Option one</h3>"), "headings"),
            ("number in a step", self.PAGE.replace("Each teaching step is 450–900 prose words", "Each teaching step is 400–900 prose words"), "numbers in steps"),
            ("dropped citation", self.PAGE.replace('<sup class="cite"><a href="#src-4">4</a></sup>', "", 1), "citations"),
            ("edit in the lede", self.PAGE.replace("a classroom moment: the page stands on its own as documentation.</p>", "a classroom moment.</p>\n        <p>The page stands on its own as documentation.</p>", 1), "tag skeleton"),
            ("attributed list", self.PAGE.replace("<ul>\n            <li>One line the reader", '<ul class="recap-list">\n            <li>One line the reader', 1), "tag skeleton"),
            ("recap label", self.PAGE.replace('<div class="k">Takeaways</div>', '<div class="k">Recap</div>', 1), "recap labels"),
            ("callout split", self.PAGE.replace('<p>A spoken answer to "how does this work under the hood?" in two or three sentences.</p>',
                                                '<p>A spoken answer to "how does this work under the hood?"</p><p>In two or three sentences.</p>', 1), "tag skeleton"),
            ("check-yourself split", self.PAGE.replace("<p>Five to ten retrieval questions that cover every teaching step. Answer out loud before you open each one.</p>",
                                                       "<p>Five to ten retrieval questions that cover every teaching step.</p><p>Answer out loud before you open each one.</p>", 1), "tag skeleton"),
        ]:
            with self.subTest(change=label):
                self.assertIn(expect, self._names(new), self._cmp(new)[0])

    def test_a_recap_may_be_added_to_a_step_that_had_none(self):
        """The whole point of the pass: a live page without recaps gains one per step and the guard stays quiet."""
        import re
        old = re.sub(r'\s*<div class="recap">\s*<div class="k">Takeaways</div>\s*<ul>.*?</ul>\s*</div>', "\n", self.PAGE, count=1, flags=re.S)   # step 0 loses its recap
        self.assertEqual(self.PAGE.count('class="recap"') - 1, old.count('class="recap"'))
        findings, warnings = prose_guard.compare(old, self.PAGE, script=False, html=True, mode="restructure")
        self.assertEqual(([], []), (findings, warnings))

    def test_practice_section_is_frozen(self):
        practice = '<section class="practice" data-step="9"><h2>Practice</h2><p>One task. Two sentences.</p></section>\n      <section class="reading-sources"'
        page = self.PAGE.replace('<section class="reading-sources"', practice, 1)
        new = page.replace("<p>One task. Two sentences.</p>", "<p>One task.</p><p>Two sentences.</p>")
        self.assertIn("tag skeleton", [f.split(":")[0] for f in prose_guard.compare(page, new, script=False, html=True, mode="restructure")[0]])

    def test_step_word_delta_is_bounded(self):
        step2_para = '<p>Prose drawn from the brief\'s Common pitfalls, with the trade-off that explains why the wrong way is tempting.<sup class="cite"><a href="#src-1">1</a></sup></p>'
        self.assertIn(step2_para, self.PAGE)
        gone = self.PAGE.replace(step2_para, '<p><sup class="cite"><a href="#src-1">1</a></sup></p>', 1)   # the step loses most of its words, cite kept
        findings, _ = self._cmp(gone)
        self.assertTrue(any(f.startswith("step 2 words") for f in findings), findings)
        padded = self.PAGE.replace(self.RECAP, self.RECAP + "\n            <li>" + "word " * 200 + "</li>", 1)
        findings, _ = self._cmp(padded)
        self.assertTrue(any(f.startswith("step 0 words") for f in findings), findings)

    def test_page_band_applies_when_given(self):
        new = self.PAGE.replace(self.SPLIT_AT, self.SPLIT_TO, 1)
        findings, _ = self._cmp(new, band=(4500, 7000))
        self.assertTrue(any(f.startswith("page words") for f in findings), findings)
        self.assertEqual([], self._cmp(new, band=None)[0])

    def test_cli_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.html"
            page.write_text(self.PAGE, encoding="utf-8")
            snap = subprocess.run([sys.executable, str(HARNESS / "prose_guard.py"), "snapshot", str(page)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT).stdout.strip()
            page.write_text(self.PAGE.replace(self.SPLIT_AT, self.SPLIT_TO, 1), encoding="utf-8")
            plain = subprocess.run([sys.executable, str(HARNESS / "prose_guard.py"), "check", snap, str(page)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
            self.assertEqual(1, plain.returncode, plain.stdout)   # html mode: a split paragraph is a skeleton change
            r = subprocess.run([sys.executable, str(HARNESS / "prose_guard.py"), "check", "--restructure", snap, str(page)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
            self.assertEqual(1, r.returncode, r.stdout)           # restructure mode: the split is fine; the exemplar is under the word band
            self.assertIn("page words", r.stdout)
            self.assertNotIn("tag skeleton", r.stdout)


class WorkflowWiringTests(unittest.TestCase):
    """Static: day-fanout.js humanizes the runbook and demo-series.js humanizes each walkthrough, between author and
    critic (D-0039, D-0055)."""

    def setUp(self):
        self.src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        self.series = (HARNESS / "workflows" / "demo-series.js").read_text(encoding="utf-8")

    def test_humanize_runs_after_each_author_and_before_its_critic(self):
        src = self.src
        self.assertEqual(1, src.count("const humanizeTrainer = "))
        self.assertEqual(1, src.count("humanizeTrainer("), "one call, for the runbook (the walkthroughs are humanized in demo-series.js)")
        runbook = src[src.index("const runbook = () =>"):src.index("// notes first (the runbook reads the page for objectives), then the runbook")]
        self.assertLess(runbook.index("You are the RUNBOOK author"), runbook.index("humanizeTrainer(d, 'runbook'"))
        self.assertLess(runbook.index("humanizeTrainer(d, 'runbook'"), runbook.index("RUNBOOK CRITIC"))
        series = self.series
        self.assertEqual(1, series.count("const humanizeBlock = "))
        block = series[series.index("async function blockStage"):series.index("phase('Blocks')")]
        self.assertLess(block.index("You are the DEMO author"), block.index("humanizeBlock(b)"))
        self.assertLess(block.index("humanizeBlock(b)"), block.index("DEMOS CRITIC"))

    def test_the_pass_is_guarded_and_on_the_humanize_tier(self):
        body = self.src[self.src.index("const humanizeTrainer = "):self.src.index("function demoFacts")]
        for needle in ("humanizer:humanizer", "prose_guard.py snapshot", "prose_guard.py check", "...tier('humanize')", "-humanize`"):
            self.assertIn(needle, body)
        self.assertRegex(body, r"contrast that corrects what the room really assumes", "the prompt keeps real spoken contrasts")
        sbody = self.series[self.series.index("const humanizeBlock = "):self.series.index("async function blockStage")]
        for needle in ("humanizer:humanizer", "prose_guard.py snapshot", "prose_guard.py check", "demo_check.py", "...tier('humanize')", ":humanize`"):
            self.assertIn(needle, sbody)
        self.assertRegex(sbody, r"contrast that corrects what the room really assumes")

    def test_authors_are_told_the_wording_rule(self):
        self.assertEqual(1, self.src.count("Wording (D-0039)"), "the runbook author carries the wording line")
        self.assertEqual(1, self.series.count("Wording (D-0039)"), "the demo author carries the wording line")
        template = (HARNESS / "templates" / "demo-script.md").read_text(encoding="utf-8")
        self.assertIn("Wording (D-0039)", template)
        self.assertNotRegex(template, r"^- <topic[^\n]*—", "the not-covered bullet in the template has no dash")


if __name__ == "__main__":
    unittest.main()
