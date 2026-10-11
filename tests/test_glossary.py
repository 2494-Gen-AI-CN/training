"""glossary.js: loads, exposes window.GLOSSARY, no duplicate surface forms."""

from __future__ import annotations

import json
import unittest

from helpers import DOCS, node_exe, run_node


@unittest.skipUnless(node_exe(), "node not available")
class GlossaryTests(unittest.TestCase):
    def test_no_duplicate_terms_or_aliases(self):
        src = (DOCS / "assets" / "js" / "glossary.js").read_text(encoding="utf-8")
        script = r"""
const vm = require('vm');
let src=''; process.stdin.setEncoding('utf8'); process.stdin.on('data', c => src += c);
process.stdin.on('end', () => {
  const window = {}; const document = { readyState: 'complete', addEventListener(){}, querySelector(){ return null; } };
  vm.runInNewContext(src, { window, document, getComputedStyle(){ return {display:'none'}; }, NodeFilter:{} }, { filename:'glossary.js' });
  process.stdout.write(JSON.stringify(window.GLOSSARY || null));
});
"""
        data = json.loads(run_node(script, src))
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 10)
        seen = {}
        for e in data:
            self.assertTrue(e.get("term") and e.get("def"), e)
            self.assertTrue(e["def"].strip().endswith("."), f"definition should be a sentence: {e['term']}")
            for form in [e["term"]] + list(e.get("aka") or []):
                k = form.lower()
                self.assertNotIn(k, seen, f"duplicate glossary form '{form}' (also in '{seen.get(k)}')")
                seen[k] = e["term"]
        self.assertIn("// GLOSSARY:BEGIN", src)
        self.assertIn("// GLOSSARY:END", src)


if __name__ == "__main__":
    unittest.main()
