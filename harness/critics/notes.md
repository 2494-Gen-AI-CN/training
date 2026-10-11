# Notes-page critic — PASS criteria

You are judging `docs/weeks/<week>/<day>.html`. You are NOT the author. Read the page, the research brief (allowed facts), `harness/templates/day.exemplar.html` (structure gold standard) and `harness/metrics.json`. Use Bash + Python to count, do not estimate. Return `pass=false` with specific critiques if ANY item fails.

## Structure (must match the exemplar)

1. `<meta name="tc-day" content="<id>">` present; `<title>` ends with the site title.
2. Topbar: brand, Home, Demos, Exercises links (relative paths `../../index.html`, config repo URL).
3. `main.lesson2 > .reading2col` with `nav.toc`, `article.reading-col`, `aside.side`.
4. `.lede` has `h1`, `.meta` with "Week W · Day D", the week theme, and "~N min" where N == round(prose words / 150).
5. `section.step` count within `metrics.notes.stepsMin..stepsMax` (5–7); `data-step` values are 0..n-1 in order; each has a `.tag` and an `h2`.
6. `section.reading-sources` present with ≥ `metrics.notes.sourcesMin` (3) `http` links, all taken from the research brief.
7. Aside: `.side-diagram` with `svg#diagram` + `.stage-caption`; `.side-cards` containing a `.demo-card` (links to ≥1 real file under `demos/<week>/<day>/` via the config repo URL, filenames exactly as on disk), a quiz `.activity-card[data-modal="quiz-modal"]`, optional deep-dive card; `.side-nav` with Back, Daily goals, and an empty `a.snav-next`.
8. Modals: `#quiz-modal` (with `section#quiz` + `.modal-next`), `#goals-modal` (3–5 `.goals-list` items + "Today's exercise" link to the exercise README + "Demo files in order" list), optional `#deep-modal`, 0–2 `#code-*` popups.
9. Script tags, in order: `theme.js` in head; at the bottom exactly `diagram.js, scrolly.js, modals.js, quiz.js, widgets.js, glossary.js, codeviewer.js` (+ `survey.js` only on `feedback: true` days). No other scripts. No `FDE_`, `roster`, `progress.js`, `day-summary`, `auth.js`, `workers.dev`, `2463` anywhere.

## Content

10. Prose word count (text inside `.reading-col` excluding `.reading-sources`, code and buttons) within `wordMin..wordMax` from args (default 1,200–1,800).
11. Every factual claim traces to the research brief. Flag invented numbers, versions, API names.
12. The page teaches THIS day's subtopics; it references the demo files by name where the reader should go run them.
13. `window.DIAGRAM` present: `captions.length == step count`; every node has `step, x, y, w, h, label`; edges reference existing node ids; each step reveals something that matters for that section (not decoration).
14. `window.QUIZ.questions.length == 6`; type mix ≥1 `scq`, ≥1 `tf`, ≥1 `mcq` or `match`, ≤1 `open`; `answer` indices in range; every `explain` present; questions test the brief's content.
15. `window.NEXT = { label, href }` points to the next day's page (or `../../index.html` after day 5).
16. Code popups (if any): `button.code-cta[data-modal="code-<x>"]` + matching `#code-<x>.modal-overlay .code-modal` with `.cv[data-file]` naming a REAL demo file; the `<pre class="cv-raw">` content is an excerpt of that file (HTML-escaped `< > &`).
17. Widgets allowed: `.ix-legend`, `.ix-predict`, `.ix-spot` only.
18. Prose reads like a person wrote it (D-0029; the `humanizer` skill's pattern list is the reference). FAIL on any of these in `.reading-col` prose, quiz `explain` text or diagram captions: "not X but Y" / "not just X, it's Y" contrasts; one-line closers that restate the paragraph ("That is the point."); forced triads where the meaning does not ask for three; em-dashes used as the default joiner (more than ~2 per section); bold labels at the start of list items or paragraphs; stock AI words (delve, crucial, robust, seamless, leverage, landscape, tapestry, navigate, journey, foster, testament, underscore, vibrant). Quote the offending sentence and give the plain rewrite. Facts, code, inline code, paths and link targets are out of scope for this item.

Verification snippet (run it):
```
python - <<'PY'
import re,sys,html
from pathlib import Path
p=Path(sys.argv[1] if len(sys.argv)>1 else 'PAGE'); s=p.read_text(encoding='utf-8')
steps=len(re.findall(r'<section class="step"',s)); caps=len(re.findall(r'^\s*"',re.search(r'captions:\s*\[(.*?)\]\s*\}',s,re.S).group(1),re.M)) if 'captions' in s else 0
body=re.search(r'<article class="reading-col">(.*?)<section class="reading-sources"',s,re.S).group(1)
body=re.sub(r'<(script|pre|button)[^>]*>.*?</\1>','',body,flags=re.S); words=len(html.unescape(re.sub(r'<[^>]+>',' ',body)).split())
print('steps',steps,'captions',caps,'words',words,'quizQ',len(re.findall(r'\{\s*type:\s*"',s)))
PY
```

Return a one-sentence summary plus critiques as concrete fixes.
