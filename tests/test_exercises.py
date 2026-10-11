"""Exercise contract: starter fails, trainer solution passes."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import unittest

from helpers import ROOT, TRAINER, live_days, metrics

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


if __name__ == "__main__":
    unittest.main()
