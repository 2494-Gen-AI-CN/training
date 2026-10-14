#!/usr/bin/env python3
"""Mechanical checks for a notes page (D-0040, stdlib only). The one checker shared by the notes author, the
notes humanizer, the notes-verify agent, the notes critic, the contract tests and the drift check.

A notes page is reference/study material: 4500-7000 prose words, 6-10 section.step blocks with h3 subsections,
one "Say it in an interview" callout per teaching step, a closing "Check yourself" step, inline citations
<sup class="cite"><a href="#src-N">N</a></sup> to <li id="src-N"> in section.reading-sources, and a
"Sources checked <date>" stamp copied from the research brief. Prose never refers to the classroom
(metrics.notes.deliveryPhrases) and never claims the reader knows something from outside the course
(metrics.notes.assumptionPhrases, D-0048).

Usage (from the repo root):
  python harness/notes_check.py <page.html> [...] [--counts] [--phrases] [--stamps] [--citations] [--links] [--json]
  python harness/notes_check.py --all-live [same flags]        every status: live day of the curriculum
No flag = --counts --phrases --stamps --citations (everything but the network). The last line printed is a JSON
summary. Exit 1 on any hard finding.

Words: text inside article.reading-col, skipping <script>, <pre>, <button>, <code>, <sup> and .reading-sources
(the same walk as tests/helpers.py prose_words()). Per-step bars apply to TEACHING steps: every step but the
last one when the last one is tagged "Check yourself".
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "harness" / "metrics.json"
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
PROSE_SKIP = {"script", "pre", "button", "code", "sup"}
CHECK_TAG = "check yourself"
STEP_PHASES = ("counts", "phrases", "stamps", "citations", "links")


# ---------------------------------------------------------------- HTML tree (mirrors tests/helpers.py)
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
        raise ValueError(f"closing tag </{tag}> has no matching open tag")

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def parse_html(text: str) -> Element:
    """Parse a page into a tree; raise ValueError on unbalanced tags (a truncated page)."""
    p = _Parser()
    p.feed(text)
    p.close()
    if len(p.stack) != 1:
        raise ValueError("unclosed tags: " + ", ".join(n.tag for n in p.stack[1:]))
    return p.root


def prose_text(el: Element, skip: set[str] = PROSE_SKIP) -> str:
    """Text of an element with code, scripts, buttons, citations and the sources section left out."""
    if el.tag in skip or "reading-sources" in el.classes():
        return ""
    return "".join(prose_text(c, skip) if isinstance(c, Element) else c for c in el.children)


def inline_js(root: Element) -> str:
    return "\n".join(s.text() for s in root.find_all("script") if not s.attrs.get("src"))


def metrics() -> dict:
    return json.loads(METRICS.read_text(encoding="utf-8"))["notes"]


def brief_for(page: Path) -> Path | None:
    """docs/weeks/<rel>.html -> harness/research/<rel>.md (None when the page is not under docs/weeks)."""
    try:
        rel = page.resolve().relative_to((ROOT / "docs" / "weeks").resolve())
    except ValueError:
        return None
    return ROOT / "harness" / "research" / rel.with_suffix(".md")


# ---------------------------------------------------------------- counts
def _captions(js: str) -> int:
    m = re.search(r"captions\s*:\s*\[(.*?)\]\s*\}", js, re.S)
    if not m:
        return 0
    return len(re.findall(r'^\s*["\']', m.group(1), re.M))


def counts(text: str) -> dict:
    """Structural counts of a page. Raises ValueError when the page does not parse."""
    root = parse_html(text)
    art = root.find("article", "reading-col")
    if art is None:
        raise ValueError("no article.reading-col")
    steps = art.find_all("section", "step")
    tags = [(s.find(class_name="tag").text().strip() if s.find(class_name="tag") else "") for s in steps]
    last_is_check = bool(tags) and tags[-1].strip().lower() == CHECK_TAG
    teaching = steps[:-1] if last_is_check else steps
    js = inline_js(root)
    meta = art.find(class_name="meta")
    mins = re.search(r"~(\d+) min", meta.text() if meta else "")
    verified = re.search(r"Sources checked (\d{4}-\d{2}-\d{2})", meta.text() if meta else "")
    sources = art.find("section", "reading-sources")
    src_items = [li for li in (sources.find_all("li") if sources else []) if any(a.attrs.get("href", "").startswith("http") for a in li.find_all("a"))]
    cites_per_step = [len([a for a in s.find_all("a") if a.attrs.get("href", "").startswith("#src-") and any(p.tag == "sup" for p in _ancestors(s, a))]) for s in teaching]
    return {
        "steps": len(steps),
        "teachingSteps": len(teaching),
        "lastTag": tags[-1] if tags else "",
        "lastIsCheck": last_is_check,
        "captions": _captions(js),
        "words": len(prose_text(art).split()),
        "h3": [len(s.find_all("h3")) for s in teaching],
        "interview": [len(s.find_all("div", "interview")) for s in teaching],
        "checkDetails": len(steps[-1].find_all("details", "check")) if last_is_check else 0,
        "codeBlocks": len(art.find_all("pre")),
        "citations": cites_per_step,
        "quizQ": len(re.findall(r'\{\s*type\s*:\s*["\']', js)),
        "declaredMinutes": int(mins.group(1)) if mins else None,
        "sourcesChecked": verified.group(1) if verified else None,
        "sources": len(src_items),
        "popups": len(art.find_all("button", "code-cta")),
    }


def _ancestors(scope: Element, target: Element) -> list[Element]:
    """Elements between scope and target (inclusive of scope), or [] when target is not inside scope."""
    path: list[Element] = []

    def walk(el: Element) -> bool:
        path.append(el)
        if el is target:
            return True
        for c in el.children:
            if isinstance(c, Element) and walk(c):
                return True
        path.pop()
        return False

    return path if walk(scope) else []


def count_findings(c: dict, m: dict, tolerance: int = 0) -> list[str]:
    """Findings against metrics.notes. tolerance widens the word band (the tests allow metrics.wordTolerance;
    the author, the humanizer and the critic use the hard band)."""
    f: list[str] = []
    if not (m["stepsMin"] <= c["steps"] <= m["stepsMax"]):
        f.append(f"steps {c['steps']} outside {m['stepsMin']}..{m['stepsMax']}")
    if c["captions"] != c["steps"]:
        f.append(f"diagram captions {c['captions']} != steps {c['steps']}")
    if not (m["wordMin"] - tolerance <= c["words"] <= m["wordMax"] + tolerance):
        f.append(f"prose words {c['words']} outside {m['wordMin'] - tolerance}..{m['wordMax'] + tolerance}")
    if not c["lastIsCheck"]:
        f.append(f"last step tag is {c['lastTag']!r}, expected 'Check yourself'")
    else:
        if not (m["checkYourselfMin"] <= c["checkDetails"] <= m["checkYourselfMax"]):
            f.append(f"Check yourself has {c['checkDetails']} details.check, expected {m['checkYourselfMin']}..{m['checkYourselfMax']}")
    for i, n in enumerate(c["h3"]):
        if n < m["h3PerStepMin"]:
            f.append(f"step {i} has {n} h3, expected >= {m['h3PerStepMin']}")
    for i, n in enumerate(c["interview"]):
        if n != m["interviewPerStep"]:
            f.append(f"step {i} has {n} .callout.interview, expected {m['interviewPerStep']}")
    for i, n in enumerate(c["citations"]):
        if n < m["citationsPerStepMin"]:
            f.append(f"step {i} has {n} citations, expected >= {m['citationsPerStepMin']}")
    if c["codeBlocks"] < m["codeBlocksMin"]:
        f.append(f"{c['codeBlocks']} <pre> code blocks, expected >= {m['codeBlocksMin']}")
    if c["quizQ"] != m["quizQuestions"]:
        f.append(f"quiz has {c['quizQ']} questions, expected {m['quizQuestions']}")
    if c["sources"] < m["sourcesMin"]:
        f.append(f"{c['sources']} sources, expected >= {m['sourcesMin']}")
    want = round(c["words"] / m["readingWpm"])
    if c["declaredMinutes"] is None:
        f.append("meta line has no '~N min'")
    elif abs(c["declaredMinutes"] - want) > 1:
        f.append(f"meta says ~{c['declaredMinutes']} min, words give ~{want}")
    if not c["sourcesChecked"]:
        f.append("meta line has no 'Sources checked YYYY-MM-DD'")
    if not (m["codePopupsMin"] <= c["popups"] <= m["codePopupsMax"]):
        f.append(f"{c['popups']} code popups outside {m['codePopupsMin']}..{m['codePopupsMax']}")
    return f


# ---------------------------------------------------------------- delivery phrases
def _js_strings(js: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', js)] + [m.group(1) for m in re.finditer(r"'((?:[^'\\]|\\.)*)'", js)]


def phrase_hits(text: str, phrases: list[str]) -> list[dict]:
    """Delivery phrases in article prose, quiz strings and diagram strings; each hit with its sentence."""
    root = parse_html(text)
    art = root.find("article", "reading-col")
    sources = [("prose", prose_text(art) if art else "")]
    sources += [("inline-js", s) for s in _js_strings(inline_js(root))]
    hits = []
    for where, body in sources:
        for ph in phrases:
            for m in re.finditer(r"(?<![\w'])" + re.escape(ph) + r"(?![\w'])", body, re.I):
                start = max(body.rfind(".", 0, m.start()), body.rfind("\n", 0, m.start())) + 1
                end = body.find(".", m.end())
                sent = re.sub(r"\s+", " ", body[start:(end + 1 if end > 0 else m.end() + 80)]).strip()
                hits.append({"phrase": ph, "where": where, "sentence": sent[:200]})
    return hits


# ---------------------------------------------------------------- stamps
def brief_header(brief_text: str) -> dict:
    v = re.search(r"^verified:\s*(\d{4}-\d{2}-\d{2})", brief_text, re.M)
    stamps = {}
    block = re.search(r"^version-stamps:\s*\n((?:\s*-\s.*\n?)+)", brief_text, re.M)
    if block:
        for ln in block.group(1).splitlines():
            m = re.match(r"\s*-\s*([^:]+?):\s*(\S+)", ln)
            if m:
                stamps[m.group(1).strip().lower()] = m.group(2).strip()
    return {"verified": v.group(1) if v else None, "stamps": stamps}


def stamp_findings(text: str, brief_text: str) -> list[str]:
    root = parse_html(text)
    meta = root.find(class_name="meta")
    span = meta.find("span", "verified") if meta else None
    if span is None:
        return ["no .meta span.verified ('Sources checked <date> · lib ver')"]
    hdr = brief_header(brief_text)
    f = []
    m = re.search(r"Sources checked (\d{4}-\d{2}-\d{2})", span.text())
    if not m:
        f.append("span.verified has no 'Sources checked YYYY-MM-DD'")
    elif hdr["verified"] and m.group(1) != hdr["verified"]:
        f.append(f"page says Sources checked {m.group(1)}, brief says verified: {hdr['verified']}")
    for part in span.text().split("·")[1:]:
        p = part.strip()
        pm = re.match(r"([A-Za-z][\w .+-]*?)\s+([\w.+-]+)$", p)
        if not pm:
            f.append(f"stamp {p!r} is not '<lib> <version>'")
            continue
        lib, ver = pm.group(1).strip().lower(), pm.group(2)
        got = hdr["stamps"].get(lib)
        if got is None:
            f.append(f"stamp {p!r}: {lib} is not in the brief's version-stamps")
        elif not got.startswith(ver) and not ver.startswith(got):
            f.append(f"stamp {p!r}: brief says {lib} {got}")
    return f


# ---------------------------------------------------------------- citations
def _urls(s: str) -> set[str]:
    return {u.rstrip("/.,)") for u in re.findall(r"https?://[^\s)>\]\"']+", s)}


def _norm_url(u: str) -> str:
    return u.split("#", 1)[0].rstrip("/")


def citation_report(text: str, brief_text: str | None) -> dict:
    root = parse_html(text)
    art = root.find("article", "reading-col")
    sources = art.find("section", "reading-sources") if art else None
    ids = {li.attrs.get("id") for li in (sources.find_all("li") if sources else []) if li.attrs.get("id")}
    unresolved = []
    for sup in (art.find_all("sup", "cite") if art else []):
        for a in sup.find_all("a"):
            tgt = a.attrs.get("href", "")
            if not tgt.startswith("#src-") or tgt[1:] not in ids:
                unresolved.append(tgt)
    page_urls = [a.attrs["href"] for li in (sources.find_all("li") if sources else []) for a in li.find_all("a") if a.attrs.get("href", "").startswith("http")]
    not_in_brief = []
    if brief_text is not None:
        brief_urls = {_norm_url(u) for u in _urls(brief_text)}
        not_in_brief = [u for u in page_urls if _norm_url(u) not in brief_urls]
    return {"sourceIds": len(ids), "unresolved": unresolved, "sourceUrls": page_urls, "notInBrief": not_in_brief}


def citation_findings(r: dict) -> list[str]:
    f = [f"citation target {t!r} has no li#src-N" for t in r["unresolved"]]
    f += [f"source URL not in the brief: {u}" for u in r["notInBrief"]]
    return f


# ---------------------------------------------------------------- links (network)
def check_url(href: str, timeout: int = 10) -> str | None:
    """None when the URL answers with a status < 400 (HEAD, then GET on 403/405); else the reason."""
    hdrs = {"User-Agent": "Mozilla/5.0 link-check"}
    try:
        with urllib.request.urlopen(urllib.request.Request(href, method="HEAD", headers=hdrs), timeout=timeout) as r:
            return None if r.status < 400 else f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        if e.code not in (403, 405):
            return f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 - any network failure is a dead link for this purpose
        return e.__class__.__name__
    try:
        with urllib.request.urlopen(urllib.request.Request(href, headers=hdrs), timeout=timeout + 5) as r:
            return None if r.status < 400 else f"HTTP {r.status}"
    except Exception as e:  # noqa: BLE001
        return f"HTTP {e.code}" if isinstance(e, urllib.error.HTTPError) else e.__class__.__name__


def page_links(text: str) -> list[str]:
    """The page's own http links: everything inside article.reading-col (prose links and the Sources list).
    Topbar and modal links come from config.json (repo tree URLs that exist only once a day is published) and
    are not citations, so liveness is not judged on them."""
    root = parse_html(text)
    art = root.find("article", "reading-col") or root
    seen, out = set(), []
    for a in art.find_all("a"):
        h = a.attrs.get("href", "")
        if h.startswith("http") and h not in seen and "REPLACE_ME" not in h:
            seen.add(h)
            out.append(h)
    return out


def dead_links(text: str) -> list[dict]:
    out = []
    for h in page_links(text):
        why = check_url(h)
        if why:
            out.append({"url": h, "why": why})
    return out


# ---------------------------------------------------------------- driver
def live_pages() -> list[Path]:
    cur = json.loads((ROOT / "harness" / "curriculum.json").read_text(encoding="utf-8"))
    out = []
    for w in cur["weeks"]:
        for d in w["days"]:
            if d.get("kind") != "holiday" and d.get("status") == "live":
                out.append(ROOT / "docs" / "weeks" / w["dir"] / f"{d['slug']}.html")
    return out


def check_page(page: Path, phases: set[str], m: dict | None = None, tolerance: int = 0) -> dict:
    m = m or metrics()
    text = page.read_text(encoding="utf-8")
    brief = brief_for(page)
    brief_text = brief.read_text(encoding="utf-8") if brief and brief.is_file() else None
    rep: dict = {"page": page.as_posix(), "findings": []}
    try:
        if "counts" in phases:
            rep["counts"] = counts(text)
            rep["findings"] += count_findings(rep["counts"], m, tolerance)
        if "phrases" in phases:
            rep["phrases"] = phrase_hits(text, m.get("deliveryPhrases", []))
            rep["findings"] += [f"delivery phrase {h['phrase']!r} in {h['where']}: {h['sentence']}" for h in rep["phrases"]]
            rep["assumptions"] = phrase_hits(text, m.get("assumptionPhrases", []))
            rep["findings"] += [f"assumption phrase {h['phrase']!r} in {h['where']}: {h['sentence']}" for h in rep["assumptions"]]
        if "stamps" in phases:
            rep["findings"] += stamp_findings(text, brief_text) if brief_text is not None else ["no research brief for this page (stamps not checked)"]
        if "citations" in phases:
            rep["citations"] = citation_report(text, brief_text)
            rep["findings"] += citation_findings(rep["citations"])
        if "links" in phases:
            rep["dead"] = dead_links(text)
            rep["findings"] += [f"dead link {d['url']} ({d['why']})" for d in rep["dead"]]
    except ValueError as exc:
        rep["findings"].append(f"page does not parse: {exc}")
    return rep


def main(argv: list[str]) -> int:
    flags = {a for a in argv if a.startswith("--")}
    files = [a for a in argv if not a.startswith("--")]
    phases = {p for p in STEP_PHASES if f"--{p}" in flags} or {"counts", "phrases", "stamps", "citations"}
    if "--all-live" in flags:
        files += [p.as_posix() for p in live_pages()]
    if not files:
        print(__doc__)
        return 2
    reports = [check_page(Path(f), phases) for f in files]
    bad = any(r["findings"] for r in reports)
    if "--json" not in flags:
        for r in reports:
            print(("FAIL " if r["findings"] else "OK ") + r["page"])
            for line in r["findings"]:
                print("  " + line)
            if "counts" in r:
                c = r["counts"]
                print(f"  steps {c['steps']} captions {c['captions']} words {c['words']} h3 {c['h3']} interview {c['interview']} "
                      f"check {c['checkDetails']} code {c['codeBlocks']} cites {c['citations']} quizQ {c['quizQ']} sources {c['sources']} ~{c['declaredMinutes']} min")
    print(json.dumps({"ok": not bad, "pages": [{"page": r["page"], "findings": len(r["findings"]), **({"counts": r["counts"]} if "counts" in r else {})} for r in reports]}, ensure_ascii=False))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
