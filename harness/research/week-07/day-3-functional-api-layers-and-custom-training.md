# w07d3 — Functional API, layers, batch norm, saving & two full builds

gate: light
verified: 2026-11-19
week: 7 · TensorFlow
day: 3 · functional-api-layers-and-custom-training

version-stamps:
  - python: 3.15 (verified 2026-11-19) — course Python, NOT used today; the notebook runs on Colab's own Python
  - colab-python: 3.13.18 (verified 2026-11-19; runs in Colab; no wheel pick on the course Python; source: googlecolab/backend-info os-info.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt; that file is the testing image, so confirm with the stamp cell on a fresh runtime before the notebook commit)
  - tensorflow: 2.21.0 (verified 2026-11-19; runs in Colab; TensorFlow has no cp315 wheel; source: googlecolab/backend-info pip-freeze.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt, line `tensorflow==2.21.0`)
  - keras: 3.13.2, reached as `tf.keras` (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `keras==3.13.2`; `.keras` files, `Conv2D`, `BatchNormalization`, `Dropout`, `EarlyStopping` all come from this Keras 3)
  - numpy: 2.4.6 (verified 2026-11-19; runs in Colab; same pip-freeze.txt)
  - pandas: 2.2.3 (verified 2026-11-19; runs in Colab; same pip-freeze.txt; `get_dummies`, `reindex`, `fillna`, `median`, `mode`)
  - scipy: 1.16.3 (verified 2026-11-19; runs in Colab; same pip-freeze.txt; not imported by this day's cells)
  - scikit-learn: 1.6.1 (verified 2026-11-19; runs in Colab; same pip-freeze.txt; `train_test_split`, `StandardScaler`, `confusion_matrix`, `ConfusionMatrixDisplay`, `classification_report`, `precision_score`, `recall_score`, `f1_score`)
  - seaborn: 0.13.2 (verified 2026-11-19; runs in Colab; same pip-freeze.txt; only `sns.load_dataset("penguins")`)
  - matplotlib: 3.10.0 (verified 2026-11-19; runs in Colab; same pip-freeze.txt)
  - h5py: 3.14.0 (verified 2026-11-19; runs in Colab; same pip-freeze.txt; named only because `.h5` is the legacy save format)
  - tflearn: 0.5.0 (verified 2026-11-18; PyPI last release 2020-11-11; NOT installed or imported by any cell; history blocks only)
  - stamp source: the file above is a Colab testing-image listing written without a runtime (light gate); the fresh-runtime cell `import sys, numpy, pandas, scipy, sklearn, seaborn, matplotlib, tensorflow as tf; print(sys.version, numpy.__version__, pandas.__version__, scipy.__version__, sklearn.__version__, seaborn.__version__, matplotlib.__version__, tf.__version__, tf.keras.__version__)` replaces these numbers before the notebook commit; pages and the runbook quote that cell's output
  - penguins loader (to confirm on the fresh runtime): `sns.load_dataset("penguins")` downloads the CSV from the seaborn-data repository on GitHub, so it needs Colab's internet access (always on); expected 344 rows, 7 columns, blanks in the four measurements (2 rows each) and `sex` (11 rows). If it fails the notebook author uses the allisonhorst/palmerpenguins CSV fallback from the conventions and records which one ran here.

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- The Functional API builds a model by creating a `keras.Input`, calling layers on tensors like functions, and wrapping the first and last tensors in `keras.Model(inputs, outputs)`; it can express branches, merges and several inputs or outputs, which `Sequential` cannot — [The Functional API](https://www.tensorflow.org/guide/keras/functional_api)
- `Sequential` is appropriate for a plain stack of layers with exactly one input tensor and one output tensor — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
- `tf.keras.layers.Concatenate` joins a list of tensors along an axis (default last), so concatenating the 784-long input with the 128-wide hidden output gives 912 values per row; a skip connection is that join (or an `Add`) — [tf.keras.layers.Concatenate](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Concatenate)
- `model.summary()` lists each layer's output shape and parameter count; a `Dense(units)` layer on n inputs has n * units + units parameters, so 784-128-10 has 101,770 — [Model.summary](https://www.tensorflow.org/api_docs/python/tf/keras/Model)
- `tf.keras.utils.plot_model(model, show_shapes=True)` draws the layer graph and needs `pydot` and Graphviz installed (Colab has both; confirm on the fresh runtime) — [plot_model](https://www.tensorflow.org/api_docs/python/tf/keras/utils/plot_model)
- `Flatten` turns each example's axes into one long vector and keeps the batch axis: a batch of (32, 28, 28) becomes (32, 784) — [tf.keras.layers.Flatten](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Flatten)
- `Conv2D` expects a batch of images with a channel axis, (batch, height, width, channels) by default; `padding="valid"` is the default, so a 3 by 3 kernel shrinks 28 by 28 to 26 by 26, and `Conv2D(16, 3)` on (32, 28, 28, 1) outputs (32, 26, 26, 16) with 160 parameters — [tf.keras.layers.Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D)
- `MaxPooling2D()` defaults to a 2 by 2 window and keeps the largest value in each, halving height and width (26 by 26 becomes 13 by 13) and having no parameters — [tf.keras.layers.MaxPooling2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/MaxPooling2D)
- The CNN build's shapes: 28x28x1 → Conv2D(16,3) 26x26x16 → pool 13x13x16 → Conv2D(32,3) 11x11x32 → pool 5x5x32 → Flatten 800 → Dense(10); parameters 160 + 4,640 + 8,010 = 12,810 (worked out here from the layer rules; the notebook's `summary()` is the check) — [tf.keras.layers.Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D)
- `Embedding(input_dim, output_dim)` maps integer token ids to dense vectors: a batch of shape (batch, length) becomes (batch, length, output_dim) — [tf.keras.layers.Embedding](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Embedding)
- `BatchNormalization` normalises its inputs per batch during training (mean near 0, standard deviation near 1) and then applies a learned scale and offset; at inference it uses moving averages kept during training — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization)
- A `BatchNormalization` layer on 128 inputs holds 512 numbers: 256 trainable (scale and offset) and 256 non-trainable (the moving mean and moving variance); `summary()` shows both counts — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization)
- Batch normalization was introduced to reduce "internal covariate shift" and speed up training; later work disputes that explanation, so the notebook measures the pair instead of promising a gain — [Batch Normalization (Ioffe and Szegedy, arXiv:1502.03167)](https://arxiv.org/abs/1502.03167)
- `Dropout(rate)` sets a random fraction `rate` of its inputs to 0 at each training step and rescales the rest; it does nothing at inference (`predict`, `evaluate`) — [tf.keras.layers.Dropout](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dropout)
- Dropout is a regularisation technique to reduce overfitting — [Overfit and underfit](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
- `EarlyStopping(monitor="val_loss", patience=2, restore_best_weights=True)` stops training when the monitored value has not improved for `patience` epochs and, with `restore_best_weights`, puts back the weights of the best epoch; `fit` gets it through `callbacks=[...]` and `history.epoch` shows how many epochs ran — [tf.keras.callbacks.EarlyStopping](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping)
- A widening gap between training and validation loss, with validation loss rising while training loss falls, is the sign of overfitting — [Overfit and underfit](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
- `model.save("name.keras")` writes one file holding the architecture, weights and optimizer state; `tf.keras.models.load_model` rebuilds it; the `.keras` extension selects the Keras 3 format — [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)
- `.h5` is the legacy format Keras still reads and writes with a warning; `model.export(path)` writes a TensorFlow SavedModel for serving, which is not reloaded as a Keras model — [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)
- `tf.keras.callbacks.ModelCheckpoint` saves the model (or only its weights) during `fit`, optionally only the best epoch — [tf.keras.callbacks.ModelCheckpoint](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/ModelCheckpoint)
- Files written in Colab's runtime live in a temporary virtual machine's disk and are deleted when the runtime is recycled; download them or copy them to Drive to keep them — [Colab FAQ](https://research.google.com/colaboratory/faq.html)
- `train_test_split(..., stratify=y)` keeps class proportions in each part; `StandardScaler.fit` learns mean and standard deviation, `transform` applies them — [train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html), [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)
- Fitting a scaler (or any imputation value) on data that includes the validation or test rows is data leakage: the evaluation then no longer measures unseen data — [Common pitfalls: data leakage](https://scikit-learn.org/stable/common_pitfalls.html)
- `pd.get_dummies(df, columns=[...])` one-hot encodes category columns; a table that lacks a category gets fewer columns, so `reindex(columns=train_columns, fill_value=0)` gives the other tables the training columns in the same order — [pandas.get_dummies](https://pandas.pydata.org/docs/reference/api/pandas.get_dummies.html), [DataFrame.reindex](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html)
- `classification_report` prints precision, recall, F1 and support per class, then macro and weighted average rows; `ConfusionMatrixDisplay` draws `confusion_matrix` — [classification_report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html), [ConfusionMatrixDisplay](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ConfusionMatrixDisplay.html)
- A regression model ends in `Dense(1)` with no activation (a linear output), is compiled with `loss="mse"` and often `metrics=["mae"]`, and its predictions are compared with actual values — [Basic regression: Predict fuel efficiency](https://www.tensorflow.org/tutorials/keras/regression)
- TFLearn's last PyPI release is 0.5.0 (2020-11-11) and the project is unmaintained; Keras in TensorFlow 2 is the maintained path for every TFLearn idea (input_data, fully_connected, regression, DNN, merge, batch_normalization, save/load) — [tflearn on PyPI](https://pypi.org/project/tflearn/), [TFLearn repository](https://github.com/tflearn/tflearn)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Functional composition
- Interview questions: When would you use the Functional API instead of `Sequential`?; What does `tf.keras.Model(inputs, outputs)` do, and what is the object returned by `Dense(128)(inputs)`?; What is a skip connection and why does it need the Functional API?
- Adjacent concept: Keras tensors versus eager tensors — a call like `Dense(128)(inputs)` on a `keras.Input` does not compute numbers, it records a graph of layers; it is why the same layer call works on real data later — one sentence on why it belongs with composition.
- Trade-off or limit: `Sequential` is shorter and enough for a straight stack; reach for the Functional API only when the model branches, merges or has several inputs or outputs — [The Functional API](https://www.tensorflow.org/guide/keras/functional_api)
- Recognise on sight: `inputs = tf.keras.Input(shape=(784,))`, `x = tf.keras.layers.Dense(128, activation="relu")(inputs)`, `outputs = tf.keras.layers.Dense(10, activation="softmax")(x)`, `model = tf.keras.Model(inputs, outputs)`
- Claims:
  - Calling a layer on a Keras tensor returns a new Keras tensor, so layers chain like function calls — [The Functional API](https://www.tensorflow.org/guide/keras/functional_api)
  - The Functional model of the 784-128-10 network has the same `summary()` and the same 101,770 parameters as the Sequential one — [The Functional API](https://www.tensorflow.org/guide/keras/functional_api)
  - `Concatenate()([inputs, x])` joins the raw input to a hidden output, giving 912 values and a Dense(10) with 9,130 parameters, so the skip model has 100,480 + 9,130 = 109,610 parameters (worked from the layer rules; the notebook's `summary()` is the check) — [tf.keras.layers.Concatenate](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Concatenate)
  - TFLearn's `merge` maps to `Concatenate` (or `Add`) in the Functional API, and TFLearn's layer stacking maps to `Sequential` — [The Functional API](https://www.tensorflow.org/guide/keras/functional_api), [TFLearn repository](https://github.com/tflearn/tflearn)
  - `plot_model(model, show_shapes=True)` shows the branch as a picture and needs `pydot` and Graphviz — [plot_model](https://www.tensorflow.org/api_docs/python/tf/keras/utils/plot_model)

### Predefined neural network layers
- Interview questions: What does `Flatten` do and why is it needed before `Dense`?; What does a `Conv2D(16, 3)` layer output for a 28 by 28 by 1 image?; How do you check that two layers fit together?
- Adjacent concept: The reading of a layer by what it takes in — each layer expects a particular input shape, so a shape mismatch error is read as a statement about which layer got the wrong shape.
- Trade-off or limit: A `Dense` layer on a flattened image ignores which pixels are neighbours; `Conv2D` keeps that structure with far fewer parameters (12,810 against 101,770 in this week's pair) — [tf.keras.layers.Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D)
- Recognise on sight: `tf.keras.layers.Conv2D(16, 3, activation="relu")` followed by `tf.keras.layers.MaxPooling2D()` and `tf.keras.layers.Flatten()`
- Claims:
  - `Dense`, `Flatten`, `Dropout`, `BatchNormalization`, `Conv2D`, `MaxPooling2D` and `Embedding` are all in `tf.keras.layers` — [Layers API](https://www.tensorflow.org/api_docs/python/tf/keras/layers)
  - `Conv2D` weights are one set of small kernels slid across the whole image, so the parameter count does not depend on image size — [tf.keras.layers.Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D)
  - `images[..., np.newaxis]` adds the channel axis a grey image lacks, (32, 28, 28) to (32, 28, 28, 1) — [tf.keras.layers.Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D)
  - `Embedding` takes integer ids and returns vectors; the notebook prints only its output shape (what the vectors mean is week 8) — [tf.keras.layers.Embedding](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Embedding)
  - TFLearn's `fully_connected` maps to `Dense`, and `input_data` maps to `tf.keras.Input` — [Layers API](https://www.tensorflow.org/api_docs/python/tf/keras/layers), [TFLearn repository](https://github.com/tflearn/tflearn)

### Batch normalization
- Interview questions: What does a batch normalization layer do?; Why does it behave differently in training and at prediction time?; How would you tell whether adding it helped?
- Adjacent concept: `StandardScaler` on the inputs — batch normalization is the same rescaling applied inside the network to a layer's values, per batch, which ties it to the preprocessing step in the tabular build.
- Trade-off or limit: The gain is not guaranteed and is small on a network this shallow, so the pair is measured on the same validation rows; the original "internal covariate shift" explanation is contested — [Batch Normalization (Ioffe and Szegedy, arXiv:1502.03167)](https://arxiv.org/abs/1502.03167)
- Recognise on sight: `tf.keras.layers.BatchNormalization()` between a `Dense` and the next layer
- Claims:
  - In training it normalises with the current batch's mean and variance; at inference it uses moving averages learned during training — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization)
  - Its four-per-feature numbers are two trainable (scale, offset) and two non-trainable (moving mean, moving variance) — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization)
  - Fitting `plain_model` and `bn_model` with the same `validation_data` makes the comparison fair; both are judged by `val_loss` and `val_accuracy` — [Model.fit](https://www.tensorflow.org/api_docs/python/tf/keras/Model)
  - TFLearn's `batch_normalization` maps to `tf.keras.layers.BatchNormalization` — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization), [TFLearn repository](https://github.com/tflearn/tflearn)

### Saving and loading a model with TFLearn
- Interview questions: How do you save a trained Keras model and load it back?; What is in a `.keras` file?; Why is a model file saved in Colab gone the next day?
- Adjacent concept: Checkpoints during training (`ModelCheckpoint`) — named at name level beside saving, since both write a model to disk and a long fit needs one.
- Trade-off or limit: A file saved in the Colab runtime disappears when the runtime resets; download it or copy it to Drive — [Colab FAQ](https://research.google.com/colaboratory/faq.html)
- Recognise on sight: `model.save("digits_cnn.keras")` and `loaded = tf.keras.models.load_model("digits_cnn.keras")`
- Claims:
  - TFLearn is unmaintained (last release 0.5.0, 2020-11-11) and `tflearn.DNN.save` and `DNN.load` map to `model.save("....keras")` and `tf.keras.models.load_model`; the notebook runs no TFLearn code — [tflearn on PyPI](https://pypi.org/project/tflearn/), [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)
  - TFLearn status as checked on 2026-11-18: last `master` commit 2020-11-30; it does not import on TensorFlow 2.21 (`tflearn/layers/recurrent.py` imports `is_sequence` from `tensorflow.python.util.nest`); Tuesday's brief confirms by one run, so pages say "checked" unless that run is recorded — [TFLearn repository](https://github.com/tflearn/tflearn)
  - A loaded model gives the same predictions: `np.allclose(model.predict(x), loaded.predict(x))` is the check — [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)
  - The `.keras` file also keeps the compile settings, so `loaded.evaluate(...)` works without calling `compile` again — [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)
  - `.h5`, `model.export` (a SavedModel for serving, week 11) and `ModelCheckpoint` get one sentence each — [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving), [tf.keras.callbacks.ModelCheckpoint](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/ModelCheckpoint)
  - TFLearn's `tensorboard_dir` maps to `tf.keras.callbacks.TensorBoard(log_dir=...)` (Thursday's page) — [tf.keras.callbacks.TensorBoard](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- The Functional API — https://www.tensorflow.org/guide/keras/functional_api
- The Sequential model — https://www.tensorflow.org/guide/keras/sequential_model
- Save, serialize, and export models — https://www.tensorflow.org/guide/keras/serialization_and_saving
- Overfit and underfit — https://www.tensorflow.org/tutorials/keras/overfit_and_underfit
- Basic regression: Predict fuel efficiency — https://www.tensorflow.org/tutorials/keras/regression
- Layers API — https://www.tensorflow.org/api_docs/python/tf/keras/layers
- tf.keras.layers.Concatenate — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Concatenate
- tf.keras.layers.Flatten — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Flatten
- tf.keras.layers.Conv2D — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D
- tf.keras.layers.MaxPooling2D — https://www.tensorflow.org/api_docs/python/tf/keras/layers/MaxPooling2D
- tf.keras.layers.Embedding — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Embedding
- tf.keras.layers.BatchNormalization — https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization
- tf.keras.layers.Dropout — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dropout
- tf.keras.callbacks.EarlyStopping — https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping
- tf.keras.callbacks.ModelCheckpoint — https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/ModelCheckpoint
- tf.keras.callbacks.TensorBoard — https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard
- tf.keras.utils.plot_model — https://www.tensorflow.org/api_docs/python/tf/keras/utils/plot_model
- Model (summary, fit, evaluate, predict) — https://www.tensorflow.org/api_docs/python/tf/keras/Model
- Batch Normalization: Accelerating Deep Network Training (arXiv:1502.03167) — https://arxiv.org/abs/1502.03167
- train_test_split (scikit-learn) — https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- StandardScaler (scikit-learn) — https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
- Common pitfalls and recommended practices: data leakage (scikit-learn) — https://scikit-learn.org/stable/common_pitfalls.html
- classification_report (scikit-learn) — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
- ConfusionMatrixDisplay (scikit-learn) — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ConfusionMatrixDisplay.html
- pandas.get_dummies — https://pandas.pydata.org/docs/reference/api/pandas.get_dummies.html
- pandas.DataFrame.reindex — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
- Colab FAQ — https://research.google.com/colaboratory/faq.html
- Colab backend-info pip-freeze.txt (fetched 2026-11-19) — https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt
- Colab backend-info os-info.txt (fetched 2026-11-19) — https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt
- tflearn on PyPI — https://pypi.org/project/tflearn/
- TFLearn repository — https://github.com/tflearn/tflearn

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- Functional API | A way to build a Keras model by calling layers on tensors like functions and wrapping the first and last in `tf.keras.Model`, which allows branches and merges a straight stack cannot. | aka: functional model, keras.Model(inputs, outputs)
- skip connection | A link that carries a layer's input past one or more layers and joins it to a later layer's output, for example with `Concatenate`. | aka: skip connections, shortcut connection, residual connection
- batch normalization | A layer that rescales its inputs to about mean 0 and spread 1 for each training batch, then applies a learned scale and offset. | aka: batch norm, BatchNormalization, BatchNorm
- dropout | A layer that switches off a random share of its values at each training step so the network cannot lean on any one of them, and does nothing when predicting. | aka: Dropout layer, Dropout(0.3)
- early stopping | Ending training when the validation loss has stopped improving for a set number of epochs, and keeping the best epoch's weights. | aka: EarlyStopping, patience
- data leakage | Letting information from the validation or test rows reach training, for example by fitting a scaler on all rows, so the evaluation looks better than the model really is. | aka: leakage, leak
- one-hot encoding | Turning a category column into one 0-or-1 column per category so a network can read it. | aka: one-hot, get_dummies, dummy variables
- confusion matrix | A table of true classes against predicted classes whose off-diagonal cells count the mistakes. | aka: confusion matrices, ConfusionMatrixDisplay

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Fitting the imputer values, the one-hot columns or the `StandardScaler` on all rows before splitting (or on the validation or test rows), so the validation number is inflated; the build splits first and learns every fill, encoding and scale from the training rows only.
- Giving `Conv2D` a (28, 28) image or the 784-long row instead of (28, 28, 1), which raises a shape error; reshape with `x.reshape(-1, 28, 28, 1)` and read `model.summary()` to see which layer got what.
- Judging dropout or batch normalization on training accuracy or a single run: dropout lowers training accuracy on purpose, so the verdict comes from validation loss and the gap between the curves; with a 6,000-row validation set a difference of a few hundredths of a percent is noise.
- Reading `val_accuracy` from the final epoch after `EarlyStopping` without `restore_best_weights=True`, or forgetting the test set must be used once: the model kept is the better one on validation, and `x_test` appears only in the build's test cell.
- Saving `penguins.keras` or `digits_cnn.keras` in Colab and finding it gone after a runtime reset, or saving with a name that does not end in `.keras` (an `.h5` name or a bare folder name selects a different format); download the file or copy it to Drive.
- Expecting the penguin table to be clean: `get_dummies` on validation or test makes a different column set when a category is missing, and median or most-common fills computed on the whole table leak; use `reindex(columns=train_columns, fill_value=0)` and fill from the training rows.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Notebook `03_wednesday_functional_api_layers_and_custom_training.ipynb`, `## 1` to `## 3`: build the digit network the Functional way (`### 1.1`), print its `summary()` beside Monday's, then add the `Concatenate` skip (`### 1.2`) and read the parameter count; in `## 2` print every shape in and out for `Flatten`, `Dense` and `Conv2D` + `MaxPooling2D` so a layer is chosen by what it reads; in `### 3.2` run the `plain_model` and `bn_model` pair on the same validation rows and read the results table and one sentence.
- `## 4` CNN build in the build order: `summary()` (12,810 against 101,770) and the reasons table, `fit` with `EarlyStopping` and read the epoch it stopped at from both curves on one chart, the grid of misclassified digits, then `Dropout(0.3)` and the before-and-after row; the "Try changing" prompt in `### 4.5` is `Dropout(0.5)`. Every fit must finish under 3 minutes on a CPU runtime (time it); if not, cut epochs.
- `## 5` save `best_cnn` to `digits_cnn.keras`, `load_model`, `np.allclose` on 100 predictions, show the file in Colab's Files panel and say it vanishes on reset; the restart-and-load prompt reruns only setup and MNIST, then evaluates the loaded file with no retraining.
- `## 6` penguins build, split first: show the blanks per column, fill from training medians and most common values, `get_dummies` + `reindex`, `StandardScaler` on training rows; run the "Try changing" prompt in `### 6.4` (scaler fitted on all rows) and say why the validation number can no longer be trusted; read `classification_report` per species and the five least-sure rows. `## 7` regression variant is the first cut: one linear unit, `mse`, `mae`, predicted against actual. Confirm on a fresh runtime that `sns.load_dataset("penguins")` loads, and record whether the fallback was needed.
