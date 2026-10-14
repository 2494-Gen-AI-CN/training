"""Exercise contract: starter fails, trainer solution passes."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest

from helpers import HARNESS, ROOT, TRAINER, all_days, live_days, load_json, metrics

TEST_FN_RE = re.compile(r"^\s*def (test_\w+)\(", re.M)


def _pytest(cwd, env_extra=None, timeout=120):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=timeout, encoding="utf-8")


class ExerciseTests(unittest.TestCase):
    def test_every_live_exercise(self):
        M = metrics()["exercise"]
        for w, d, rel in live_days():
            edir = ROOT / "exercises" / rel
            with self.subTest(rel=rel):
                self.assertTrue((edir / "README.md").exists())
                if d.get("exerciseKind", "pytest") == "rubric":
                    # D-0025: hands-on deliverable marked against a rubric; no starter, no pytest
                    text = (edir / "README.md").read_text(encoding="utf-8")
                    for h in ("## Deliverable", "## Acceptance criteria", "## Rubric", "## Getting started"):
                        self.assertIn(h, text, f"rubric README missing {h}")
                    self.assertFalse((edir / "starter").exists(), "rubric exercise must not have starter/")
                    self.assertFalse((edir / "tests").exists(), "rubric exercise must not have tests/")
                    continue
                self.assertTrue((edir / "tests" / "conftest.py").exists())
                starters = [p for p in (edir / "starter").glob("*.py") if p.name != "__init__.py"]
                self.assertEqual(1, len(starters), "exactly one starter module")
                module = starters[0].stem
                test_file = edir / "tests" / f"test_{module}.py"
                self.assertTrue(test_file.exists(), f"missing tests/test_{module}.py")
                n = len(TEST_FN_RE.findall(test_file.read_text(encoding="utf-8")))
                self.assertTrue(M["testsMin"] <= n <= M["testsMax"], f"{n} tests")
                self.assertIn("NotImplementedError", starters[0].read_text(encoding="utf-8"))
                text = test_file.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"\b(requests|urllib|http\.client|socket)\b", "exercise tests must not use the network")

                starter_run = _pytest(edir, timeout=M["pytestTimeoutSec"])
                self.assertNotEqual(0, starter_run.returncode, "starter must FAIL the tests\n" + starter_run.stdout)

                sol = TRAINER / rel / "solutions"
                if not sol.exists():
                    continue  # trainer repo not cloned here; solution check runs where it is
                sol_run = _pytest(edir, {"EXERCISE_SRC": str(sol)}, timeout=M["pytestTimeoutSec"])
                self.assertEqual(0, sol_run.returncode, "solution must PASS the tests\n" + sol_run.stdout + sol_run.stderr)


class LearnerRepoTests(unittest.TestCase):
    """D-0037, D-0051: one public FirstnameLastname repo per trainee in the cohort organisation, recorded once in
    config.json learnerRepo and carried to the exercise and runbook prompts through args."""

    def setUp(self):
        self.cfg = load_json(HARNESS / "config.json")
        self.lr = self.cfg["learnerRepo"]

    def test_config_records_the_convention(self):
        org = re.fullmatch(r"https://github\.com/([^/]+)/[^/]+", self.cfg["repoUrl"]).group(1)
        self.assertEqual(org, self.lr["org"], "learner repos live in the same organisation as the training repo")
        self.assertEqual("public", self.lr["visibility"])
        self.assertRegex(self.lr["name"], r"^[A-Za-z]+$", "the name placeholder is plain letters (it is quoted inside <...>)")
        for k in ("nameRule", "createdIn", "handIn"):
            self.assertTrue(self.lr.get(k), f"learnerRepo lacks {k}")
        self.assertIn("PascalCase", self.lr["nameRule"])
        self.assertIn("hyphen or underscore", self.lr["nameRule"], "the rule tolerates a separator between the names")
        self.assertEqual({"root", "exercises", "codeAlong", "scratch", "hackathon"}, set(self.lr["layout"]))
        self.assertIn(self.lr["createdIn"], {d["id"] for w, d, rel in all_days()}, "createdIn must be a curriculum day id")

    def test_args_carry_it_to_the_workflows(self):
        w, d, rel = next(all_days())
        for argv in ((str(w["week"]), str(d["day"]), "--no-plan"), (str(w["week"]), "--plan")):
            with self.subTest(argv=argv):
                res = subprocess.run([sys.executable, str(HARNESS / "args_for.py"), *argv, "--today", "2026-10-12"],
                                     capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(0, res.returncode, res.stderr)
                self.assertEqual(self.lr, json.loads(res.stdout)["config"]["learnerRepo"])

    def test_day_fanout_quotes_it_to_exercise_and_runbook_agents_only(self):
        src = (HARNESS / "workflows" / "day-fanout.js").read_text(encoding="utf-8")
        self.assertIn("CFG.learnerRepo", src)
        header = src[src.index("const dayHeader"):src.index("const LR = ")]
        self.assertNotRegex(header, r"\$\{[^}]*(LR\b|learner)", "dayHeader reaches research, demo and notes prompts; keep the learner repo out of it")
        # exercise author + critic (pytest and rubric kinds), runbook author + critic
        self.assertEqual(6, src.count("${learnerCtx(d)}"))
        for chunk in src.split("agent(")[1:]:
            if "${learnerCtx(d)}" in chunk.split("{ schema:")[0]:
                self.assertRegex(chunk, r"label:`\$\{d\.id\}:(exercise|runbook)", "learnerCtx belongs to exercise and runbook prompts only")

    def test_templates_and_critics_name_it(self):
        for name in ("exercise-README.md", "exercise-rubric-README.md", "runbook.md"):
            self.assertIn(f"<{self.lr['name']}>", (HARNESS / "templates" / name).read_text(encoding="utf-8"), name)
        for name in ("exercise.md", "runbook.md"):
            text = (HARNESS / "critics" / name).read_text(encoding="utf-8")
            self.assertIn("D-0037", text, name)
            self.assertIn("D-0051", text, name)

    def test_the_creating_exercise_asks_for_the_learner_repo(self):
        rel = next(rel for w, d, rel in all_days() if d["id"] == self.lr["createdIn"])
        readme = ROOT / "exercises" / rel / "README.md"
        if not readme.is_file():
            self.skipTest(f"{rel} is not authored yet")
        text = readme.read_text(encoding="utf-8")
        self.assertIn(f"https://github.com/{self.lr['org']}/<{self.lr['name']}>.git", text)
        self.assertRegex(text, r"\*\*public\*\* GitHub repository")
        self.assertNotRegex(text, r"\*\*private\*\*|github\.com/<you>/", "the deliverable is the organisation's public learner repo (D-0051)")
        self.assertNotIn(f"{self.lr['createdIn']}-team-repo", text, "the per-day repo name was replaced by the learner repo")


if __name__ == "__main__":
    unittest.main()
