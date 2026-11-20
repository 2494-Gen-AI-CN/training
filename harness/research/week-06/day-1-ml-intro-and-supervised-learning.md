# w06d1 — ML introduction & supervised learning

gate: light
verified: 2026-11-16
week: 6 · AI/ML fundamentals
day: 1 · day-1-ml-intro-and-supervised-learning

version-stamps:
  - python: 3.13.18 (verified 2026-11-16) — runs in Colab, NOT the course Python 3.15; source: Colab runtime 2026.10, `os-info.txt` of googlecolab/backend-info (https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt, read 2026-11-16: "Python 3.13.18", Ubuntu 24.04.5 LTS)
  - numpy: 2.4.6 (verified 2026-11-16) — runs in Colab (preinstalled); source: `pip-freeze.txt` of googlecolab/backend-info (https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt, read 2026-11-16: `numpy==2.4.6`)
  - scipy: 1.16.3 (verified 2026-11-16) — runs in Colab; same `pip-freeze.txt` (`scipy==1.16.3`); used on D1 only through scikit-learn
  - scikit-learn: 1.6.1 (verified 2026-11-16) — runs in Colab; same `pip-freeze.txt` (`scikit-learn==1.6.1`); the notebook calls `LinearRegression`, `LogisticRegression(max_iter=5000)`, `PolynomialFeatures`, `train_test_split`, `make_regression`, `make_classification`, `load_diabetes`, `load_breast_cancer`, `accuracy_score`, `mean_squared_error`, `r2_score`
  - matplotlib: 3.10.0 (verified 2026-11-16) — runs in Colab; same `pip-freeze.txt` (`matplotlib==3.10.0`)
  - tensorflow: not imported on D1 (Thursday and Friday only; stamped on those days' briefs) (verified 2026-11-16)
  - note: same manifest the day-2, day-3 and day-5 briefs read; backend-info's README warns its files can lag the live runtime by a day or two, so the notebook author runs the convention's stamp cell (`import sys, numpy, scipy, sklearn, matplotlib; print(sys.version, numpy.__version__, scipy.__version__, sklearn.__version__, matplotlib.__version__)`) on a fresh CPU runtime before the commit, and if any value differs the page and runbook quote the printed value, never 3.15

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- scikit-learn estimators share one pattern: construct, `fit(X, y)` on training data, then `predict(X_new)`; X is a 2-D array (rows are samples, columns are features) and y is 1-D — [scikit-learn Getting Started](https://scikit-learn.org/stable/getting_started.html)
- `LinearRegression` fits a linear model by ordinary least squares, minimising the sum of squared residuals; the fitted slope(s) are in `coef_` and the intercept in `intercept_` — [LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- Ordinary least squares has a closed-form solution, so `LinearRegression.fit` finds the line in one step with no repeated small corrections — [Linear Models, Ordinary Least Squares](https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares)
- `LinearRegression.score(X, y)` returns R², the coefficient of determination; 1.0 is a perfect fit and it can be negative on unseen data — [LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- `mean_squared_error` averages the squared differences between true and predicted values — [mean_squared_error](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_squared_error.html)
- `train_test_split` shuffles then splits arrays; `test_size=0.2` holds out 20 percent, `random_state` fixes the shuffle, and `stratify=y` keeps class proportions — [train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- Evaluating on the data a model was fitted on rewards memorising; a held-out test set estimates performance on new data — [Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html)
- `PolynomialFeatures(degree=d)` adds powers of the input, so a plain `LinearRegression` on those columns fits a degree-d curve; it is still linear in its coefficients — [Polynomial regression](https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions)
- Underfitting (too simple, poor on train and test) and overfitting (fits noise, good on train and poor on test) are shown by a degree 1 against a degree 15 polynomial — [Underfitting vs. Overfitting](https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html)
- `LogisticRegression` is a classifier despite its name; `predict` returns the class, `predict_proba` returns one probability per class, and the decision boundary is linear — [Logistic regression](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)
- `LogisticRegression` defaults to `max_iter=100` with the lbfgs solver, which can stop early with a `ConvergenceWarning` on unscaled features; raising `max_iter` or scaling the features fixes it — [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- `accuracy_score` is the fraction of predictions equal to the true labels; it can mislead when one class is rare, which is why precision, recall and F1 exist (week 8) — [Metrics and scoring: accuracy_score](https://scikit-learn.org/stable/modules/model_evaluation.html#accuracy-score)
- `make_regression`, `make_classification`, `load_diabetes` and `load_breast_cancer` ship with scikit-learn, so no download or upload is needed — [Dataset loading utilities](https://scikit-learn.org/stable/datasets.html)
- `make_classification` defaults to `n_features=20`; the notebook sets `n_features=2` so a 2-column mesh grid can be passed to `predict` for the boundary plot — [make_classification](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_classification.html)
- Supervised learning learns from labelled examples (regression predicts a continuous target, classification a category); unsupervised learning finds structure in data with no target — [Supervised learning](https://scikit-learn.org/stable/supervised_learning.html), [Unsupervised learning](https://scikit-learn.org/stable/unsupervised_learning.html)
- Colab is a hosted Jupyter notebook service run by Google: code is written and executed in the browser on Google's machines, with no setup, signed in with a Google account; a notebook is a page of code cells run one at a time, each cell's output shown under it — [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)
- Colab ships its own Python (3.13.18 on the 2026.10 runtime) with numpy, scipy, scikit-learn and matplotlib preinstalled — [backend-info os-info.txt](https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt), [backend-info pip-freeze.txt](https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Intro to machine learning - algorithms and use cases
- Interview questions: What is the difference between a hand-written rule and a learned model?; What are a sample, a feature, a label and a model?; Why is a test set kept apart from training?
- Adjacent concept: Parameters against hyperparameters — a fitted number (slope) is learned, a setting (`max_iter`, polynomial degree) is chosen by a person; it belongs here because the first fit already shows both.
- Trade-off or limit: A learned model is only as good as its examples and can fail silently on data unlike them — [Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html)
- Recognise on sight: `model = SomeEstimator(); model.fit(X_train, y_train); model.predict(X_test)`
- Claims:
  - Every scikit-learn estimator exposes `fit` and `predict`, so swapping algorithms changes one line — [scikit-learn Getting Started](https://scikit-learn.org/stable/getting_started.html)
  - X is shaped (n_samples, n_features); passing a 1-D array as X raises a shape error — [scikit-learn Getting Started](https://scikit-learn.org/stable/getting_started.html)
  - The week's three families are regression (a number), classification (a category) and clustering (groups with no label) — [Supervised learning](https://scikit-learn.org/stable/supervised_learning.html)
  - The scikit-learn user guide groups algorithms by task, which is the quickest map of "what to use for what" — [Choosing the right estimator](https://scikit-learn.org/stable/machine_learning_map.html)

### Supervised/unsupervised learning
- Interview questions: How do you tell whether a problem is supervised?; Give one supervised and one unsupervised example; Where does the label come from in practice, and what does it cost?
- Adjacent concept: Labelling cost and label quality — noisy labels cap what any model can reach; it belongs here because the card sort turns on whether a label exists.
- Trade-off or limit: Supervised learning needs labelled data, which is often the expensive part; unsupervised learning needs none but has no answer key to score against — [Unsupervised learning](https://scikit-learn.org/stable/unsupervised_learning.html)
- Recognise on sight: `fit(X, y)` is supervised; `fit(X)` with no y is unsupervised.
- Claims:
  - Supervised estimators take both `X` and `y` in `fit`; unsupervised ones take `X` only — [Supervised learning](https://scikit-learn.org/stable/supervised_learning.html)
  - Clustering is the standard unsupervised task (named here, taught Tuesday) — [Clustering](https://scikit-learn.org/stable/modules/clustering.html)
  - A classification label is discrete; a regression target is continuous — [Supervised learning](https://scikit-learn.org/stable/supervised_learning.html)

### Applications of regression
- Interview questions: Name three problems that are regression; What are the features and the label for predicting delivery time?; Why is "will this ticket be closed in 2 days" a different problem from "how many hours will it take"?
- Adjacent concept: Turning a number into a category by thresholding — regression and classification can blur; it belongs here because the ticket-hours example invites it.
- Trade-off or limit: Linear regression extrapolates a straight line beyond its data, which can give impossible values such as negative prices — [Linear Models](https://scikit-learn.org/stable/modules/linear_model.html)
- Recognise on sight: `LinearRegression().fit(X, y)` where `y` is prices, hours or demand.
- Claims:
  - Regression targets are continuous numbers — [Supervised learning](https://scikit-learn.org/stable/supervised_learning.html)
  - `load_diabetes` is a regression dataset whose target is a disease-progression measure for each patient — [load_diabetes](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html)
  - The ten feature columns of the diabetes dataset are not raw measurements (added 2026-11-19, checked that day): each "have been mean centered and scaled by the standard deviation times the square root of `n_samples` (i.e. the sum of squares of each column totals 1)", so a column such as `bmi` holds small values either side of 0, and a negative value means below the average — [Toy datasets: diabetes dataset](https://scikit-learn.org/stable/datasets/toy_dataset.html)
  - Multiple regression uses several feature columns and returns one coefficient per column — [LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)

### Types of regression, fitting the line
- Interview questions: What does least squares minimise?; What do slope and intercept mean for `y = 2x + 5`?; What does R² of 0.9 on training and 0.2 on test tell you?
- Adjacent concept: Reading coefficients in multiple regression (one slope per feature, each the change in the prediction for one unit of that feature with the others held fixed) — it belongs here because `### 4.1` fits `load_diabetes` and prints one `coef_` entry per column — [Linear Models, Ordinary Least Squares](https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares)
- Trade-off or limit: A high-degree polynomial drives training error down while test error rises — [Underfitting vs. Overfitting](https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html)
- Recognise on sight: `make_pipeline(PolynomialFeatures(3), LinearRegression())` or `model.coef_, model.intercept_`
- Claims:
  - A residual is the true value minus the prediction; least squares minimises the sum of their squares — [Ordinary Least Squares](https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares)
  - `make_regression(noise=15)` adds Gaussian noise of standard deviation 15 to the target, and `random_state` makes it repeatable — [make_regression](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_regression.html)
  - `r2_score` is 1 minus the ratio of residual to total sum of squares — [r2_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html)
  - A constant model that always predicts the mean of y, ignoring the features, scores R² = 0.0, so a negative R² is worse than that baseline — [r2_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html)
  - OLS coefficient estimates rely on the features being independent; when features are correlated (multicollinearity) the least-squares estimate becomes highly sensitive to random errors in the target, so coefficients can swing widely — [Linear Models, Ordinary Least Squares](https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares)
  - For multiple regression `coef_` has one entry per feature column, in column order, so `load_diabetes` (10 features) gives 10 slopes and one `intercept_` — [LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
  - Ridge and lasso are the regularised types of linear regression, named in one line on Monday and taught in week 8 — [Ridge regression](https://scikit-learn.org/stable/modules/linear_model.html#ridge-regression-and-classification)
  - Polynomial regression is still a linear model because it is linear in its coefficients — [Polynomial regression](https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions)
  - Bias and variance (added 2026-11-20, checked that day on the scikit-learn 1.9.1 page): an estimator's "generalization error can be decomposed in terms of bias, variance and noise. The bias of an estimator is its average error for different training sets. The variance of an estimator indicates how sensitive it is to varying training sets. Noise is a property of the data."; in the degree 1 / 4 / 15 example the first estimator "is too simple (high bias)" and the last "is very sensitive to varying training data (high variance)"; "we usually have to select learning algorithms and hyperparameters so that both bias and variance are as low as possible" — [Validation curves: plotting scores to evaluate models](https://scikit-learn.org/stable/modules/learning_curve.html)
  - Reading two scores (added 2026-11-20, checked that day): "If the training score and the validation score are both low, the estimator will be underfitting. If the training score is high and the validation score is low, the estimator is overfitting" — [Validation curves: plotting scores to evaluate models](https://scikit-learn.org/stable/modules/learning_curve.html)
  - Three-way split (added 2026-11-20, checked that day on the scikit-learn 1.9.1 page): when settings are tuned against the test set "knowledge about the test set can "leak" into the model and evaluation metrics no longer report on generalization performance"; so "yet another part of the dataset can be held out as a so-called "validation set": training proceeds on the training set, after which evaluation is done on the validation set, and when the experiment seems to be successful, final evaluation can be done on the test set" — [Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html)

### Applications of classification
- Interview questions: Name three classification problems and their classes; What does a wrong answer cost in fraud against spam?; Why can 95 percent accuracy be a bad result?
- Adjacent concept: Class imbalance (one class much rarer than the other, so always predicting the common class scores a high accuracy while missing every rare case) — it belongs here because fraud, diagnosis and churn are all rare-class problems and Monday names accuracy's limit — [Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html#accuracy-score)
- Trade-off or limit: Accuracy treats every error as equal, though a missed diagnosis costs more than a false alarm — [Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html#accuracy-score)
- Recognise on sight: `LogisticRegression(max_iter=5000).fit(X_train, y_train)` then `accuracy_score(y_test, model.predict(X_test))`
- Claims:
  - `load_breast_cancer` is a binary classification dataset of 569 samples and 30 numeric features — [load_breast_cancer](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html)
  - `predict_proba` returns one column per class, and each row sums to 1 — [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
  - How the model gets from features to a class (added 2026-11-19, checked that day): in the binary case `predict_proba` gives the probability of the positive class as the logistic function of a weighted sum of the features plus an intercept, `expit(X w + w0)`, which is a number between 0 and 1 (the guide: "the probabilities describing the possible outcomes of a single trial are modeled using a logistic function"); that probability becomes a class "by applying a threshold (by default 0.5) to it"; and the guide says that, despite its name, logistic regression "is implemented as a linear model for classification rather than regression". The points where the weighted sum gives exactly 0.5 lie on a straight line, which is why the boundary is linear — [Logistic regression](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)
  - The logistic regression boundary is a straight line in two features — [Logistic regression](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)
  - `accuracy_score(y_true, y_pred)` returns the fraction of predictions that match the true labels, a number between 0 and 1 — [Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html#accuracy-score)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- scikit-learn Getting Started — https://scikit-learn.org/stable/getting_started.html
- scikit-learn Linear Models user guide — https://scikit-learn.org/stable/modules/linear_model.html
- LinearRegression API — https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
- Toy datasets: diabetes dataset (read 2026-11-19) — https://scikit-learn.org/stable/datasets/toy_dataset.html
- LogisticRegression API — https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- train_test_split API — https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- Underfitting vs. Overfitting example — https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html
- Validation curves: plotting scores to evaluate models (read 2026-11-20) — https://scikit-learn.org/stable/modules/learning_curve.html
- Metrics and scoring user guide — https://scikit-learn.org/stable/modules/model_evaluation.html
- Dataset loading utilities — https://scikit-learn.org/stable/datasets.html
- Supervised learning user guide — https://scikit-learn.org/stable/supervised_learning.html
- Unsupervised learning user guide — https://scikit-learn.org/stable/unsupervised_learning.html
- Cross-validation: evaluating estimator performance — https://scikit-learn.org/stable/modules/cross_validation.html
- Choosing the right estimator — https://scikit-learn.org/stable/machine_learning_map.html
- Colab release notes — https://colab.research.google.com/notebooks/relnotes.ipynb
- Google Colab FAQ — https://research.google.com/colaboratory/faq.html
- Colab backend-info: runtime OS and Python (os-info.txt, read 2026-11-16) — https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt
- Colab backend-info: preinstalled packages (pip-freeze.txt, read 2026-11-16) — https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- supervised learning | Learning from examples that each come with a known correct answer, so the model can be scored against it. | aka: supervised
- unsupervised learning | Finding structure in data that has no label, such as natural groups. | aka: unsupervised
- regression | A task that predicts a number, such as a price or a delivery time. | aka: regression model, regression models
- classification | A task that predicts which category a sample belongs to, such as spam or not spam. | aka: classifier, classifiers
- least squares | Choosing the line whose sum of squared misses between prediction and true value is smallest. | aka: ordinary least squares, OLS
- residual | The gap between a true value and the model's prediction for one sample. | aka: residuals
- train/test split | Dividing the data so the model is fitted on one part and scored on rows it never saw. | aka: train test split, test set, held-out data
- underfitting | When a model is too simple to capture the pattern and scores poorly on both training and test data. | aka: underfit, underfits

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Scoring a model on the rows it was fitted on and reading the high number as quality; the degree-15 polynomial's near-perfect training score is the example.
- Passing a 1-D array as X: `fit(x, y)` needs a 2-D X, so a single feature needs `x.reshape(-1, 1)` or `x[:, None]`, and the shape error confuses learners new to numpy.
- Thinking `LogisticRegression` is a regression because of its name, or a `ConvergenceWarning` means the code is broken (it means the solver stopped early on unscaled features; `max_iter=5000` is the Monday fix and scaling is Tuesday).
- Trusting accuracy when one class is rare: 95 percent can come from always predicting the common class.
- Leaving out `random_state` so the numbers in the markdown no longer match the cell output after a rerun or a different split.
- Editing the shared notebook in place: learners must File > Save a copy in Drive before changing anything, or the changes are lost and the first-contact Colab setup stalls.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Part 1 (`## 1. What a model learns`, `## 2. Fitting the line`): show X as a table and y as the label, then `fit` and `predict`, read `coef_` and `intercept_` as slope and intercept, and draw the residuals so "smallest sum of squared misses" is visible before MSE and R² appear.
- Part 2 (`## 3. Train and test`, `## 4. Types of regression`): show the training score beating the test score, then degrees 1, 3 and 15 side by side on the seeded curved set; name underfit and overfit from the plots, and name ridge and lasso in one line only.
- Part 3 (`## 5. Classification`, `## 6. A real dataset: breast cancer`): draw the straight boundary with `plot_decision_boundary`, print `predict` against `predict_proba` for the same rows, and read the test `accuracy_score`; say aloud that `max_iter=5000` only lets the solver finish.
- Setup check first: every learner opens the notebook from GitHub, saves a copy in Drive and sees `Setup complete`; run the fresh-runtime version stamp cell here so page and runbook quote Colab's numbers.
