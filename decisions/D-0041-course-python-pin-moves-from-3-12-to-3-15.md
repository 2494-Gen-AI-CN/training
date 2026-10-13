# D-0041 — Course Python pin moves from 3.12 to 3.15 (config.json python); week-1 pages, briefs, plan and templates restamped by hand

- Date: 2026-10-13
- Status: accepted
- Decision: Course Python pin moves from 3.12 to 3.15 (config.json python); week-1 pages, briefs, plan and templates restamped by hand
- Why: Trainer decision 2026-10-13. The 3.12 pin was a scaffold default (commit 3ebdbf6) with no recorded reason; 3.15.0 is the current stable release (2026-10-09) and the version docs.python.org/3/ documents.
- Affects: harness/config.json python; harness/critics/research.md item 12 example; harness/templates (day.exemplar.html, week-plan.md); harness/plans/week-01.md; harness/research/week-01 briefs; docs/weeks/week-01 pages; README.md; tests/test_notes_check.py; trainer week-1 runbooks and demo scripts (D3-D5 setup lines)
- Supersedes: —
- Superseded-by: —

## Notes

Revisit (O-16): 3.15.0 is four days old. Nothing in weeks 1-2 needs a third-party wheel beyond pytest, but later weeks do (MySQL connector wk 3, BigQuery client wk 4, anthropic wk 5, pandas/numpy/scikit-learn wk 6, TensorFlow/Keras wk 7, Chroma/Pinecone wk 8, boto3 and LangChain/LangGraph wk 9-10, SageMaker wk 11). Wheel support for 3.15 was not checked. If a required library has no 3.15 wheel when its week is researched, supersede this entry with the newest version every library supports. Verified on 3.15.0 on the trainer machine: the 12 week-1 answer keys run clean with warnings as errors; the is-with-literal SyntaxWarning text and the cpython-315 cache tag match the notes pages. Not re-recorded: the W1D2 tooling-check transcript (recorded on python 3.12.10, delivered 2026-10-13 against 3.12).
