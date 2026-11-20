# w07d4 — Custom training loops, TensorBoard runs & project workflow

gate: light
verified: 2026-11-19
week: 7 · TensorFlow
day: w07d4 · custom-training-tensorboard-and-project-workflow

version-stamps:
  - python: 3.13.18 on Colab, not the course 3.15 (verified 2026-11-19; runs in Colab; TensorFlow has no 3.15 wheel, so no cp315 wheel is picked; source: googlecolab/backend-info os-info.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt, read 2026-11-19: "Python 3.13.18", Ubuntu 24.04.5 LTS)
  - tensorflow: 2.21.0 (verified 2026-11-19; runs in Colab; source: backend-info pip-freeze.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt, read 2026-11-19, line `tensorflow==2.21.0`)
  - keras: 3.13.2 reached as `tf.keras` (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `keras==3.13.2`)
  - tensorboard: 2.21.0 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `tensorboard==2.21.0`; `%load_ext tensorboard`, `%tensorboard --logdir logs/compare`)
  - numpy: 2.4.6 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `numpy==2.4.6`)
  - pandas: 2.2.3 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `pandas==2.2.3`; `pd.read_csv(url)`, the results table)
  - scipy: 1.16.3 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `scipy==1.16.3`; only through scikit-learn)
  - scikit-learn: 1.6.1 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `scikit-learn==1.6.1`; `fetch_20newsgroups`, `train_test_split`)
  - seaborn: 0.13.2 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `seaborn==0.13.2`; stamp cell only)
  - matplotlib: 3.10.0 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `matplotlib==3.10.0`)
  - tensorflow-datasets: 4.9.10 imported as `tensorflow_datasets` (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `tensorflow-datasets==4.9.10`, so it is preinstalled and Part B's TFDS cell needs no `!pip install`; the import itself is confirmed by the fresh-runtime run below)
  - tflearn: 0.5.0, last PyPI release 2020-11-11, last master commit 2020-11-30; does not import on TensorFlow 2.21 (history blocks only, never run) (verified 2026-11-18)
  - note: OWED BEFORE NOTES AUTHORING CITES ANY NUMBER. The stamps above are read from Colab's published manifest (backend-info), whose header warns it can lag the live runtime; no Colab runtime was reachable from this research session, so nothing above or below was printed by a fresh runtime. The page author (or whoever does the week-7 fresh-Colab pass) opens a new notebook on a fresh CPU runtime, runs (1) the stamp cell `import sys, numpy, pandas, scipy, sklearn, seaborn, matplotlib, tensorflow as tf; print(sys.version, numpy.__version__, pandas.__version__, scipy.__version__, sklearn.__version__, seaborn.__version__, matplotlib.__version__, tf.__version__, tf.keras.__version__)`, (2) `import tensorflow_datasets as tfds; print(tfds.__version__)`, (3) the page's MNIST cell, then the hand loop, `fit_model`, `plain` and `batchnorm` fits each wrapped as `t0 = time.time()` ... `print(f"{time.time() - t0:.0f} s")`, and replaces this line with the printed stamp line, the TFDS result and the four times. If any value differs from the manifest, the page and runbook quote the printed value, never 3.15. Expected, not measured: each of the four fits is well under the 3-minute cap on a CPU runtime (54,000 rows in 422 batches of 128 per epoch on a 101,770-parameter network; the hand loop runs eagerly, so it is the slowest per epoch but has only 2 epochs).

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- `model.fit` loops over epochs, and in each epoch over batches; per batch it runs a forward pass, computes the loss, computes gradients of the loss with respect to the trainable weights and has the optimizer update the weights — [Writing a training loop from scratch](https://www.tensorflow.org/guide/keras/writing_a_training_loop_from_scratch), [Keras: Model training APIs](https://keras.io/api/models/model_training_apis/)
- `fit` knobs the page names: `epochs`, `batch_size`, `validation_data`, `callbacks`, `shuffle` (on by default), `verbose`; each is one sentence, none is tuned — [tf.keras.Model.fit](https://www.tensorflow.org/api_docs/python/tf/keras/Model#fit), [Keras: Model training APIs](https://keras.io/api/models/model_training_apis/)
- `tf.GradientTape` records operations run inside its `with` block so `tape.gradient(loss, variables)` can return the slope of the loss for each variable — [tf.GradientTape](https://www.tensorflow.org/api_docs/python/tf/GradientTape)
- `optimizer.apply_gradients(zip(grads, model.trainable_variables))` applies one update step — [tf.keras.optimizers.Optimizer](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/Optimizer)
- Calling a model as `model(x, training=True)` runs a forward pass in training mode; it changes the output only for layers such as `Dropout` and `BatchNormalization` (the hand loop's 784-128-10 net has neither, so the flag is shown as the habit), and `fit` sets it for you, which is why the `batchnorm` run in the TensorBoard pair normalises with each batch's own mean and spread while training and with moving averages in `evaluate` — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization)
- A model that is never compiled can be called and trained by a hand loop; `compile` is needed only for `evaluate` and `fit`, so the page compiles `loop_model` with a loss and metrics purely to call `evaluate` — [tf.keras.Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model), [Writing a training loop from scratch](https://www.tensorflow.org/guide/keras/writing_a_training_loop_from_scratch)
- Teams write their own loop for a custom loss or update rule, several models trained against each other (GANs), or research code; otherwise `fit` plus callbacks is the default — [Writing a training loop from scratch](https://www.tensorflow.org/guide/keras/writing_a_training_loop_from_scratch)
- `SparseCategoricalCrossentropy()` takes integer labels 0 to 9 and probabilities from a softmax output; it matches the string `"sparse_categorical_crossentropy"` used with `compile` — [tf.keras.losses.SparseCategoricalCrossentropy](https://www.tensorflow.org/api_docs/python/tf/keras/losses/SparseCategoricalCrossentropy)
- The Keras `TensorBoard` callback writes event files to `log_dir`; `histogram_freq=1` also writes weight histograms each epoch, shown in the Histograms tab — [tf.keras.callbacks.TensorBoard](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard)
- In Colab and Jupyter, `%load_ext tensorboard` then `%tensorboard --logdir logs/compare` shows a dashboard in the cell; a parent folder with one subfolder per run overlays the runs in the Scalars tab — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
- An empty TensorBoard usually means a wrong `--logdir` or a fit that never ran with the callback — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
- Keras built-in datasets load from code with `tf.keras.datasets.<name>.load_data()` (cached download, no upload) — [tf.keras.datasets](https://www.tensorflow.org/api_docs/python/tf/keras/datasets), [Keras: Datasets](https://keras.io/api/datasets/)
- scikit-learn `fetch_*` loaders (e.g. `fetch_california_housing`, `fetch_20newsgroups`) download once and cache under `~/scikit_learn_data`; `random_state` controls shuffling where offered — [scikit-learn: Dataset loading utilities](https://scikit-learn.org/stable/datasets.html)
- `pd.read_csv(url)` reads a public CSV straight from a URL, no upload — [pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- `tf.keras.utils.set_random_seed(n)` sets Python, NumPy and TensorFlow seeds in one call; exact repeatability across machines or GPUs is not guaranteed, same-runtime reruns on CPU are the aim — [tf.keras.utils.set_random_seed](https://www.tensorflow.org/api_docs/python/tf/keras/utils/set_random_seed)
- `model.save("name.keras")` writes one zip file holding the architecture, the weights, the compile settings and the optimizer state; `tf.keras.models.load_model` reads it back, and the guide checks the reload by comparing predictions — [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)
- TensorFlow Datasets loads named datasets with `tfds.load(name, split=..., as_supervised=True)`; with `batch_size=-1` it returns the whole split at once, and `tfds.as_numpy` turns it into numpy arrays, so the page never iterates a `tf.data` pipeline (a corner under D-0086) — [tfds.load](https://www.tensorflow.org/datasets/api_docs/python/tfds/load), [TensorFlow Datasets](https://www.tensorflow.org/datasets)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Customizing the training process
- Interview questions: What happens inside one step of `model.fit`?; Why does `GradientTape` exist, and what does `tape.gradient` return?; When would you write the loop yourself instead of calling `fit`?
- Adjacent concept: batches and epochs, and why the weights update once per batch not once per epoch — one sentence on why a hand loop must reproduce the slicing `fit` does for you; never Wednesday's Functional API or later days.
- Trade-off or limit: a hand loop gives full control (custom loss, gradient clipping, multiple optimizers) but you also own shuffling, metrics, validation and callbacks that `fit` gives free — [Writing a training loop from scratch](https://www.tensorflow.org/guide/keras/writing_a_training_loop_from_scratch)
- Recognise on sight: `with tf.GradientTape() as tape: preds = model(xb, training=True); loss = loss_fn(yb, preds)` then `grads = tape.gradient(loss, model.trainable_variables)` and `optimizer.apply_gradients(zip(grads, model.trainable_variables))`
- Claims:
  - The loss inside the tape must be computed from operations the tape watched; computing it outside returns `None` gradients — [tf.GradientTape](https://www.tensorflow.org/api_docs/python/tf/GradientTape)
  - A hand loop on the same data, seed, batch size and epochs lands near `fit`'s validation accuracy, not on the identical number (`fit` shuffles by default; the page's slices are in order) — [Writing a training loop from scratch](https://www.tensorflow.org/guide/keras/writing_a_training_loop_from_scratch), [tf.keras.Model.fit](https://www.tensorflow.org/api_docs/python/tf/keras/Model#fit)
  - `fit` reports a running average of loss over the epoch; a hand loop prints whatever the author averages, so epoch losses are compared loosely — [tf.keras.Model.fit](https://www.tensorflow.org/api_docs/python/tf/keras/Model#fit), [Keras: Model training APIs](https://keras.io/api/models/model_training_apis/)
  - Adam is chosen by name in `compile`; in a hand loop the optimizer object is made explicitly with `learning_rate=0.001` — [tf.keras.optimizers.Adam](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/Adam)
  - Iterating `range(0, len(x_tr), 128)` yields a short final batch (54000 is not a multiple of 128; 54000/128 = 421.875) that the loop handles without special code — [Python docs: range](https://docs.python.org/3/library/stdtypes.html#range)

### TensorBoard with TFLearn
- Interview questions: What does TensorBoard show and where do its files come from?; How do you compare two training runs?; TFLearn is mentioned in an old tutorial: what is it today and what replaces it?
- Adjacent concept: validation curves, seen as train versus validation on one chart — comparing two runs is the same reading skill applied across runs; never later days' tuning.
- Trade-off or limit: TFLearn is unmaintained (last release 0.5.0, 2020-11-11; last commit 2020-11-30) and does not import on Colab's TensorFlow 2.21, so it appears only as a history block — [tflearn on PyPI](https://pypi.org/project/tflearn/)
- Recognise on sight: `model = tflearn.DNN(net, tensorboard_verbose=3, tensorboard_dir="logs")` in old code; today `tf.keras.callbacks.TensorBoard(log_dir="logs/compare/plain", histogram_freq=1)`
- Claims:
  - Mapping: `DNN(tensorboard_verbose=..., tensorboard_dir=...)` becomes `tf.keras.callbacks.TensorBoard(log_dir=...)` passed to `fit(callbacks=[...])` — [tf.keras.callbacks.TensorBoard](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard)
  - One log folder per run (`logs/compare/plain`, `logs/compare/batchnorm`) lets the Scalars tab draw both as separate coloured lines — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
  - Re-running a fit into the same folder adds a second run's events onto the first; the fix is a new folder name per run — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
  - `histogram_freq=1` writes weight histograms each epoch; the Histograms tab shows how each layer's weights spread and shift (named only, not interpreted in depth) — [tf.keras.callbacks.TensorBoard](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard)
  - The second run differs by one `BatchNormalization` layer, which rescales the hidden layer's outputs with each batch's mean and spread while training; the overlaid curves show whether that one change helped on validation loss, the same measure used for every before-and-after in the week — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization), [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)

### Working on a model project: datasets from code, reproducible runs, hand-in
- Interview questions: How do you make a notebook reproducible?; Why is the test set used once?; What goes in a README for a model?
- Adjacent concept: the README and short deck for a model — one sentence: they tell one story in the order the notebook ran (the problem, the data's source and size, the preprocessing, the model and why, the results table with before and after, the test number used once, the limitations and how to rerun the notebook), and the results table kept as you go is what makes "what I tried" honest; never week 8's cross-validation.
- Trade-off or limit: seeds make a rerun on the same runtime repeatable, but different hardware, library versions or a GPU may still change numbers; Runtime > Run all on a fresh runtime is the real check — [tf.keras.utils.set_random_seed](https://www.tensorflow.org/api_docs/python/tf/keras/utils/set_random_seed)
- Recognise on sight: `RANDOM_STATE = 42; np.random.seed(RANDOM_STATE); tf.keras.utils.set_random_seed(RANDOM_STATE)` at the top; `train_test_split(..., random_state=RANDOM_STATE)`
- Claims:
  - Four code-only loading routes need no upload: Keras `load_data()`, scikit-learn `fetch_*`, `tfds.load`, `pd.read_csv(url)` — [scikit-learn datasets](https://scikit-learn.org/stable/datasets.html), [tfds.load](https://www.tensorflow.org/datasets/api_docs/python/tfds/load)
  - Look before modelling: `df.shape`, `df.dtypes`, `df.isna().sum()`, `df.head()`, class counts with `value_counts()` — [pandas: DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)
  - Split the test set first and fit every fill, encoder and scaler on the training rows only — [scikit-learn: train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
  - Stratifying (`stratify=y`) keeps class proportions the same in each part — [scikit-learn: train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
  - The hand-in file is `model.save("model.keras")`, checked by reloading with `load_model` and comparing predictions on the same rows — [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)
  - Teams document a trained model in a short written card that gives context on how it was developed and how it performs; a project README plays that role — [Model Card Toolkit guide](https://www.tensorflow.org/responsible_ai/model_card_toolkit/guide)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Writing a training loop from scratch (TensorFlow guide) — https://www.tensorflow.org/guide/keras/writing_a_training_loop_from_scratch
- tf.keras.Model (fit, evaluate, compile) — https://www.tensorflow.org/api_docs/python/tf/keras/Model
- Keras: Model training APIs — https://keras.io/api/models/model_training_apis/
- tf.GradientTape — https://www.tensorflow.org/api_docs/python/tf/GradientTape
- tf.keras.optimizers.Optimizer — https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/Optimizer
- tf.keras.optimizers.Adam — https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/Adam
- tf.keras.losses.SparseCategoricalCrossentropy — https://www.tensorflow.org/api_docs/python/tf/keras/losses/SparseCategoricalCrossentropy
- tf.keras.layers.BatchNormalization (read 2026-11-19) — https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization
- tf.keras.callbacks.TensorBoard — https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard
- Get started with TensorBoard — https://www.tensorflow.org/tensorboard/get_started
- tf.keras.utils.set_random_seed — https://www.tensorflow.org/api_docs/python/tf/keras/utils/set_random_seed
- Save, serialize, and export models (read 2026-11-19) — https://www.tensorflow.org/guide/keras/serialization_and_saving
- Model Card Toolkit guide (read 2026-11-19) — https://www.tensorflow.org/responsible_ai/model_card_toolkit/guide
- tf.keras.datasets — https://www.tensorflow.org/api_docs/python/tf/keras/datasets
- Keras: Datasets — https://keras.io/api/datasets/
- TensorFlow Datasets — https://www.tensorflow.org/datasets
- tfds.load — https://www.tensorflow.org/datasets/api_docs/python/tfds/load
- scikit-learn: Dataset loading utilities — https://scikit-learn.org/stable/datasets.html
- scikit-learn: train_test_split — https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- pandas.read_csv — https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- pandas: DataFrame — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
- Python docs: range — https://docs.python.org/3/library/stdtypes.html#range
- tflearn on PyPI — https://pypi.org/project/tflearn/
- Colab backend-info: runtime OS and Python (os-info.txt, read 2026-11-19) — https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt
- Colab backend-info: preinstalled packages (pip-freeze.txt, read 2026-11-19) — https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- GradientTape | A TensorFlow tool that records the steps of a calculation so it can then report how much each weight changed the loss. | aka: tf.GradientTape, tape
- training loop | The code that repeats forward pass, loss, gradients and weight update over every batch of every epoch, which `fit` runs for you. | aka: custom training loop, hand-written loop
- batch | The small group of rows a model sees before its weights are updated once. | aka: mini-batch, batch size
- random seed | A starting number that makes random choices, such as weight starting values and shuffles, repeat on a rerun. | aka: seed, random_state
- log folder | The folder a callback writes a run's curves into, one per run, which TensorBoard reads. | aka: log_dir, logdir, run folder
- results table | A short table kept as you go with one row per trained model and its validation numbers, so before-and-after comparisons are on record. | aka: experiment log

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Computing the loss outside the `with tf.GradientTape()` block, so `tape.gradient` returns `None` and `apply_gradients` errors or does nothing.
- Writing two runs into the same log folder, or pointing `--logdir` at the wrong path, so TensorBoard shows one merged run or an empty page.
- Comparing the hand loop's printed epoch loss with `fit`'s and expecting identical numbers; compare validation accuracy and expect "close", not equal.
- Fitting a scaler, filling blanks or choosing settings with the test set in view, or running the test cell more than once, which makes the final number a validation number in disguise.
- Trusting a notebook that only works in the current session (out-of-order cells, leftover variables); skipping Runtime > Run all on a fresh runtime, or forgetting that Colab loses `.keras` files and logs when the runtime resets.
- Installing or importing `tflearn` from an old tutorial and hitting an import error instead of using the Keras equivalent.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- No call is delivered; every "Run in Colab" cell must run in a fresh notebook with only the cells above it on the page (its own imports, `RANDOM_STATE = 42` seeds and the MNIST split cell). The fresh-runtime stamp line, the `import tensorflow_datasets` result and the measured times of the 2-epoch hand loop, `fit_model` (2 epochs), `plain` and `batchnorm` are OWED (see the `note:` stamp line); until they are recorded the page quotes no time and no accuracy figure for these cells.
- The hand-loop step: one build cell makes the fresh, uncompiled 784-128-10 `loop_model`, `loss_fn = tf.keras.losses.SparseCategoricalCrossentropy()` and `optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)`; the loop cell slices `x_tr` in numpy batches of 128 for 2 epochs and prints the mean loss per epoch; then `loop_model.compile(loss=loss_fn, metrics=["accuracy"])` only so a final cell can print `loop_model.evaluate(x_val, y_val)` beside `fit_model` (same shape, compiled as the digit-network row says, `fit(x_tr, y_tr, epochs=2, batch_size=128, validation_data=(x_val, y_val))`) so "close, not identical" is visible.
- The TensorBoard pair, defined exactly: `plain` is the 784-128-10 digit network (`Input(shape=(784,))`, `Dense(128, activation="relu")`, `Dense(10, activation="softmax")`); `batchnorm` is the same shape with one `tf.keras.layers.BatchNormalization()` placed after the hidden `Dense(128, activation="relu")` and before the output layer (Wednesday's `bn_model` placement). Both are compiled with `optimizer="adam"`, `loss="sparse_categorical_crossentropy"`, `metrics=["accuracy"]`, fitted from the same seed on `x_tr, y_tr` for the same 5 epochs (Wednesday's pair count, so the numbers sit beside `### 3.2`) with `batch_size=128`, `validation_data=(x_val, y_val)` and `callbacks=[tf.keras.callbacks.TensorBoard(log_dir="logs/compare/plain", histogram_freq=1)]` and `log_dir="logs/compare/batchnorm"` respectively; then `%load_ext tensorboard` and `%tensorboard --logdir logs/compare`. The fresh-runtime run confirms both runs overlay in Scalars (`epoch_loss` and `epoch_accuracy`, train and validation) and the Histograms tab appears; the page reads the overlay on validation loss and ties `training=True` to the `BatchNormalization` layer (`fit` sets it; the hand loop's model has no such layer).
- Part B's loading block shows one cell per route, each printing shape and a few rows, and each on a dataset the course already uses so no example takes a project candidate off the table: Keras `tf.keras.datasets.mnist.load_data()`; scikit-learn `fetch_20newsgroups(subset="train", categories=["rec.autos", "rec.motorcycles"])`; TFDS `tfds.as_numpy(tfds.load("mnist", split="train", batch_size=-1, as_supervised=True))`; pandas `pd.read_csv("https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv")`. No cell touches Fashion-MNIST, Titanic or IMDB reviews, which are also Keras or TFDS built-ins; if the fresh run finds `tensorflow_datasets` does not import, the page names TFDS in one sentence and shows no TFDS cell.
