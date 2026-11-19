# D-0099 — Notes critic gains item 23, Read alone: clarity checks for a learner reading the page at home (the why behind a stated result, terms glossed at first use, the key code line and every output read back, one worked number per formula, the week read as one, words that teach nothing named as the cut); the notes word bars are unchanged

- Date: 2026-11-19
- Status: accepted
- Decision: Notes critic gains item 23, Read alone: clarity checks for a learner reading the page at home (the why behind a stated result, terms glossed at first use, the key code line and every output read back, one worked number per formula, the week read as one, words that teach nothing named as the cut); the notes word bars are unchanged
- Why: A cold read of the five week 6 pages on 2026-11-19 (one reader per page, as the D-0048 learner) found every page sufficient but with the same gaps: results stated without the reason, terms and code lines left unexplained, outputs described but not interpreted, formulas with no worked number, and passages or words repeated or reused across the days of the week because each page is authored alone. Raising metrics.notes wordMax or stepsMax was considered and rejected: the gaps are clarity gaps, each fixed by a sentence or two, and no week 6 page is near the cap (after the fixes the five pages run 5436 to 6537 words against a 7000 cap; only W6D5 got shorter, because most planned cuts were held up by a quiz item, a takeaway, a practice task or a sole citation that depended on the passage)
- Affects: harness/critics/notes.md, docs/weeks/week-06 (all five pages hand-fixed to the new item), week 7 authoring
- Supersedes: —
- Superseded-by: —

## Notes

Clarity only: the item never asks for more depth and no fix may add a fact the brief lacks (item 11). Not changed: the per-step 450-900 bar is still prose in item 10 and unenforced by notes_check.py; Closed the same day:

- The notes author prompt in harness/workflows/day-fanout.js now tells the author to read item 23 before writing (a READ ALONE line), so a first pass is written to it.
- Where a clarity fix needed a fact the brief lacked, the brief got a sourced line first (item 11): the week 6 briefs for days 1, 2 and 4 gained lines dated 2026-11-19 (how logistic regression gets from features to a class, the diabetes columns' centring and scaling, DBSCAN's three kinds of point, the lines of a plot_tree box, what MNIST is, Keras training inside a graph), each with its official URL.
- The Keras evaluate output on W6D5 was run in Colab on 2026-11-19 (TensorFlow 2.21.0, Keras 3.13.2, seed 42, same figures on a rerun) and is on the page as an output block.
- Pages said 'step N' while nothing numbered the steps: D-0100 numbers the step tags.
- The hand edits got a humanizer pass limited to the edited prose, proven prose-only with prose_guard.py snapshot and check; prose_guard.py git cannot pass on these pages because the content edits themselves add paragraphs.

Still open: no official scikit-learn page says in so many words that the class line of a plot_tree box is the node's majority class, or whether the box prints counts or proportions by default, so W6D2 says neither.
