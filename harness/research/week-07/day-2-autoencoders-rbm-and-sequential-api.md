# w07d2 — Autoencoders, RBM & the Keras Sequential API

gate: light
verified: 2026-11-19
week: 7 · TensorFlow
day: 2 · day-2-autoencoders-rbm-and-sequential-api

version-stamps:
  - python: 3.13.18 on Colab, not the course 3.15 (verified 2026-11-19; runs in Colab; TensorFlow has no 3.15 wheel, so no cp315 wheel is picked; source: googlecolab/backend-info os-info.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt)
  - tensorflow: 2.21.0 (verified 2026-11-19; runs in Colab; source: googlecolab/backend-info pip-freeze.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt, line `tensorflow==2.21.0`)
  - keras: 3.13.2, reached as `tf.keras` (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt; `tf_keras==2.21.0` is also installed but `tf.keras` resolves to Keras 3 unless `TF_USE_LEGACY_KERAS` is set, which the notebook never sets)
  - numpy: 2.4.6 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt)
  - scipy: 1.16.3 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt; not imported by this day's cells)
  - scikit-learn: 1.6.1 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt; `BernoulliRBM`, `fetch_20newsgroups`, `TfidfVectorizer`, `train_test_split`, the metric functions)
  - pandas: 2.2.3 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt)
  - matplotlib: 3.10.0 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt)
  - seaborn: 0.13.2 (verified 2026-11-19; runs in Colab; source: the same pip-freeze.txt; imported by the setup cell only if the convention's stamp cell is kept)
  - tflearn: 0.5.0, released 2020-11-11 (PyPI); last commit on `master` 2020-11-30 (GitHub API); history only, never imported in a cell (verified 2026-11-19; source: https://pypi.org/pypi/tflearn/json and https://api.github.com/repos/tflearn/tflearn/commits?sha=master&per_page=1)
  - stamp note: backend-info records the image of Colab's latest submitted runtime build and can lead or lag production by a release. No Colab runtime was run for this brief (light gate, no browser): the notebook author must run the convention's stamp cell on a fresh runtime and quote that printout where it differs. Four items are still owed from that runtime and are listed under the demo plan hints: the `import tflearn` failure, the `BernoulliRBM` `learning_rate` and `n_iter`, the `fetch_20newsgroups` download time, and the wrong-post count on the validation set.

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- An autoencoder is a network trained to reproduce its own input through a narrow layer (the bottleneck), so it needs no labels; the input is also the target. — [Build an autoencoder (Keras example)](https://keras.io/examples/vision/autoencoder/)
- A dense autoencoder is an encoder that compresses the input to a small code and a decoder that rebuilds the input from that code. — [Build an autoencoder (Keras example)](https://keras.io/examples/vision/autoencoder/)
- A sigmoid output layer with the mean-squared-error (or binary cross-entropy) loss suits pixels scaled to the range 0 to 1, because a sigmoid can only produce values in (0, 1). — [tf.keras.activations.sigmoid](https://www.tensorflow.org/api_docs/python/tf/keras/activations/sigmoid)
- `fit(x, x, validation_data=(x_val, x_val))` trains an autoencoder; the targets are the inputs. — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
- Reconstruction error per example (the mean squared difference between an input and its rebuild) is a score for how unusual the example is relative to the training data; a threshold on it turns the score into a flag. — [Anomaly detection with autoencoders (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/generative/autoencoder)
- The TensorFlow tutorial picks a threshold from the errors on normal training data (mean plus one standard deviation); a percentile of errors on held-out data, as the notebook does, is another common choice, and either choice is a decision rather than a fact about the data. — [Anomaly detection with autoencoders (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/generative/autoencoder)
- `numpy.percentile(errors, 99)` returns the value below which 99 percent of the errors lie, so by construction about one validation image in a hundred is above it. — [numpy.percentile](https://numpy.org/doc/stable/reference/generated/numpy.percentile.html)
- scikit-learn's `BernoulliRBM` is a restricted Boltzmann machine with binary visible and hidden units, fitted with stochastic maximum likelihood (persistent contrastive divergence); it takes `n_components`, `learning_rate`, `batch_size`, `n_iter` and `random_state`. — [BernoulliRBM](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.BernoulliRBM.html)
- `BernoulliRBM.transform` returns the hidden-unit activation probabilities for each row; `components_` holds the weights (shape hidden by visible) and `intercept_visible_` the visible biases; `gibbs` also exists to resample the visible units. — [BernoulliRBM](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.BernoulliRBM.html)
- In a restricted Boltzmann machine there are links only between the visible and the hidden layer, none inside a layer, and this restriction is what makes the hidden units cheap to compute. — [Neural network models (unsupervised): Restricted Boltzmann machines (scikit-learn user guide)](https://scikit-learn.org/stable/modules/neural_networks_unsupervised.html#restricted-boltzmann-machines)
- Keras has no RBM layer; an RBM is a scikit-learn estimator here. — [Keras layers API](https://keras.io/api/layers/)
- A `Sequential` model is a plain stack of layers where each layer has exactly one input tensor and one output tensor; it is wrong when a model has several inputs or outputs, needs layer sharing or a non-linear topology. — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
- A Sequential model can be built from a list, or by calling `model.add(layer)` one layer at a time, and read back through `model.layers`. — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
- A model is itself a layer, so a `Sequential` can be a layer inside another `Sequential`, and each part can be called alone. — [Making new layers and models via subclassing](https://www.tensorflow.org/guide/keras/making_new_layers_and_models_via_subclassing)
- Setting `layer.trainable = False` freezes a layer's weights for training, and the change takes effect when the model is compiled afterward. — [Transfer learning and fine-tuning](https://www.tensorflow.org/guide/keras/transfer_learning)
- `TfidfVectorizer(max_features=N)` keeps only the N terms with the highest term frequency across the corpus it is fitted on; `fit` on training texts only, then `transform` the rest. — [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- `fetch_20newsgroups` downloads the dataset on first use and caches it; `categories=` picks topics and `remove=("headers", "footers", "quotes")` strips text that lets a model identify a post without reading it. — [fetch_20newsgroups](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html)
- `precision_score`, `recall_score` and `f1_score` take the true labels first and the predictions second; F1 is the harmonic mean of precision and recall. — [Metrics and scoring (scikit-learn user guide)](https://scikit-learn.org/stable/modules/model_evaluation.html)
- `confusion_matrix` rows are true labels and columns are predictions; for a binary problem `ravel()` gives true negatives, false positives, false negatives, true positives in that order. — [confusion_matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html)
- TFLearn 0.5.0 (PyPI, 2020-11-11) is the last release; the project is unmaintained and is built on TensorFlow 1 graph mode. — [tflearn on PyPI](https://pypi.org/project/tflearn/)
- TensorFlow 1 style code (sessions, placeholders, `tf.contrib`) has a documented migration path to TensorFlow 2 and Keras. — [Migrate to TensorFlow 2](https://www.tensorflow.org/guide/migrate)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Collaborative filtering with RBM
- Interview questions: What is collaborative filtering and what does it need as data?; What does a restricted Boltzmann machine learn from a ratings table, and what do its hidden units stand for?; What does a recommender do for a brand-new user with no ratings (the cold-start problem), and how would you cope?
- Adjacent concept: matrix factorisation as the method teams use instead of RBMs today — one sentence only; it fills the same blanks by splitting the table into two smaller ones, and it belongs here because the interviewer asks "what would you use now".
- Trade-off or limit: an RBM on a table of 0 and 1 treats "not seen" and "not liked" alike, because its visible units are binary — [Neural network models (unsupervised) (scikit-learn user guide)](https://scikit-learn.org/stable/modules/neural_networks_unsupervised.html#restricted-boltzmann-machines); and a new user or film with no history has nothing to be matched on (the cold-start problem) — [Collaborative filtering advantages and disadvantages (Google ML recommendation course)](https://developers.google.com/machine-learning/recommendation/collaborative/summary)
- Recognise on sight: `rbm = BernoulliRBM(n_components=2, random_state=42).fit(ratings)` then `hidden = rbm.transform(ratings)` and `1 / (1 + np.exp(-(hidden @ rbm.components_ + rbm.intercept_visible_)))`.
- Claims:
  - Collaborative filtering recommends to a user what similar users liked, using only the ratings table, never the contents of the films — [Collaborative filtering (Google ML Crash Course)](https://developers.google.com/machine-learning/recommendation/collaborative/basics)
  - In an RBM the visible units are the films and the hidden units are learned tastes; each hidden unit connects to every film and none connect within a layer — [Neural network models (unsupervised) (scikit-learn user guide)](https://scikit-learn.org/stable/modules/neural_networks_unsupervised.html#restricted-boltzmann-machines)
  - `rbm.transform(ratings)` gives each user's hidden-taste probabilities; multiplying by `components_` and adding `intercept_visible_` before a sigmoid rebuilds the user's row, which scores the unseen films — [BernoulliRBM](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.BernoulliRBM.html)
  - `n_components=1` leaves one taste, so two groups with different likes are merged into one — [BernoulliRBM](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.BernoulliRBM.html)
  - Keras has no RBM layer, and a team today would pick matrix factorisation or a deep recommender — [Recommendation systems overview (Google for Developers)](https://developers.google.com/machine-learning/recommendation/overview/types)

### Autoencoders
- Interview questions: What is an autoencoder and why does it need no labels?; Why must the bottleneck be smaller than the input?; What are the activation and the loss of the output layer for images scaled to 0 to 1, and why?
- Adjacent concept: dimensionality reduction by PCA — a linear autoencoder with a small bottleneck learns a similar subspace, which is why the interviewer asks how an autoencoder differs; one sentence only.
- Trade-off or limit: a bottleneck that is too wide lets the network copy the input and learn nothing useful, and one that is too narrow blurs the rebuilds — [Build an autoencoder (Keras example)](https://keras.io/examples/vision/autoencoder/)
- Recognise on sight: `autoencoder.fit(x_tr, x_tr, ..., validation_data=(x_val, x_val))` and `Dense(784, activation="sigmoid")` as the last layer.
- Claims:
  - The encoder maps the 784 pixels to the code (here 32 numbers) and the decoder maps the code back to 784 pixels, so the model has 784*32+32 = 25,120 plus 32*784+784 = 25,872 parameters, 50,992 in all (the number the `### 2.3` `summary()` prints and its markdown quotes) — [Build an autoencoder (Keras example)](https://keras.io/examples/vision/autoencoder/) (derived: a Dense layer holds inputs times units plus units parameters, per the [Dense layer API](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense))
  - The reconstruction loss is the mean squared difference between the input and its rebuild, so the model needs no label — [Intro to Autoencoders (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/generative/autoencoder)
  - Passing the validation data as `(x_val, x_val)` gives a validation loss curve that can be drawn on one chart beside the training curve — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
  - A denoising autoencoder is trained to rebuild a clean image from a noisy copy; it is named in one sentence and built on Friday's page — [Intro to Autoencoders (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/generative/autoencoder)

### An autoencoder as an anomaly detector (notes step 4, inside "Autoencoders")
- Interview questions: How would you use an autoencoder to flag unusual examples?; How do you choose the threshold, and on which data?; Why is a lower reconstruction error not always better for flagging?
- Adjacent concept: precision and recall of the flags — the threshold trades false alarms against misses, the same trade-off the text build reads in its confusion matrix.
- Trade-off or limit: an autoencoder trained on all digits learns to rebuild many shapes, so an anomaly it has partly learned goes unflagged; a model that rebuilds everything well flags nothing — [Anomaly detection with autoencoders (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/generative/autoencoder)
- Recognise on sight: `errors = np.mean((x - model.predict(x)) ** 2, axis=1)` and `flags = errors > threshold`.
- Claims:
  - The error per example is the mean over the 784 pixels, `axis=1`, so one number per image — [numpy.mean](https://numpy.org/doc/stable/reference/generated/numpy.mean.html)
  - A threshold chosen on data the model was trained on is optimistic, because training errors are smaller than errors on new data, so the notebook uses the validation errors; this is the general rule that every choice is judged on data the model did not learn from — [Common pitfalls and recommended practices (scikit-learn user guide)](https://scikit-learn.org/stable/common_pitfalls.html). Contrast for the page: the TensorFlow tutorial picks its threshold from the training loss (mean plus one standard deviation), a simpler choice the notebook does not follow — [Intro to Autoencoders (TensorFlow tutorial)](https://www.tensorflow.org/tutorials/generative/autoencoder)
  - The digits with the highest error are usually thick, unusual or ambiguous strokes (confirm on the fresh run before the page quotes it) — [Build an autoencoder (Keras example)](https://keras.io/examples/vision/autoencoder/)
  - A 64-number bottleneck should rebuild better than 32 on average, and a better rebuild also rebuilds oddities better, so the gap between normal and unusual errors can shrink — [Build an autoencoder (Keras example)](https://keras.io/examples/vision/autoencoder/)

### TFLearn API
- Interview questions: What is TFLearn and what would you use today?; What does `tflearn.fully_connected` correspond to in Keras?; Why does an old TFLearn tutorial fail on a current TensorFlow?
- Adjacent concept: the TensorFlow 1 to 2 migration — TFLearn was a wrapper over TensorFlow 1 graph mode, which is the part TensorFlow 2 replaced.
- Trade-off or limit: TFLearn is unmaintained (last release 0.5.0 on 2020-11-11, last commit 2020-11-30) and does not import on Colab's TensorFlow 2.21; code from it is read, never run — [tflearn on PyPI](https://pypi.org/project/tflearn/)
- Recognise on sight: `net = tflearn.input_data(shape=[None, 784])`, `net = tflearn.fully_connected(net, 128, activation='relu')`, `net = tflearn.regression(net)`, `model = tflearn.DNN(net)`, `model.fit(X, Y)`.
- Claims:
  - `tflearn.input_data` maps to `tf.keras.Input`, `tflearn.fully_connected` to `tf.keras.layers.Dense`, `tflearn.regression` to `model.compile`, `tflearn.DNN(...)` and its `fit` to `model.fit`, TFLearn's stacking to `tf.keras.Sequential`, `tflearn.merge` to `tf.keras.layers.Concatenate`, `tflearn.batch_normalization` to `tf.keras.layers.BatchNormalization` — [Keras layers API](https://keras.io/api/layers/)
  - `DNN.save` and `DNN.load` map to `model.save("....keras")` and `tf.keras.models.load_model`; `tensorboard_dir` maps to `tf.keras.callbacks.TensorBoard(log_dir=...)` — [Save, serialize, and export models](https://www.tensorflow.org/guide/keras/serialization_and_saving)
  - The author's statement that `import tflearn` fails on TensorFlow 2.21 (`is_sequence` missing from `tensorflow.python.util.nest`, and the `tf.disable_v2_behavior()` call in `__init__.py`) is from reading the source, not from a run; the notebook author confirms it in a scratch Colab notebook before any page says it was run — [tflearn on PyPI](https://pypi.org/project/tflearn/)
  - Keras is TensorFlow's own high-level API and is the replacement the TensorFlow documentation points to — [Migrate to TensorFlow 2](https://www.tensorflow.org/guide/migrate)

### Composing models in TFLearn
- Interview questions: Can one model be a layer of another model in Keras?; How do you use only the encoder of a trained autoencoder?; What does freezing a layer do?
- Adjacent concept: transfer learning — reusing a trained encoder under a new classifier is the same idea named in one sentence, and the going-deeper cell shows it with 3 epochs.
- Trade-off or limit: a frozen encoder keeps the features it learned for rebuilding digits, which may not be the ones that separate the classes best — [Transfer learning and fine-tuning](https://www.tensorflow.org/guide/keras/transfer_learning)
- Recognise on sight: `composed = tf.keras.Sequential([encoder, decoder])` and `encoder.trainable = False`.
- Claims:
  - A `Sequential` built from two `Sequential` models works because a model is a layer; `composed.summary()` shows the two models as single rows, each with its own parameter count — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
  - Layers named in the constructor (`name="encoder"`) can be fetched from the composed model with `get_layer` or read in `summary()` — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
  - The weights of the parts are shared with the composed model, so training `composed` trains `encoder` and `decoder`, and `encoder.predict` afterward gives the learned codes — [Making new layers and models via subclassing](https://www.tensorflow.org/guide/keras/making_new_layers_and_models_via_subclassing)
  - Composition with `tflearn.merge` in TFLearn becomes `Concatenate` in the Functional API, which Wednesday teaches — [The Functional API](https://www.tensorflow.org/guide/keras/functional_api)

### Sequential composition
- Interview questions: What is a Sequential model and when can you not use one?; Name three ways to build one.; What happens if the first layer has no declared input shape?
- Adjacent concept: a model is a layer — one Sequential can sit inside another (`### 4.1`), and a built stack is inspected by reading `model.layers` or `model.get_layer("name")`; both belong to this day.
- Trade-off or limit: Sequential cannot share a layer, branch, merge or have several inputs or outputs; Wednesday handles two inputs or a skip (one line only) — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
- Recognise on sight: `model = tf.keras.Sequential()` followed by `model.add(tf.keras.layers.Dense(...))`, or a list passed to the constructor.
- Claims:
  - A Sequential built without an input declaration has no weights until it is called on data or given a `tf.keras.Input`, so `summary()` can show an unbuilt model — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
  - `model.layers` returns the list of layers in order and `model.pop()` removes the last one — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
  - A Keras 3 `Dense` layer declares only its number of units, not its input size, and builds its weights from whatever width arrives, so reordering the `.add()` calls of Dense layers after `Input` never raises a shape error: it gives a different model with a different `summary()` and parameter count (for example `Dense(10)` before `Dense(128)` gives 784*10+10 = 7,850 plus 10*128+128 = 1,408, 9,258 parameters against 101,770, and an output 128 wide); the one reorder that fails is an `Input` placed after a layer, and the author records that error's text on the fresh run — [Dense layer API](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense) and [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
  - A list, repeated `.add()` and a list followed by `.add()` give the same architecture, so the three builds print the same `summary()` — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)

### A text classifier built in a project's order (notes step 8; the day note's text build)
- Interview questions: Walk me through a text classifier you built; What does TF-IDF do and why fit the vectorizer on training posts only?; A model has 90% accuracy on a topic split but only 60% recall for one topic: what do you check next?
- Adjacent concept: bag of words against TF-IDF weighting — a plain word count treats every word alike, while the IDF part down-weights words that appear in almost every post ("the", "and", "it"), so the words that separate the topics carry the most weight; `max_features` then caps the vocabulary at the most frequent terms. (The only later-day mention allowed here is the one `### 6.9` limitations sentence the plan already holds.)
- Trade-off or limit: `max_features` trades vocabulary against columns and fit time, and a vocabulary fitted on the training posts leaves unseen words out of validation and test posts — [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- Recognise on sight: `vectorizer.fit_transform(texts_tr).toarray().astype("float32")` and `Dense(1, activation="sigmoid")` with `binary_crossentropy`.
- Claims:
  - `fit_transform` on training posts and `transform` on validation and test posts avoids learning the vocabulary and the document frequencies from the posts used to judge the model — [Common pitfalls and recommended practices: Data leakage (scikit-learn user guide)](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)
  - A single sigmoid unit with binary cross-entropy is the output for two classes; the 0.5 threshold on its probability turns it into a label — [tf.keras.losses.BinaryCrossentropy](https://www.tensorflow.org/api_docs/python/tf/keras/losses/BinaryCrossentropy)
  - Lowering the threshold from 0.5 to 0.3 raises recall and lowers precision for the positive class — [Metrics and scoring (scikit-learn user guide)](https://scikit-learn.org/stable/modules/model_evaluation.html)
  - `TfidfVectorizer.transform` returns a scipy sparse matrix; the notebook densifies it with `.toarray().astype("float32")` so every cell sees a plain float32 array, and the table is small enough to hold dense (a choice of the notebook, not a limit of Keras) — [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
  - The two topics' train subset is about 1,190 posts; after the 80/20 split about 950 are training rows and about 240 validation rows. About 950 rows by 5,000 columns in float32 is about 19 MB, and `max_features=20000` is about 76 MB, both small for a CPU runtime (derived: rows times columns times 4 bytes) — [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- The Sequential model — https://www.tensorflow.org/guide/keras/sequential_model
- Training and evaluation with the built-in methods — https://www.tensorflow.org/guide/keras/training_with_built_in_methods
- Making new layers and models via subclassing — https://www.tensorflow.org/guide/keras/making_new_layers_and_models_via_subclassing
- Transfer learning and fine-tuning — https://www.tensorflow.org/guide/keras/transfer_learning
- Save, serialize, and export models — https://www.tensorflow.org/guide/keras/serialization_and_saving
- The Functional API — https://www.tensorflow.org/guide/keras/functional_api
- Intro to Autoencoders (TensorFlow tutorial) — https://www.tensorflow.org/tutorials/generative/autoencoder
- Build an autoencoder (Keras example) — https://keras.io/examples/vision/autoencoder/
- Keras layers API — https://keras.io/api/layers/
- Migrate to TensorFlow 2 — https://www.tensorflow.org/guide/migrate
- Dense layer API — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense
- tf.keras.activations.sigmoid — https://www.tensorflow.org/api_docs/python/tf/keras/activations/sigmoid
- tf.keras.losses.BinaryCrossentropy — https://www.tensorflow.org/api_docs/python/tf/keras/losses/BinaryCrossentropy
- BernoulliRBM — https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.BernoulliRBM.html
- Neural network models (unsupervised) (scikit-learn user guide) — https://scikit-learn.org/stable/modules/neural_networks_unsupervised.html
- fetch_20newsgroups — https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html
- TfidfVectorizer — https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- confusion_matrix — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
- Metrics and scoring (scikit-learn user guide) — https://scikit-learn.org/stable/modules/model_evaluation.html
- Common pitfalls and recommended practices (scikit-learn user guide) — https://scikit-learn.org/stable/common_pitfalls.html
- numpy.percentile — https://numpy.org/doc/stable/reference/generated/numpy.percentile.html
- numpy.mean — https://numpy.org/doc/stable/reference/generated/numpy.mean.html
- Collaborative filtering (Google ML Crash Course) — https://developers.google.com/machine-learning/recommendation/collaborative/basics
- Collaborative filtering advantages and disadvantages (Google ML recommendation course) — https://developers.google.com/machine-learning/recommendation/collaborative/summary
- Recommendation systems overview (Google for Developers) — https://developers.google.com/machine-learning/recommendation/overview/types
- tflearn on PyPI — https://pypi.org/project/tflearn/
- Colab runtime package list (googlecolab/backend-info) — https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt
- Colab runtime Python version (googlecolab/backend-info) — https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- autoencoder | A network trained to rebuild its own input through a narrow middle layer, so it needs no labels and learns a short code for each input. | aka: autoencoders, auto-encoder
- bottleneck | The narrow layer in the middle of an autoencoder whose few numbers are all the decoder gets to rebuild the input from. | aka: bottleneck layer, code layer
- reconstruction error | How far an autoencoder's rebuild is from the original input, averaged over the pixels or features, used as a score for how unusual an example is. | aka: reconstruction loss, rebuild error
- restricted Boltzmann machine | A two-layer network of visible and hidden units, linked across the layers but never within one, that learns hidden tastes able to rebuild its input rows. | aka: RBM, RBMs
- collaborative filtering | Recommending to a user what similar users liked, using only the table of who rated what and no facts about the items. | aka: collaborative filter, ratings-based recommendation
- Keras Sequential model | A Keras model built as a plain stack of layers in which each layer has one input and feeds the next. | aka: tf.keras.Sequential, Sequential API

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Fitting the autoencoder with the labels (`fit(x_tr, y_tr)`) or forgetting that the target is the input: the loss shape errors or the model learns nothing, and the learner blames the architecture.
- Choosing the anomaly threshold from training errors, or reading a high percentile as "this share of images is abnormal": the 99th percentile of validation errors flags about 1% by construction, so the count of flags says nothing about how many digits are really odd.
- Believing a lower reconstruction error is always better: the 64-number bottleneck rebuilds everything well, odd digits included, so it can flag less usefully than the 32-number one.
- Running `import tflearn` or copying a TFLearn tutorial and treating the failure as a typo or a missing `pip install`; the library targets TensorFlow 1 and is history, and every call has a Keras line in the mapping table.
- Fitting the `TfidfVectorizer` on all posts (or on validation and test posts) before the split, or calling `fit_transform` again on the validation posts: the vocabulary changes, the columns shift and the metrics are optimistic or meaningless.
- Forgetting `.toarray().astype("float32")` or the `Input(shape=(5000,))` that must equal the vocabulary size: with `max_features=20000` the improvement attempt needs `shape=(20000,)` too, and the shape error is read as a data problem.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Sections 1 and 2 (the RBM, then the autoencoder build): print the 8-by-6 ratings table, fit `BernoulliRBM(n_components=2)`, rank each user's unseen films and show the planted blank on top; then `### 2.5` originals over rebuilds, `### 2.6` the error histogram with the 99th-percentile line, `### 2.7` the ten worst rebuilds with their errors, and the `### 2.8` before-and-after row. Open owed items for the author on a fresh Colab CPU runtime: pick `learning_rate` and `n_iter` for `BernoulliRBM` (no run here: try about 0.05 to 0.1 and 200 to 1000 iterations against the table, and confirm the blank film ranks first for both groups with `random_state=42`) and time the two 10-epoch autoencoder fits (expected well under a minute each at 54,000 rows and batch size 256).
- Section 3 (TFLearn to Keras): the history block and the mapping table, with the `### 3.2` cell building the 784-128-10 network unfitted and printing `summary()` (101,770 parameters); before any page says "does not import on Colab", run `import tflearn` once in a scratch Colab notebook, record the exact error text and the date, and quote the printout; the brief's claim comes from reading the source, not from a run.
- Sections 4 and 5 (composing, Sequential): the `encoder`/`decoder` pair composed and trained 5 epochs, then `encoder.predict` on five digits showing five 32-number codes and `decoder.predict` turning one back into an image; three builds of one Sequential (list, `.add()`, `model.layers`) printing the same `summary()`, then the "Try changing" prompt with `.add()` in a different order: Dense layers after `Input` in any order build without error and print a different `summary()` and parameter count (`Dense(10)` before `Dense(128)`: 9,258 parameters, output 128 wide), which is the thing to read; only an `Input` added after a layer raises an error, so the prompt promises a changed summary, not a shape error.
- Section 6 (the text build): time `fetch_20newsgroups` for `rec.autos` and `rec.motorcycles` (train and test subsets) on a fresh runtime, since only the "well under a minute" claim decides the dataset (the archive is a single download of about 14 MB from scikit-learn's own host); after the split check the validation set (about 240 posts) leaves at least six wrong posts to read, and swap `TOPICS` for `comp.sys.ibm.pc.hardware` and `comp.sys.mac.hardware` if it does not; run the `### 6.6` "Try changing" prompt with a 0.3 threshold and read how precision falls and recall rises, and time both 10-epoch fits (5000 and 20000 columns) under 3 minutes.
