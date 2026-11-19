# w06d4 — TensorFlow introduction

gate: light
verified: 2026-11-16
week: 6 · AI/ML fundamentals
day: 4 · tensorflow-introduction

version-stamps:
  - python: 3.15 (verified 2026-11-16) — course Python, NOT used today; the notebook runs on Colab's own Python
  - colab-python: 3.12.x (runs in Colab; no wheel pick on the course Python; light gate, not read from a fresh runtime: confirm with the stamp cell before the commit)
  - tensorflow: 2.21.x or newer, whatever Colab preinstalls (runs in Colab; TensorFlow has no cp315 wheel; the tensorflow.org API docs render from v2.21.0 as of 2026-11-16; confirm with `tf.__version__` on a fresh runtime)
  - keras: 3.15.x (runs in Colab; `tf.keras.__version__` reports the Keras 3 line since TensorFlow 2.16; the mnist.load_data docs link Keras v3.15.1 as of 2026-11-16; confirm on a fresh runtime)
  - numpy: Colab preinstalled, 2.x line (runs in Colab; confirm on a fresh runtime)
  - scipy / scikit-learn / matplotlib: Colab preinstalled (not used by the Thursday notebook beyond the setup cell; confirm on a fresh runtime)
  - stamp source: the fresh-runtime cell `import sys, numpy, scipy, sklearn, matplotlib, tensorflow as tf; print(sys.version, numpy.__version__, scipy.__version__, sklearn.__version__, matplotlib.__version__, tf.__version__, tf.keras.__version__)`; the lines above are light-gate major-line stamps written without a runtime, and that cell's output on a fresh Colab runtime replaces them in this brief before the notebook commit, so pages and the runbook quote the cell's numbers

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- TensorFlow is an open-source library for numerical computation on tensors, with Keras as its high-level model-building API — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)
- A tensor is a multi-dimensional array with a uniform dtype; rank is the number of axes and shape is the length of each — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)
- Tensors created with `tf.constant` are immutable; to change values you build a new tensor, while `tf.Variable` holds state (Friday) — [Introduction to Variables](https://www.tensorflow.org/guide/variable)
- TensorFlow 2 runs operations eagerly by default, returning concrete values immediately — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
- `tf.function` traces a Python function into a `tf.Graph`; the graph is a set of `tf.Operation` nodes and `tf.Tensor` edges that can be optimised and run without Python — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
- During tracing, a Python `print` runs once; `tf.print` becomes a graph operation and prints on every call — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
- A `tf.function` retraces when it sees a new input shape or dtype, or a new Python value as argument; `input_signature` with `tf.TensorSpec` fixes this — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
- `tf.reduce_sum`, `tf.reduce_mean` and `tf.reduce_max` reduce over `axis`; with `axis=None` they reduce every element, and `keepdims=True` keeps reduced axes with length 1 — [tf.math.reduce_sum](https://www.tensorflow.org/api_docs/python/tf/math/reduce_sum)
- `tf.reduce_mean` on an integer tensor returns an integer mean (the docs' example gives int32 0 for `[1, 0, 1, 0]`, and the docs note its aggressive type inference from the input; "truncated" is what that int result shows, e.g. `[1, 2]` gives 1), so images are cast to `float32` first — [tf.math.reduce_mean](https://www.tensorflow.org/api_docs/python/tf/math/reduce_mean)
- `tf.argmax` takes a single integer axis, has no `keepdims`, and returns indices, not values; its signature shows `axis=None` while the Args table says "Default to 0", and `axis=None` is treated as axis 0, so leaving `axis` out does not search the whole tensor — [tf.math.argmax](https://www.tensorflow.org/api_docs/python/tf/math/argmax)
- TensorFlow 1 required you to stitch a graph together with `tf.*` calls and then run it by passing output and input tensors to `session.run`, with placeholders fed through `feed_dict` (`outputs = session.run(f(placeholder), feed_dict={placeholder: input})` becomes `outputs = f(input)` in TF2) — [TF1.x vs TF2: behaviors and APIs](https://www.tensorflow.org/guide/migrate/tf1_vs_tf2)
- In TF2 you never need to define a Placeholder or a `tf.Session` — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
- `tf.compat.v1` holds legacy TF1 endpoints as a migration bridge; it is not idiomatic TF2 and is not for brand-new code — [Migrate to TF2](https://www.tensorflow.org/guide/migrate), [TF1.x vs TF2: behaviors and APIs](https://www.tensorflow.org/guide/migrate/tf1_vs_tf2)
- TensorFlow's API and reference implementation were released as open source under the Apache 2.0 licence in November 2015 — [TensorFlow: Large-Scale Machine Learning on Heterogeneous Distributed Systems (arXiv:1603.04467)](https://arxiv.org/abs/1603.04467)
- TensorFlow 1.0.0 was released in February 2017 and TensorFlow 2.0.0 in September 2019 — [tensorflow v1.0.0 release](https://github.com/tensorflow/tensorflow/releases/tag/v1.0.0), [tensorflow v2.0.0 release](https://github.com/tensorflow/tensorflow/releases/tag/v2.0.0)
- From TensorFlow 2.16, `tf.keras` is Keras 3, which can train on any of three backends, TensorFlow, JAX or PyTorch (Keras 3.8+ also lists an inference-only OpenVINO backend) — [Keras 3 announcement](https://keras.io/keras_3/)
- PyTorch and JAX are the other widely used open-source frameworks for array computation and deep learning; JAX pairs a NumPy-style API with transformations such as `jit` and `grad` — [PyTorch documentation](https://pytorch.org/docs/stable/index.html), [JAX documentation](https://docs.jax.dev/en/latest/)
- TensorBoard's Graphs tab shows a traced function when you call `tf.summary.trace_on(graph=True)`, run it, then `tf.summary.trace_export` under a default writer (the guide's TF 2.2-era example also passes `profiler=True` and `profiler_outdir`; `profiler` defaults to False and `profiler_outdir` is optional, so `graph=True` alone exports the graph; confirm on the fresh Colab runtime with the stamp cell) — [Examining the TensorFlow Graph](https://www.tensorflow.org/tensorboard/graphs), [tf.summary.trace_export](https://www.tensorflow.org/api_docs/python/tf/summary/trace_export)
- `tf.keras.datasets.mnist.load_data()` returns `uint8` arrays: 60000 training images of 28 by 28 and 10000 test images — [mnist.load_data](https://www.tensorflow.org/api_docs/python/tf/keras/datasets/mnist/load_data)
- What MNIST is (added 2026-11-19, checked that day): the loader's page calls it "a dataset of 60,000 28x28 grayscale images of the 10 digits, along with a test set of 10,000 images", with labels that are integers 0 to 9 — [mnist.load_data](https://www.tensorflow.org/api_docs/python/tf/keras/datasets/mnist/load_data); the digits are handwritten: the TensorFlow Datasets catalog names it "The MNIST database of handwritten digits" — [TensorFlow Datasets catalog: mnist](https://www.tensorflow.org/datasets/catalog/mnist)
- Keras trains inside a graph (added 2026-11-19, checked that day): "`tf.keras.Model` methods such as `fit`, `evaluate`, and `predict` execute as graphs with `tf.function` under the hood", and `compile(run_eagerly=True)` stops the model's logic being wrapped in a `tf.function`. So what this day teaches about tracing (a Python `print` that runs once, a retrace on a new shape or dtype) is what happens when a Keras model trains — [Effective TensorFlow 2](https://www.tensorflow.org/guide/effective_tf2)
- Broadcasting stretches a size-1 or missing axis so tensors of different shapes can be combined elementwise — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### TensorFlow introduction
- Interview questions: What is a tensor and how is it different from a NumPy array?; What do rank, shape and dtype tell you?; Why does `tf.constant` need a dtype and what happens when you add an int tensor to a float tensor?
- Adjacent concept: Keras as the layer on top of TensorFlow — it is the API teams actually write models in, so the page names it and leaves building models to Friday.
- Trade-off or limit: TensorFlow tensors are immutable and strictly typed, unlike a NumPy array you can edit in place — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)
- Recognise on sight: `import tensorflow as tf` then `x = tf.constant([[1., 2.], [3., 4.]])` and `x.numpy()`
- Claims:
  - A tensor has a shape and a single dtype; `tf.constant` infers float32 for Python floats and int32 for Python ints — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)
  - `.numpy()` copies a tensor into a NumPy array in eager mode — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)
  - Operations on mismatched dtypes raise an error rather than casting silently; use `tf.cast` — [tf.cast](https://www.tensorflow.org/api_docs/python/tf/cast)
  - Elementwise arithmetic uses broadcasting; `tf.matmul` is matrix multiplication — [Introduction to Tensors](https://www.tensorflow.org/guide/tensor)
  - Colab ships TensorFlow preinstalled and runs on CPU unless a GPU runtime is chosen — [Colab FAQ](https://research.google.com/colaboratory/faq.html)

### History of TensorFlow
- Interview questions: Who built TensorFlow and when was it released?; What changed between TensorFlow 1 and 2?; Where does PyTorch or JAX fit next to it?
- Adjacent concept: Why old tutorials still use `Session` — most of the online material predates 2019, so recognising TF1 code matters for reading it.
- Trade-off or limit: TF1 code does not run unchanged on TF2; `tf.compat.v1` exists only as a migration bridge — [Migrate to TF2](https://www.tensorflow.org/guide/migrate)
- Recognise on sight: `sess = tf.Session()` or `tf.placeholder(tf.float32)` in a tutorial
- Claims:
  - TensorFlow is Google Brain's second-generation system after DistBelief, and its API and reference implementation were open-sourced in November 2015 — [TensorFlow: Large-Scale Machine Learning on Heterogeneous Distributed Systems (arXiv:1603.04467)](https://arxiv.org/abs/1603.04467)
  - TensorFlow 1.0.0 was released in February 2017; TensorFlow 1 builds a graph first and runs it in a session — [tensorflow v1.0.0 release](https://github.com/tensorflow/tensorflow/releases/tag/v1.0.0), [TF1.x vs TF2: behaviors and APIs](https://www.tensorflow.org/guide/migrate/tf1_vs_tf2)
  - TensorFlow 2.0.0 was released in September 2019 and made eager execution the default and Keras the main high-level API — [tensorflow v2.0.0 release](https://github.com/tensorflow/tensorflow/releases/tag/v2.0.0), [Effective TensorFlow 2](https://www.tensorflow.org/guide/effective_tf2)
  - From TensorFlow 2.16, `tf.keras` is Keras 3, and Keras 3 can train on three backends (TensorFlow, JAX, PyTorch); an inference-only OpenVINO backend also exists since Keras 3.8 — [Keras 3 announcement](https://keras.io/keras_3/)
  - PyTorch is an open-source deep-learning framework that runs eagerly, and JAX is Google's NumPy-style library with composable `jit`, `grad` and `vmap` transformations — [PyTorch documentation](https://pytorch.org/docs/stable/index.html), [JAX documentation](https://docs.jax.dev/en/latest/)

### Implementing basic graphs
- Interview questions: What is the difference between eager and graph execution?; What does `@tf.function` do to a Python function?; What is a trace?
- Adjacent concept: AutoGraph, which rewrites Python `if` and `for` into graph operations — it explains why Python control flow works inside `tf.function`.
- Trade-off or limit: Python side effects such as `print` or appending to a list run only during tracing — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
- Recognise on sight: `@tf.function` above a `def`, and `f.get_concrete_function(...).graph.get_operations()`
- Claims:
  - Eager execution is easy to debug; graphs allow optimisation and export — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
  - `get_concrete_function` returns the traced graph for one input signature — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
  - A new shape or dtype creates a new concrete function (retrace) — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
  - `tf.print` is the graph-safe way to print tensor values — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
  - A traced graph's `get_operations()` lists nodes such as `Placeholder`, `Const`, `AddV2` and `Identity`; here `Placeholder` is the node for the traced function's input argument, not TensorFlow 1's `tf.placeholder` API (section 5 history) — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)

### Reducing tensors of arbitrary shape
- Interview questions: What does `axis=0` mean for a rank-3 tensor?; What does `keepdims=True` change?; How is `tf.argmax` different from `tf.reduce_max`?
- Adjacent concept: Broadcasting a reduced result back against the original — `keepdims=True` exists so the shapes line up.
- Trade-off or limit: `tf.argmax` accepts one integer axis only and does not flatten when axis is omitted — [tf.math.argmax](https://www.tensorflow.org/api_docs/python/tf/math/argmax)
- Recognise on sight: `tf.reduce_mean(images, axis=0)` for a mean image, `tf.reduce_max(images, axis=(1, 2))`
- Claims:
  - `axis=None` reduces every element to a rank-0 tensor — [tf.math.reduce_sum](https://www.tensorflow.org/api_docs/python/tf/math/reduce_sum)
  - `axis` may be an int, a tuple or list of ints; negative axes count from the end — [tf.math.reduce_sum](https://www.tensorflow.org/api_docs/python/tf/math/reduce_sum)
  - The reduced axes disappear from the shape unless `keepdims=True` — [tf.math.reduce_sum](https://www.tensorflow.org/api_docs/python/tf/math/reduce_sum)
  - Reducing the MNIST batch `(60000, 28, 28)` over axis 0 gives `(28, 28)`; over `(1, 2)` gives `(60000,)` — [tf.math.reduce_max](https://www.tensorflow.org/api_docs/python/tf/math/reduce_max)
  - `tf.TensorSpec(shape=None, dtype=tf.float32)` accepts any shape in one traced graph — [Better performance with tf.function](https://www.tensorflow.org/guide/function)
  - `tf.reshape(images, (-1, 784))` infers the batch axis from the other lengths — [tf.reshape](https://www.tensorflow.org/api_docs/python/tf/reshape)

### Graphs, sessions, TensorBoard
- Interview questions: What was a `tf.Session` and why is it gone?; How do you look at a graph in TensorBoard?; What is the difference between TF1 placeholders and `tf.function` arguments?
- Adjacent concept: How the Graphs tab names and groups nodes — every operation gets a name, `tf.name_scope` prefixes the names of operations made inside it, and TensorBoard collapses each scope into one expandable node, which is how a reader finds their way round a larger graph.
- Trade-off or limit: The Graphs tab shows structure, not training behaviour — [Examining the TensorFlow Graph](https://www.tensorflow.org/tensorboard/graphs)
- Recognise on sight: `writer = tf.summary.create_file_writer("logs/graph")` and `%tensorboard --logdir logs`
- Claims:
  - In TF1 a graph was built first and evaluated by `session.run` with placeholders fed through `feed_dict` — [TF1.x vs TF2: behaviors and APIs](https://www.tensorflow.org/guide/migrate/tf1_vs_tf2)
  - In TF2 no Placeholder or `tf.Session` is needed — [Introduction to graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
  - In TF2 a `tf.function` replaces the session; arguments replace placeholders — [Effective TensorFlow 2](https://www.tensorflow.org/guide/effective_tf2)
  - `trace_export` must run with a default writer, so it sits inside `with writer.as_default():` — [tf.summary.trace_export](https://www.tensorflow.org/api_docs/python/tf/summary/trace_export)
  - Colab loads TensorBoard with `%load_ext tensorboard` then `%tensorboard --logdir logs` — [Get started with TensorBoard](https://www.tensorflow.org/tensorboard/get_started)
  - `tf.name_scope(name)` adds a prefix to the names of operations created inside the context, and the Graphs tab groups operations that share a scope into one collapsible node — [tf.name_scope](https://www.tensorflow.org/api_docs/python/tf/name_scope), [Examining the TensorFlow Graph](https://www.tensorflow.org/tensorboard/graphs)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Introduction to Tensors — https://www.tensorflow.org/guide/tensor
- Introduction to Variables — https://www.tensorflow.org/guide/variable
- Introduction to graphs and tf.function — https://www.tensorflow.org/guide/intro_to_graphs
- Better performance with tf.function — https://www.tensorflow.org/guide/function
- Effective TensorFlow 2 — https://www.tensorflow.org/guide/effective_tf2
- Migrate to TF2 — https://www.tensorflow.org/guide/migrate
- TF1.x vs TF2: behaviors and APIs — https://www.tensorflow.org/guide/migrate/tf1_vs_tf2
- Examining the TensorFlow Graph (TensorBoard) — https://www.tensorflow.org/tensorboard/graphs
- Get started with TensorBoard — https://www.tensorflow.org/tensorboard/get_started
- tf.math.reduce_sum — https://www.tensorflow.org/api_docs/python/tf/math/reduce_sum
- tf.math.reduce_mean — https://www.tensorflow.org/api_docs/python/tf/math/reduce_mean
- tf.math.argmax — https://www.tensorflow.org/api_docs/python/tf/math/argmax
- tf.summary.trace_export — https://www.tensorflow.org/api_docs/python/tf/summary/trace_export
- tf.keras.datasets.mnist.load_data — https://www.tensorflow.org/api_docs/python/tf/keras/datasets/mnist/load_data
- TensorFlow Datasets catalog: mnist (read 2026-11-19) — https://www.tensorflow.org/datasets/catalog/mnist
- tf.name_scope — https://www.tensorflow.org/api_docs/python/tf/name_scope
- TensorFlow: Large-Scale Machine Learning on Heterogeneous Distributed Systems (arXiv:1603.04467) — https://arxiv.org/abs/1603.04467
- tensorflow v1.0.0 release (GitHub) — https://github.com/tensorflow/tensorflow/releases/tag/v1.0.0
- tensorflow v2.0.0 release (GitHub) — https://github.com/tensorflow/tensorflow/releases/tag/v2.0.0
- Keras 3 announcement — https://keras.io/keras_3/
- PyTorch documentation — https://pytorch.org/docs/stable/index.html
- JAX documentation — https://docs.jax.dev/en/latest/
- Colab FAQ — https://research.google.com/colaboratory/faq.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- eager execution | TensorFlow 2's default mode, where each operation runs at once and returns a real value you can print. | aka: eager mode, eagerly
- tf.function | A decorator that traces a Python function into a TensorFlow graph so repeated calls run the graph instead of the Python code. | aka: @tf.function, graph execution
- computation graph | A set of operations (nodes) joined by the tensors that flow between them (edges), which TensorFlow can optimise and run without Python. | aka: dataflow graph, tf.Graph
- tracing | The first call of a `tf.function` with a new input shape or dtype, when Python runs once to record the graph. | aka: retracing, trace
- reduction | An operation such as sum, mean or max that collapses one or more dimensions of a tensor into fewer values. | aka: reduce, reduce_sum, reduce_mean
- TensorBoard | A browser dashboard that reads log files and shows a traced graph, and later training curves. | aka: Graphs tab
- Keras | The high-level API for building and training neural networks on top of TensorFlow. | aka: tf.keras

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Following a tutorial that uses `tf.Session` or `tf.placeholder`; it fails on TensorFlow 2 with an AttributeError, and the fix is to read it as history, not to import `compat.v1`.
- Taking `tf.reduce_mean` of the raw `uint8` MNIST arrays, which gives a truncated integer mean (or a `TypeError` when passed as a `uint8` tensor to the float-only reducer); cast to `float32` and divide by 255 first.
- Confusing `axis=0` with `axis=(1, 2)` on a batch: one gives a `(28, 28)` mean image, the other gives one value per image.
- Expecting `tf.argmax(x)` to search the whole tensor or to accept `keepdims`; it defaults to axis 0, takes one integer axis, and returns positions.
- Putting a Python `print` inside a `@tf.function` and being surprised it prints once; use `tf.print`.
- Calling `trace_export` outside `with writer.as_default():`, or running `%tensorboard` before `%load_ext tensorboard`, so the Graphs tab stays empty.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Notebook `04_thursday_tensorflow_introduction.ipynb`, sections 1 and 2: show `tf.__version__` and `tf.config.list_physical_devices()`, then a `tf.constant`'s rank, shape, dtype, `.numpy()` and broadcasting, so the library reads as Wednesday's numpy arithmetic.
- Section 3: the same function eager and under `@tf.function`, list `graph.get_operations()`, and run the `print` against `tf.print` pair, showing the Python print once and `tf.print` every call.
- Section 4: cast MNIST first (`tf.cast(x_train, tf.float32) / 255.0`), then reduce over `axis=0` and `axis=(1, 2)` and read the shapes aloud; this is the "Try changing" prompt.
- Section 5: show the TF1 `Session` block as history only, then run the trace-export cell in order and open the TensorBoard Graphs tab once.
