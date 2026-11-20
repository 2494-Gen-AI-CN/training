# w07d1 — Multi-layer perceptrons, backprop & digit classifier

gate: light
verified: 2026-11-19
week: 7 · TensorFlow
day: 1 · day-1-mlp-backprop-and-digit-classifier

version-stamps:
  - python: 3.13.18 on Colab, not the course 3.15 (verified 2026-11-19; runs in Colab; TensorFlow has no 3.15 wheel, so no cp315 wheel is picked; re-read 2026-11-19 from googlecolab/backend-info os-info.txt, commit of 2026-11-12, line `Python 3.13.18`, https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt)
  - tensorflow: 2.21.0 (verified 2026-11-19; runs in Colab; re-read 2026-11-19 from backend-info pip-freeze.txt, commit of 2026-11-12, line `tensorflow==2.21.0`, https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt)
  - keras: 3.13.2, reached as `tf.keras` (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `keras==3.13.2`; `tf.keras` resolves to Keras 3 unless `TF_USE_LEGACY_KERAS` is set, which the notebook never sets)
  - tensorboard: 2.21.0 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `tensorboard==2.21.0`; `%load_ext tensorboard` and `%tensorboard --logdir logs/fit` in `## 9`)
  - numpy: 2.4.6 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `numpy==2.4.6`)
  - pandas: 2.2.3 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `pandas==2.2.3`; the results table, `pd.DataFrame(results).round(4)`)
  - scikit-learn: 1.6.1 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `scikit-learn==1.6.1`; `confusion_matrix`, `ConfusionMatrixDisplay`, `precision_score`, `recall_score`, `f1_score`)
  - matplotlib: 3.10.0 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `matplotlib==3.10.0`)
  - scipy: 1.16.3 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `scipy==1.16.3`; printed by the convention's stamp cell, not imported by this day's cells)
  - seaborn: 0.13.2 (verified 2026-11-19; runs in Colab; same pip-freeze.txt, line `seaborn==0.13.2`; printed by the convention's stamp cell, not imported by this day's cells)
  - stamp note: no fresh Colab runtime was opened for this brief (light gate); the lines are backend-info's 2026-11-12 snapshot, which can lead or lag production by a release. The notebook author runs the convention's stamp cell on a fresh CPU runtime before the commit, times every `fit` cell (10 epochs of 784-128-10 on 54,000 rows at `batch_size=128`, the 1,000-row 50-epoch overfit fit, the `deeper_model` fit, and the XOR fits of `## 3` and `### 4.1`, each expected well under 3 minutes), restamps the epoch count `### 4.1` needs to reach accuracy 1.0, and the pages and runbook quote that printout where it differs.

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- A loss function turns the gap between prediction and target into one number that training tries to lower. — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
- Mean squared error averages the squared differences between targets and predictions and suits a numeric answer. — [MeanSquaredError](https://www.tensorflow.org/api_docs/python/tf/keras/losses/MeanSquaredError)
- Binary cross-entropy is the loss for two classes; the Keras loss averages over the batch it is given. — [BinaryCrossentropy](https://www.tensorflow.org/api_docs/python/tf/keras/losses/BinaryCrossentropy)
- `SparseCategoricalCrossentropy` takes labels as integers 0 to 9, where `CategoricalCrossentropy` expects one-hot vectors. — [SparseCategoricalCrossentropy](https://www.tensorflow.org/api_docs/python/tf/keras/losses/SparseCategoricalCrossentropy)
- Plain gradient descent updates each weight as `w = w - learning_rate * g`, a small step against the slope `g`; the learning rate sets the step size. — [SGD](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/SGD)
- A learning rate that is too large makes the loss bounce or grow instead of fall (shown by `### 2.2`'s rate 0.2 on `y = 2.0 * x`; the diverging run is to be confirmed by the fresh run). — [SGD](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/SGD)
- A single perceptron is a linear classifier, so it cannot separate XOR, whose two classes no straight line splits; one hidden layer with a nonlinear activation can. — [Perceptron (scikit-learn user guide)](https://scikit-learn.org/stable/modules/linear_model.html#perceptron)
- Without a nonlinear activation, stacked Dense layers collapse into one linear map; `relu` and `tanh` supply the nonlinearity. — [tf.keras.activations](https://www.tensorflow.org/api_docs/python/tf/keras/activations)
- Backpropagation computes the gradient of the loss with respect to every weight by passing it backward layer by layer, and an optimizer then applies the update. — [Introduction to gradients and automatic differentiation](https://www.tensorflow.org/guide/autodiff)
- `tf.GradientTape` records operations inside its `with` block and `tape.gradient(loss, variables)` returns the slopes. — [Introduction to gradients and automatic differentiation](https://www.tensorflow.org/guide/autodiff)
- `Dense(128)` on a 784-long input holds 784 x 128 weights plus 128 biases = 100,480 parameters; with `Dense(10)` (1,290) the network has 101,770. — [Dense layer API](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
- A softmax output layer returns ten probabilities that sum to 1, and `argmax` picks the predicted digit. — [tf.keras.activations.softmax](https://www.tensorflow.org/api_docs/python/tf/keras/activations/softmax)
- `fit(..., validation_data=(x_val, y_val))` reports `val_loss` each epoch on rows the weights are never updated from, and `History.history` holds both curves. — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
- `tf.keras.datasets.mnist.load_data()` returns 60,000 training and 10,000 test images of 28 x 28 pixels. — [tf.keras.datasets.mnist.load_data](https://www.tensorflow.org/api_docs/python/tf/keras/datasets/mnist/load_data)
- Early stopping halts training when a monitored metric such as `val_loss` stops improving. — [EarlyStopping](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping)
- `confusion_matrix(y_true, y_pred)` puts true classes on the rows and predicted classes on the columns. — [confusion_matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html)
- Precision is TP / (TP + FP), recall is TP / (TP + FN), and F1 is their harmonic mean. — [precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)
- The TensorBoard callback writes event files to `log_dir`, and the Scalars tab plots loss and metrics per epoch. — [TensorBoard callback](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard)
- In notebooks TensorBoard opens with `%load_ext tensorboard` then `%tensorboard --logdir <dir>`. — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
- TFLearn status as checked on 2026-11-18 (the plan's wording): the last release is 0.5.0 (2020-11-11, PyPI), the last commit on its `master` branch is 2020-11-30, and it does not import on Colab's TensorFlow 2.21, because `tflearn/layers/recurrent.py` imports `is_sequence` from `tensorflow.python.util.nest`, which TensorFlow 2.21 no longer defines, and its `__init__.py` calls `tf.disable_v2_behavior()`; Tuesday's research brief confirms the import failure by one run in a scratch Colab notebook before any page quotes it as run, so Monday's page states the status and never says it was run. — [tflearn on PyPI](https://pypi.org/project/tflearn/); [tflearn on GitHub](https://github.com/tflearn/tflearn)
- TFLearn to Keras for this day's topics (history only, never imported or installed; TFLearn code appears only in markdown blocks labelled "TFLearn (history, do not run)"): `tflearn.input_data` -> `tf.keras.Input`; `tflearn.fully_connected` -> `tf.keras.layers.Dense`; `tflearn.regression` (optimizer, loss, learning rate) -> `model.compile`; `tflearn.DNN(...)` and its `fit` -> `model.fit`; TFLearn's layer stacking (each layer called on the one before) -> the list form of `tf.keras.Sequential`; `DNN(tensorboard_verbose=..., tensorboard_dir=...)` -> `tf.keras.callbacks.TensorBoard(log_dir=...)`. — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model); [TensorBoard callback](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Limitations of single perceptrons
- Interview questions: What is a perceptron and what can it not do?; Why can't a single perceptron learn XOR?; How does adding a hidden layer fix it?
- Adjacent concept: linear separability — a single neuron draws one straight line, which is why the XOR table fails it.
- Trade-off or limit: a single neuron can only learn what one straight line can split, however long it trains — [Perceptron (scikit-learn user guide)](https://scikit-learn.org/stable/modules/linear_model.html#perceptron)
- Recognise on sight: `Sequential([Input(shape=(2,)), Dense(1, activation="sigmoid")])` fitted on `X_xor` sitting at 0.5 or 0.75 accuracy.
- Claims:
  - XOR labels (0,0)→0, (0,1)→1, (1,0)→1, (1,1)→0 cannot be split by one line — [Perceptron (scikit-learn user guide)](https://scikit-learn.org/stable/modules/linear_model.html#perceptron)
  - A sigmoid output with no hidden layer is a linear decision boundary — [Dense layer API](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
  - Accuracy stuck at 0.5 or 0.75 on four points is the sign of a model that is not able, not one that needs more epochs (arithmetic: any one line puts at most three of the four XOR points on their correct side, so 0.75 is the ceiling; the figure the notebook prints is to be confirmed by the fresh run) — [Perceptron (scikit-learn user guide)](https://scikit-learn.org/stable/modules/linear_model.html#perceptron)

### Multi-layer perceptrons
- Interview questions: What is a multi-layer perceptron?; Why does a hidden layer need a nonlinear activation?; What do the hidden units learn?
- Adjacent concept: activation functions (ReLU, tanh, softmax) — each layer's output choice follows from the answer the model gives.
- Trade-off or limit: more hidden units fit more shapes but also memorise a small training set — [Overfit and underfit](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
- Recognise on sight: `Dense(4, activation="tanh")` followed by `Dense(1, activation="sigmoid")`; in older tutorials, `tflearn.fully_connected(net, 4, activation="tanh")` is the same layer (history only).
- Claims:
  - Two stacked linear layers equal one linear layer, so the hidden activation is what adds power — [tf.keras.activations](https://www.tensorflow.org/api_docs/python/tf/keras/activations)
  - A multi-layer perceptron (one or more hidden layers with a nonlinear activation) can learn decision boundaries a single linear unit cannot — [Neural network models (scikit-learn user guide)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)
  - One hidden layer of 4 tanh units reaches accuracy 1.0 on XOR (expected figure, to be confirmed by the fresh run; the notebook author restamps the epoch count `### 4.1` needs and the markdown quotes it) — [Neural network models (scikit-learn user guide)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)
  - The hidden units re-describe the four points so that a single line separates them (shown by `### 4.2`'s printout of the hidden outputs, to be confirmed by the fresh run; going deeper) — [Neural network models (scikit-learn user guide)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)
  - TFLearn's `input_data`, `fully_connected` and stacking map to `tf.keras.Input`, `tf.keras.layers.Dense` and the list form of `tf.keras.Sequential` (history only; the Sequential API as a topic is Tuesday's) — [The Sequential model](https://www.tensorflow.org/guide/keras/sequential_model)

### Backpropagation algorithm
- Interview questions: Explain backpropagation in plain words; What does the learning rate do in the update?; Why is backprop cheaper than nudging every weight one at a time?
- Adjacent concept: gradient descent and the optimizer (Adam is gradient descent with per-weight adaptive steps) — backprop supplies the slopes, the optimizer takes the step.
- Trade-off or limit: backprop needs differentiable layers and a loss it can take a slope of; a step function gives no slope — [Introduction to gradients and automatic differentiation](https://www.tensorflow.org/guide/autodiff)
- Recognise on sight: `model.fit(...)`, which runs forward pass, loss, backward pass and update for every batch; in older tutorials, `tflearn.regression(...)` then `tflearn.DNN(net).fit(...)` (history only; `model.compile` then `model.fit`).
- Claims:
  - One training step is forward pass, loss, backward pass for the slopes, update, repeat — [Introduction to gradients and automatic differentiation](https://www.tensorflow.org/guide/autodiff)
  - A centred nudge `(loss(w + h) - loss(w - h)) / (2h)` approximates the same slope backprop returns — [Introduction to gradients and automatic differentiation](https://www.tensorflow.org/guide/autodiff)
  - Worked row x=2, target 1, w1=0.5, w2=1.5: prediction 1.5, loss 0.25, slopes 1.0 and 3.0, at rate 0.02 new loss about 0.091 (arithmetic; `tf.GradientTape` confirms the slopes) — [Introduction to gradients and automatic differentiation](https://www.tensorflow.org/guide/autodiff)
  - Adam, the optimizer every Keras model this week compiles with, is gradient descent whose step size adapts per weight; Monday names it in one line — [Adam](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/Adam)

### Understand backprop - neural network
- Interview questions: Walk me through one weight update on a two-weight network; Why does w1 get a larger slope than w2 in the worked row?; What happens to the loss after one update?
- Adjacent concept: the chain of slopes — each earlier weight's slope is multiplied by every weight it passes on the way back (named, never derived under D-0086).
- Trade-off or limit: a hand-worked network has no activation or bias, so it shows the bookkeeping, not the full behaviour of a real layer — [Dense layer API](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
- Recognise on sight: `tape.gradient(loss, [w1, w2])` returning two numbers.
- Claims:
  - A prediction above the target means both weights must shrink, so the update subtracts the slope — [SGD](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/SGD)
  - After w2=1.48 and w1=0.44 the prediction is 0.88 x 1.48 = about 1.30, closer to 1.0 (arithmetic) — [Introduction to gradients and automatic differentiation](https://www.tensorflow.org/guide/autodiff)
  - The update is plain gradient descent, `w - 0.02 * slope`; at rate 0.02 the loss falls from 0.25 to about 0.091, so this step does not overshoot (arithmetic on the worked row, not a property of any optimizer) — [SGD](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/SGD)

### MLP digit classifier using TensorFlow
- Interview questions: Walk me through a model you built, in order; How do you read training and validation curves together?; Why hold a test set out and use it once?
- Adjacent concept: evaluation beyond accuracy (confusion matrix, precision, recall, F1) — it says which digits the model confuses; averaged metrics stay for week 8.
- Trade-off or limit: flattening 28 x 28 images discards which pixels are neighbours, which a CNN keeps — [Convolutional Neural Network (CNN)](https://www.tensorflow.org/tutorials/images/cnn)
- Recognise on sight: `Dense(128, activation="relu")`, `Dense(10, activation="softmax")`, `loss="sparse_categorical_crossentropy"`, `optimizer="adam"`.
- Claims:
  - Divide pixels by 255.0 so inputs sit between 0 and 1 — [Keras quickstart](https://www.tensorflow.org/tutorials/quickstart/beginner)
  - Validation loss rising while training loss falls is overfitting; training on 1,000 rows for 50 epochs shows it — [Overfit and underfit](https://www.tensorflow.org/tutorials/keras/overfit_and_underfit)
  - Fixed validation rows (the last 6,000 of `x_train`) make a before-and-after comparison fair — [Training and evaluation with the built-in methods](https://www.tensorflow.org/guide/keras/training_with_built_in_methods)
  - A model that always answers "not 5" scores about 91% accuracy and has recall 0 for digit 5 (arithmetic: 5s are about one row in eleven of MNIST; the notebook prints the figure on `y_val`) — [precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)
  - Expected figures on this setup are about 97 to 98% validation accuracy for the 784-128-10 network (to be restamped by the fresh run) — [Keras quickstart](https://www.tensorflow.org/tutorials/quickstart/beginner)

### TensorBoard
- Interview questions: What is TensorBoard for?; How do you get your training curves into it from Keras?; What does an empty Scalars tab usually mean?
- Adjacent concept: the Scalars tab against `plot_history` — both draw the same per-epoch `loss` and `val_loss` of one fit, so reading one is reading the other; the tab adds a smoothing slider, set to 0 to see each epoch's raw value.
- Trade-off or limit: TensorBoard only shows what the callback wrote, so a wrong `--logdir` shows an empty tab — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
- Recognise on sight: `callbacks=[tf.keras.callbacks.TensorBoard(log_dir="logs/fit")]`; in older tutorials, `tflearn.DNN(net, tensorboard_verbose=0, tensorboard_dir="...")` (history only).
- Claims:
  - The callback writes loss and metrics per epoch to `log_dir`, with training and validation in separate subfolders, so one fit shows a training line and a validation line on the `epoch_loss` chart — [TensorBoard callback](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard)
  - The Scalars tab draws the same curves `plot_history` draws; W6D4's Graphs tab drew structure — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
  - The Scalars tab has a smoothing slider that averages neighbouring points; at 0 it shows each epoch's value as `History.history` holds it — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
  - TFLearn's `DNN(tensorboard_verbose=..., tensorboard_dir=...)` maps to `tf.keras.callbacks.TensorBoard(log_dir=...)` (history only) — [TensorBoard callback](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Training and evaluation with the built-in methods — https://www.tensorflow.org/guide/keras/training_with_built_in_methods
- The Sequential model — https://www.tensorflow.org/guide/keras/sequential_model
- Introduction to gradients and automatic differentiation — https://www.tensorflow.org/guide/autodiff
- SGD optimizer — https://www.tensorflow.org/api_docs/python/tf/keras/optimizers/SGD
- Overfit and underfit — https://www.tensorflow.org/tutorials/keras/overfit_and_underfit
- Get started with TensorBoard — https://www.tensorflow.org/tensorboard/get_started
- TensorBoard callback — https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/TensorBoard
- tf.keras.datasets.mnist.load_data — https://www.tensorflow.org/api_docs/python/tf/keras/datasets/mnist/load_data
- confusion_matrix — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
- Perceptron (scikit-learn user guide) — https://scikit-learn.org/stable/modules/linear_model.html#perceptron
- Neural network models (scikit-learn user guide) — https://scikit-learn.org/stable/modules/neural_networks_supervised.html
- tflearn on PyPI — https://pypi.org/project/tflearn/
- Colab backend-info pip-freeze.txt — https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- loss function | One number that says how wrong a model's predictions are, which training tries to make smaller. | aka: loss, cost function, error function
- cross-entropy | The loss used when the answer is a class: it is small when the model gives the true class a high probability and grows fast when it is confident and wrong. | aka: log loss, binary cross-entropy
- gradient descent | Repeatedly nudging each weight a small step in the direction that lowers the loss. | aka: steepest descent, downhill steps
- backpropagation | The method that works out each weight's share of the loss by passing it backward through the layers so gradient descent can update it. | aka: backprop, backward pass
- multi-layer perceptron | A network of Dense layers with at least one hidden layer between input and output. | aka: MLP, feedforward network
- confusion matrix | A table of true classes against predicted classes that shows which classes get mistaken for which. | aka: confusion matrices
- precision | Of the items the model labels as a class, the share that truly belong to it. | aka: positive predictive value
- recall | Of the items that truly belong to a class, the share the model finds. | aka: sensitivity, true positive rate

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Reading only training accuracy: it keeps rising while validation turns, so the model looks better than it is; both curves go on one chart.
- Treating a hidden layer as enough: stacking Dense layers with no nonlinear activation stays linear and still fails XOR.
- Using the test set to choose a model: it is touched once at the end; every choice before it is made on the validation rows.
- Trusting accuracy on an unbalanced problem: "always not 5" scores about 91% with recall 0.
- Passing one-hot labels to `sparse_categorical_crossentropy` (or integers to the non-sparse loss), or forgetting to divide pixels by 255.
- An empty TensorBoard tab: the `--logdir` does not match the callback's `log_dir`, or the fit ran without the callback.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Open `## 1` and `## 2` (loss as one number, then the bowl over `w` with learning rates 0.01, 0.05, 0.2 and the "Try changing" 0.1 and 0.15), then `## 3` and `## 4`: one sigmoid neuron stuck at 0.5 or 0.75 on XOR, the 4-unit tanh hidden layer reaching 1.0 with its curved boundary.
- Show `### 5.2` after the Scratch-cell paper exercise: slopes 1.000 and 3.000, loss 0.25 to about 0.091, with no derivative written; run `### 4.2` and `### 5.3` without discussion.
- Run the `## 6` build in Project 1's order: problem, MNIST and the held-out test set, 784-128-10 `summary()` (101,770), `plot_history` with both curves, then the 1,000-row overfit fit where validation loss rises.
- Run `## 7` to `## 9`: confusion matrix, digit 5 precision, recall and F1, the always-"not 5" trap, the misclassified grid, `deeper_model` before and after, the one test cell, then `%tensorboard --logdir logs/fit` Scalars tab read beside `plot_history` (smoothing at 0).
