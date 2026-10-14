"""Shared helpers for the contract tests (stdlib only)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HARNESS = ROOT / "harness"
TRAINER = ROOT / "trainer"
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

# Strings that only exist in the reference site / its backend. Any hit in docs/ is a leak.
FORBIDDEN_RE = re.compile(
    r"FDE_|fde_|fde-|roster\.js|progress\.js|day-summary|auth\.js|reading-coach|coding-coach|codex-usage|"
    r"usage-notice|learning-chrome|interactive-rag|interactive-agents|gauntlet|workers\.dev|jestercharles|2463",
)
ALLOWED_JS = {"theme.js", "diagram.js", "scrolly.js", "modals.js", "quiz.js", "widgets.js", "glossary.js", "codeviewer.js", "survey.js", "pyworker.js"}
PAGE_SCRIPT_ORDER = ["diagram.js", "scrolly.js", "modals.js", "quiz.js", "widgets.js", "glossary.js", "codeviewer.js"]
SECRET_RE = re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def curriculum() -> dict:
    return load_json(HARNESS / "curriculum.json")


def metrics() -> dict:
    return load_json(HARNESS / "metrics.json")


def all_slots():
    """Yield (week, slot) for every weekday slot, holidays included."""
    for w in curriculum()["weeks"]:
        for d in w["days"]:
            yield w, d


def all_days():
    """Yield (week, day, rel) for every teaching day (holiday slots have no slug)."""
    for w, d in all_slots():
        if d.get("kind") != "holiday":
            yield w, d, f"{w['dir']}/{d['slug']}"


def live_days():
    """Days linked from the index (status live). Visibility tests use this."""
    for w, d, rel in all_days():
        if d.get("status") == "live":
            yield w, d, rel


def authored_days():
    """Days whose artifacts all exist (status authored or live, D-0052). Artifact-contract tests use this."""
    for w, d, rel in all_days():
        if d.get("status") in ("authored", "live"):
            yield w, d, rel


def trainer_demos(rel: str) -> Path:
    """Where a day's demo scripts + key/ are authored (private trainer repo, D-0030)."""
    return TRAINER / rel / "demos"


def public_demos(rel: str) -> Path:
    """Where a day's answer keys land once the day is taught (publish_demos.py, D-0030)."""
    return ROOT / "demos" / rel


def node_exe() -> str | None:
    found = shutil.which("node")
    if found:
        return found
    for cand in (r"C:\Program Files\nodejs\node.exe", "/usr/local/bin/node", "/usr/bin/node"):
        if Path(cand).exists():
            return cand
    return None


def run_node(script: str, stdin: str = "") -> str:
    exe = node_exe()
    if not exe:
        raise RuntimeError("node not found")
    res = subprocess.run([exe, "-e", script], input=stdin, text=True, capture_output=True, check=True, encoding="utf-8")
    return res.stdout


class Element:
    def __init__(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tag = tag
        self.attrs = dict(attrs)
        self.children: list[Element | str] = []

    def classes(self) -> set[str]:
        return set((self.attrs.get("class") or "").split())

    def find_all(self, tag: str | None = None, class_name: str | None = None, **attr_eq) -> list["Element"]:
        out = []
        if (tag is None or self.tag == tag) and (class_name is None or class_name in self.classes()) \
                and all(self.attrs.get(k.replace("_", "-")) == v for k, v in attr_eq.items()):
            out.append(self)
        for c in self.children:
            if isinstance(c, Element):
                out.extend(c.find_all(tag, class_name, **attr_eq))
        return out

    def find(self, *a, **k) -> "Element | None":
        r = self.find_all(*a, **k)
        return r[0] if r else None

    def text(self) -> str:
        return "".join(c.text() if isinstance(c, Element) else c for c in self.children)


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Element("document", [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
        raise AssertionError(f"closing tag </{tag}> has no matching open tag")

    def handle_data(self, data):
        self.stack[-1].children.append(data)


class ParsedPage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.raw = path.read_text(encoding="utf-8")
        p = _Parser()
        p.feed(self.raw)
        p.close()
        if len(p.stack) != 1:
            raise AssertionError(f"unclosed tags in {path}: {[n.tag for n in p.stack[1:]]}")
        self.root = p.root

    @property
    def embedded_js(self) -> str:
        return "\n".join(s.text() for s in self.root.find_all("script") if not s.attrs.get("src"))

    @property
    def script_srcs(self) -> list[str]:
        return [s.attrs["src"].split("?")[0].rsplit("/", 1)[-1] for s in self.root.find_all("script") if s.attrs.get("src")]

    @property
    def meta(self) -> dict:
        return {m.attrs.get("name"): m.attrs.get("content") for m in self.root.find_all("meta") if m.attrs.get("name")}

    def hrefs(self) -> list[str]:
        out = []
        for a in self.root.find_all("a"):
            if a.attrs.get("href"):
                out.append(a.attrs["href"])
        for l in self.root.find_all("link"):
            if l.attrs.get("href"):
                out.append(l.attrs["href"])
        for s in self.root.find_all("script"):
            if s.attrs.get("src"):
                out.append(s.attrs["src"])
        return out

    def prose_words(self) -> int:
        art = self.root.find("article", "reading-col")
        if not art:
            return 0
        skip_tags = {"script", "pre", "button", "code", "sup"}   # sup = citation markers (D-0040); same walk as harness/notes_check.py

        def walk(el: Element) -> str:
            if el.tag in skip_tags or "reading-sources" in el.classes():
                return ""
            return "".join(walk(c) if isinstance(c, Element) else c for c in el.children)

        return len(walk(art).split())

    def probe(self) -> dict:
        """Evaluate inline window.DIAGRAM / QUIZ / NEXT in node and return a summary."""
        script = r"""
const vm = require('vm');
let src = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => src += c);
process.stdin.on('end', () => {
  const sb = { window: {} };
  vm.runInNewContext(src, sb, { filename: 'page-inline.js' });
  const D = sb.window.DIAGRAM || {}, Q = sb.window.QUIZ || {}, N = sb.window.NEXT || {};
  const qs = Q.questions || [];
  process.stdout.write(JSON.stringify({
    captions: (D.captions || []).length,
    nodes: (D.nodes || []).length,
    nodeIds: (D.nodes || []).map(n => n.id),
    edgesOk: (D.edges || []).every(e => (D.nodes || []).some(n => n.id === e.from) && (D.nodes || []).some(n => n.id === e.to)),
    nodesOk: (D.nodes || []).every(n => ['x','y','w','h','label'].every(k => k in n) && typeof n.step === 'number'),
    questions: qs.length,
    types: qs.map(q => q.type || 'scq'),
    answersOk: qs.every(q => q.type === 'open' ? !!q.model : q.type === 'tf' ? typeof q.answer === 'boolean' : q.type === 'match' ? Array.isArray(q.pairs) && q.pairs.length >= 3 : q.type === 'mcq' ? Array.isArray(q.answer) && q.answer.every(i => i >= 0 && i < q.options.length) : typeof q.answer === 'number' && q.answer >= 0 && q.answer < (q.options || []).length),
    explainsOk: qs.every(q => q.type === 'open' || !!q.explain),
    next: N.href || null, nextLabel: N.label || null
  }));
});
"""
        return json.loads(run_node(script, self.embedded_js))
