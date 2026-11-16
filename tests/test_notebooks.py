"""harness/notebook_check.py, the format check and path rule of a demoFormat notebook day's demo notebook (D-0085).

The style reference is the substitute trainer's notebook in the demo repo clone (gitignored): the tests that read it
skip when demo-repo/ is absent. The rule tests build notebooks in a temp folder.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import HARNESS, ROOT

sys.path.insert(0, str(HARNESS))
import notebook_check  # noqa: E402

REFERENCE = notebook_check.demo_repo_dir() / "notebooks" / "week-06" / "02_tuesday_trees_and_clustering.ipynb"


def _md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def _code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(keepends=True)}


def minimal() -> dict:
    return {"nbformat": 4, "nbformat_minor": 0, "metadata": {}, "cells": [
        _md("# Week 6 · Monday: Regression\n\nToday:\n\n1. **Lines**\n2. **Curves**\n3. **Classes**\n\nRun the next cell first."),
        _code("# ---------- Setup (run once) ----------\nimport numpy as np\nRANDOM_STATE = 42\n"),
        _md("## 1. Lines\n\nA line."), _code("x = np.arange(5)\nprint(x)\n"),
        _md("## 2. Curves\n\nA curve."), _code("print(x ** 2)\n"),
        _md("## 3. Classes\n\nA class."), _code("print(x > 2)\n"),
        _md("## Recap\n\n| Idea | Good at |\n|---|---|\n| line | trends |\n\n**Quick check**\n1. a?\n2. b?\n3. c?\n4. d?\n"),
    ]}


class NotebookRuleTests(unittest.TestCase):
    def _check(self, nb: dict, name: str = "01_monday_regression.ipynb", folder: str = "notebooks/week-06") -> list[str]:
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / folder
            d.mkdir(parents=True)
            f = d / name
            f.write_text(json.dumps(nb), encoding="utf-8")
            return notebook_check.check(f)

    def test_minimal_notebook_passes(self):
        self.assertEqual([], self._check(minimal()))

    def test_each_rule_fails(self):
        def broken(fn) -> dict:
            nb = copy.deepcopy(minimal())
            fn(nb)
            return nb
        cases = [
            ("is not the slot of tuesday", minimal(), "01_tuesday_regression.ipynb", "notebooks/week-06"),
            ("file name must read", minimal(), "Monday-Regression.ipynb", "notebooks/week-06"),
            ("notebooks/week-WW/", minimal(), "01_monday_regression.ipynb", "week-06"),
            ("nbformat 4", broken(lambda nb: nb.update(nbformat=3)), None, None),
            ("numbered agenda", broken(lambda nb: nb["cells"].__setitem__(0, _md("# Title\n\nno agenda"))), None, None),
            ("first cell", broken(lambda nb: nb["cells"].__setitem__(0, _md("Title\n1. a\n2. b\n3. c"))), None, None),
            ("setup cell", broken(lambda nb: nb["cells"].__setitem__(1, _md("## not code"))), None, None),
            ("'## ' sections", broken(lambda nb: nb["cells"].__delitem__(slice(6, 8))), None, None),
            ("'## Recap'", broken(lambda nb: nb["cells"].__setitem__(-1, _md("**Quick check**\n1. a\n2. b\n3. c\n4. d"))), None, None),
            ("Quick check", broken(lambda nb: nb["cells"].__setitem__(-1, _md("## Recap\n\n| a |\n"))), None, None),
            (">= 4 numbered questions", broken(lambda nb: nb["cells"].__setitem__(-1, _md("## Recap\n**Quick check**\n1. a\n2. b"))), None, None),
            ("stored outputs", broken(lambda nb: nb["cells"][3].update(outputs=[{"output_type": "stream", "name": "stdout", "text": ["0\n"]}])), None, None),
            ("execution count", broken(lambda nb: nb["cells"][3].update(execution_count=1)), None, None),
            ("pip-installs", broken(lambda nb: nb["cells"][3].update(source=["!pip install tensorflow\n"])), None, None),
            ("split it", broken(lambda nb: nb["cells"][3].update(source=["x = 1\n"] * 41)), None, None),
        ]
        for needle, nb, name, folder in cases:
            with self.subTest(rule=needle):
                problems = self._check(nb, name or "01_monday_regression.ipynb", folder or "notebooks/week-06")
                self.assertTrue([p for p in problems if needle in p], problems)
        self.assertEqual([], self._check(broken(lambda nb: nb["cells"][1].update(source=["x = 1\n"] * 80))), "the setup cell may be long")

    def test_path_rule_helpers(self):
        self.assertEqual("03_wednesday", notebook_check.day_prefix(3))
        self.assertEqual("01_monday_ml_intro_and_supervised_learning.ipynb",
                         notebook_check.default_name(1, "day-1-ml-intro-and-supervised-learning"))
        self.assertRegex(notebook_check.default_name(5, "day-5-perceptrons-and-tensorflow-basics"), notebook_check.NAME_RE)
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "x.ipynb"
            f.write_text(json.dumps(minimal()), encoding="utf-8")
            self.assertEqual(["# Week 6 · Monday: Regression", "## 1. Lines", "## 2. Curves", "## 3. Classes", "## Recap"],
                             notebook_check.outline(f))


@unittest.skipUnless(REFERENCE.is_file(), "demo-repo/ clone (or the substitute's week-06 notebook) not present")
class ReferenceNotebookTests(unittest.TestCase):
    def test_the_substitutes_notebook_passes_unchanged(self):
        self.assertEqual([], notebook_check.check(REFERENCE))
        res = subprocess.run([sys.executable, str(HARNESS / "notebook_check.py"), str(REFERENCE.parent)],
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(0, res.returncode, res.stdout + res.stderr)
        self.assertTrue(res.stdout.strip().endswith("OK"))

    def test_it_is_w6d2s_notebook(self):
        nb = notebook_check.notebook_for(6, 2, "day-2-clustering-and-k-means")
        self.assertEqual(("notebooks/week-06/02_tuesday_trees_and_clustering.ipynb", True), (nb["path"], nb["exists"]))
        self.assertIn("## Recap", nb["outline"])
        self.assertIn("## 4. K-means by hand", nb["outline"])


class TemplateTests(unittest.TestCase):
    def test_style_guide_and_config_name_the_rule(self):
        guide = (HARNESS / "templates" / "notebook-style.md").read_text(encoding="utf-8")
        for needle in ("02_tuesday_trees_and_clustering.ipynb", "## Recap", "Quick check", "RANDOM_STATE = 42", "Colab", "notebook_check.py"):
            self.assertIn(needle, guide)
        cfg = json.loads((HARNESS / "config.json").read_text(encoding="utf-8"))
        self.assertIn("D-0085", cfg["demoRepo"]["layout"]["notebooks"])
        self.assertIn("notebooks/week-WW/NN_<weekday>_<slug>.ipynb", cfg["demoRepo"]["layout"]["notebooks"])


if __name__ == "__main__":
    unittest.main()
