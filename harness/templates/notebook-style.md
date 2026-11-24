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
  notebook leaves without one; a notebook with the study layer (below) carries them all itself.

## Study layer (D-0105)

A notebook is also the learner's study copy: someone who was not on the call, or who is revising a week later, works
through it alone with no recording. The layer below adds that without slowing the live pass (answers are collapsed,
nothing adds a heading or a cell). It is checked by `notebook_check.py`; `--study` fails a notebook without it. The
pilot is `demo-repo/notebooks/week-07/01_monday_mlp_backprop_and_digit_classifier.ipynb`.

1. **Study block in the title cell**, after the going-deeper line and before "Run the next cell first": the line
   `**Studying on your own**`, a table of sections against minutes (the plan's pass timings) with the natural stopping
   points, how to work a subsection (predict, run, compare, try changing, put it back), what to do after a runtime
   disconnect (Runtime > Run before) and a link to the day's notes page. Bullets, never a numbered list (the numbered
   list in the title cell is the agenda).
2. **`**Predict first:**`** one question at the end of the markdown above a code cell, answerable from that markdown
   alone and settled by the cell's output and the bullets under it. At least one per numbered `##` section, and one
   per core subsection where a prediction is possible. Going-deeper subsections carry none. When nothing below
   settles it (a markdown-only subsection, a sum the cell does not print), the answer follows in a collapsed block.
3. **Try changing, complete**: every prompt names the edit, what the reader should then see (a number from the run,
   or the direction of the change when it depends on a fit) and ends "Put it back". The runbook no longer holds
   prompts the notebook lacks.
4. **`**Common mistake:**`** one bullet in the result markdown where the runbook has a `Trap`, reworded for the
   reader: the mistake, then why it is one.
5. **Work it by hand**: an activity the trainer runs on the call (a paper exercise, a grid in the chat) is written
   into the notebook as `**Work it by hand first.**` with the task, then the answer key and the usual wrong answers
   in a collapsed block.
6. **`**Before you move on**`** at the end of every numbered `##` section: two to four things the reader can now do,
   each one checkable ("count the parameters of a small Dense network"), never "understand X".
7. **Quick check answers**: the numbered questions stay as they are; one collapsed block follows them with one
   numbered answer per question, in the words a learner would say aloud.

Collapsed blocks are written exactly like this, blank lines included, so Colab renders the markdown inside them:

```
<details>
<summary>Check your answer</summary>

The answer, in a sentence or two.

</details>
```

Wording: the reader is alone. No "the room", "on the call", "your trainer" or "the chat" in the study layer. Every
number in it comes from the notebook's own run, the brief or arithmetic the reader can redo; a result that depends on
a fit is quoted as "about" or described by its direction.

## Before committing

- Run it top to bottom on a fresh Colab runtime, then Edit > Clear all outputs and save: no stored outputs and no
  execution counts in the committed file.
- `python harness/notebook_check.py demo-repo/notebooks/week-WW` prints OK.
- Commit on `main` of the demo repo before the day (close_day.py records the last commit touching the file).
