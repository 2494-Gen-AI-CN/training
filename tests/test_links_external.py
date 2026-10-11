"""Opt-in external link check: CHECK_EXTERNAL=1 python -m unittest tests.test_links_external -v"""

from __future__ import annotations

import os
import unittest
import urllib.request

from helpers import DOCS, ParsedPage, live_days


@unittest.skipUnless(os.environ.get("CHECK_EXTERNAL") == "1", "set CHECK_EXTERNAL=1 to run")
class ExternalLinkTests(unittest.TestCase):
    def test_external_links_respond(self):
        seen = set()
        for w, d, rel in live_days():
            page = ParsedPage(DOCS / "weeks" / f"{rel}.html")
            for href in page.hrefs():
                if not href.startswith("http") or href in seen or "REPLACE_ME" in href:
                    continue
                seen.add(href)
                with self.subTest(url=href):
                    req = urllib.request.Request(href, method="HEAD", headers={"User-Agent": "Mozilla/5.0 link-check"})
                    try:
                        with urllib.request.urlopen(req, timeout=10) as r:
                            self.assertLess(r.status, 400)
                    except urllib.error.HTTPError as e:
                        if e.code in (403, 405):  # some hosts refuse HEAD; try GET
                            req = urllib.request.Request(href, headers={"User-Agent": "Mozilla/5.0 link-check"})
                            with urllib.request.urlopen(req, timeout=15) as r:
                                self.assertLess(r.status, 400)
                        else:
                            raise


if __name__ == "__main__":
    unittest.main()
