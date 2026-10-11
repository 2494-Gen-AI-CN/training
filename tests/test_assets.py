"""Site asset hygiene: allowed JS set, no reference-site leaks, index links resolve."""

from __future__ import annotations

import unittest

from helpers import ALLOWED_JS, DOCS, FORBIDDEN_RE, ParsedPage


class AssetTests(unittest.TestCase):
    def test_js_set_is_exactly_allowed(self):
        names = {p.name for p in (DOCS / "assets" / "js").glob("*.js")}
        self.assertEqual(ALLOWED_JS, names)

    def test_no_reference_site_leaks_anywhere_in_docs(self):
        for p in DOCS.rglob("*"):
            if p.is_file() and p.suffix in (".html", ".js", ".css", ".sh", ".md"):
                text = p.read_text(encoding="utf-8", errors="replace")
                m = FORBIDDEN_RE.search(text)
                self.assertIsNone(m, f"{p.relative_to(DOCS)}: leaked '{m.group(0) if m else ''}'")

    def test_required_files(self):
        for rel in (".nojekyll", "index.html", "bump-css.sh", "assets/css/style.css", "assets/favicon.svg"):
            self.assertTrue((DOCS / rel).exists(), rel)

    def test_index_parses_and_relative_links_resolve(self):
        page = ParsedPage(DOCS / "index.html")
        self.assertIn("theme.js", page.script_srcs)
        for href in page.hrefs():
            if href.startswith(("http", "#", "mailto:")):
                continue
            target = (DOCS / href.split("?")[0]).resolve()
            self.assertTrue(target.exists(), f"index.html broken link {href}")


if __name__ == "__main__":
    unittest.main()
