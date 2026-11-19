# D-0098 — A notebook day's notes page links its notebook in Colab: one span.notebook in the lede meta, the only place the page names the notebook

- Date: 2026-11-19
- Status: accepted
- Decision: A notebook day's notes page links its notebook in Colab: one span.notebook in the lede meta, the only place the page names the notebook
- Why: The trainer asked on 2026-11-19 for the runbooks' Colab links on the notes pages of the days they belong to. Learners study from the site at home, and the notebook is the day's hand-out; without the link they rebuild the path through File > Open notebook > GitHub.
- Affects: docs/weeks/week-06 (five pages, link added by hand), harness/templates/day.exemplar.html, harness/critics/notes.md (item 22), harness/workflows/day-fanout.js (notes author and critic prompts), tests/test_pages.py, AGENTS.md, every notebook day authored from week 7
- Supersedes: —
- Superseded-by: —

## Notes

Amends D-0085 and D-0055 for notebook days only: the page still carries no demo card, list or popup and its prose still names no notebook and does not describe the session; the one addition is <span class="notebook"><a href="<colab url>" target="_blank" rel="noopener">Open the notebook in Colab</a></span> in .lede .meta. Same URL as D-0097, built from config.json demoRepo and the day's notebook path. Walkthrough and concept days carry no such span.
