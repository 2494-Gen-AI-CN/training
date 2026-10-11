"""Demo folder contract for every live day."""

from __future__ import annotations

import py_compile
import re
import unittest

from helpers import ROOT, SECRET_RE, live_days, metrics

STEP_RE = re.compile(r"^# --- STEP (\d+):", re.M)


class DemoTests(unittest.TestCase):
    def test_every_live_demo_dir(self):
        M = metrics()["demos"]
        for w, d, rel in live_days():
            ddir = ROOT / "demos" / rel
            with self.subTest(rel=rel):
                self.assertTrue((ddir / "README.md").exists())
                readme = (ddir / "README.md").read_text(encoding="utf-8")
                code = sorted(p for p in ddir.iterdir() if p.suffix in (".py", ".ipynb") and re.match(r"^\d{2}_", p.name))
                self.assertTrue(M["filesMin"] <= len(code) <= M["filesMax"], [p.name for p in code])
                for p in code:
                    self.assertIn(p.name, readme, f"README does not list {p.name}")
                    text = p.read_text(encoding="utf-8")
                    self.assertIsNone(SECRET_RE.search(text), f"secret-looking string in {p.name}")
                    if p.suffix == ".py":
                        py_compile.compile(str(p), doraise=True)
                        self.assertLessEqual(len(text.splitlines()), M["maxLinesPerFile"], f"{p.name} too long")
                        steps = [int(n) for n in STEP_RE.findall(text)]
                        self.assertGreaterEqual(len(steps), 2, f"{p.name} needs STEP markers")
                        self.assertEqual(list(range(1, len(steps) + 1)), steps, f"{p.name} STEP numbering")
                        self.assertTrue(text.lstrip().startswith(('"""', "'''", "#!")), f"{p.name} needs a top docstring")
                    else:
                        try:
                            import nbformat
                        except ImportError:
                            self.skipTest("nbformat not installed (pip install -r requirements-dev.txt)")
                        nb = nbformat.read(str(p), as_version=4)
                        nbformat.validate(nb)
                        for c in nb.cells:
                            if c.cell_type == "code":
                                self.assertFalse(c.get("outputs"), f"{p.name} has stored outputs — clear them")
                if d["demoFormat"] == "nb":
                    self.assertTrue(any(p.suffix == ".ipynb" for p in code), "nb day needs at least one notebook")
                env = ddir / ".env.example"
                if env.exists():
                    for line in env.read_text(encoding="utf-8").splitlines():
                        if "=" in line and not line.startswith("#"):
                            self.assertFalse(line.split("=", 1)[1].strip(), f".env.example must not contain values: {line}")


if __name__ == "__main__":
    unittest.main()
