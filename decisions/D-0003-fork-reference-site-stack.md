# D-0003 — Fork the reference site HTML/JS stack (style.css, quiz, diagram, scrolly, modals, glossary, codeviewer); strip everything backend-coupled

- Date: 2026-10-11
- Status: accepted
- Decision: Fork the reference site HTML/JS stack (style.css, quiz, diagram, scrolly, modals, glossary, codeviewer); strip everything backend-coupled
- Why: Zero build step, proven UI. The reference 2463 site's Cloudflare Worker features (LLM proxy, AI grading, progress sync, dashboard) do not fit an in-person cohort with no backend.
- Affects: docs/assets/, harness/templates/day.exemplar.html, tests/test_assets.py
- Supersedes: —
- Superseded-by: —

## Notes

Any FDE_, workers.dev or 2463 string in docs/ is a leak and fails tests/test_assets.py. Walkthrough section 1 (Site stack) and section 8.
