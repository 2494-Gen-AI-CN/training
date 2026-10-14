"""Demo contract for every authored or live day (D-0030, D-0052; publish state stays on live/taught).

A demo is a walkthrough script the trainer types (trainer/<rel>/demos/NN_<slug>.md) plus an answer key
(trainer/<rel>/demos/key/NN_<slug>.py|.md). Answer keys are published to demos/<rel>/ only once the day
carries `taught` in curriculum.json. demoFormat "none" days have no demos at all. demoFormat "loose" days (D-0050)
publish whatever the trainer typed in the demo repo (harness/close_day.py); their authored scripts, when present, are
only a fallback that still passes demo_check and is never published.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import HARNESS, ROOT, SECRET_RE, TRAINER, authored_days, live_days, load_json, metrics, public_demos, trainer_demos

sys.path.insert(0, str(HARNESS))
import demo_check  # noqa: E402
import publish_demos  # noqa: E402

CONFIG = load_json(HARNESS / "config.json")
KEY_RE = re.compile(r"^\d{2}_")


class DemoScriptTests(unittest.TestCase):
    """Scripts + answer keys in the private repo; skipped per day when trainer/ is absent."""

    def test_every_authored_day(self):
        for w, d, rel in authored_days():  # D-0052: authored or live
            with self.subTest(rel=rel):
                if d["demoFormat"] == "none":
                    self.assertFalse(trainer_demos(rel).exists(), "demoFormat none: no demo folder in trainer/")
                    continue
                if not TRAINER.exists():
                    continue
                ddir = trainer_demos(rel)
                if d["demoFormat"] == "loose" and not ddir.is_dir():
                    continue  # D-0050: a loose day's fallback scripts are optional
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


class ThreadChainTests(unittest.TestCase):
    """Every authored or live rung's `Starts from` key exists and its surviving lines are still in the rung's key, so
    re-authoring an earlier day fails the later ones loudly instead of silently staling them (A7, A12; D-0052)."""

    def test_every_authored_rung_chains(self):
        if not TRAINER.exists():
            self.skipTest("trainer/ private repo not cloned here")
        seen = 0
        for w, d, rel in authored_days():
            if d["demoFormat"] == "none":
                continue
            ddir = trainer_demos(rel)
            if d["demoFormat"] == "loose" and not ddir.is_dir():
                continue  # D-0050: no fallback scripts for this loose day
            for script in sorted(ddir.glob("*.md")):
                if not KEY_RE.match(script.name):
                    continue
                with self.subTest(script=f"{rel}/{script.name}"):
                    hdr = demo_check._header(script.read_text(encoding="utf-8"))
                    self.assertIn("Thread", hdr, "header needs '- Thread:'")
                    self.assertIn("Starts from", hdr, "header needs '- Starts from:'")
                    starts = hdr["Starts from"]
                    if starts == "cold":
                        continue
                    seen += 1
                    start = ROOT / starts
                    self.assertTrue(start.is_file(), f"Starts from key {starts} missing")
                    key = ddir / "key" / Path(hdr["Answer key"]).name
                    if start.suffix == ".py" and key.suffix == ".py":
                        surviving = demo_check.carried_lines(start) - demo_check.script_replaced_lines(script.read_text(encoding="utf-8"))
                        klines = set(demo_check._lines(key.read_text(encoding="utf-8")))
                        self.assertEqual(set(), surviving - klines, f"{key.name} lost carried lines from {starts}")
        self.assertGreaterEqual(seen, 1, "at least one live rung should start from an earlier rung (W1D2 demo 3)")


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
                    if d["demoFormat"] == "loose":  # D-0050: any filename the trainer typed, subfolders included
                        files = [(f.relative_to(pub).as_posix(), f) for f in publish_demos.bi.published_files(pub)]
                    else:
                        files = [(f.name, f) for f in pub.iterdir() if f.is_file() and KEY_RE.match(f.name)]
                    for name, f in files:
                        self.assertIn(name, readme, f"published README does not list {name}")
                        self.assertIsNone(SECRET_RE.search(f.read_text(encoding="utf-8", errors="replace")), f"secret-looking string in {name}")


class DemoCheckSelfTests(unittest.TestCase):
    """harness/demo_check.py itself: the template passes once filled; the both-ways check catches drift."""

    M = {"scriptsMin": 1, "scriptsMax": 5, "minutesPerScriptMin": 15, "minutesPerScriptMax": 45, "maxLinesPerFile": 90,
         "maxLinesPerThreadKey": 200, "maxTypedLinesPerRung": 60}

    def _fixture(self, tmp: Path, key_lines: str, script_blocks: str, key_name: str = "01_demo.py", extra_sections: str = "",
                 thread: str = "standalone", starts: str = "cold"):
        (tmp / "key").mkdir(exist_ok=True)
        (tmp / "key" / key_name).write_text(key_lines, encoding="utf-8")
        (tmp / "key" / "README.md").write_text(f"| 1 | `{key_name}` | x | run | no |\n", encoding="utf-8")
        script = (
            "# 01 — Demo\n\n"
            "- Objective: do a thing\n- Time: 20 min\n- Before the room arrives: terminal open\n- Delivery mode: typed\n"
            "- Audience: grads\n- Prerequisite reading: none\n"
            f"- Answer key: key/{key_name}\n- Hand-typed files: {key_name}\n- Tool-generated files: none\n"
            f"- Thread: {thread}\n- Starts from: {starts}\n\n"
            + script_blocks
            + "\n## Common pitfalls\n\n| a | b |\n\n## What we did NOT cover (intentional)\n\n- x: deferred to later. It is not needed today.\n\n## Wrap-up questions\n\n1. q\n\n## Sequence pointer\n\nnext\n"
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

    START = "trainer/week-00/day-1-start/demos/key/01_start.py"
    TWO_STEPS = ("## Step 1 — add (10 min)\n\ncwd: `ticket-desk/`\n\n```python\ny = 2\n```\n\n"
                 "## Step 2 — print (10 min)\n\ncwd: `ticket-desk/`\n\n```python\nprint(y)\n```\n")

    def _thread_root(self, root: Path) -> Path:
        """A scratch repo root with a previous rung's .py key at START; returns this rung's demo dir."""
        start = root / self.START
        start.parent.mkdir(parents=True)
        start.write_text("x = 1\nprint(x)\n", encoding="utf-8")
        rung = root / "trainer/week-00/day-2-rung/demos"
        rung.mkdir(parents=True)
        return rung

    def test_thread_rung_carries_lines_from_starts_from_key(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            rung = self._thread_root(root)
            # the key is the whole end state: carried lines + this rung's typed lines
            self._fixture(rung, "x = 1\nprint(x)\ny = 2\nprint(y)\n", self.TWO_STEPS, thread="p0-demo", starts=self.START)
            self.assertEqual([], demo_check.check_dir(rung, self.M, root=root))
            # a carried line silently dropped from the key fails (chain breaks loudly)
            (rung / "key" / "01_demo.py").write_text("x = 1\ny = 2\nprint(y)\n", encoding="utf-8")
            probs = demo_check.check_dir(rung, self.M, root=root)
            self.assertTrue(any("carried line" in p and "print(x)" in p for p in probs), probs)
            # ... unless the rung shows it in a ```python replaced block
            self._fixture(rung, "x = 1\ny = 2\nprint(y)\n",
                          "## Step 1 — drop (10 min)\n\ncwd: `ticket-desk/`\n\n```python replaced\nprint(x)\n```\n\n```python\ny = 2\n```\n\n"
                          "## Step 2 — print (10 min)\n\ncwd: `ticket-desk/`\n\n```python\nprint(y)\n```\n",
                          thread="p0-demo", starts=self.START)
            self.assertEqual([], demo_check.check_dir(rung, self.M, root=root))
            # a replaced line that the start key never had fails
            self._fixture(rung, "x = 1\nprint(x)\ny = 2\nprint(y)\n",
                          "## Step 1 — bogus (10 min)\n\ncwd: `ticket-desk/`\n\n```python replaced\nz = 9\n```\n\n```python\ny = 2\n```\n\n"
                          "## Step 2 — print (10 min)\n\ncwd: `ticket-desk/`\n\n```python\nprint(y)\n```\n",
                          thread="p0-demo", starts=self.START)
            probs = demo_check.check_dir(rung, self.M, root=root)
            self.assertTrue(any("replaced line is not in the Starts from key" in p for p in probs), probs)
            # a key line that is neither typed nor carried still fails
            self._fixture(rung, "x = 1\nprint(x)\ny = 2\nprint(y)\nw = 0\n", self.TWO_STEPS, thread="p0-demo", starts=self.START)
            probs = demo_check.check_dir(rung, self.M, root=root)
            self.assertTrue(any("never typed" in p and "w = 0" in p for p in probs), probs)

    def test_thread_header_rules(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            rung = self._thread_root(root)
            # a standalone demo must start cold
            self._fixture(rung, "y = 2\nprint(y)\n", self.TWO_STEPS, thread="standalone", starts=self.START)
            probs = demo_check.check_dir(rung, self.M, root=root)
            self.assertTrue(any("must start cold" in p for p in probs), probs)
            # a Starts from key that is not on disk fails (rungs are authored in ladder order)
            self._fixture(rung, "y = 2\nprint(y)\n", self.TWO_STEPS, thread="p0-demo", starts="trainer/week-00/day-1-start/demos/key/02_missing.py")
            probs = demo_check.check_dir(rung, self.M, root=root)
            self.assertTrue(any("does not exist" in p for p in probs), probs)
            # a transcript start carries nothing: the .py rung types its file from the first line
            tstart = root / "trainer/week-00/day-1-start/demos/key/02_transcript.md"
            tstart.write_text("```console\n$ git init\n```\n", encoding="utf-8")
            self._fixture(rung, "y = 2\nprint(y)\n", self.TWO_STEPS, thread="p0-demo", starts="trainer/week-00/day-1-start/demos/key/02_transcript.md")
            self.assertEqual([], demo_check.check_dir(rung, self.M, root=root))
            # the typed-lines cap applies per rung
            probs = demo_check.check_dir(rung, {**self.M, "maxTypedLinesPerRung": 1}, root=root)
            self.assertTrue(any("maxTypedLinesPerRung" in p for p in probs), probs)
            # thread keys get the larger cap, standalone keys the smaller one
            probs = demo_check.check_dir(rung, {**self.M, "maxLinesPerFile": 1}, root=root)
            self.assertEqual([], probs, probs)
            probs = demo_check.check_dir(rung, {**self.M, "maxLinesPerThreadKey": 1}, root=root)
            self.assertTrue(any("maxLinesPerThreadKey" in p for p in probs), probs)

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
        self.assertEqual([], demo_check.not_covered_problems(text), "the template's own bullet follows the one format")

    def test_not_covered_bullets_take_one_format(self):
        """D-0039: '- <topic>: <where it goes>. <reason>.' on every script, no dash between topic and note."""
        head = "## What we did NOT cover (intentional)\n\n"
        tail = "\n\n## Wrap-up questions\n\n- not a bullet of that section — ignored\n"
        good = [
            "- Lists and tuples: deferred to Thursday (w01d4). The ticket stays six flat variables.",
            '- `if __name__ == "__main__":` around the script body: deferred to week 2 day 1, when the file splits into modules.',
            "- `for` over `ticket.items()`: deferred to Friday. The items print as a list here.",
        ]
        self.assertEqual([], demo_check.not_covered_problems(head + "\n".join(good) + tail))
        for bad in (
            "- Lists and tuples — deferred to Thursday (w01d4); the ticket stays flat.",
            "- Lists and tuples are deferred to Thursday (w01d4); the ticket stays flat.",
            "- Lists and tuples. Deferred to Thursday (w01d4); the ticket stays flat.",
            "- `datetime` for `hours_open` -- deferred to Demo 4.",
        ):
            with self.subTest(bullet=bad):
                self.assertEqual([bad], demo_check.not_covered_problems(head + bad + tail))
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            self._fixture(tmp, 'x = 1\nprint(x)\n',
                          "## Step 1 — set (10 min)\n\ncwd: `s/`\n\n```python\nx = 1\n```\n\n## Step 2 — print (10 min)\n\ncwd: `s/`\n\n```python\nprint(x)\n```\n")
            self.assertEqual([], demo_check.check_dir(tmp, self.M))
            script = tmp / "01_demo.md"
            script.write_text(script.read_text(encoding="utf-8").replace("- x: deferred to later. It is not needed today.", "- x — deferred to later because it is not needed today."), encoding="utf-8")
            probs = demo_check.check_dir(tmp, self.M)
            self.assertTrue(any("NOT cover" in p for p in probs), probs)


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

    def test_loose_card_variants(self):
        """D-0050: a loose day's card links any typed file (subfolders too), or says there was no code demo."""
        html = (HARNESS / "templates" / "day.exemplar.html").read_text(encoding="utf-8")
        rel = "week-00/day-0-example"
        out = publish_demos.flip_card(html, CONFIG["repoUrl"], "main", rel, ["hello.py", "notes/scratch.py"], meta=publish_demos.LOOSE_META)
        self.assertIn(publish_demos.CARD_PUBLISHED, out)
        self.assertIn(f"/demos/{rel}/hello.py", out)
        self.assertIn(f"/demos/{rel}/notes/scratch.py", out)
        self.assertIn(publish_demos.LOOSE_META, out)
        self.assertNotIn(publish_demos.PENDING_TEXT, out)
        out = publish_demos.flip_card_none(html)
        self.assertIn(publish_demos.CARD_NONE, out)
        self.assertIn(publish_demos.NONE_TEXT, out)
        self.assertNotIn(publish_demos.CARD_PENDING, out)
        start = out.index(publish_demos.CARD_NONE)
        card = out[start:out.index(publish_demos.NONE_META, start) + len(publish_demos.NONE_META)]
        self.assertNotIn("<a ", card)
        with self.assertRaises(ValueError):
            publish_demos.flip_card_none(out)


if __name__ == "__main__":
    unittest.main()
