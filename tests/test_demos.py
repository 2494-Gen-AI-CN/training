"""Demo contract for every live day (D-0030).

A demo is a walkthrough script the trainer types (trainer/<rel>/demos/NN_<slug>.md) plus an answer key
(trainer/<rel>/demos/key/NN_<slug>.py|.md). Answer keys are published to demos/<rel>/ only once the day
carries `taught` in curriculum.json. demoFormat "none" days have no demos at all.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import HARNESS, ROOT, SECRET_RE, TRAINER, live_days, load_json, metrics, public_demos, trainer_demos

sys.path.insert(0, str(HARNESS))
import demo_check  # noqa: E402
import publish_demos  # noqa: E402

CONFIG = load_json(HARNESS / "config.json")
KEY_RE = re.compile(r"^\d{2}_")


class DemoScriptTests(unittest.TestCase):
    """Scripts + answer keys in the private repo; skipped per day when trainer/ is absent."""

    def test_every_live_day(self):
        for w, d, rel in live_days():
            with self.subTest(rel=rel):
                if d["demoFormat"] == "none":
                    self.assertFalse(trainer_demos(rel).exists(), "demoFormat none: no demo folder in trainer/")
                    continue
                if not TRAINER.exists():
                    continue
                ddir = trainer_demos(rel)
                self.assertTrue(ddir.is_dir(), f"missing {ddir}")
                problems = demo_check.check_dir(ddir, metrics()["demos"])
                self.assertEqual([], problems, "\n".join(problems))
                key_dir = ddir / "key"
                keys = sorted(p for p in key_dir.iterdir() if p.is_file() and KEY_RE.match(p.name))
                if d["demoFormat"] == "nb":
                    self.assertTrue(any(p.suffix == ".ipynb" for p in keys), "nb day needs at least one notebook key")
                for p in list(keys) + sorted(ddir.glob("*.md")):
                    self.assertIsNone(SECRET_RE.search(p.read_text(encoding="utf-8")), f"secret-looking string in {p.name}")
                for p in keys:
                    if p.suffix == ".ipynb":
                        try:
                            import nbformat
                        except ImportError:
                            self.skipTest("nbformat not installed (pip install -r requirements-dev.txt)")
                        nb = nbformat.read(str(p), as_version=4)
                        nbformat.validate(nb)
                        for c in nb.cells:
                            if c.cell_type == "code":
                                self.assertFalse(c.get("outputs"), f"{p.name} has stored outputs — clear them")
                env = key_dir / ".env.example"
                if env.exists():
                    for line in env.read_text(encoding="utf-8").splitlines():
                        if "=" in line and not line.startswith("#"):
                            self.assertFalse(line.split("=", 1)[1].strip(), f".env.example must not contain values: {line}")


class PublishStateTests(unittest.TestCase):
    """Public demos/<rel>/ exists iff the day is taught, and mirrors key/ when the private repo is present."""

    def test_every_live_day(self):
        for w, d, rel in live_days():
            with self.subTest(rel=rel):
                problems = publish_demos.check(d, rel, CONFIG)
                self.assertEqual([], problems, "\n".join(problems))
                if d.get("taught") and d["demoFormat"] != "none":
                    pub = public_demos(rel)
                    readme = (pub / "README.md").read_text(encoding="utf-8")
                    for p in pub.iterdir():
                        if p.is_file() and KEY_RE.match(p.name):
                            self.assertIn(p.name, readme, f"published README does not list {p.name}")
                            self.assertIsNone(SECRET_RE.search(p.read_text(encoding="utf-8")), f"secret-looking string in {p.name}")


class DemoCheckSelfTests(unittest.TestCase):
    """harness/demo_check.py itself: the template passes once filled; the both-ways check catches drift."""

    M = {"scriptsMin": 1, "scriptsMax": 5, "minutesPerScriptMin": 15, "minutesPerScriptMax": 45, "maxLinesPerFile": 90}

    def _fixture(self, tmp: Path, key_lines: str, script_blocks: str, key_name: str = "01_demo.py", extra_sections: str = ""):
        (tmp / "key").mkdir()
        (tmp / "key" / key_name).write_text(key_lines, encoding="utf-8")
        (tmp / "key" / "README.md").write_text(f"| 1 | `{key_name}` | x | run | no |\n", encoding="utf-8")
        script = (
            "# 01 — Demo\n\n"
            "- Objective: do a thing\n- Time: 20 min\n- Before the room arrives: terminal open\n- Delivery mode: typed\n"
            "- Audience: grads\n- Prerequisite reading: none\n"
            f"- Answer key: key/{key_name}\n- Hand-typed files: {key_name}\n- Tool-generated files: none\n\n"
            + script_blocks
            + "\n## Common pitfalls\n\n| a | b |\n\n## What we did NOT cover (intentional)\n\n- x\n\n## Wrap-up questions\n\n1. q\n\n## Sequence pointer\n\nnext\n"
            + extra_sections
        )
        (tmp / "01_demo.md").write_text(script, encoding="utf-8")

    def test_py_key_both_ways(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            self._fixture(tmp, 'x = 1\nprint(x)\n',
                          "## Step 1 — set (10 min)\n\ncwd: `s/`\n\n```python\nx = 1\n```\n\n## Step 2 — print (10 min)\n\ncwd: `s/`\n\n```python\nprint(x)\n```\n")
            self.assertEqual([], demo_check.check_dir(tmp, self.M))
            # a key line never typed in the script fails; a typed line missing from the key fails
            (tmp / "key" / "01_demo.py").write_text('x = 1\nprint(x)\ny = 2\n', encoding="utf-8")
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any("never typed" in p for p in probs), probs)
            (tmp / "key" / "01_demo.py").write_text('x = 1\n', encoding="utf-8")
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any("not in the answer key" in p for p in probs), probs)

    def test_transcript_key_sequence(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            self._fixture(tmp, "```console\n$ git init\nInitialized empty Git repository\n$ git status\nOn branch main\n```\n",
                          "## Step 1 — init (10 min)\n\ncwd: `s/`\n\n```bash\n# start here\ngit init\n```\n\n## Step 2 — status (10 min)\n\ncwd: `s/`\n\n```bash\ngit status\n```\n",
                          key_name="01_demo.md")
            self.assertEqual([], demo_check.check_dir(tmp, self.M))
            (tmp / "key" / "01_demo.md").write_text("```console\n$ git init\n$ git log\n```\n", encoding="utf-8")
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any("command sequences differ" in p for p in probs), probs)

    def test_header_and_steps_enforced(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            self._fixture(tmp, 'x = 1\n', "## Step 1 — only one (20 min)\n\n```python\nx = 1\n```\n")
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any(">= 2" in p for p in probs), probs)
            self.assertTrue(any("cwd" in p for p in probs), probs)

    def test_template_is_well_formed(self):
        text = (HARNESS / "templates" / "demo-script.md").read_text(encoding="utf-8")
        for f in demo_check.HEADER_FIELDS:
            self.assertIn(f"- {f}:", text)
        for s in demo_check.REQUIRED_SECTIONS:
            self.assertIn(s, text)
        steps = demo_check._steps(text)
        self.assertEqual([1, 2, 3], [s[0] for s in steps])
        self.assertEqual(30, sum(s[1] for s in steps))


class FlipCardTests(unittest.TestCase):
    def test_exemplar_card_flips(self):
        html = (HARNESS / "templates" / "day.exemplar.html").read_text(encoding="utf-8")
        self.assertIn(publish_demos.CARD_PENDING, html)
        out = publish_demos.flip_card(html, CONFIG["repoUrl"], "main", "week-00/day-0-example", ["01_a.py", "02_b.md"])
        self.assertIn('data-demo="published"', out)
        self.assertIn("/demos/week-00/day-0-example/01_a.py", out)
        self.assertIn("/demos/week-00/day-0-example/02_b.md", out)
        self.assertNotIn(publish_demos.PENDING_TEXT, out)
        self.assertIn(publish_demos.PUBLISHED_META, out)


if __name__ == "__main__":
    unittest.main()
