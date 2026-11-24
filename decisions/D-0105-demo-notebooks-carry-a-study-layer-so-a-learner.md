# D-0105 — Demo notebooks carry a study layer so a learner can work through them alone: study block, Predict first, Common mistake, work-it-by-hand, Before you move on, collapsed Quick check answers; piloted on W7D1, no backfill

- Date: 2026-11-23
- Status: accepted
- Decision: Demo notebooks carry a study layer so a learner can work through them alone: study block, Predict first, Common mistake, work-it-by-hand, Before you move on, collapsed Quick check answers; piloted on W7D1, no backfill
- Why: Asked 2026-11-23 what trainees lose if notebooks become self-study with office hours. The gap was in the trainer's voice, not the content: Monday's runbook holds a Predict before running question and a Trap for nearly every subsection and the backprop paper activity, none of which a learner reading the notebook alone ever sees, and no notebook carries Quick check answers. Trainees should be able to study from the notebook without the call recording. Live delivery is unchanged, so D-0101 (every Project 1 option built in a training demo) stands.
- Affects: harness/templates/notebook-style.md (Study layer section), harness/notebook_check.py (study rules, enforced when the title cell declares the layer; --study requires it), tests/test_notebooks.py, demo-repo/notebooks/week-07/01_monday_mlp_backprop_and_digit_classifier.ipynb (pilot)
- Supersedes: —
- Superseded-by: —

## Notes

Pilot first: W7D1 by hand, trainer reviews it locally before any push. W7D2 and W7D3 follow the pilot once approved. Week 6 notebooks are not backfilled. Whether the layer is required from week 8 (notebook_check --study in the release gate) is decided after the pilot. Numbers in the layer are arithmetic or already in the notebook's markdown; nothing fit-dependent was added from the runbook's locally measured figures. Rejected: full self-study with office hours only (breaks D-0101, loses the stragglers the chat checkpoints catch).
