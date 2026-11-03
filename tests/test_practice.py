"""Practice tasks as a stage after authoring (D-0047): harness/practice_tasks.py, the --practice modes of
harness/args_for.py and harness/workflows/practice-tasks.js. The tasks themselves (starters, model answers,
cases) are tested through the page in tests/test_assets.py PracticeTaskTests."""

from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import DOCS, HARNESS, ROOT, all_days, authored_days, load_json, metrics, node_exe, run_node

sys.path.insert(0, str(HARNESS))
import args_for  # noqa: E402
import build_index as bi  # noqa: E402
import build_tracker  # noqa: E402
import practice_tasks as pt  # noqa: E402

EXEMPLAR = HARNESS / "templates" / "day.exemplar.html"
WORKFLOW = (HARNESS / "workflows" / "practice-tasks.js").read_text(encoding="utf-8")
FANOUT = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
CONFIG = load_json(HARNESS / "config.json")
TASKS = [
    {"id": "t1", "title": "Strings & <tags>", "q": "Write <code>shout(text)</code>. It returns \"text\" in upper case; it's short.",
     "starter": "def shout(text):\n    ...", "tests": "assert shout(\"a<b\") == 'A<B', \"upper-cases the text & keeps '<'\"\nassert shout(\"\") == \"\", \"empty stays empty\""},
    {"id": "t2", "title": "Lists", "q": "Write <code>first(items)</code>.",
     "starter": "def first(items):\n    ...", "tests": "rows = [1, 2]\nassert first(rows) == 1, \"returns the first item\"\nassert rows == [1, 2], \"leaves the list alone\""},
]
CHOICE = {"id": "t3", "title": "Pasting & <secrets>", "kind": "choice",
          "q": "Your <code>.env</code> file holds the key. What do you paste into the assistant? It's \"one\" choice.",
          "options": ["The whole <code>.env</code> file, so it sees the setting", "The error message and the function, with the key left out",
                      "A screenshot of the terminal & the key", "Nothing: an assistant never helps with config"],
          "answer": 1, "explain": "The step's rule: paste the code and the error, never a secret; <code>.env</code> stays on your machine."}


def _built_choice(**over) -> dict:
    """A built choice task as the build writes it into the day's file (D-0084)."""
    return {"id": "t1", "title": "A", "step": None, "kind": "choice", "idea": "Pick what to paste.", "checks": ["pastes the secret", "pastes a screenshot"],
            "approved": True, "q": CHOICE["q"], "options": list(CHOICE["options"]), "answer": 1, "explain": CHOICE["explain"],
            "starter": "", "tests": ""} | over


def _proposal(rel: str, day_id: str, approved=None) -> dict:
    return {
        "day": day_id, "page": f"docs/weeks/{rel}.html", "assessed": "2026-10-13", "verdict": "partial", "summary": "Two steps fit.",
        "steps": [{"step": 0, "title": "A", "suitable": True, "reason": "returns a value", "task": "t1"},
                  {"step": 1, "title": "B", "suitable": False, "reason": "teaches a convention", "task": None},
                  {"step": 2, "title": "C", "suitable": True, "reason": "returns a value", "task": "t2"}],
        "tasks": [{"id": "t1", "title": "A", "step": 0, "idea": "Write f.", "checks": ["one", "two"], "approved": approved, "q": "", "starter": "", "tests": ""},
                  {"id": "t2", "title": "C", "step": 2, "idea": "Write g.", "checks": ["one", "two"], "approved": approved, "q": "", "starter": "", "tests": ""}],
    }


def _quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        code = fn(*a)
    return code, out.getvalue()


class FileTests(unittest.TestCase):
    def test_every_practice_file_is_valid_against_its_page(self):
        rels = {rel for _w, _d, rel in all_days()}
        for path in sorted(pt.PRACTICE.rglob("*.json")):
            rel = path.relative_to(pt.PRACTICE).with_suffix("").as_posix()
            with self.subTest(rel=rel):
                self.assertIn(rel, rels, "a practice file sits at harness/practice/<week-dir>/<day-slug>.json")
                page = pt.page_for(rel)
                self.assertTrue(page.is_file(), "practice tasks come after the page is authored")
                self.assertEqual([], pt.problems(pt.load(rel), rel, pt.read_text(page), metrics()["practice"]))

    def test_every_page_section_is_what_its_file_renders(self):
        """The section is generated: a page that carries tasks has a file, and insert would change nothing."""
        for _w, _d, rel in all_days():
            with self.subTest(rel=rel):
                self.assertIsNone(pt.in_sync(rel))

    def test_bounds_live_in_metrics(self):
        for key in ("checksPerTaskMin", "checksPerTaskMax", "acceptMin", "starterLinesMax", "modelLinesMax", "choiceOptionsMin", "choiceOptionsMax"):
            self.assertIsInstance(metrics()["practice"].get(key), int, key)
        self.assertLessEqual(2, metrics()["practice"]["choiceOptionsMin"])
        self.assertLessEqual(metrics()["practice"]["choiceOptionsMin"], metrics()["practice"]["choiceOptionsMax"])

    def test_critic_spec_names_the_bars_and_the_three_steps(self):
        spec = (HARNESS / "critics" / "practice.md").read_text(encoding="utf-8")
        for needle in ("D-0047", "## The runtime", "## Suitability", "## Build", "checksPerTaskMin", "acceptMin", "modelLinesMax",
                       "practice_tasks.py validate", "practice_tasks.py verify", "practice_tasks.py insert", "input()",
                       "## Choice tasks (D-0084", "choiceOptionsMin", "all of the above", "correct answer", "for Python tasks"):
            self.assertIn(needle, spec)
        self.assertIn("practice_tasks.py insert", (HARNESS / "critics" / "notes.md").read_text(encoding="utf-8"))


class SectionTests(unittest.TestCase):
    def setUp(self):
        self.page = EXEMPLAR.read_bytes().decode("utf-8")

    def test_insert_goes_before_check_yourself_and_reads_back(self):
        self.assertNotIn('class="practice"', self.page)
        new = pt.put_section(self.page, TASKS)
        self.assertEqual(TASKS, pt.page_tasks(new), "what is written is what is read back, escapes included")
        last_step = [m.start() for m in pt.STEP_RE.finditer(new)][-1]
        section = pt.SECTION_RE.search(new)
        self.assertEqual("\n", new[section.end():last_step], "the section sits directly before the last step, one blank line between")
        self.assertEqual(new, pt.put_section(new, TASKS), "insert twice changes nothing")
        self.assertEqual(self.page, pt.put_section(new, []), "no built task: the section is gone and the page is as it was")

    def test_replace_keeps_the_rest_of_the_page(self):
        one = pt.put_section(self.page, TASKS)
        two = pt.put_section(one, TASKS[:1])
        self.assertEqual(TASKS[:1], pt.page_tasks(two))
        self.assertEqual(self.page, pt.put_section(two, []))

    def test_the_browser_sees_the_same_markup_the_tests_parse(self):
        from helpers import _Parser
        p = _Parser()
        p.feed(pt.put_section(self.page, TASKS))
        tasks = p.root.find_all("div", "ix-task")
        self.assertEqual(["t1", "t2"], [t.attrs["data-id"] for t in tasks])
        self.assertEqual(TASKS[0]["q"], tasks[0].attrs["data-q"])
        self.assertEqual(TASKS[0]["tests"], tasks[0].find("pre", "task-tests").text())
        self.assertIn("hidden", tasks[0].find("pre", "task-tests").attrs)
        self.assertIn("hidden", p.root.find("section", "practice").attrs)

    def test_teaching_steps_leave_out_check_yourself(self):
        steps = pt.teaching_steps(self.page)
        self.assertTrue(steps)
        self.assertEqual(list(range(len(steps))), [s["step"] for s in steps])
        self.assertNotIn("Check yourself", [s["title"] for s in steps])

    def test_choice_tasks_round_trip_beside_python_tasks(self):
        """D-0084: both kinds render and read back, in page order, escapes included; insert twice changes nothing."""
        for tasks in ([CHOICE], [TASKS[0], CHOICE, TASKS[1]], [CHOICE | {"id": "t1"}, CHOICE | {"id": "t2", "answer": 3}]):
            with self.subTest(ids=[t["id"] for t in tasks]):
                new = pt.put_section(self.page, tasks)
                self.assertEqual(tasks, pt.page_tasks(new))
                self.assertEqual(new, pt.put_section(new, tasks))
                self.assertEqual(self.page, pt.put_section(new, []))

    def test_python_markup_is_unchanged_by_the_choice_kind(self):
        """A task with "kind": "python" renders exactly as one without the key, so live pages stay in sync."""
        self.assertEqual(pt.render(TASKS), pt.render([t | {"kind": "python"} for t in TASKS]))
        self.assertNotIn("ix-choice", pt.render(TASKS))

    def test_the_browser_sees_the_choice_markup_the_tests_parse(self):
        from helpers import _Parser
        import practice_browser as pb
        p = _Parser()
        p.feed(pt.put_section(self.page, [TASKS[0], CHOICE]))
        py, choice = p.root.find_all("div", "ix-task")
        self.assertEqual((False, True), (pb.is_choice(py), pb.is_choice(choice)))
        self.assertEqual([(1, py)], pb.python_tasks(p.root), "a choice task keeps its number and runs no Python")
        self.assertEqual(("choice", CHOICE["id"], CHOICE["q"]), (choice.attrs["data-kind"], choice.attrs["data-id"], choice.attrs["data-q"]))
        radios = choice.find_all("input")
        self.assertEqual([("radio", CHOICE["id"], str(i)) for i in range(len(CHOICE["options"]))],
                         [(r.attrs["type"], r.attrs["name"], r.attrs["value"]) for r in radios])
        key = choice.find("pre", "task-answer")
        self.assertIn("hidden", key.attrs)
        self.assertEqual({"answer": CHOICE["answer"], "explain": CHOICE["explain"]}, json.loads(key.text()))
        self.assertIsNone(choice.find("pre", "task-starter"))

    def test_widget_and_driver_handle_the_choice_kind(self):
        widgets = (DOCS / "assets" / "js" / "widgets.js").read_text(encoding="utf-8")
        driver = (HARNESS / "practice_browser.js").read_text(encoding="utf-8")
        css = (DOCS / "assets" / "css" / "style.css").read_text(encoding="utf-8")
        for needle in ("ix-choice", "task-answer", 'data-act="retry"', "task-explain", "D-0084"):
            self.assertIn(needle, widgets)
        for needle in (".ix-choice", "data.choice", 'data-act="retry"', "explanation shown"):
            self.assertIn(needle, driver)
        self.assertIn(".ix-choice .task-options li.ok", css)


class ShapeTests(unittest.TestCase):
    REL = "week-01/day-x"

    def _problems(self, change) -> list[str]:
        doc = _proposal(self.REL, "w01dx")
        change(doc)
        return pt.problems(doc, self.REL, None, metrics()["practice"])

    def test_a_clean_proposal_passes(self):
        self.assertEqual([], self._problems(lambda d: None))

    def test_what_the_shape_check_catches(self):
        def build(t, **over):
            t.update({"approved": True, "q": "Write <code>f()</code>.", "starter": "def f():\n    ...",
                      "tests": 'assert f() == 1, "returns 1"\nassert f() != 2, "is not 2"'} | over)
        cases = {
            "verdict is": lambda d: d.update(verdict="full"),
            "suitable, so task must name": lambda d: d["steps"][0].update(task="t9"),
            "not suitable, so task must be null": lambda d: d["steps"][1].update(task="t1"),
            "does not name it back": lambda d: d["tasks"][1].update(step=0),
            "duplicate task id": lambda d: d["tasks"][1].update(id="t1"),
            "written together": lambda d: d["tasks"][0].update(approved=True, q="Write it."),
            "without the trainer's approval": lambda d: build(d["tasks"][0], approved=None),
            "needs an idea": lambda d: d["tasks"][0].update(idea=""),
            "checks, expected": lambda d: build(d["tasks"][0], tests='assert f() == 1, "returns 1"'),
            "carries a message": lambda d: build(d["tasks"][0], tests="assert f() == 1\nassert f() != 2"),
            "share a label": lambda d: build(d["tasks"][0], tests='assert f() == 1, "same"\nassert f() != 2, "same"'),
            "<code> and nothing else": lambda d: build(d["tasks"][0], q="Write <b>f</b>."),
            "does not parse": lambda d: build(d["tasks"][0], starter="def f(:"),
            "reason is empty": lambda d: d["steps"][1].update(reason=""),
        }
        for needle, change in cases.items():
            with self.subTest(needle=needle):
                self.assertTrue(any(needle in x for x in self._problems(change)), self._problems(change))

    def test_a_built_task_is_approved_and_complete(self):
        doc = _proposal(self.REL, "w01dx", approved=True)
        self.assertEqual([], pt.built(doc))
        doc["tasks"][0].update(q="Write f.", starter="def f():\n    ...", tests='assert f() == 1, "one"')
        self.assertEqual(["t1"], [t["id"] for t in pt.built(doc)])
        doc["tasks"][0]["approved"] = False
        self.assertEqual([], pt.built(doc))

    def test_a_built_choice_task_is_approved_and_complete(self):
        """D-0084: q, options, answer and explain make it built; answer 0 counts; starter and tests stay empty."""
        self.assertTrue(pt.is_built(_built_choice()))
        self.assertTrue(pt.is_built(_built_choice(answer=0)))
        self.assertFalse(pt.is_built(_built_choice(approved=None)))
        self.assertFalse(pt.is_built(_built_choice(explain="")))
        self.assertFalse(pt.is_built(_built_choice(options=[])))
        self.assertFalse(pt.is_built(_built_choice(answer=None)))
        self.assertFalse(pt.is_built({k: v for k, v in _built_choice().items() if k != "options"}))
        self.assertEqual("python", pt.kind_of(TASKS[0]))

    def _choice_problems(self, **over) -> list[str]:
        doc = _proposal(self.REL, "w01dx")
        doc["tasks"][0] = _built_choice(id="t1", step=0, title="A") | over
        return pt.problems(doc, self.REL, None, metrics()["practice"])

    def test_a_clean_choice_task_passes(self):
        self.assertEqual([], self._choice_problems())
        proposal = {"kind": "choice", "approved": None, "q": "", "options": [], "answer": None, "explain": ""}
        self.assertEqual([], self._choice_problems(**proposal), "a choice proposal: kind, idea and checks, nothing built")
        bare = {k: v for k, v in _built_choice(id="t1", step=0, title="A", approved=None, q="").items() if k not in ("options", "answer", "explain")}
        doc = _proposal(self.REL, "w01dx")
        doc["tasks"][0] = bare
        self.assertEqual([], pt.problems(doc, self.REL, None, metrics()["practice"]), "the proposal may leave the built keys out")

    def test_choice_bounds_come_from_metrics(self):
        b = metrics()["practice"]
        lo, hi = b["choiceOptionsMin"], b["choiceOptionsMax"]
        opts = [f"Option {i}" for i in range(hi + 1)]
        self.assertEqual([], self._choice_problems(options=opts[:lo], answer=0))
        self.assertEqual([], self._choice_problems(options=opts[:hi], answer=hi - 1))
        self.assertTrue(any(f"expected {lo} to {hi}" in x for x in self._choice_problems(options=opts[:lo - 1], answer=0)))
        self.assertTrue(any(f"expected {lo} to {hi}" in x for x in self._choice_problems(options=opts[:hi + 1], answer=0)))
        tight = pt.problems(_proposal(self.REL, "w01dx") | {"tasks": [_built_choice(id="t1", step=0), _proposal(self.REL, "w01dx")["tasks"][1]]},
                            self.REL, None, b | {"choiceOptionsMax": 3})
        self.assertTrue(any("expected" in x and "to 3" in x for x in tight), tight)

    def test_what_the_choice_check_catches(self):
        opts = CHOICE["options"]
        cases = [
            ("two options are the same", dict(options=[opts[0], opts[1], " ".join(opts[0].upper().split())])),
            ("an option is empty", dict(options=[opts[0], opts[1], "  "])),
            ("starts or ends with white space", dict(options=[opts[0], opts[1], opts[2] + " "])),
            ("answer must be the 0-based index", dict(answer=4)),
            ("answer must be the 0-based index", dict(answer=-1)),
            ("answer must be the 0-based index", dict(answer=True)),
            ("answer must be the 0-based index", dict(answer="1")),
            ("options must be a list of strings", dict(options=[1, 2, 3])),
            ("q may hold <code> and nothing else", dict(q="Pick <b>one</b>.")),
            ("option 2 may hold <code> and nothing else", dict(options=[opts[0], opts[1], "A <i>screenshot</i>"])),
            ("explain may hold <code> and nothing else", dict(explain="See <a href='x'>this</a>.")),
            ("of the above", dict(options=[opts[0], opts[1], "All of the above"])),
            ("of the above", dict(options=[opts[0], opts[1], "None of these"])),
            ("never 'correct answer'", dict(explain="The correct answer is the second one.")),
            ("written together", dict(explain="")),
            ("keeps starter and tests empty", dict(starter="def f():\n    ...")),
            ("without the trainer's approval", dict(approved=None)),
            ("kind must be one of", dict(kind="essay")),
        ]
        for needle, over in cases:
            with self.subTest(needle=needle, over=over):
                found = self._choice_problems(**over)
                self.assertTrue(any(needle in x for x in found), found)

    def test_a_python_task_does_not_carry_choice_keys(self):
        doc = _proposal(self.REL, "w01dx")
        doc["tasks"][0].update(options=["a", "b", "c"])
        self.assertTrue(any("belong to a choice task" in x for x in pt.problems(doc, self.REL, None, metrics()["practice"])))


class GateTests(unittest.TestCase):
    """The trainer's answer is the gate between the two runs. Works on a temporary harness/practice/."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.real, pt.PRACTICE = pt.PRACTICE, Path(self.tmp.name)
        self.addCleanup(lambda: setattr(pt, "PRACTICE", self.real))
        self.cur = bi.load_curriculum()
        self.week, self.day, self.rel = next((w, d, rel) for w, d, rel in authored_days())
        pt.save(self.rel, _proposal(self.rel, self.day["id"]))

    def _args(self, build: bool, days=None):
        return args_for.practice_args(self.cur, self.week, days or [], build, "2026-10-13", metrics(), CONFIG)

    def test_build_is_refused_until_the_trainer_answers(self):
        out, why = self._args(True)
        self.assertIsNone(out)
        self.assertTrue(any("BLOCKED" in x and self.day["id"] in x for x in why), why)

    def test_approve_records_the_answer_and_build_takes_only_approved_tasks(self):
        code, _ = _quiet(pt.cmd_approve, self.week["week"], self.day["day"], ["t2"])
        self.assertEqual(0, code)
        self.assertEqual({"t1": False, "t2": True}, {t["id"]: t["approved"] for t in pt.load(self.rel)["tasks"]})
        out, _why = self._args(True)
        day = next(d for d in out["days"] if d["id"] == self.day["id"])
        self.assertEqual("build", out["mode"])
        self.assertEqual(["t2"], [t["id"] for t in day["tasks"]])
        self.assertEqual({"id", "title", "step", "idea", "checks", "kind", "built"}, set(day["tasks"][0]))
        self.assertEqual("python", day["tasks"][0]["kind"], "the build is told each task's kind (D-0084)")
        self.assertFalse(day["tasks"][0]["built"])
        for key in ("pageFile", "practiceFile", "solutionsDir", "spoilerRows", "researchBrief"):
            self.assertIn(key, day)
        self.assertNotIn("exerciseReadme", day, "practice keys are not exercise solutions (D-0068)")

    def test_a_day_with_nothing_approved_is_not_built(self):
        _quiet(pt.cmd_approve, self.week["week"], self.day["day"], ["--none"])
        out, why = self._args(True, [self.day["day"]])
        self.assertIsNone(out)
        self.assertTrue(any("no task of it was approved" in x for x in why), why)

    def test_approve_refuses_an_unknown_task(self):
        with self.assertRaises(SystemExit):
            _quiet(pt.cmd_approve, self.week["week"], self.day["day"], ["t9"])
        _quiet(pt.cmd_approve, self.week["week"], self.day["day"], ["--all"])
        self.assertTrue(all(t["approved"] for t in pt.load(self.rel)["tasks"]))

    def test_suitability_takes_authored_pages_without_built_tasks(self):
        out, _why = self._args(False)
        self.assertEqual("suitability", out["mode"])
        self.assertIn(self.day["id"], [d["id"] for d in out["days"]])
        self.assertTrue(all(pt.page_for(d["rel"]).is_file() for d in out["days"]))
        self.assertTrue(out["critic"].endswith("harness/critics/practice.md"))
        self.assertRegex(out["runtime"]["pyodide"], r"^\d+\.\d+\.\d+$")
        for stage in ("practice-suitability", "practice", "critic", "wire", "verify"):
            self.assertIn(stage, out["models"]["stages"])
        doc = pt.load(self.rel)
        for t in doc["tasks"]:
            t.update(approved=True, q="Write f.", starter="def f():\n    ...", tests='assert f() == 1, "one"')
        pt.save(self.rel, doc)
        out, why = self._args(False, [self.day["day"]])
        self.assertIsNone(out)
        self.assertTrue(any("already carries built tasks" in x for x in why), why)

    def test_a_day_that_is_not_authored_is_refused(self):
        planned = next(((w, d) for w, d, rel in all_days() if d.get("status") not in ("authored", "live") and not pt.page_for(rel).is_file()), None)
        if planned is None:
            self.skipTest("every day is authored")
        out, why = args_for.practice_args(self.cur, planned[0], [planned[1]["day"]], False, "2026-10-13", metrics(), CONFIG)
        self.assertIsNone(out)
        self.assertTrue(any("not authored yet" in x for x in why), why)


MIXED_MODEL = '"""Model answers."""\n\n\n# Task 2: Lists\ndef first(items):\n    return items[0]\n'
MIXED_CASES = ('CASES = {"t2": {"accept": ["def first(items):\\n    for x in items:\\n        return x\\n"],\n'
               '                "reject": [("def first(items):\\n    return items[-1]\\n", "returns the first item"),\n'
               '                           ("def first(items):\\n    return items.pop(0)\\n", "leaves the list alone")]}}\n')


class VerifyTests(unittest.TestCase):
    """`practice_tasks.py verify` on a temporary day (D-0084): choice tasks are validated only, and the trainer's
    files are needed only when the day has a Python task. Works on temporary harness/practice/, docs/weeks/ and trainer/."""
    REL = "week-99/day-9-choice"

    def setUp(self):
        import practice_browser as pb
        self.pb = pb
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        saved = [(pt, "PRACTICE"), (pt, "page_for"), (pt, "locate"), (pb, "PRACTICE"), (pb, "PAGES"), (pb, "TRAINER")]
        for mod, name in saved:
            self.addCleanup(setattr, mod, name, getattr(mod, name))
        pt.PRACTICE = pb.PRACTICE = self.root / "practice"
        pb.PAGES = self.root / "weeks"
        pb.TRAINER = self.root / "trainer"
        pt.page_for = lambda rel: self.root / "weeks" / f"{rel}.html"
        pt.locate = lambda w, d: ({}, {}, self.REL)
        self.exemplar = EXEMPLAR.read_bytes().decode("utf-8")

    def _day(self, tasks: list[dict]) -> None:
        doc = {"day": "w99d9", "page": f"docs/weeks/{self.REL}.html", "assessed": "2026-11-03", "verdict": "partial",
               "summary": "A test day.", "steps": [], "tasks": tasks}
        pt.save(self.REL, doc)
        pt.write_text(pt.page_for(self.REL), pt.put_section(self.exemplar, pt.built(doc)))

    def _verify(self) -> tuple[int, str]:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            try:
                code = pt.cmd_verify(99, 9)
            except SystemExit as exc:
                code = f"exit: {exc}"
        return code, out.getvalue()

    def test_a_day_of_choice_tasks_needs_no_trainer_file(self):
        self._day([_built_choice()])
        self.assertFalse(self.pb.TRAINER.exists())
        code, out = self._verify()
        self.assertEqual(0, code, out)
        self.assertIn("1 choice task(s) validated", out)
        self.assertIn("t1: choice, 4 options, right marked 1/1, wrong marked 3/3, explanation shown 4/4", out)
        data, problems = self.pb.expected(self.REL)
        self.assertEqual(([], {}, {}), (problems, data["model"], data["cases"]))
        self.assertEqual({"t1": {"options": 4, "answer": 1, "explain": CHOICE["explain"]}}, data["choice"])

    def test_a_bad_choice_task_fails_validation(self):
        self._day([_built_choice(options=CHOICE["options"][:2], answer=0)])
        code, out = self._verify()
        self.assertEqual(1, code, out)
        self.assertIn("2 options, expected", out)

    def _mixed(self) -> None:
        t2 = TASKS[1] | {"step": None, "idea": "Write first.", "checks": ["one", "two"], "approved": True}
        self._day([_built_choice(), t2])

    def test_a_mixed_day_runs_the_python_contract_and_needs_the_trainer_files(self):
        self._mixed()
        code, out = self._verify()
        self.assertIn("missing", str(code), "a Python task on the day: practice.py and practice_cases.py are required")
        sol = self.pb.TRAINER / self.REL / "solutions"
        pt.write_text(sol / "practice.py", MIXED_MODEL)
        pt.write_text(sol / "practice_cases.py", MIXED_CASES)
        code, out = self._verify()
        self.assertEqual(0, code, out)
        self.assertIn("t2: starter unsolved, model pass, right 1/1, wrong caught 2/2, per check 1 1", out)
        self.assertIn("1 task(s) under CPython, 1 choice task(s) validated", out)
        self.assertEqual(["t1", "t2"], list(self.pb.expected(self.REL)[0]["expected"]), "lines in page order")

    def test_a_mixed_day_numbers_practice_py_by_the_page(self):
        self._mixed()
        sol = self.pb.TRAINER / self.REL / "solutions"
        pt.write_text(sol / "practice.py", MIXED_MODEL.replace("# Task 2:", "# Task 1:"))
        pt.write_text(sol / "practice_cases.py", MIXED_CASES)
        code, out = self._verify()
        self.assertEqual(1, code, out)
        self.assertIn("numbered 2 in page order", out)

    def test_the_page_is_held_to_the_file(self):
        self._day([_built_choice()])
        page = pt.page_for(self.REL)
        pt.write_text(page, pt.read_text(page).replace('value="3"> ', 'value="3"> Changed: '))
        code, out = self._verify()
        self.assertEqual(1, code, out)
        self.assertIn("differs from harness/practice", out)


class CliTests(unittest.TestCase):
    def test_args_for_practice_modes(self):
        run = lambda *a: subprocess.run([sys.executable, str(HARNESS / "args_for.py"), *a], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)  # noqa: E731
        both = run("1", "--practice", "--practice-build")
        self.assertEqual(2, both.returncode)
        self.assertIn("one mode at a time", both.stderr)
        built = [(w, d) for w, d, rel in authored_days() if pt.built(pt.load(rel))]
        if built:
            w, d = built[0]
            r = run(str(w["week"]), str(d["day"]), "--practice", "--today", "2026-10-13")
            self.assertEqual(2, r.returncode)
            self.assertIn("already carries built tasks", r.stderr)
            r = run(str(w["week"]), str(d["day"]), "--practice-build", "--today", "2026-10-13")
            self.assertEqual(0, r.returncode, r.stderr)
            a = json.loads(r.stdout)
            self.assertEqual(("build", [d["id"]]), (a["mode"], [x["id"] for x in a["days"]]))

    def test_check_command_is_green(self):
        r = subprocess.run([sys.executable, str(HARNESS / "practice_tasks.py"), "check"], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)


DRY_RUN = r"""
let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => raw += c);
process.stdin.on('end', async () => {
  const { src, args, criticPass } = JSON.parse(raw);
  const calls = [], logs = [];
  const agent = async (prompt, o) => {
    o = o || {};
    calls.push({ label: o.label, phase: o.phase, model: o.model, effort: o.effort, prompt });
    const req = (o.schema || {}).required || [];
    if (req.includes('pass')) return { pass: criticPass, critiques: criticPass ? [] : ['t1: fix it'], summary: 's' };
    if (req.includes('validated')) return { verdict: 'partial', teachingSteps: 5, tasksProposed: 3, validated: true, summary: 's' };
    if (req.includes('tasksBuilt')) return { tasksBuilt: 2, checks: 6, rightAnswers: 3, wrongAnswers: 7, verifyOutput: 'OK', summary: 's' };
    if (req.includes('passed')) return { passed: true, failures: [] };
    return 'ok';
  };
  const parallel = (thunks) => Promise.all(thunks.map(t => t().catch(() => null)));
  const body = src.replace('export const meta', 'const meta');
  const fn = new (Object.getPrototypeOf(async function () {}).constructor)('args', 'agent', 'parallel', 'phase', 'log', body);
  let result = null, error = null;
  try { result = await fn(args, agent, parallel, () => {}, m => logs.push(m)); } catch (e) { error = String(e && e.message || e); }
  process.stdout.write(JSON.stringify({ result, error, calls, logs }));
});
"""


class WorkflowTests(unittest.TestCase):
    def test_script_spreads_a_configured_tier_on_every_agent_call(self):
        self.assertTrue(WORKFLOW.lstrip().startswith("//"))
        self.assertIn("export const meta", WORKFLOW)
        chunks = re.split(r"\bagent\((?!\))", WORKFLOW)   # real calls carry a prompt; "agent()" in comments does not
        self.assertGreaterEqual(len(chunks) - 1, 5, "assessor, author, critic, record, verify")
        for i, chunk in enumerate(chunks[1:], 1):
            self.assertIn("...tier(", chunk, f"agent() call #{i} in practice-tasks.js does not spread a tier(...)")
        used = set(re.findall(r"tier\('([\w-]+)'", WORKFLOW))
        self.assertEqual({"practice-suitability", "practice", "critic", "wire", "verify"}, used)
        self.assertEqual(set(), used - set(CONFIG["models"]["stages"]), "practice-tasks.js uses tiers config.json does not define")
        self.assertIn("...tier('practice', pass)", WORKFLOW, "a repass escalates")

    def test_script_names_the_commands_and_keeps_the_page_generated(self):
        for needle in ("practice_tasks.py validate", "practice_tasks.py insert", "practice_tasks.py verify", "practice_tasks.py check",
                       "practice_tasks.py show", "practice_browser.py", "kind: 'practice'", "log_run.py add", "NEVER edit that section"):
            self.assertIn(needle, WORKFLOW)
        self.assertIn("practice", build_tracker.RUN_KINDS)

    def test_day_fanout_puts_the_section_back_after_a_reauthor(self):
        wire = FANOUT[FANOUT.index("WIRE step"):FANOUT.index("// ---------- report")]
        self.assertIn("practice_tasks.py insert", wire)

    def _dry(self, args: dict, critic_pass: bool = True) -> dict:
        out = json.loads(run_node(DRY_RUN, json.dumps({"src": WORKFLOW, "args": args, "criticPass": critic_pass})))
        self.assertIsNone(out["error"], out["error"])
        return out

    def _base(self, mode: str, days: list[dict]) -> dict:
        return {"root": "/r", "today": "2026-10-13", "week": 1, "theme": "T", "mode": mode, "days": days, "critic": "/r/harness/critics/practice.md",
                "models": CONFIG["models"], "metrics": metrics(), "config": {"python": CONFIG["python"], "audience": CONFIG["audience"]},
                "runtime": {"pyodide": "314.0.7", "worker": "docs/assets/js/pyworker.js", "widgets": "docs/assets/js/widgets.js"}, "exemplar": None, "threads": {}}

    def _day(self, n: int, tasks=None) -> dict:
        d = {"id": f"w01d{n}", "day": n, "title": f"Day {n}", "dateLabel": "Tue Oct 13, 2026", "subtopics": ["A"], "rel": f"week-01/day-{n}",
             "pageFile": f"/r/docs/weeks/week-01/day-{n}.html", "pageRel": f"docs/weeks/week-01/day-{n}.html",
             "practiceFile": f"/r/harness/practice/week-01/day-{n}.json", "solutionsDir": f"trainer/week-01/day-{n}/solutions", "spoilerRows": []}
        if tasks is not None:
            d["tasks"] = tasks
        return d

    @unittest.skipUnless(node_exe(), "node not found")
    def test_dry_run_suitability(self):
        out = self._dry(self._base("suitability", [self._day(3), self._day(5)]))
        self.assertEqual(["w01d3:suitability", "w01d5:suitability", "record", "verify"], [c["label"] for c in out["calls"]])
        tiers = CONFIG["models"]["stages"]
        self.assertEqual((tiers["practice-suitability"]["model"], tiers["practice-suitability"]["effort"]), (out["calls"][0]["model"], out["calls"][0]["effort"]))
        self.assertNotIn("practice_tasks.py insert", out["calls"][0]["prompt"], "the suitability pass does not touch the page")
        record = json.loads(re.search(r"EXACTLY this JSON:\n(\{.*\})\n", out["calls"][2]["prompt"]).group(1))
        self.assertEqual(("practice", 4, ["w01d3", "w01d5"], 0), (record["kind"], record["agents"], record["days"], record["flagged"]))
        self.assertEqual({"practice-proposal"}, {a["name"] for a in record["artifacts"]})
        res = out["result"]
        self.assertEqual(("suitability", 0), (res["mode"], res["flaggedCount"]))
        self.assertIn("practice_tasks.py show 1", res["next"])
        self.assertIn("--practice-build", res["next"])

    @unittest.skipUnless(node_exe(), "node not found")
    def test_dry_run_build_and_its_three_pass_cap(self):
        task = {"id": "t1", "title": "A", "step": 0, "idea": "Write f.", "checks": ["one", "two"], "built": False}
        out = self._dry(self._base("build", [self._day(5, [task])]))
        self.assertEqual(["w01d5:practice", "w01d5:practice-crit", "record", "verify"], [c["label"] for c in out["calls"]])
        self.assertIn("practice_browser.py 1", out["result"]["next"])
        self.assertEqual("done", out["result"]["report"][0]["status"])
        out = self._dry(self._base("build", [self._day(5, [task])]), critic_pass=False)
        labels = [c["label"] for c in out["calls"]]
        self.assertEqual((3, 3), (labels.count("w01d5:practice"), labels.count("w01d5:practice-crit")), "author and critic, three passes, then flagged")
        self.assertEqual(("flagged", 3), (out["result"]["report"][0]["status"], out["result"]["report"][0]["passes"]))
        self.assertIn("REPASS", out["calls"][2]["prompt"])
        esc = CONFIG["models"]["escalate"]
        self.assertEqual((esc["model"], esc["effort"]), (out["calls"][2]["model"], out["calls"][2]["effort"]), "pass 2 runs on the escalate tier")

    @unittest.skipUnless(node_exe(), "node not found")
    def test_dry_run_choice_kind(self):
        """D-0084: the assessor may propose a choice task; a day of choice tasks only writes no trainer file;
        a mixed day writes them for its Python tasks only; the agent count is unchanged."""
        out = self._dry(self._base("suitability", [self._day(3)]))
        self.assertIn('"kind": "choice"', out["calls"][0]["prompt"])
        self.assertIn('"kind" ("python" or "choice", on every task)', out["calls"][0]["prompt"])
        choice = {"id": "t1", "title": "A", "step": 0, "idea": "Pick one.", "checks": ["one", "two"], "kind": "choice", "built": False}
        python = {"id": "t2", "title": "B", "step": 1, "idea": "Write f.", "checks": ["one", "two"], "kind": "python", "built": False}
        out = self._dry(self._base("build", [self._day(5, [choice])]))
        self.assertEqual(["w01d5:practice", "w01d5:practice-crit", "record", "verify"], [c["label"] for c in out["calls"]])
        author, critic = out["calls"][0]["prompt"], out["calls"][1]["prompt"]
        self.assertIn("write NO file under trainer/week-01/day-5/solutions", author)
        self.assertNotIn("CASES = {", author)
        self.assertIn('"options"', author)
        self.assertIn("Choice tasks (D-0084)", critic)
        self.assertIn("holds no practice file", critic)
        record = json.loads(re.search(r"EXACTLY this JSON:\n(\{.*\})\n", out["calls"][2]["prompt"]).group(1))
        self.assertEqual(4, record["agents"])
        out = self._dry(self._base("build", [self._day(5, [choice, python])]))
        author = out["calls"][0]["prompt"]
        self.assertIn("one model answer per built Python task (t2)", author)
        self.assertIn("CASES = {", author)
        self.assertNotIn("write NO file", author)

    @unittest.skipUnless(node_exe(), "node not found")
    def test_dry_run_refuses_args_it_was_not_given_by_args_for(self):
        for bad in (self._base("other", [self._day(5)]), self._base("build", [self._day(5)])):
            out = json.loads(run_node(DRY_RUN, json.dumps({"src": WORKFLOW, "args": bad, "criticPass": True})))
            self.assertIn("args_for.py", out["error"] or "")


class DocsTests(unittest.TestCase):
    def test_agents_md_and_readme_describe_the_stage(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for needle in ("D-0047", "practice_tasks.py", "--practice-build", "practice-tasks.js", "harness/practice/", "Never approve on the trainer's behalf"):
            self.assertTrue(needle in agents, f"AGENTS.md does not mention {needle}")
        readme = (HARNESS / "README.md").read_text(encoding="utf-8")
        for needle in ("practice_tasks.py", "practice-tasks.js", "--practice-build"):
            self.assertTrue(needle in readme, f"harness/README.md does not mention {needle}")
        self.assertTrue((DOCS / "assets" / "js" / "pyworker.js").is_file())


if __name__ == "__main__":
    unittest.main()
