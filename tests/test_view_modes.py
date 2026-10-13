"""Page views (D-0044): theme.js and style.css agree on the views, and the view rules never reach print."""

from __future__ import annotations

import re
import unittest

from helpers import DOCS, HARNESS

VIEWS = ("compact", "focus")   # Full is the absence of html[data-view]


def _top_level_blocks(css: str):
    """Yield (prelude, body) for each top-level block of a stylesheet, comments removed."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    depth, start, prelude, body_start = 0, 0, "", 0
    for i, ch in enumerate(css):
        if ch == "{":
            if depth == 0:
                prelude, body_start = css[start:i].rsplit(";", 1)[-1].strip(), i + 1
            depth += 1
        elif ch == "}":
            if depth == 1:
                yield prelude, css[body_start:i]
            depth = max(depth - 1, 0)   # the stylesheet carries a stray closing brace; do not let it skew what follows
            if depth == 0:
                start = i + 1


class ViewModeTests(unittest.TestCase):
    def setUp(self):
        self.css = (DOCS / "assets" / "css" / "style.css").read_text(encoding="utf-8")
        self.js = (DOCS / "assets" / "js" / "theme.js").read_text(encoding="utf-8")

    def test_script_and_stylesheet_name_the_same_views(self):
        self.assertIn('"tc_view"', self.js, "the view is kept in localStorage under tc_view")
        for view in VIEWS:
            self.assertIn(f'"{view}"', self.js, f"theme.js does not offer the {view} view")
            self.assertIn(f'html[data-view="{view}"]', self.css, f"style.css has no rule for the {view} view")
        named = set(re.findall(r'html\[data-view="([a-z]+)"\]', self.css))
        self.assertEqual(set(VIEWS), named, "style.css styles a view theme.js never sets")

    def test_view_rules_are_screen_only(self):
        """Print keeps the full reading layout whatever view the reader was in."""
        seen = 0
        for prelude, body in _top_level_blocks(self.css):
            if "html[data-view" in prelude or "html[data-view" in body:
                seen += 1
                self.assertTrue(prelude.startswith("@media screen"), f"view rule outside @media screen: {prelude[:80]!r}")
        self.assertGreater(seen, 0)

    def test_default_view_is_one_the_script_offers(self):
        default = re.search(r'var DEFAULT_VIEW = "([a-z]+)";', self.js)
        self.assertIsNotNone(default, "theme.js names the view a first-time reader gets")
        self.assertIn(default.group(1), VIEWS + ("full",))

    def test_no_page_ships_with_a_view_set(self):
        """The attribute is only ever set by theme.js: the reader's own choice, or the default for a first visit."""
        pages = list(DOCS.rglob("*.html")) + [HARNESS / "templates" / "day.exemplar.html"]
        for p in pages:
            self.assertNotRegex(p.read_text(encoding="utf-8"), r"<html[^>]*\bdata-view", p.name)

    def test_cache_buster_covers_theme_js(self):
        """theme.js and style.css change together for a view, so --all has to bump both."""
        sh = (DOCS / "bump-css.sh").read_text(encoding="utf-8")
        assets = re.search(r"--all\) ASSETS=\(([^)]*)\)", sh).group(1).split()
        self.assertIn("theme.js", assets)
        self.assertIn("style.css", assets)


if __name__ == "__main__":
    unittest.main()
