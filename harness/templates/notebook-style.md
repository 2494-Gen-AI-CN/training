# Demo notebook style (D-0085)

One page for whoever writes a `demoFormat: notebook` day's notebook. The reference is the substitute trainer's
`demo-repo/notebooks/week-06/02_tuesday_trees_and_clustering.ipynb`: when this page and that file disagree, the file
wins. `python harness/notebook_check.py <file or folder>` checks the format; it does not run the notebook.

## Where it lives

- Demo repo (`config.json` `demoRepo`, cloned at `demo-repo/`), branch `main`, `notebooks/week-WW/NN_<weekday>_<slug>.ipynb`:
  `NN` is the weekday slot (`01` Monday .. `05` Friday), the weekday is lowercase English, the slug is lowercase words
  joined by underscores (`02_tuesday_trees_and_clustering.ipynb`).
- One notebook per notebook day. No prep branch and no walkthrough: the trainer runs this file in front of the room.

## Runtime

- Google Colab, opened from the demo repo on GitHub (File > Open notebook > GitHub). Every learner has a Google
  account from week 4.
- Colab's own Python and preinstalled packages: numpy, scipy, scikit-learn, matplotlib, TensorFlow/Keras. Never
  `!pip install` them. The course Python (3.15) is not the runtime; the research brief stamps Colab's versions.
- No files to upload, no API key, no Drive mount. Data comes from `sklearn.datasets` (or `tf.keras.datasets` on the
  TensorFlow days), so the notebook runs top to bottom on a fresh runtime.

## Structure

1. **Title cell** (markdown): `# <Week · Day>: <topic>`, one line linking to yesterday ("Yesterday's models drew one
   line or one curve. Today:"), a numbered agenda that matches the `##` sections, and one line telling the room to
   run the next cell first.
2. **Setup cell** (code, second cell): headed `# ---------- Setup and plotting helpers (run once; no need to read live) ----------`.
   It holds the imports used all day, `RANDOM_STATE = 42` and `np.random.seed(RANDOM_STATE)`, and the plotting
   helpers (scatter by label, decision boundary, line chart) with one-line docstrings, ending with
   `print("Setup complete")`. Only this cell may run past 40 lines. Nothing taught lives here.
3. **Numbered sections**: `## 1. <topic>` per agenda item, with `### 1.1 <question or example>` subsections. Each
   subsection is a short markdown explanation, then one or two short code cells, then a markdown cell that reads the
   result (bullets naming the parameter, what the plot shows, the trade-off).
4. **Recap and Quick check** (the last markdown cell): `## Recap` with a table (algorithm or idea, type, good at,
   watch out for), then `**Quick check**` with 4–6 numbered questions the trainer can ask aloud.

## Voice and cells

- Plain, spoken English, second person or "we"; short paragraphs; bold the term the paragraph defines.
- Markdown between every one or two code cells: the room reads the reason before the code runs.
- Code cells are short (most under 20 lines, never over 40): one idea per cell, a comment on the line that matters,
  results printed with f-strings (`print(f"Inertia: {kmeans.inertia_:.1f}")`) or drawn with a helper.
- Every random call takes `random_state=RANDOM_STATE` (or a fixed seed), so the numbers in the markdown hold.
- Small formulas and pseudo-trees go in markdown (fenced or inline), not in code.

## Data and examples

- Synthetic data first (`make_classification`, `make_moons`, `make_blobs`, `make_circles`) to show the idea on a
  shape the room can see, then one real built-in dataset (iris, wine, digits, breast cancer, California housing, MNIST
  on the TensorFlow days) to show it on data nobody built for the purpose.
- Show the failure case as well as the success: an underfit and an overfit setting, a shape the method cannot handle,
  a metric that disagrees with what we know.
- Prompt the room where a parameter is worth changing: "Try changing it: single linkage tends to chain points" /
  "Try `eps=0.1` and `eps=0.5` in the cell above". The runbook adds a "Try changing" prompt for every section the
  notebook leaves without one.

## Before committing

- Run it top to bottom on a fresh Colab runtime, then Edit > Clear all outputs and save: no stored outputs and no
  execution counts in the committed file.
- `python harness/notebook_check.py demo-repo/notebooks/week-WW` prints OK.
- Commit on `main` of the demo repo before the day (close_day.py records the last commit touching the file).
