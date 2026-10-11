# D-0022 — Notes pages render code Markdown-style: inline <code> as a chip, multi-command sequences as <pre><code> blocks; authors put any 2+ command sequence in a block, never inline in a sentence

- Date: 2026-10-11
- Status: accepted
- Decision: Notes pages render code Markdown-style: inline <code> as a chip, multi-command sequences as <pre><code> blocks; authors put any 2+ command sequence in a block, never inline in a sentence
- Why: The pilot page inlined every git command in running prose (64 inline code tags, zero blocks) and the chip style existed only under .prose, which notes pages do not use, so commands read as plain monospace text. Trainer asked for the boxed look Markdown gives.
- Affects: docs/assets/css/style.css (.reading-col code/pre), harness/templates/day.exemplar.html (fenced-block example), harness/workflows/day-fanout.js notes author prompt, docs/weeks/week-01/day-2-orientation-agile-and-git.html (retrofit)
- Supersedes: —
- Superseded-by: —

## Notes

Word-count tooling already skips pre and code (tests/helpers.py, critic snippet), so blocks do not count toward the 1200-1800 band.
