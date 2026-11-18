# D-0091 — Week 7 keeps TFLearn as history only: every TFLearn-named subtopic is taught in Keras / TensorFlow 2, confirming D-0012 after a check of TFLearn's status

- Date: 2026-11-18
- Status: accepted
- Decision: Week 7 keeps TFLearn as history only: every TFLearn-named subtopic is taught in Keras / TensorFlow 2, confirming D-0012 after a check of TFLearn's status
- Why: Checked 2026-11-18 against primary sources. TFLearn's last release is 0.5.0 (2020-11-11, PyPI) and the last commit on its master branch is 2020-11-30. Colab ships TensorFlow 2.21.0 and Keras 3.13.2 (googlecolab/backend-info pip-freeze.txt). TFLearn does not import there: tflearn/layers/recurrent.py imports is_sequence from tensorflow.python.util.nest, which TensorFlow 2.21 no longer defines (tflearn issue 1188, fix PR 1189 unmerged), and its __init__.py calls tf.disable_v2_behavior(), which would switch eager mode off for every Keras cell in the same runtime. The import failure was read from source, not run; Tuesday's research brief confirms it in a scratch Colab. Revature's published exit criteria (qc-1 to qc-3) never name TFLearn and qc-4 is not published. Both earlier cohorts (260629-AI-Engineer-Cognizant/notes-and-demos, AICogEngineer) taught Keras throughout; the only by-name assessment found is the interview-prep question 'What is TFlearn?'. Project 1 is Keras.
- Affects: harness/plans/week-07.md (TFLearn as history row pins the verified status; w07d2 TFLearn API facilitation 20 to 10 minutes with the 10 moved to sprint / project work; w07d2 section 3.1 and the Quick check answer 'What is TFLearn, and what would you use today?'; room wording brought to D-0090), AGENTS.md sharp edges, w07d2 and w07d3 research briefs
- Supersedes: —
- Superseded-by: —

## Notes

Rejected: a real TFLearn cell beside the Keras one (needs pip install, a patched source file and its own runtime, for nothing assessable) and teaching TFLearn as named (not importable; would displace the Keras topics Project 1 needs). A Keras-first week keeps a trained CNN section cheap if O-30 adds one.
