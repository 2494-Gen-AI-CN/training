# w06d5 — Perceptrons & TensorFlow basics

gate: light
verified: 2026-11-16
week: 6 · AI/ML fundamentals
day: 5 · day-5-perceptrons-and-tensorflow-basics

version-stamps:
  - python: 3.13.18 on Colab, not the course 3.15 (verified 2026-11-16; runs in Colab; TensorFlow has no 3.15 wheel, so no cp315 wheel is picked; source: googlecolab/backend-info os-info.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt)
  - tensorflow: 2.21.0 (verified 2026-11-16; runs in Colab; source: googlecolab/backend-info pip-freeze.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt, line `tensorflow==2.21.0`)
  - keras: 3.13.2, reached as `tf.keras` (verified 2026-11-16; runs in Colab; source: the same pip-freeze.txt, line `keras==3.13.2`; `tf_keras==2.21.0` is also installed but `tf.keras` resolves to Keras 3 unless `TF_USE_LEGACY_KERAS` is set, which the notebook never sets)
  - tensorboard: 2.21.0 (verified 2026-11-16; runs in Colab; source: the same pip-freeze.txt; only the section 6 fallback uses it)
  - numpy: 2.4.6 (verified 2026-11-16; runs in Colab; source: the same pip-freeze.txt)
  - scipy: 1.16.3 (verified 2026-11-16; runs in Colab; source: the same pip-freeze.txt; not imported by this day's cells)
  - scikit-learn: 1.6.1 (verified 2026-11-16; runs in Colab; source: the same pip-freeze.txt; `Perceptron`, `LogisticRegression`, `StandardScaler`, `make_blobs`, `load_breast_cancer`)
  - matplotlib: 3.10.0 (verified 2026-11-16; runs in Colab; source: the same pip-freeze.txt)
  - pydot: 4.0.1 (verified 2026-11-16; runs in Colab; source: the same pip-freeze.txt, line `pydot==4.0.1`; preinstalled, so `plot_model` needs no `!pip install`)
  - graphviz: system package 2.42.2 (the `dot` binary `plot_model` calls) plus the Python wrapper `graphviz==0.21` (verified 2026-11-16; runs in Colab; source: googlecolab/backend-info apt-list.txt, https://raw.githubusercontent.com/googlecolab/backend-info/main/apt-list.txt, line `graphviz/noble-updates,now 2.42.2-9ubuntu0.1 amd64 [installed]`, and pip-freeze.txt; confirmed: Colab ships pydot and graphviz, so section 6 shows `plot_model`; the TensorBoard trace stays a contingency only)
  - stamp note: backend-info records the image of Colab's latest submitted runtime build and can lead or lag the production runtime by a release; the notebook author runs the convention's stamp cell (`import sys, numpy, scipy, sklearn, matplotlib, tensorflow as tf; print(sys.version, numpy.__version__, scipy.__version__, sklearn.__version__, matplotlib.__version__, tf.__version__, tf.keras.__version__)`) plus `!pip show pydot` and `!dot -V` on a fresh runtime before the commit, and pages and the runbook quote that printout where it differs from the lines above

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- TensorFlow 2 runs operations eagerly by default: each op executes at once and returns a concrete value. — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
- `tf.function` traces a Python function into a `tf.Graph` that TensorFlow can optimise and reuse. — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
- Graph tracing runs the Python body once per new input signature, so a plain `print` inside it fires at trace time, while `tf.print` fires on every call. — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
- A `tf.Tensor` is immutable; a `tf.Variable` is a tensor-like object whose value can be changed with `assign`, `assign_add` and `assign_sub`. — [Introduction to Variables](https://www.tensorflow.org/guide/variable)
- `tf.constant` creates an immutable tensor; there is no assignment to it. — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)
- A `tf.Variable` created with `trainable=False` is excluded from the variables a gradient step updates. — [Introduction to Variables](https://www.tensorflow.org/guide/variable)
- TensorFlow 1 placeholders and sessions (`tf.placeholder`, `tf.Session`, `feed_dict`) belong to graph mode of TF1; TF2 replaces them with function arguments and eager execution, and the migration guide lists the replacement for each. — [Migrate to TensorFlow 2](https://www.tensorflow.org/guide/migrate)
- A graph is traced into TensorBoard with `tf.summary.trace_on(graph=True)`, one call of the traced function, then `tf.summary.trace_export` inside `with writer.as_default():`. — [Examining the TensorFlow Graph](https://www.tensorflow.org/tensorboard/graphs)
- A `tf.keras.Sequential` model is a stack of layers with one input and one output per layer. — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
- `Dense(1, activation="sigmoid")` on a 30-feature input holds a kernel of shape (30, 1) and a bias of shape (1,): 31 trainable parameters. — [Dense layer API](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
- `model.compile` takes an optimizer, a loss and metrics; `fit` trains for a number of epochs, `evaluate` returns loss and metrics on held-out data, `predict` returns outputs. — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
- `model.summary()` prints each layer, its output shape and its parameter count; `tf.keras.utils.plot_model` draws the layer graph and needs pydot and graphviz installed. — [plot_model API](https://www.tensorflow.org/api_docs/python/tf/keras/utils/plot_model)
- `tf.keras.activations` provides `sigmoid`, `tanh`, `relu` and `softmax`, but no step function. — [tf.keras.activations](https://www.tensorflow.org/api_docs/python/tf/keras/activations)
- scikit-learn's `Perceptron` implements the perceptron learning rule as a linear classifier trained with stochastic gradient descent and a perceptron loss and a constant learning rate. — [Linear models: Perceptron (scikit-learn user guide)](https://scikit-learn.org/stable/modules/linear_model.html#perceptron)
- `StandardScaler` rescales each feature to mean 0 and standard deviation 1, which lets sigmoid units and gradient-based optimisers converge in few epochs. — [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)
- Seeds are fixed in Keras with `tf.keras.utils.set_random_seed`, which seeds Python, NumPy and TensorFlow together. — [tf.keras.utils.set_random_seed](https://www.tensorflow.org/api_docs/python/tf/keras/utils/set_random_seed)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Activation functions
- Interview questions: What does an activation function do in a neuron?; Which activation suits a yes-or-no output, and why?; What does the step function output at z = 0, and why does the perceptron need one fixed rule for it?
- Adjacent concept: softmax for multi-class outputs — one sentence on why it turns a vector of scores into probabilities that sum to 1, the multi-class counterpart of a single sigmoid output.
- Trade-off or limit: sigmoid and tanh flatten at large positive or negative inputs, so a big change in z barely moves the output there; ReLU is cheap to compute but outputs 0 for every negative input — [Neural networks: Activation functions (Google ML Crash Course)](https://developers.google.com/machine-learning/crash-course/neural-networks/activation-functions)
- Recognise on sight: `tf.keras.layers.Dense(1, activation="sigmoid")`, `tf.keras.activations.relu(z)` and `np.where(z >= 0, 1, 0)` for the step.
- Claims:
  - Sigmoid maps any real number into (0, 1) and is the usual output for a yes-or-no label — [tf.keras.activations.sigmoid](https://www.tensorflow.org/api_docs/python/tf/keras/activations/sigmoid)
  - Tanh maps into (-1, 1) and is centred on 0 — [tf.keras.activations.tanh](https://www.tensorflow.org/api_docs/python/tf/keras/activations/tanh)
  - ReLU returns max(0, x) — [tf.keras.activations.relu](https://www.tensorflow.org/api_docs/python/tf/keras/activations/relu)
  - Softmax turns a vector of scores into probabilities that sum to 1 — [tf.keras.activations.softmax](https://www.tensorflow.org/api_docs/python/tf/keras/activations/softmax)
  - Each neuron applies a weighted linear sum followed by a non-linear activation; linear operations applied to linear operations are still linear, so without the non-linear activation extra weighted sums add no expressive power — [Neural network models (supervised) (scikit-learn user guide)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html) (supplement: [Neural networks: Activation functions (Google ML Crash Course)](https://developers.google.com/machine-learning/crash-course/neural-networks/activation-functions))
  - `tf.keras.activations` has no step function; the step is written in numpy, and the notebook's rule outputs 1 at z = 0 — [tf.keras.activations](https://www.tensorflow.org/api_docs/python/tf/keras/activations)

### Perceptrons - illustration, training, parameters
- Interview questions: Walk through what a perceptron computes; What are its parameters and what are the hyperparameters?; Why does the learning rule stop on linearly separable data but never settle otherwise?
- Adjacent concept: linear separability — a perceptron can only draw one straight boundary; the XOR failure is deferred to week 7 and never shown.
- Trade-off or limit: the rule converges only if the classes can be separated by a line; on overlapping classes the boundary keeps moving — [sklearn.linear_model.Perceptron](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Perceptron.html)
- Recognise on sight: `if y_pred != y: w += lr * (y - y_pred) * x; b += lr * (y - y_pred)`.
- Claims:
  - Parameters (weights, bias) are learned; learning rate and epochs are hyperparameters, which are not learnt by the estimator and are set by the person before training — [Tuning the hyper-parameters of an estimator (scikit-learn user guide)](https://scikit-learn.org/stable/modules/grid_search.html) (supplement: [Linear regression: Hyperparameters (Google ML Crash Course)](https://developers.google.com/machine-learning/crash-course/linear-regression/hyperparameters))
  - scikit-learn's perceptron updates its model only on mistakes and by default does not require a learning rate — [Linear models: Perceptron (scikit-learn user guide)](https://scikit-learn.org/stable/modules/linear_model.html#perceptron)
  - Starting from zero weights and bias, the learning rate only rescales w and b, so every prediction and the drawn boundary are identical at any rate; this is why the perceptron does not require a learning rate — [Linear models: Perceptron (scikit-learn user guide)](https://scikit-learn.org/stable/modules/linear_model.html#perceptron) (derived: every update adds lr times the same ±x, so w and b are lr times the lr = 1 values; the AND cell in `### 2.2` shows it)
  - `Perceptron` takes `eta0` (learning rate), `max_iter` (epochs) and `random_state` — [sklearn.linear_model.Perceptron](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Perceptron.html)
  - One sigmoid neuron trained on log loss is logistic regression — [sklearn LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)

### TensorFlow basics
- Interview questions: What is a tensor and what are its rank, shape and dtype?; What is eager execution?; What does `tf.function` buy you?
- Adjacent concept: NumPy interop — `tensor.numpy()` and `tf.constant(np_array)`; the same arithmetic reads the same.
- Trade-off or limit: tracing cost and retracing on new shapes or Python values — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
- Recognise on sight: `@tf.function` above a def, `tf.constant([[1., 2.], [3., 4.]])`.
- Claims:
  - A tensor has a dtype and a shape, and a default float is `float32` — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)
  - Operations like `tf.matmul` and `+` run eagerly and return tensors — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
  - `tf.function` is the TF2 route to a graph — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
  - The `.numpy()` method converts an eager tensor to a NumPy array — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)

### Graph visualization
- Interview questions: What is a computation graph?; How do you inspect a Keras model's structure?; What does TensorBoard's Graphs tab show?
- Adjacent concept: model structure vs. execution graph — `plot_model` draws layers, TensorBoard draws traced ops; they are different pictures.
- Trade-off or limit: `plot_model` needs pydot and the graphviz binary (both preinstalled on Colab, see the stamps); on a laptop without them it raises an error that asks for them, which says nothing about the model — [plot_model API](https://www.tensorflow.org/api_docs/python/tf/keras/utils/plot_model)
- Recognise on sight: `tf.keras.utils.plot_model(model, show_shapes=True)`; `%tensorboard --logdir logs`.
- Claims:
  - `model.summary()` lists layer types, output shapes and parameter counts — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
  - `show_shapes=True` adds input and output shapes to each node — [plot_model API](https://www.tensorflow.org/api_docs/python/tf/keras/utils/plot_model)
  - TensorBoard graph export needs the writer, `trace_on`, a call, then `trace_export` in the writer's context — [Examining the TensorFlow Graph](https://www.tensorflow.org/tensorboard/graphs)

### Constants, placeholders, variables
- Interview questions: What is the difference between `tf.constant` and `tf.Variable`?; What was a placeholder and what replaced it?; Which variables does training update?
- Adjacent concept: state — a variable is how a model keeps weights between calls; a tensor cannot.
- Trade-off or limit: `Variable.assign` keeps shape and dtype fixed, so a value of another shape raises an error — [Introduction to Variables](https://www.tensorflow.org/guide/variable)
- Recognise on sight: `w = tf.Variable([0., 0.])`, `w.assign_add([1., 1.])`; in old code `tf.placeholder(tf.float32)` and `sess.run(..., feed_dict=...)`.
- Claims:
  - `tf.Variable` supports `assign`, `assign_add` and `assign_sub` — [Introduction to Variables](https://www.tensorflow.org/guide/variable)
  - `trainable=False` marks a variable as not updated by training — [Introduction to Variables](https://www.tensorflow.org/guide/variable)
  - Placeholders and sessions are TF1 graph-mode history; use function arguments in TF2 — [Migrate to TensorFlow 2](https://www.tensorflow.org/guide/migrate)
  - A Keras 3 `Variable` is a backend-agnostic container for state with `assign`, `assign_add`, `trainable`, `path` and `value` attributes; a Dense layer's `kernel` and `bias` are Keras `Variable`s (printed as `<Variable path=sequential/dense/kernel, ...>`) — [tf.keras.Variable](https://www.tensorflow.org/api_docs/python/tf/keras/Variable)
  - A Keras `Variable`'s `.value` returns the variable's backing tensor — [tf.keras.Variable](https://www.tensorflow.org/api_docs/python/tf/keras/Variable) (its concrete class on the TensorFlow backend is left to the `## 5` cell's `type(layer.kernel.value)` printout, which the notebook author confirms on the fresh runtime; pages quote that printout, not this brief)

### Creating a model
- Interview questions: Build a one-layer classifier in Keras and say what each line does; What do `compile`, `fit`, `evaluate` and `predict` each return?; Why scale features before training?
- Adjacent concept: loss and optimizer — named in one line each (`"binary_crossentropy"`, `"adam"`); their mechanics belong to week 7.
- Trade-off or limit: a one-layer sigmoid model is logistic regression and can only draw a line; accuracy on the training split overstates generalisation — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
- Recognise on sight: `model = tf.keras.Sequential([tf.keras.Input(shape=(30,)), tf.keras.layers.Dense(1, activation="sigmoid")])`.
- Claims:
  - `tf.keras.Input(shape=...)` declares the input so weights exist before training — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)
  - `fit` returns a History object holding the per-epoch loss and metrics — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
  - `predict` returns the model's outputs for new inputs, and a sigmoid output lies in (0, 1), so it reads as the probability of class 1; the page thresholds it at 0.5 — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods), [tf.keras.activations.sigmoid](https://www.tensorflow.org/api_docs/python/tf/keras/activations/sigmoid)
  - `layer.get_weights()` returns the layer's weights (for a Dense layer the kernel, then the bias) as a list of NumPy arrays — [tf.keras.Layer](https://www.tensorflow.org/api_docs/python/tf/keras/Layer)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Introduction to graphs and tf.function — https://www.tensorflow.org/guide/intro_to_graphs
- Better performance with tf.function — https://www.tensorflow.org/guide/function
- Introduction to Tensors — https://www.tensorflow.org/guide/tensor
- Introduction to Variables — https://www.tensorflow.org/guide/variable
- Examining the TensorFlow Graph — https://www.tensorflow.org/tensorboard/graphs
- Migrate to TensorFlow 2 — https://www.tensorflow.org/guide/migrate
- The Sequential model — https://www.tensorflow.org/guide/keras/sequential_model
- Training and evaluation with the built-in methods — https://www.tensorflow.org/guide/keras/training_with_built_in_methods
- tf.keras.activations — https://www.tensorflow.org/api_docs/python/tf/keras/activations
- Dense layer API — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense
- plot_model API — https://www.tensorflow.org/api_docs/python/tf/keras/utils/plot_model
- sklearn.linear_model.Perceptron — https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Perceptron.html
- StandardScaler — https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
- Linear models: Perceptron (scikit-learn user guide) — https://scikit-learn.org/stable/modules/linear_model.html#perceptron
- Neural network models (supervised) (scikit-learn user guide) — https://scikit-learn.org/stable/modules/neural_networks_supervised.html
- Tuning the hyper-parameters of an estimator (scikit-learn user guide) — https://scikit-learn.org/stable/modules/grid_search.html
- tf.keras.Variable — https://www.tensorflow.org/api_docs/python/tf/keras/Variable
- tf.keras.Layer — https://www.tensorflow.org/api_docs/python/tf/keras/Layer
- Neural networks: Activation functions (Google ML Crash Course) — https://developers.google.com/machine-learning/crash-course/neural-networks/activation-functions
- Linear regression: Hyperparameters (Google ML Crash Course) — https://developers.google.com/machine-learning/crash-course/linear-regression/hyperparameters
- Colab runtime package list (googlecolab/backend-info) — https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt
- Colab runtime system packages (googlecolab/backend-info) — https://raw.githubusercontent.com/googlecolab/backend-info/main/apt-list.txt

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- activation function | A function applied to a neuron's weighted sum that sets the neuron's output and makes a network non-linear. | aka: activation, activations
- perceptron | The simplest neuron: a weighted sum plus a bias passed through a step, trained by nudging weights after each wrong answer. | aka: perceptrons
- weights and bias | The numbers a neuron learns: one weight per input that scales it, plus a bias that shifts the sum. | aka: weight, bias term
- learning rate | The size of each correction applied to the weights during training. | aka: step size, eta
- tf.Variable | A TensorFlow value that keeps its shape and type but can be changed in place with `assign`, which is how a model holds the weights it learns. | aka: tf.Variables, TensorFlow variable
- Dense layer | A layer in which every output is a weighted sum of all the inputs plus a bias, passed through an activation function. | aka: Dense, fully connected layer

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Treating `tf.Session`, `tf.placeholder`, `feed_dict` and `tf.global_variables_initializer()` from old tutorials as current: they fail under TF2 or need `tf.compat.v1`; TF2 uses eager values, `tf.function` arguments and `tf.Variable`.
- Skipping `StandardScaler` on `load_breast_cancer`: the unscaled features make the single neuron train slowly and give a poor first epoch, and the learner blames the model.
- Mixing the step convention: a paper epoch that outputs 0 at z = 0 gives different weights from the notebook's rule (output 1 at z = 0), so the pair's check fails.
- Expecting `Perceptron` to settle on overlapping classes: raising `cluster_std` makes the boundary keep moving, which reads as a bug, not as the limit of the rule.
- Reading `plot_model` output as the execution graph, or hitting the pydot/graphviz error and thinking the model is wrong.
- Calling `fit` and reading the printed loss as accuracy, or judging on training accuracy only; `evaluate` on the held-out split is the figure to quote.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Section 1 (activation functions): plot sigmoid, tanh and ReLU against their numpy formulas and the numpy-only step, and state the step-at-zero rule once so the paper exercise and the AND cell agree.
- Sections 2 and 3 (the perceptron, training a perceptron): run the AND-training cell and read the first printed epoch aloud for the pairs' paper check; then `### 3.1` the blobs loop from the seeded random start with the boundary redrawn each epoch, and `### 3.2` scikit-learn's `Perceptron` agreeing on the same blobs; the section's "Try changing" runs learning rate 0.01 against 1.0 from the seeded random start, then raises `make_blobs` `cluster_std` until the classes overlap and the boundary never settles.
- Sections 4 and 5 (TensorFlow basics, creating a model): `tf.constant` against `tf.Variable` with `assign`, the TF1 placeholder block as history beside a `tf.function` argument, then the Sequential model on scaled breast cancer, with its kernel and bias printed and set against `LogisticRegression`; 5 against 50 epochs as the "Try changing".
- Section 6 (graph visualization): run `model.summary()`, then `tf.keras.utils.plot_model(model, show_shapes=True)` (Colab ships pydot 4.0.1 and the graphviz binary, see the stamps); the TensorBoard trace by Thursday's `trace_on` method is a contingency only, used if the fresh-runtime `!dot -V` check ever fails.
