# w06d3 — Introduction to deep learning

gate: light
verified: 2026-11-16
week: 6 · AI/ML fundamentals
day: 3 · deep-learning-concepts

version-stamps:
  - python: 3.13.18 (verified 2026-11-16) — runs in Colab; source: Colab's published runtime manifest os-info.txt (`python --version` line), https://github.com/googlecolab/backend-info/blob/main/os-info.txt at the commit of 2026-11-12 (the release-notes page https://colab.research.google.com/notebooks/relnotes.ipynb renders only a sign-in shell to a fetch, so the manifest Colab generates from its runtime image is the source); the runbook's setup check reprints it with the convention's stamp command
  - numpy: 2.4.6 (verified 2026-11-16) — runs in Colab; source: Colab's `pip freeze` manifest https://github.com/googlecolab/backend-info/blob/main/pip-freeze.txt, commit of 2026-11-12, line `numpy==2.4.6`
  - scipy: 1.16.3 (verified 2026-11-16) — runs in Colab; source: same pip-freeze.txt, commit of 2026-11-12, line `scipy==1.16.3`; `scipy.signal.correlate2d`
  - scikit-learn: 1.6.1 (verified 2026-11-16) — runs in Colab; source: same pip-freeze.txt, commit of 2026-11-12, line `scikit-learn==1.6.1`; `load_digits`, `load_sample_image`, `CountVectorizer`, `TfidfVectorizer`, `LogisticRegression`, `make_pipeline`
  - matplotlib: 3.10.0 (verified 2026-11-16) — runs in Colab; source: same pip-freeze.txt, commit of 2026-11-12, line `matplotlib==3.10.0`
  - tensorflow: 2.21.0 (verified 2026-11-16) — runs in Colab; reference only, not imported on Wednesday (first used Thursday); source: same pip-freeze.txt, commit of 2026-11-12, line `tensorflow==2.21.0`
  - keras: 3.13.2 (verified 2026-11-16) — runs in Colab; reference only, reached as `tf.keras` from Thursday; source: same pip-freeze.txt, commit of 2026-11-12, line `keras==3.13.2`

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- `load_digits` returns 1,797 samples of 8 by 8 greyscale images (64 features, pixel values 0 to 16, 10 classes) — [load_digits](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html)
- `load_sample_image("china.jpg")` returns a 427 by 640 RGB uint8 array bundled with scikit-learn — [load_sample_image](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_sample_image.html)
- `LogisticRegression` defaults to `max_iter=100` and warns with ConvergenceWarning when lbfgs stops early — [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- `scipy.signal.correlate2d` slides the kernel without flipping it, while `convolve2d` flips it first — [correlate2d](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate2d.html)
- `tf.keras.layers.Conv2D` slides a kernel over the input unflipped (cross-correlation), which deep learning calls convolution — [tf.keras.layers.Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D)
- With `mode="valid"`, a k by k kernel over an n by n image yields an (n-k+1) by (n-k+1) output, so a 3 by 3 kernel on an 8 by 8 digit gives 6 by 6 — [correlate2d](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate2d.html)
- A 2 by 2 max pooling with stride 2 halves each spatial dimension and keeps the largest value in each window — [tf.keras.layers.MaxPooling2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/MaxPooling2D)
- A 64-16-10 dense network has 64*16+16 = 1,040 plus 16*10+10 = 170, so 1,210 parameters — [tf.keras.layers.Dense](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
- A dense layer computes activation(dot(input, kernel) + bias) with the kernel of shape (inputs, units) — [tf.keras.layers.Dense](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
- A random-weight 10-class network is right about one time in ten, since chance is 1/10 — [scikit-learn: dummy baselines](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html)
- `CountVectorizer` builds a vocabulary of tokens and returns a sparse document-term count matrix (bag of words) — [CountVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html)
- `CountVectorizer` lowercases and drops single-character tokens by default, via a token pattern of two or more word characters — [CountVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html)
- `TfidfVectorizer` equals CountVectorizer followed by TfidfTransformer, using a smoothed idf and L2-normalised rows by default — [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- `ngram_range=(1, 2)` extracts 2-grams of words in addition to the 1-grams, so adjacent word pairs join the vocabulary — [Text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)
- Each term found during `fit` gets a column; words not seen in the training corpus are ignored in later calls to `transform`, so new text goes through `transform` with the training vocabulary — [Text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)
- A CNN tutorial on image classification stacks Conv2D, MaxPooling2D, Flatten and Dense layers — [Convolutional Neural Network (CNN) tutorial](https://www.tensorflow.org/tutorials/images/cnn)
- `TfidfVectorizer(ngram_range=(1, 2))` builds a vocabulary holding both unigrams and bigrams, so a title such as 'Login page returns 500' contributes 'login', 'page' and the bigram 'login page' — [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- The `@` operator is shorthand for `np.matmul` on arrays: two 1-D arrays give their inner (dot) product, and two 2-D arrays are multiplied like conventional matrices — [numpy.matmul](https://numpy.org/doc/stable/reference/generated/numpy.matmul.html) (fetched 2026-11-16)
- `argmax` returns the indices of the maximum values along an axis; with `axis=1` on a 2-D array that is the position of the largest value in each row — [numpy.argmax](https://numpy.org/doc/stable/reference/generated/numpy.argmax.html) (fetched 2026-11-16)
- `reshape` gives an array a new shape without changing its data; one dimension can be -1 and is inferred from the length, so `reshape(-1)` flattens to one dimension — [numpy.reshape](https://numpy.org/doc/stable/reference/generated/numpy.reshape.html) (fetched 2026-11-16)
- `max` with a tuple of axes takes the maximum over several axes at once — [numpy.max](https://numpy.org/doc/stable/reference/generated/numpy.max.html) (fetched 2026-11-16)
- `np.roll` shifts array elements along an axis, and elements that roll beyond the last position are re-introduced at the first — [numpy.roll](https://numpy.org/doc/stable/reference/generated/numpy.roll.html) (fetched 2026-11-16)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Intro to deep learning
- Interview questions: What is deep learning and how does it differ from classical machine learning?; Why did deep learning take off after 2012?; When would you pick logistic regression or a tree over a deep network?
- Adjacent concept: Feature engineering versus learned features — a classical model needs hand-made columns while a network learns its own from raw pixels or text (framing, uncited: deep learning is the innermost of week 5's nested circles, a kind of machine learning, itself a kind of AI).
- Trade-off or limit: Deep networks need large labelled datasets and compute, and are harder to explain than a small linear model — [Neural network models (supervised)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)
- Recognise on sight: `LogisticRegression(max_iter=5000).fit(X_train, y_train)` on 64 raw digit pixels as the baseline image classifier.
- Claims:
  - `load_digits` gives 64 pixel features per image, so a linear model can be fit on raw pixels with no hand-made features — [load_digits](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html)
  - Raising `max_iter` lets lbfgs finish on unscaled features — [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
  - Compare training and test accuracy with `accuracy_score` before trusting a model — [accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html)
  - scikit-learn's own neural network is not meant for large-scale work and has no GPU support, one reason deep-learning work runs on GPU frameworks such as TensorFlow — [Neural network models (supervised)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)

### Neural networks - types
- Interview questions: Name the main neural network types and the input each suits; What does a transformer do that a recurrent network does not?; What is an autoencoder for?
- Adjacent concept: Architecture follows data shape — table rows, images, sequences, text at scale, unlabelled data to compress.
- Trade-off or limit: Recurrent networks process a sequence step by step, which is slow to train compared with attention over the whole sequence — [Neural machine translation with a Transformer and Keras](https://www.tensorflow.org/text/tutorials/transformer)
- Recognise on sight: `Conv2D`, `LSTM`, `Dense`, `MultiHeadAttention` layer names in a model definition (named only; Keras code is Thursday).
- Claims:
  - Feedforward networks pass data one way through dense layers; scikit-learn's MLPClassifier is one — [MLPClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html)
  - Convolutional networks suit grid data such as images — [Convolutional Neural Network (CNN)](https://www.tensorflow.org/tutorials/images/cnn)
  - Recurrent layers such as LSTM read sequences in order — [tf.keras.layers.LSTM](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
  - Transformers use attention and underlie large language models — [tf.keras.layers.MultiHeadAttention](https://www.tensorflow.org/api_docs/python/tf/keras/layers/MultiHeadAttention)
  - Self-attention against recurrence (added 2026-11-20, checked that day): "The global self-attention layer ... lets every sequence element directly access every other sequence element, with only a few operations, and all the outputs can be computed in parallel"; "Attention allows each location to have access to the entire input at each layer, while in RNNs and CNNs, the information needs to pass through many processing steps to move a long distance, which makes it harder to learn"; "Unlike [RNNs], Transformers are parallelizable. This makes them efficient on hardware like GPUs and TPUs" — [Neural machine translation with a Transformer and Keras](https://www.tensorflow.org/text/tutorials/transformer)
  - Positional encoding (added 2026-11-20, checked that day): "The attention layers used throughout the model see their input as a set of vectors, with no order", so without it `how are you`, `how you are` and `you how are` "are indistinguishable"; "A Transformer adds a "Positional Encoding" to the embedding vectors" — [Neural machine translation with a Transformer and Keras](https://www.tensorflow.org/text/tutorials/transformer)
  - An autoencoder is trained to rebuild its input through a narrow middle (one card only today) — [Intro to Autoencoders](https://www.tensorflow.org/tutorials/generative/autoencoder)

### CNN and image classification
- Interview questions: What does a convolution layer compute?; Why pool, and what does max pooling throw away?; Why does a CNN beat a flat classifier on large images?
- Adjacent concept: A kernel is a small grid of weights; a CNN learns its kernels instead of using hand-made ones.
- Trade-off or limit: Max pooling shrinks the output and gives some shift tolerance but discards exact position — [tf.keras.layers.MaxPooling2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/MaxPooling2D)
- Recognise on sight: `correlate2d(img, kernel, mode="valid")` with `kernel = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])`, the vertical-edge kernel.
- Claims:
  - `correlate2d` does not flip the kernel, matching what `Conv2D` computes — [correlate2d](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate2d.html)
  - A `valid` convolution of an n by n image with a k by k kernel is (n-k+1) square — [correlate2d](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate2d.html)
  - ReLU is max(0, x), applied elementwise after the convolution — [tf.keras.activations.relu](https://www.tensorflow.org/api_docs/python/tf/keras/activations/relu)
  - A CNN stack runs convolution, pooling, then Flatten and Dense output layers — [CNN tutorial](https://www.tensorflow.org/tutorials/images/cnn)
  - Swapping to a horizontal kernel (the transpose) lights horizontal edges instead — [correlate2d](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate2d.html)

### Artificial neural network, layers
- Interview questions: What does one neuron compute?; How do you count the parameters of a dense layer?; Why do shapes have to line up between layers?
- Adjacent concept: Weights, biases and a forward pass in numpy, with random weights; backpropagation and training are week 7.
- Trade-off or limit: Untrained random weights give chance accuracy (about 10 percent on ten digits); only training fixes that — [DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html)
- Recognise on sight: `h = np.maximum(0, X @ W1 + b1)` then `logits = h @ W2 + b2` with W1 (64, 16) and W2 (16, 10).
- Claims:
  - A layer's weight matrix has shape (inputs, units) and its bias has shape (units,) — [tf.keras.layers.Dense](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
  - Parameters per dense layer = inputs*units + units — [tf.keras.layers.Dense](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense)
  - Sigmoid squashes a value into 0 to 1; ReLU zeroes negatives (one line each; activations are Friday) — [tf.keras.activations.sigmoid](https://www.tensorflow.org/api_docs/python/tf/keras/activations/sigmoid)
  - Fixing a random seed makes the untrained forward pass reproducible — [numpy.random.default_rng](https://numpy.org/doc/stable/reference/random/generator.html)
  - Hidden layers are the layers between input and output — [Neural network models (supervised)](https://scikit-learn.org/stable/modules/neural_networks_supervised.html)

### Natural language processing - techniques, components, applications
- Interview questions: Explain bag of words and its main weakness; What does TF-IDF change compared with raw counts?; How would you route support tickets automatically?
- Adjacent concept: The text pipeline of tokenizer, vocabulary, vectorizer and model; embeddings and named entity recognition are week 8.
- Trade-off or limit: Bag of words ignores word order, and a word absent from the training vocabulary is silently dropped at prediction time — [CountVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html)
- Recognise on sight: `TfidfVectorizer(ngram_range=(1, 2))` followed by `LogisticRegression(max_iter=5000)` in a `make_pipeline`.
- Claims:
  - `get_feature_names_out()` lists the learned vocabulary — [CountVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html)
  - TF-IDF down-weights words that appear in many documents — [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
  - `make_pipeline` chains vectorizer and classifier so `fit` and `predict` take raw strings — [Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.make_pipeline.html)
  - `make_pipeline` names each step automatically after its type in lower case (e.g. `tfidfvectorizer`), and the `named_steps` attribute inspects the steps — [make_pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.make_pipeline.html)
  - Bag-of-words or TF-IDF features combined with fast linear models train document classifiers in a supervised setting — [Text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)
  - Spam filtering, sentiment, ticket routing, translation and chat assistants are common NLP applications (framing from the week plan, uncited)
  - With only 24 labelled titles the model is a teaching toy, and the labels are invented for the notebook (week plan's datasets row, uncited)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- scikit-learn load_digits — https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- scikit-learn load_sample_image — https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_sample_image.html
- scikit-learn LogisticRegression — https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- scikit-learn CountVectorizer — https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
- scikit-learn TfidfVectorizer — https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- scikit-learn Text feature extraction — https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction (fetched 2026-11-16; replaces the Working with text data tutorial, which now returns HTTP 404)
- scikit-learn Neural network models (supervised) — https://scikit-learn.org/stable/modules/neural_networks_supervised.html
- SciPy correlate2d — https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate2d.html
- TensorFlow tf.keras.layers.Conv2D — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D
- TensorFlow tf.keras.layers.MaxPooling2D — https://www.tensorflow.org/api_docs/python/tf/keras/layers/MaxPooling2D
- TensorFlow tf.keras.layers.Dense — https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense
- TensorFlow tf.keras.layers.MultiHeadAttention — https://www.tensorflow.org/api_docs/python/tf/keras/layers/MultiHeadAttention
- TensorFlow CNN tutorial — https://www.tensorflow.org/tutorials/images/cnn
- TensorFlow Intro to Autoencoders — https://www.tensorflow.org/tutorials/generative/autoencoder
- TensorFlow Text: Neural machine translation with a Transformer and Keras — https://www.tensorflow.org/text/tutorials/transformer
- scikit-learn DummyClassifier — https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html
- Colab backend-info runtime manifests (pip-freeze.txt, os-info.txt; commit of 2026-11-12) — https://github.com/googlecolab/backend-info
- NumPy numpy.matmul — https://numpy.org/doc/stable/reference/generated/numpy.matmul.html (fetched 2026-11-16)
- NumPy numpy.argmax — https://numpy.org/doc/stable/reference/generated/numpy.argmax.html (fetched 2026-11-16)
- NumPy numpy.reshape — https://numpy.org/doc/stable/reference/generated/numpy.reshape.html (fetched 2026-11-16)
- NumPy numpy.max — https://numpy.org/doc/stable/reference/generated/numpy.max.html (fetched 2026-11-16)
- NumPy numpy.roll — https://numpy.org/doc/stable/reference/generated/numpy.roll.html (fetched 2026-11-16)

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- convolution | A small grid of numbers (a kernel) slides across an image and produces a new grid that lights up where the pattern appears, which in deep learning is cross-correlation with the kernel unflipped. | aka: cross-correlation, convolutional layer, Conv2D
- max pooling | A step that shrinks a grid by keeping only the largest value in each small window, such as 2 by 2. | aka: pooling, MaxPooling2D
- forward pass | Running an input through a network's layers in order to get its output, with no learning involved. | aka: forward propagation
- bag of words | A way to turn text into numbers by counting how often each vocabulary word appears, ignoring word order. | aka: BoW, word counts, CountVectorizer
- TF-IDF | A word-count score that rewards words frequent in one text and rare across all texts, so common words count for less. | aka: tf-idf, TfidfVectorizer, term frequency-inverse document frequency
- n-gram | A run of n neighbouring words (a bigram is two) treated as one vocabulary entry so some word order is kept. | aka: n-grams, bigram, bigrams, ngram_range

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Using `scipy.signal.convolve2d` and then wondering why the edge lights up on the opposite side: it flips the kernel, so the notebook uses `correlate2d`, which matches `Conv2D`.
- Forgetting `max_iter=5000` on raw pixels and getting a ConvergenceWarning, or reading the warning as a broken model.
- Shape mismatches in the forward pass (multiplying (1, 64) by a (16, 64) matrix) because weights are stored as (inputs, units).
- Expecting the random-weight network to classify digits: it scores about one in ten until trained in week 7.
- Calling `fit_transform` on a new ticket title, which rebuilds the vocabulary, instead of `transform`; or being surprised that unseen words are ignored.
- Treating 24 invented ticket labels as proof the classifier works: it is a toy for showing the pipeline.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Section 1 then 2 and 3: run the raw-pixel baseline and read its test accuracy, compute one neuron by hand, then print the shape at each layer of the 64-16-10 forward pass and the 1,210 parameter count; state that guessing is about 10 percent.
- Section 4: show the vertical-edge kernel over a digit and over `china.jpg` in greyscale with `correlate2d`, then ReLU and 2 by 2 max pooling, and the "Try changing" swap to a horizontal kernel (revert after).
- Section 5: print the `CountVectorizer` vocabulary for a few titles, show TF-IDF weights, then fit the 24-title classifier and predict a new title, naming tokenizer, vocabulary, vectorizer and model as the pipeline.
- Facilitation slots (no notebook): the learned-features contrast with Monday's models, and the five-card network types matching; keep Keras code and training out of today.
