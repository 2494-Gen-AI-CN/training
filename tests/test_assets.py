"""Site asset hygiene: allowed JS set, no reference-site leaks, index links resolve."""

from __future__ import annotations

import ast
import json
import re
import runpy
import unittest

from helpers import ALLOWED_JS, DOCS, FORBIDDEN_RE, TRAINER, ParsedPage, authored_days


def _runner() -> dict:
    """The Python runner pyworker.js ships to the browser, loaded here so the tests exercise the same source."""
    js = (DOCS / "assets" / "js" / "pyworker.js").read_text(encoding="utf-8")
    g: dict = {}
    exec(re.search(r"const RUNNER = `(.*?)`;", js, re.S).group(1), g)
    return g


def _check(g: dict, code: str, checks: str) -> tuple[bool, list[dict]]:
    """What the page's Check button gets: did code run to its end, and one {ok, label, detail} per check."""
    finished = g["_tc_run"](lambda kind, text: None, code, [])
    return finished, (json.loads(g["_tc_check"](checks)) if finished else [])


def _solves(g: dict, code: str, checks: str) -> bool:
    """True when code runs to its end and passes every check, as the page would mark it Solved."""
    finished, results = _check(g, code, checks)
    return finished and bool(results) and all(r["ok"] for r in results)


def _tasks(rel: str) -> list:
    return ParsedPage(DOCS / "weeks" / f"{rel}.html").root.find_all("div", "ix-task")


class AssetTests(unittest.TestCase):
    def test_js_set_is_exactly_allowed(self):
        names = {p.name for p in (DOCS / "assets" / "js").glob("*.js")}
        self.assertEqual(ALLOWED_JS, names)

    def test_no_reference_site_leaks_anywhere_in_docs(self):
        for p in DOCS.rglob("*"):
            if p.is_file() and p.suffix in (".html", ".js", ".css", ".sh", ".md"):
                text = p.read_text(encoding="utf-8", errors="replace")
                m = FORBIDDEN_RE.search(text)
                self.assertIsNone(m, f"{p.relative_to(DOCS)}: leaked '{m.group(0) if m else ''}'")

    def test_scripts_load_code_from_pinned_jsdelivr_packages(self):
        """D-0042, D-0043: the site's scripts name two external URLs, each a jsDelivr package at an exact version."""
        where: dict[str, set[str]] = {}
        for p in (DOCS / "assets" / "js").glob("*.js"):
            for url in re.findall(r"https?://[^\s\"'`)<>]+", p.read_text(encoding="utf-8")):
                if url.startswith("http://www.w3.org/"):   # XML namespaces are names, not requests
                    continue
                m = re.fullmatch(r"https://cdn\.jsdelivr\.net/npm/([a-z]+)@\d+\.\d+\.\d+/", url)
                self.assertIsNotNone(m, f"{p.name}: {url} is not a jsDelivr package pinned to an exact version")
                where.setdefault(m.group(1), set()).add(p.name)
        self.assertEqual({"pyodide": {"pyworker.js"}, "codemirror": {"widgets.js"}}, where)

    def test_runnable_blocks_are_well_formed(self):
        """D-0042: a runnable block is <pre data-run="python"><code>; data-continues needs a runnable block above it."""
        for _w, _d, rel in authored_days():
            page = ParsedPage(DOCS / "weeks" / f"{rel}.html")
            above = 0
            for pre in page.root.find_all("pre"):
                with self.subTest(rel=rel, block=pre.text().strip()[:40]):
                    if "data-run" not in pre.attrs:
                        self.assertNotIn("data-continues", pre.attrs, "data-continues without data-run")
                        continue
                    self.assertEqual("python", pre.attrs["data-run"])
                    self.assertIsNotNone(pre.find("code"), "a runnable block wraps its source in <code>")
                    if "data-continues" in pre.attrs:
                        self.assertGreater(above, 0, "data-continues on the first runnable block of the page")
                    above += 1

    def test_required_files(self):
        for rel in (".nojekyll", "index.html", "bump-css.sh", "assets/css/style.css", "assets/favicon.svg"):
            self.assertTrue((DOCS / rel).exists(), rel)

    def test_index_parses_and_relative_links_resolve(self):
        page = ParsedPage(DOCS / "index.html")
        self.assertIn("theme.js", page.script_srcs)
        for href in page.hrefs():
            if href.startswith(("http", "#", "mailto:")):
                continue
            target = (DOCS / href.split("?")[0]).resolve()
            self.assertTrue(target.exists(), f"index.html broken link {href}")


class PracticeTaskTests(unittest.TestCase):
    """D-0043: practice tasks a reader solves in the page (div.ix-task inside section.practice)."""

    def test_tasks_are_well_formed_and_not_solved_by_their_starter(self):
        g = _runner()
        for _w, _d, rel in authored_days():
            page = ParsedPage(DOCS / "weeks" / f"{rel}.html")
            sections = page.root.find_all("section", "practice")
            tasks = page.root.find_all("div", "ix-task")
            self.assertEqual(len(tasks), sum(len(s.find_all("div", "ix-task")) for s in sections), f"{rel}: a task outside section.practice")
            for s in sections:
                self.assertIn("hidden", s.attrs, f"{rel}: section.practice is hidden in the markup; widgets.js shows it")
            ids = [t.attrs.get("data-id") for t in tasks]
            self.assertEqual(len(ids), len(set(ids)), f"{rel}: duplicate task data-id")
            for t in tasks:
                with self.subTest(rel=rel, task=t.attrs.get("data-id")):
                    for attr in ("data-id", "data-title", "data-q"):
                        self.assertTrue(t.attrs.get(attr), f"missing {attr}")
                    starter, checks = t.find_all("pre", "task-starter"), t.find_all("pre", "task-tests")
                    self.assertEqual((1, 1), (len(starter), len(checks)), "one task-starter and one task-tests")
                    self.assertIn("hidden", checks[0].attrs, "task-tests is hidden")
                    code, source = starter[0].text().strip("\n") + "\n", checks[0].text()
                    compile(code, "starter", "exec")
                    asserts = [n for n in ast.parse(source).body if isinstance(n, ast.Assert)]
                    self.assertTrue(asserts, "task-tests needs at least one top-level assert")
                    self.assertTrue(all(isinstance(n.msg, ast.Constant) for n in asserts), "every assert carries a message: it is the label the reader sees")
                    self.assertFalse(_solves(g, code, source), "the starter already passes every check")

    @unittest.skipUnless(TRAINER.exists(), "trainer/ (private repo) not present")
    def test_model_answers_pass_every_check(self):
        g = _runner()
        for _w, _d, rel in authored_days():
            tasks = _tasks(rel)
            if not tasks:
                continue
            answers = TRAINER / rel / "solutions" / "practice.py"
            self.assertTrue(answers.is_file(), f"{rel}: the page has tasks, so the trainer repo needs solutions/practice.py")
            code = answers.read_text(encoding="utf-8")
            for t in tasks:
                with self.subTest(rel=rel, task=t.attrs.get("data-id")):
                    self.assertTrue(_solves(g, code, t.find("pre", "task-tests").text()))

    @unittest.skipUnless(TRAINER.exists(), "trainer/ (private repo) not present")
    def test_checks_pass_right_answers_and_catch_wrong_ones(self):
        """The checks are tested themselves, from trainer/<rel>/solutions/practice_cases.py: other right answers
        pass every check, each known wrong answer is caught by the check meant for it, and every check on the
        page is failed by at least one wrong answer."""
        g = _runner()
        for _w, _d, rel in authored_days():
            tasks = _tasks(rel)
            if not tasks:
                continue
            path = TRAINER / rel / "solutions" / "practice_cases.py"
            self.assertTrue(path.is_file(), f"{rel}: the page has tasks, so the trainer repo needs solutions/practice_cases.py")
            cases = runpy.run_path(str(path))["CASES"]
            self.assertEqual({t.attrs["data-id"] for t in tasks}, set(cases), f"{rel}: practice_cases.py covers exactly the page's tasks")
            for t in tasks:
                tid, source = t.attrs["data-id"], t.find("pre", "task-tests").text()
                labels = [n.msg.value for n in ast.parse(source).body if isinstance(n, ast.Assert)]
                caught: set[str] = set()
                for i, code in enumerate(cases[tid]["accept"]):
                    with self.subTest(rel=rel, task=tid, accept=i):
                        finished, results = _check(g, code, source)
                        self.assertTrue(finished, "a right answer stopped with an error")
                        self.assertEqual([], [f"{r['label']} — {r['detail']}" for r in results if not r["ok"]], "a right answer fails a check")
                for i, (code, label) in enumerate(cases[tid]["reject"]):
                    with self.subTest(rel=rel, task=tid, reject=i):
                        finished, results = _check(g, code, source)
                        failed = [r["label"] for r in results if not r["ok"]]
                        caught.update(failed)
                        if label is None:
                            self.assertFalse(finished, "this entry is meant to stop with an error before the checks")
                            continue
                        self.assertIn(label, labels, "the label names no check of this task")
                        self.assertTrue(finished, "this entry is meant to run to its end and fail a check")
                        self.assertIn(label, failed, "the wrong answer got past the check meant to catch it")
                with self.subTest(rel=rel, task=tid, what="every check is failed by some wrong answer"):
                    self.assertEqual([], [x for x in labels if x not in caught])


if __name__ == "__main__":
    unittest.main()
