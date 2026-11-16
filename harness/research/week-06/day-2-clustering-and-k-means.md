# w06d2 — Unsupervised learning: clustering

gate: light
verified: 2026-11-16
week: 6 · AI/ML fundamentals
day: 2 · clustering-and-k-means

version-stamps:
  - python: 3.13.18 (verified 2026-11-16) — runs in Colab, NOT the course Python 3.15; source: Colab runtime 2026.10, `os-info.txt` of googlecolab/backend-info (https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt, read 2026-11-16: "Python 3.13.18", Ubuntu 24.04.5 LTS)
  - scikit-learn: 1.6.1 (verified 2026-11-16) — runs in Colab (preinstalled; no wheel pip picks on the course Python); source: `pip-freeze.txt` of googlecolab/backend-info (https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt, read 2026-11-16: `scikit-learn==1.6.1`); the notebook calls `DecisionTreeClassifier`, `DecisionTreeRegressor`, `plot_tree`, `KMeans(n_init=10)`, `DBSCAN`, `silhouette_score`, `StandardScaler`
  - scipy: 1.16.3 (verified 2026-11-16) — runs in Colab; same `pip-freeze.txt` (`scipy==1.16.3`); the notebook uses `scipy.cluster.hierarchy` (`linkage`, `dendrogram`) and `scipy.spatial.distance.cdist`
  - numpy: 2.4.6 (verified 2026-11-16) — runs in Colab; same `pip-freeze.txt` (`numpy==2.4.6`)
  - matplotlib: 3.10.0 (verified 2026-11-16) — runs in Colab; same `pip-freeze.txt` (`matplotlib==3.10.0`)
  - tensorflow: 2.21.0, keras 3.13.2 (verified 2026-11-16) — runs in Colab; same `pip-freeze.txt`; NOT imported on Tuesday (TensorFlow/Keras appears on D4-D5 only)
  - note: backend-info's README warns its files can lag the live runtime by a day or two; the notebook author runs the convention's stamp cell (`import sys, numpy, scipy, sklearn, matplotlib; print(sys.version, numpy.__version__, scipy.__version__, sklearn.__version__, matplotlib.__version__)`) on a fresh CPU runtime before the commit, and if any value differs the page and runbook quote the printed value, never 3.15

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- Clustering is unsupervised learning: it groups samples by similarity with no label to check against, so the result is judged by usefulness and by internal measures, not by accuracy — [Clustering (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html)
- K-means divides n samples into K clusters; each cluster is described by the mean of its samples, the centroid, and the algorithm chooses centroids that minimise inertia, the within-cluster sum of squared distances — [K-means (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#k-means)
- The k-means loop alternates two steps: assign every point to its nearest centroid, then move each centroid to the mean of its assigned points; it stops when centroids stop moving (or the change falls under `tol`) — [K-means (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#k-means)
- K-means can land in a local minimum that depends on the starting centroids, so scikit-learn runs it `n_init` times and keeps the run with the lowest inertia — [sklearn.cluster.KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
- Inertia always falls as K grows, so the lowest inertia cannot choose K; the elbow method looks for the K after which the drop flattens — [K-means (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#k-means)
- K-means assumes roughly convex, similarly sized clusters and responds poorly to elongated or ring-shaped clusters — [K-means (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#k-means)
- The silhouette coefficient of a sample is (b − a) / max(a, b), with a the mean distance to its own cluster and b the mean distance to the nearest other cluster; it runs from −1 to +1, higher is better — [Silhouette Coefficient (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#silhouette-coefficient)
- `silhouette_score` returns the mean over all samples and needs at least 2 and at most n_samples − 1 distinct labels — [sklearn.metrics.silhouette_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)
- Hierarchical (agglomerative) clustering starts with every point as its own cluster and repeatedly merges the closest pair; the linkage criterion defines "closest" between two clusters — [Hierarchical clustering (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering)
- Single linkage uses the minimum distance between points of two clusters, complete linkage the maximum, average linkage the mean over all pairs, and Ward linkage the merge that least increases total within-cluster variance — [Hierarchical clustering (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering)
- `scipy.cluster.hierarchy.linkage` builds the merge table (method `single`, `complete`, `average`, `centroid`, `ward`) and `dendrogram` draws the merge tree, where the vertical axis is the distance at which clusters merged — [scipy.cluster.hierarchy.linkage](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html)
- `scipy.spatial.distance.cdist` returns the matrix of distances between every row of one array and every row of another, with Euclidean as default metric and `cityblock` for Manhattan — [scipy.spatial.distance.cdist](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html)
- Euclidean distance is the straight-line (L2) distance and Manhattan (cityblock) distance sums absolute coordinate differences (L1) — [scipy.spatial.distance.cdist](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html)
- Distance-based methods are dominated by the feature with the largest numeric range; `StandardScaler` rescales each feature to mean 0 and unit variance so every feature counts equally — [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)
- DBSCAN groups points in dense regions: a core point has at least `min_samples` neighbours within `eps`; points reachable from no core point get label −1 (noise); it needs no K and finds non-convex shapes — [DBSCAN (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#dbscan)
- A decision tree predicts by asking a chain of threshold questions on one feature each; `max_depth` limits its size, and an unlimited tree can memorise training data (overfit) — [Decision Trees (scikit-learn user guide)](https://scikit-learn.org/stable/modules/tree.html)
- `DecisionTreeRegressor` predicts the mean of the training targets in each leaf, so its output is a staircase of constant pieces — [Decision Trees (scikit-learn user guide)](https://scikit-learn.org/stable/modules/tree.html#regression)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Unsupervised learning - clustering
- Interview questions: What is the difference between supervised and unsupervised learning?; Give two uses of clustering; How do you know a clustering is good when there are no labels?
- Adjacent concept: Decision trees as a labelled-data contrast — the day's notebook opens with them, so the page sets one labelled model beside the unlabelled task; no later day's content.
- Trade-off or limit: No ground truth exists, so two algorithms can both be "right" with different groupings and the number of clusters is a choice, not a fact — [Clustering (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html)
- Recognise on sight: `labels = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(X)` — there is no `y` in the call
- Claims:
  - [feeds notes step 1, decision trees; keep out of step 2] A decision tree asks one threshold question per node and draws axis-aligned boundaries — [Decision Trees (scikit-learn user guide)](https://scikit-learn.org/stable/modules/tree.html)
  - [feeds notes step 1, decision trees; keep out of step 2] `max_depth=None` lets a tree grow until its leaves are pure, which is how it overfits (Monday's degree-15 polynomial again) — [Decision Trees (scikit-learn user guide)](https://scikit-learn.org/stable/modules/tree.html)
  - [feeds notes step 1, decision trees; keep out of step 2] `plot_tree` draws the fitted tree with each node's question, gini impurity and sample count — [sklearn.tree.plot_tree](https://scikit-learn.org/stable/modules/generated/sklearn.tree.plot_tree.html)
  - Clustering is used for customer segments, grouping documents and finding structure before labels exist — [Clustering (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html)
  - `make_blobs` generates isotropic Gaussian blobs for clustering demos and returns labels that a clustering algorithm never sees — [sklearn.datasets.make_blobs](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_blobs.html)

### Distance between clusters
- Interview questions: What is the difference between Euclidean and Manhattan distance?; What are single, complete and average linkage?; How do you read a dendrogram and where do you cut it?
- Adjacent concept: Feature scaling before distance — distances are meaningless when one feature spans a larger range; belongs here because every linkage is built on a point distance.
- Trade-off or limit: Single linkage can chain far-apart points through a line of close ones; complete linkage favours compact clusters; Ward only works with Euclidean distance — [Hierarchical clustering (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering)
- Recognise on sight: `Z = linkage(X, method="average"); dendrogram(Z)`
- Claims:
  - Cutting a dendrogram at a height gives the clusters that merged below it — [scipy.cluster.hierarchy.dendrogram](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html)
  - Each row of the `linkage` output records two merged cluster indices, their distance and the new cluster's size — [scipy.cluster.hierarchy.linkage](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html)
  - Cosine distance measures the angle between vectors rather than the length; it is named once here and taught in week 8 — [scipy.spatial.distance.cdist](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html)
  - `StandardScaler` stores `mean_` and `scale_` from `fit` and applies them in `transform` — [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)

### k-means algorithm
- Interview questions: Walk through one round of k-means; Why does k-means depend on the starting centroids, and what does `n_init` do?; How do you choose K and why can't you just take the lowest inertia?
- Adjacent concept: DBSCAN as the answer when k-means fails on rings and noise — it needs `eps` and `min_samples` rather than K.
- Trade-off or limit: K-means needs K up front, is sensitive to scale and outliers, and assumes round clusters — [K-means (scikit-learn user guide)](https://scikit-learn.org/stable/modules/clustering.html#k-means)
- Recognise on sight: `inertias = [KMeans(n_clusters=k, n_init=10, random_state=42).fit(X).inertia_ for k in range(1, 9)]`
- Claims:
  - `labels_` holds each sample's cluster index and `cluster_centers_` the centroid coordinates after `fit` — [sklearn.cluster.KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
  - `inertia_` is the sum of squared distances of samples to their closest centre — [sklearn.cluster.KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
  - Default initialisation is `k-means++`, which spreads the starting centroids apart — [sklearn.cluster.KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
  - The notebook's `## 6` clusters iris on petal length and width only (`iris.data[:, [2, 3]]`), scores `KMeans(n_init=10, random_state=42)` for K = 2 to 8 with `silhouette_score`, and its markdown reports the peak at K = 2 although the dataset has three species of 50 samples each (setosa sits alone, versicolor and virginica overlap); metrics guide K, they do not decide it (re-read the printed peak on the fresh-runtime run before the commit) — [sklearn.datasets.load_iris](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html) and [sklearn.metrics.silhouette_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)
  - In `DBSCAN`, raising `eps` merges clusters and lowers noise; lowering `eps` or raising `min_samples` labels more points -1 (noise) — [sklearn.cluster.DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Clustering (scikit-learn user guide) — https://scikit-learn.org/stable/modules/clustering.html
- sklearn.cluster.KMeans — https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
- sklearn.cluster.DBSCAN — https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html
- sklearn.metrics.silhouette_score — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html
- Decision Trees (scikit-learn user guide) — https://scikit-learn.org/stable/modules/tree.html
- sklearn.preprocessing.StandardScaler — https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
- scipy.cluster.hierarchy.linkage — https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html
- scipy.spatial.distance.cdist — https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html
- Silhouette analysis example — https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
- sklearn.datasets.load_iris — https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html
- sklearn.tree.plot_tree — https://scikit-learn.org/stable/modules/generated/sklearn.tree.plot_tree.html
- scipy.cluster.hierarchy.dendrogram — https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html
- Colab backend-info: preinstalled packages (pip-freeze.txt, read 2026-11-16) — https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt
- Colab backend-info: runtime OS and Python (os-info.txt, read 2026-11-16) — https://raw.githubusercontent.com/googlecolab/backend-info/main/os-info.txt
- Colab release notes — https://colab.research.google.com/notebooks/relnotes.ipynb
- Google Colab FAQ — https://research.google.com/colaboratory/faq.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- decision tree | A model that predicts by asking a chain of yes/no threshold questions about the features, one question per branch. | aka: decision trees, tree classifier
- centroid | The mean position of all the points in a cluster, used by k-means as the cluster's centre. | aka: centroids, cluster centre, cluster center
- k-means | A clustering algorithm that repeats "assign each point to its nearest centroid, then move each centroid to the mean of its points" until nothing moves. | aka: k-means clustering, KMeans
- inertia | The sum of squared distances from every point to its cluster's centroid, which k-means tries to make small. | aka: within-cluster sum of squares
- linkage | The rule that decides how far apart two clusters are, such as the closest pair, the farthest pair or the average of all pairs. | aka: single linkage, complete linkage, average linkage
- dendrogram | A tree diagram that shows which clusters merged and at what distance during hierarchical clustering. | aka: dendrograms
- silhouette score | A number from -1 to +1 that says how well each point fits its own cluster compared with the nearest other cluster. | aka: silhouette coefficient
- DBSCAN | A clustering algorithm that grows clusters from dense regions of points and labels isolated points as noise. | aka: density-based clustering

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Treating the lowest inertia as the best K: inertia always falls as K rises, so the elbow and silhouette score guide the choice and a human decides.
- Clustering unscaled features: the feature with the largest range dominates every distance, so a column in thousands swamps a column in single digits; scale first.
- Expecting k-means to find any shape: it draws round, similar-sized clusters and splits rings wrongly, which is where DBSCAN is used; then turning DBSCAN's knobs the wrong way: a smaller `eps` or a larger `min_samples` labels more points -1 (noise), and a larger `eps` merges clusters and lowers noise.
- Reading the silhouette score as a verdict: on the iris petal measurements it prefers K = 2 while three species exist; the species labels were never given to the algorithm.
- Using the unlimited-depth tree because its training accuracy is 100%: it memorises noise, so compare against test accuracy and limit `max_depth`.
- Running a learner's own edits on the shared notebook instead of a Drive copy, or forgetting that a changed "Try changing" value must be reverted before the next section.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Run `### 1.2` (depth 1, 4, no limit on `make_moons`) and say "underfit, fit, overfit" over the three boundaries, tying back to Monday's polynomial degrees 1, 3 and 15.
- Run `### 3.2` and `### 3.3`: show the single `cdist` table, read off single, complete, average and centroid linkage, then draw the dendrogram and re-run once with `method="single"` as the "Try changing" prompt.
- Run `## 4. K-means by hand` (four panels until the centroids stop moving) after the whiteboard round on eight points, then `## 5` and `### 5.1`/`### 5.2`: `labels_`, `cluster_centers_`, inertia, the elbow against the silhouette score, and raw against `StandardScaler`-scaled features.
- Run `## 7` with `eps=0.1` and `eps=0.5` on the rings and point at label -1 as noise; close with the `## Recap` table and Quick check read aloud.
