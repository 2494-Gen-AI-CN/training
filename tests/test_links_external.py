"""Opt-in external link check: CHECK_EXTERNAL=1 python -m unittest tests.test_links_external -v

The notes critic runs the same check on every pass through harness/notes_check.py --links (D-0040); this test
re-runs it over every live page by hand or in the drift check."""

from __future__ import annotations

import os
import sys
import unittest

from helpers import DOCS, HARNESS, live_days

sys.path.insert(0, str(HARNESS))
import notes_check  # noqa: E402


@unittest.skipUnless(os.environ.get("CHECK_EXTERNAL") == "1", "set CHECK_EXTERNAL=1 to run")
class ExternalLinkTests(unittest.TestCase):
    def test_external_links_respond(self):
        seen: dict[str, str | None] = {}
        for w, d, rel in live_days():
            text = (DOCS / "weeks" / f"{rel}.html").read_text(encoding="utf-8")
            for href in notes_check.page_links(text):
                if href not in seen:
                    seen[href] = notes_check.check_url(href)
                with self.subTest(url=href, page=rel):
                    self.assertIsNone(seen[href], f"{href}: {seen[href]}")


if __name__ == "__main__":
    unittest.main()
