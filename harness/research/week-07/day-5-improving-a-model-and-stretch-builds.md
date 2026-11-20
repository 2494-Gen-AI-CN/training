# w07d5 — Improving a model & stretch builds

gate: light
verified: 2026-11-19
week: 7 · TensorFlow
day: w07d5 · improving-a-model-and-stretch-builds

version-stamps:
  - python: 3.13.18 on Colab, not the course 3.15 (verified 2026-11-19; runs in Colab; TensorFlow has no 3.15 wheel; source: googlecolab/backend-info os-info.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt, line `Python 3.13.18`, the same stamp the w07d1, w07d2 and w07d4 briefs carry)
  - tensorflow: 2.21.0 (verified 2026-11-19; runs in Colab; source: googlecolab/backend-info pip-freeze.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt, line `tensorflow==2.21.0`)
  - keras: 3.13.2, reached as `tf.keras` (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt)
  - numpy: 2.4.6 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt; np.random.normal, np.clip)
  - pandas: 2.2.3 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt; the results table as pd.DataFrame)
  - scikit-learn: 1.6.1 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt; TfidfVectorizer, fetch_20newsgroups, train_test_split)
  - matplotlib: 3.10.0 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt; plot_history, show_image_grid)
  - tflearn: 0.5.0 (status checked 2026-11-18: last PyPI release 2020-11-11, last master commit 2020-11-30; NOT installed or imported by any cell; history blocks only) (verified 2026-11-19)

stamp note: light gate, so no fresh Colab runtime was opened for this brief; the stamps above are read from googlecolab/backend-info (os-info.txt and pip-freeze.txt), which records Colab's latest submitted runtime image and can lead or lag production by a release; the fresh run the author makes before publishing quotes the stamp one-liner's printout where it differs, never 3.15. That run also owes the printed values the page leaves unquoted: the epoch of `base_20`'s lowest validation loss, both results tables, the kept model's test accuracy, the two-row text results table and the exact train and validation post counts.

fit plan (CPU-sized fits; every fit under 3 minutes on a fresh Colab CPU runtime): estimated from step counts and the week's earlier MNIST fits, not timed here; the fresh run that stamps the versions times each cell and the page quotes those times.
  - Part A worked example, `base_20` (784-128-10, 20 epochs, `batch_size=128`, 54,000 rows, 422 steps an epoch): about 2 to 4 s an epoch, so about 40 to 80 s; fallback if over 3 minutes: train on the first 20,000 rows of `x_tr` (one markdown line says so) and keep 20 epochs, because the rising validation curve is the point.
  - Part A lever, `dropout_20` (the same shape with `Dropout(0.2)` after the hidden layer, 20 epochs, `batch_size=128`): the same budget as `base_20`; same fallback, applied to both fits so the comparison stays fair.
  - Part B denoising, `denoiser` (784-32-784, 10 epochs as on Tuesday, `batch_size=256`, 211 steps an epoch, `validation_data=(x_val_noisy, x_val)`): about 20 to 40 s.
  - Part B text, `tfidf_model` rebuilt (Input 5000, Dense 32 relu, Dense 1 sigmoid, 10 epochs, `batch_size=32`, about 950 training posts): a few seconds; `embed_model` (`Input(shape=(200,))`, `Embedding(10000, 16)`, `GlobalAveragePooling1D()`, `Dense(1, activation="sigmoid")`, 30 epochs, `batch_size=32`, about 30 steps an epoch): under 30 s; the embedding table starts from random numbers and learns slower than TF-IDF, so it gets 30 epochs and the page says so in one line; `TextVectorization.adapt` on the training posts takes about a second.

## Claims

- Keras models are trained with `fit`, which accepts `validation_data=(x_val, y_val)` and returns a History whose `history` dict holds `loss` and `val_loss` (and each metric with its `val_` twin) per epoch, the source of the curves read in step 1 — [tf.keras.Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model)
- `tf.keras.utils.set_random_seed(seed)` sets the Python, NumPy and backend random seeds in one call, which is what "seeds fixed" means for a fair before-and-after — [tf.keras.utils.set_random_seed](https://www.tensorflow.org/api_docs/python/tf/keras/utils/set_random_seed)
- `Dropout(rate)` sets a random fraction `rate` of its inputs to 0 at each training step and scales the rest up by 1 / (1 - rate); it is active only during `fit`, and at `predict` and `evaluate` time every unit is used; because it changes the weights that are learned, validation loss changes too, which is the reason to use it — [tf.keras.layers.Dropout](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dropout)
- `BatchNormalization` normalizes its inputs with the current batch's mean and spread during training and with moving averages it stored during training at inference — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization)
- `EarlyStopping(monitor="val_loss", patience=n, restore_best_weights=True)` stops training when the monitored value has not improved for n epochs and puts back the weights of the best epoch — [tf.keras.callbacks.EarlyStopping](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping)
- Adam's `learning_rate` argument defaults to 0.001, and a different rate is set with `optimizer=tf.keras.optimizers.Adam(learning_rate=...)` in `compile` — [tf.keras.optimizers.Adam](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/Adam)
- A learning rate that is too small makes the loss fall slowly over many epochs; one that is too large makes the loss bounce or grow instead of settling — [Machine Learning Crash Course: hyperparameters](https://developers.google.com/machine-learning/crash-course/linear-regression/hyperparameters)
- Overfitting shows as training loss still falling while validation loss rises; underfitting shows as both losses high and flat — [Overfit and underfit (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
- A sigmoid output is a probability, and Keras's precision and recall metrics turn it into a yes or no at a threshold of 0.5 unless told otherwise; the cut can move, trading precision against recall, and the page names this as one lever line only (tuning the threshold is week 8) — [tf.keras.metrics.Precision](https://www.tensorflow.org/api_docs/python/tf/keras/metrics/Precision)
- A denoising autoencoder is trained with a corrupted input and the clean input as the target, `fit(x_noisy, x_clean)`, and the TensorFlow tutorial draws the noisy and the denoised images side by side as its evidence — [Intro to Autoencoders (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/generative/autoencoder)
- `np.clip(x, 0.0, 1.0)` keeps the noisy pixels in the 0 to 1 range that the sigmoid output layer can reproduce — [numpy.clip](https://numpy.org/doc/stable/reference/generated/numpy.clip.html)
- `TextVectorization(max_tokens=10000, output_sequence_length=200)` maps raw strings to integer word ids, padding or cutting each post to 200; `adapt(texts)` learns the vocabulary and is called on the training posts only — [tf.keras.layers.TextVectorization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/TextVectorization)
- `Embedding(input_dim, output_dim)` is a trainable lookup table from an integer id to a list of `output_dim` numbers; `input_dim` must be at least the vocabulary size (`max_tokens`) — [tf.keras.layers.Embedding](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Embedding)
- `GlobalAveragePooling1D` averages the per-word vectors over the sequence axis, so a post of any length becomes one fixed-length list for a Dense layer — [tf.keras.layers.GlobalAveragePooling1D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/GlobalAveragePooling1D)
- `TfidfVectorizer(max_features=5000)` fitted on the training posts into a Dense network is the baseline; it ignores word order, and so does an Embedding plus average-pooling model — [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- `fetch_20newsgroups(categories=..., remove=("headers", "footers", "quotes"))` downloads the corpus on its first call and strips the sender's metadata so the model reads the post — [fetch_20newsgroups](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html)
- TFLearn is unmaintained: its last release is 0.5.0 (2020-11-11, PyPI), the last commit on `master` is 2020-11-30, and as checked on 2026-11-18 it does not import on Colab's TensorFlow 2.21 (`tflearn/layers/recurrent.py` imports `is_sequence` from `tensorflow.python.util.nest`, which 2.21 no longer defines, and its `__init__.py` calls `tf.disable_v2_behavior()`); the page shows its code only in a fenced block labelled "TFLearn (history, do not run)" — [tflearn on PyPI](https://pypi.org/project/tflearn/), [TFLearn repository](https://github.com/tflearn/tflearn)
- This day's TFLearn terms map to Keras as: `tflearn.dropout` / `tflearn.layers.core.dropout` to `tf.keras.layers.Dropout` (TFLearn's argument is `keep_prob`, the share kept, so its 0.8 is Keras's `Dropout(0.2)`); `tflearn.batch_normalization` to `tf.keras.layers.BatchNormalization`; `tflearn.embedding` to `tf.keras.layers.Embedding`; `tflearn.regression(learning_rate=...)` to `model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=...))`; `DNN.fit(validation_set=...)` to `model.fit(validation_data=...)`; TFLearn has no built-in early-stopping callback, and Keras's is `tf.keras.callbacks.EarlyStopping` — [TFLearn repository](https://github.com/tflearn/tflearn), [Keras layers API](https://www.tensorflow.org/api_docs/python/tf/keras/layers)

## Notes depth

### Improving a model: one change, measured
- Interview questions: Your model's training accuracy is 99% and its validation accuracy is 90%; what do you do first?; Why change one thing at a time?; Why must the test set stay out of these choices, and what do you report when a change did not help?
- Adjacent concept: overfitting against underfitting as read from the two curves — it is the sign that says which lever to pull; no regularization theory.
- Trade-off or limit: a gain of 0.1 point on 6,000 validation rows may be noise; with seeds fixed a rerun repeats the number, but a different seed can flip a small gap, so a tiny gap is reported as "did not help" — [Overfit and underfit](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
- Recognise on sight: `tf.keras.layers.Dropout(0.2)` between two Dense layers; `callbacks=[tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)]`; `results.append({"model": "dropout 0.2", "val_loss": ..., "val_accuracy": ...})`; in an old tutorial, `net = tflearn.dropout(net, 0.8)` (history only)
- Claims:
  - Read both curves and the wrong examples before choosing a lever: the curves speak about fit (too little, too much), the wrong examples about the data, the labels and the preprocessing — [Overfit and underfit](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
  - More hidden units or layers raise capacity: try them when both curves stay high (underfit), and expect more overfitting when validation loss already rises; a second architecture (a CNN for images) is the bigger version of the same lever — [tf.keras.layers.Dense](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
  - Dropout and early stopping are the levers for a growing gap between training and validation loss; early stopping with `restore_best_weights=True` lets validation loss choose the epoch count — [tf.keras.callbacks.EarlyStopping](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping)
  - Batch normalization is tried when training is slow or unsteady in a deeper stack — [tf.keras.layers.BatchNormalization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization)
  - Each trained model adds one row to the results table from `model.evaluate(x_val, y_val)`, which returns the loss and then the metrics in the order `compile` listed them — [tf.keras.Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model)
  - The test set is scored once, on the kept model; scoring it after each change turns it into a second validation set and its number stops being an honest estimate — [Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html)

### Denoising autoencoders
- Interview questions: What is an autoencoder trained to do?; What changes for a denoising one?; Why clip the noisy image to 0 to 1?
- Adjacent concept: Tuesday's autoencoder with its bottleneck and error threshold — the denoising one keeps the model shape and changes only what `fit` is given.
- Trade-off or limit: the noise level 0.3 is a choice: too little and the model learns to copy, too much and the digit cannot be recovered; the rebuilt digits are blurry because the loss is MSE — [Intro to Autoencoders](https://www.tensorflow.org/tutorials/generative/autoencoder)
- Recognise on sight: `x_tr_noisy = np.clip(x_tr + 0.3 * np.random.normal(size=x_tr.shape), 0.0, 1.0)` then `denoiser.fit(x_tr_noisy, x_tr, ...)`
- Claims:
  - The TensorFlow autoencoder tutorial has a denoising section that adds random noise to the input, clips it, and trains against the clean image — [Intro to Autoencoders](https://www.tensorflow.org/tutorials/generative/autoencoder)
  - The validation pair is `(x_val_noisy, x_val)`, with the noise drawn once before `fit` so every epoch is scored on the same rows — [tf.keras.Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model)
  - The 784-32-784 shape from Tuesday is reused unchanged; its sigmoid output gives pixels between 0 and 1, matching the clean target — [tf.keras.layers.Dense](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
  - A grid of noisy, rebuilt and clean digits is the evidence, as in the tutorial's side-by-side figure; the validation MSE alone does not show that the noise was removed — [Intro to Autoencoders](https://www.tensorflow.org/tutorials/generative/autoencoder)

### Text with TextVectorization and Embedding layers
- Interview questions: What does `TextVectorization` do, and why adapt it on the training text only?; What does an `Embedding` layer take in and give out?; When would TF-IDF beat an embedding model?
- Adjacent concept: Tuesday's TF-IDF into a Dense network is the baseline — the same posts, the same validation set, compared in one results table; what an embedding vector means and similarity between vectors stay in week 8.
- Trade-off or limit: with about a thousand short posts the embedding model learns its table from scratch and often matches TF-IDF rather than beating it; the page says so plainly when it does not help — [Word embeddings (TensorFlow text guide)](https://www.tensorflow.org/text/guide/word_embeddings)
- Recognise on sight: `vectorize = tf.keras.layers.TextVectorization(max_tokens=10000, output_sequence_length=200)`, `vectorize.adapt(np.array(texts_tr))`, `tf.keras.layers.Embedding(10000, 16)`, `tf.keras.layers.GlobalAveragePooling1D()`
- Claims:
  - `adapt` takes a numpy array of strings; the page converts the posts once with `np.array(texts_tr)` and turns each split into ids with `vectorize(...)` before `fit`, so the model's input is `Input(shape=(200,))` — [tf.keras.layers.TextVectorization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/TextVectorization)
  - Id 0 is padding and id 1 is the out-of-vocabulary token `[UNK]`, and `max_tokens` counts both, so the vocabulary holds 9,998 real words at most — [tf.keras.layers.TextVectorization](https://www.tensorflow.org/api_docs/python/tf/keras/layers/TextVectorization)
  - The layer can also sit inside the model so a saved model reads raw text; the TensorFlow text tutorial does this in its export step, named in one sentence on the page — [Basic text classification (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/keras/text_classification)
  - `Embedding(10000, 16)` holds 160,000 trainable numbers, which `summary()` shows, against the TF-IDF model's 5000 times 32 plus 32 in its first layer — [tf.keras.layers.Embedding](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Embedding)
  - Both models are scored with `model.evaluate` on the same validation posts and labels and shown in one `pd.DataFrame(results)` — [pandas.DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)

## Sources

- TensorFlow Keras API reference — https://www.tensorflow.org/api_docs/python/tf/keras
- tf.keras.Model — https://www.tensorflow.org/api_docs/python/tf/keras/Model
- Overfit and underfit (TensorFlow tutorial) — https://www.tensorflow.org/tutorials/keras/overfit_and_underfit
- Intro to Autoencoders (TensorFlow tutorial) — https://www.tensorflow.org/tutorials/generative/autoencoder
- Word embeddings (TensorFlow text guide) — https://www.tensorflow.org/text/guide/word_embeddings
- Basic text classification (TensorFlow tutorial) — https://www.tensorflow.org/tutorials/keras/text_classification
- tf.keras.layers.TextVectorization — https://www.tensorflow.org/api_docs/python/tf/keras/layers/TextVectorization
- tf.keras.callbacks.EarlyStopping — https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping
- tf.keras.metrics.Precision — https://www.tensorflow.org/api_docs/python/tf/keras/metrics/Precision
- Machine Learning Crash Course: hyperparameters — https://developers.google.com/machine-learning/crash-course/linear-regression/hyperparameters
- scikit-learn TfidfVectorizer — https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- scikit-learn fetch_20newsgroups — https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html
- pandas DataFrame reference — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
- tflearn on PyPI (history: last release) — https://pypi.org/project/tflearn/
- TFLearn repository (history: last commit, layer names) — https://github.com/tflearn/tflearn

## Glossary terms

- validation data | Rows held back from fitting that are used to compare models and choose changes, with the test set kept for one final score. | aka: validation set, val set
- denoising autoencoder | An autoencoder given a noisy copy of each input and trained to output the clean original. | aka: denoising autoencoders, DAE
- TextVectorization | A Keras layer that turns raw strings into fixed-length lists of integer word ids using a vocabulary learned from the training texts. | aka: text vectorization layer
- Embedding layer | A trainable table in a Keras model that turns each word id into a short list of numbers learned during training. | aka: tf.keras.layers.Embedding, Embedding(10000, 16)
- global average pooling | Averaging a list of per-word vectors into one vector of the same width, so a text of any length gives a fixed-size input. | aka: GlobalAveragePooling1D
- out-of-vocabulary token | The one id a text layer gives every word that is not in its learned vocabulary. | aka: OOV token, [UNK]
- lever | One setting you change to try to improve a model, such as the hidden units, the learning rate or dropout. | aka: levers, improvement lever
- capacity | How much a network can learn, set mostly by its number of layers and units; too little underfits, too much overfits. | aka: model capacity

## Common pitfalls

- Changing several things at once (a wider layer, dropout and a new learning rate) and then not knowing which one moved the number; or leaving the seed unset so a rerun of the same model differs.
- Comparing before and after on different data, or scoring the test set after every change, so the final test number is no longer an honest estimate.
- Reading a 0.1-point gain as a win, or leaving out a change that did not help; the results table keeps every row and the kept model is the better validation number.
- Fitting the denoising autoencoder on noisy input and noisy target (`fit(x_noisy, x_noisy)`), forgetting to clip the noise so pixels fall outside 0 to 1, or drawing fresh noise for the validation rows on every call so the validation loss wobbles.
- Leaving `output_sequence_length` unset on `TextVectorization`: the training ids come out as wide as the longest training post and the validation ids as wide as the longest validation post, so they do not match each other or `Input(shape=(200,))`; and adapting on all posts, validation included, which leaks the validation words into the vocabulary.
- Copying TFLearn's `dropout(net, 0.8)` into Keras as `Dropout(0.8)`: TFLearn's number is the share kept, Keras's is the share dropped, so the Keras layer would switch off 80% of the units.

## Demo plan hints

- No block is delivered (self-directed page day, demoFormat none): the page's "Run in Colab" cells are the only demonstration, each runnable in a fresh notebook with only the cells above it (imports, `RANDOM_STATE = 42` and both seeds, the MNIST cell with the 54,000 / 6,000 split, `plot_history` and `show_image_grid`).
- Part A worked example: fit `base_20` (784-128-10, 20 epochs, `batch_size=128`) and show on one `plot_history` chart validation loss turning up after a few epochs; read the misclassified grid; add `Dropout(0.2)` after the hidden layer as `dropout_20`, refit with the same seed, epochs and validation data; show the two-row results table and one plain sentence on whether it helped; then the test cell once on the kept model. The TFLearn mapping sits in one fenced "TFLearn (history, do not run)" block.
- Denoising stretch: noise drawn once for `x_tr` and `x_val` (`0.3 * np.random.normal(size=...)`, clipped to 0 to 1), `denoiser` 784-32-784 fitted 10 epochs at `batch_size=256` on `(x_tr_noisy, x_tr)` with `validation_data=(x_val_noisy, x_val)`; one `show_image_grid` of five noisy, five rebuilt and five clean digits in three rows of five.
- Text stretch: rebuild the TF-IDF baseline in the page's own cells (the same `TOPICS`, the same `train_test_split(test_size=0.2, stratify=labels, random_state=RANDOM_STATE)`, 10 epochs, `batch_size=32`), then `embed_model` (30 epochs, `batch_size=32`) on `vectorize`'s ids for the same posts, and both rows in one results table; the fresh run that stamps the versions times every fit against the fit plan above and the 3-minute bar.
