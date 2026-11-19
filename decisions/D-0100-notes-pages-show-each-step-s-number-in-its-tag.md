# D-0100 — Notes pages show each step's number in its tag (Step 4 · Mechanics), drawn by a CSS counter over section.step in page order, so the prose's 'step N' references have something to point at

- Date: 2026-11-19
- Status: accepted
- Decision: Notes pages show each step's number in its tag (Step 4 · Mechanics), drawn by a CSS counter over section.step in page order, so the prose's 'step N' references have something to point at
- Why: The 2026-11-19 cold read of week 6 (D-0099) found pages say 'step 4 explains' while nothing on the page numbers the steps: h2s, tags and the TOC are unnumbered. 76 such references across 13 live pages were checked by script and every one matches the 1-based section.step order, so numbering the tag fixes all of them without touching page prose. A counter in style.css needs no page markup, no author-prompt change and no JS; the practice section is not a step and is not counted
- Affects: docs/assets/css/style.css, every notes page (display only), ?v= cache-buster bumped to 20261119
- Supersedes: —
- Superseded-by: —
