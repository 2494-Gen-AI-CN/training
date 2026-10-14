"""D-0048: no material claims the reader knows something from outside the course (metrics.notes.assumptionPhrases).

Notes pages are covered by notes_check.py --phrases (tests/test_pages.py); this covers the Markdown a trainee
reads (exercise READMEs) and the Markdown the trainer reads aloud (demo scripts and runbooks, when trainer/ exists).
"""

from __future__ import annotations

import re
import unittest

from helpers import ROOT, TRAINER, metrics

PHRASES = metrics()["notes"]["assumptionPhrases"]


def hits(text: str) -> list[str]:
    out = []
    for ph in PHRASES:
        for m in re.finditer(r"(?<![\w'])" + re.escape(ph) + r"(?![\w'])", text, re.I):
            line = text.count("\n", 0, m.start()) + 1
            out.append(f"line {line}: {ph!r}")
    return out


class AssumptionPhraseTests(unittest.TestCase):
    def test_matcher(self):
        self.assertEqual(["line 2: 'from coursework'"], hits("A list already knows its length.\nYou know it From Coursework."))

    def test_exercise_readmes(self):
        for f in sorted((ROOT / "exercises").glob("**/README.md")):
            with self.subTest(f=f.relative_to(ROOT).as_posix()):
                self.assertEqual([], hits(f.read_text(encoding="utf-8")))

    @unittest.skipUnless(TRAINER.exists(), "trainer/ private repo not cloned here")
    def test_trainer_scripts_and_runbooks(self):
        for f in sorted(TRAINER.glob("week-*/**/*.md")):
            with self.subTest(f=f.relative_to(TRAINER).as_posix()):
                self.assertEqual([], hits(f.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
