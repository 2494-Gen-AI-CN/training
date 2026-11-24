# QC - 4

<!-- D-0103, D-0107: sections follow the grouping the QC team asks by. AI/ML Fundamentals and TensorFlow and Keras are written by us from weeks 6 to 8 as authored (no Revature unit exists for TensorFlow, Keras, scikit-learn, clustering or feature engineering); where a topic is also in the Revature unit Applying AI and Machine Learning Concepts (IST In Progress, read 2026-11-24) the row uses that unit's wording, and rows of that unit we do not teach are left out. Vector Databases carries the rows of the Revature units Vector DB Fundamentals, Introduction to ChromaDB and Introduction to Pinecone (read 2026-11-24), as written except seven rows reworded to what week 8 does (Chroma in Colab, in-memory and on-disk clients, a sentence-transformers model, deployment and backups explained, not carried out), then four rows for what week 8 teaches beyond them; three RAG rows of those units are held for qc-5, where RAG is taught. Ids are positional: append only. -->

## AI/ML Fundamentals

| Criteria Difficulty | Exit Criteria |
|---------------------|---------------|
| Required            | Can explain what machine learning is, how a rule learned from examples differs from a rule written by hand, and define sample, feature, label and model. |
| Required            | Can differentiate between the supervised and unsupervised learning paradigms, and between regression and classification, and give an example problem for each. |
| Required            | Can build a Linear Regression model to predict a continuous target variable, explain how the line is fitted (slope, intercept, residuals, least squares) and interpret mean squared error and R². |
| Required            | Can implement a train, validation and test split and explain the role of each part, including why a model is scored on data it was not trained on and why the test set is used once. |
| Required            | Can describe scikit-learn's fit and predict pattern and use train_test_split, including what random_state and stratify do. |
| Required            | Can identify signs of the bias-variance tradeoff, underfitting and overfitting from training and validation scores. |
| Required            | Can build a Logistic Regression model for a binary classification task and explain the probability it outputs, how predict turns that probability into a class at 0.5, and the decision boundary. |
| Required            | Can distinguish a model's parameters from its hyperparameters and give an example of each. |
| Required            | Can explain what clustering is, name uses of it, and explain how a clustering is judged when there are no labels. |
| Required            | Can describe the k-means algorithm step by step (assign, update, repeat) and explain why the starting centroids matter. |
| Required            | Can choose a value of K using the elbow method and the silhouette score, and explain what inertia measures. |
| Required            | Can explain why features are scaled before a distance-based algorithm and what StandardScaler does. |
| Required            | Can explain what deep learning is, how learned features differ from hand-made features, and when deep learning is and is not a good fit. |
| Required            | Can name the main neural network families (feedforward, convolutional, recurrent, transformer, autoencoder) and match each to the kind of data it suits. |
| Required            | Can describe a neuron (weighted sum, bias, activation), a layer and a forward pass, and count the parameters of a Dense layer. |
| Required            | Can explain how a CNN reads an image (kernels, convolution, ReLU, max pooling) and why it suits images better than a flat Dense network. |
| Required            | Can explain how text becomes numbers: tokens, a vocabulary, bag of words and TF-IDF. |
| Required            | Can explain what an activation function does, describe sigmoid, tanh, ReLU and softmax, and explain why the activation must be non-linear. |
| Required            | Can describe the mathematical formulation of a Perceptron (weighted sum, bias, step) and its learning rule, and explain linear separability and what a single perceptron cannot learn. |
| Required            | Can explain what a loss function is and describe the difference between MSE and cross-entropy and the practical application of each. |
| Required            | Can explain gradient descent and the effect of a learning rate that is too small or too large. |
| Required            | Can build a Multi-Layer Perceptron (MLP) and explain why a hidden layer with a non-linear activation solves problems a single perceptron cannot. |
| Required            | Can explain the concepts of backpropagation and gradient descent in weight updating: one training step (forward pass, loss, backward pass, update), what backpropagation computes and what the optimizer does with it. |
| Required            | Can identify overfitting and underfitting from learning curves (training and validation loss over epochs). |
| Required            | Can implement Dropout layers in a neural network and an early stopping callback, and explain how each reduces overfitting. |
| Required            | Can describe the order of a model-building project: problem statement, data, split, preprocessing, model with a reason for each choice, training, evaluation, the test set once, limitations. |
| Required            | Can read a Confusion Matrix and calculate and interpret Precision, Recall and F1 scores for one class. |
| Required            | Can explain why accuracy misleads for imbalanced classification and choose between precision and recall by what a wrong answer costs. |
| Required            | Can carry out error analysis: look at the examples a model gets wrong and say what they have in common. |
| Required            | Can make one improvement attempt: change one thing, compare before and after on the same validation data, and say plainly whether it helped. |
| Required            | Can explain what an autoencoder is (encoder, bottleneck, decoder) and what it is trained to do. |
| Required            | Can explain how reconstruction error and a threshold turn an autoencoder into an anomaly detector. |
| Required            | Can explain what feature engineering is, create a new feature from existing columns and judge whether it helped. |
| Required            | Can encode categorical data (one-hot, ordinal, frequency) and say when one-hot encoding is the wrong choice. |
| Required            | Can handle missing values and outliers in a dataset and give a reason for the method chosen. |
| Required            | Can choose an evaluation metric from what each kind of wrong answer costs, and choose a decision threshold on validation data. |
| Required            | Implement L1 (Lasso) and L2 (Ridge) regularization to penalize complex models |
| Preferred           | Can explain multiple and polynomial regression and read a fitted model's coefficients. |
| Preferred           | Can explain how a decision tree makes a prediction and how its depth relates to overfitting. |
| Preferred           | Can give examples of regression and classification problems in industry and say what a wrong answer costs in each. |
| Preferred           | Can compute Euclidean and Manhattan distance between two points. |
| Preferred           | Can explain hierarchical clustering, name common linkage methods, and describe how a dendrogram is read and cut. |
| Preferred           | Can describe where k-means fails and how DBSCAN differs (dense regions, noise points, eps and min_samples). |
| Preferred           | Can compute the output size of a convolution and of a pooling layer. |
| Preferred           | Can explain n-grams and what bag of words loses. |
| Preferred           | Can describe the steps of a text classification pipeline and why new text goes through transform, not fit. |
| Preferred           | Can explain at a high level why self-attention handles distant positions better than recurrence, and the role of positional encoding in the Transformer architecture. |
| Preferred           | Can work one backpropagation update by hand on a network with two weights. |
| Preferred           | Can explain what batch normalization does and how to measure whether it helped. |
| Preferred           | Can demonstrate code reproducibility using random seeds, and explain why a notebook is checked with Run all on a fresh runtime. |
| Preferred           | Can fit preprocessing on the training rows only and explain what leaks otherwise. |
| Preferred           | Can name the levers for improving a model (capacity, dropout, early stopping, batch normalization, learning rate, preprocessing, the decision threshold) and the sign that says to pull each. |
| Preferred           | Can keep a results table across runs and explain what to do when a change did not help. |
| Preferred           | Can explain collaborative filtering and the cold-start problem. |
| Preferred           | Can explain what a restricted Boltzmann machine is and how it produces a recommendation. |
| Preferred           | Can explain feature selection techniques (filter methods, model-based ranking, permutation importance) and measure whether removing features helps. |
| Preferred           | Can build preprocessing and a model into one scikit-learn Pipeline and explain what that prevents. |
| Preferred           | Can explain the macro and weighted averages of precision, recall and F1. |
| Preferred           | Generate and analyze an AUC-ROC curve and Confusion Matrix |
| Preferred           | Implement stratified k-fold cross-validation in evaluating model performance |
| Stretch             | Can explain why a straight-line model is unreliable outside the range of its training data. |
| Stretch             | Can run two iterations of k-means by hand on a small set of points. |
| Stretch             | Can explain why the operation deep learning libraries call convolution is cross-correlation. |
| Stretch             | Can explain what a denoising autoencoder is and how its training pairs differ from a plain autoencoder's. |
| Stretch             | Can explain why some columns may not be used as features even when they improve a score. |

## TensorFlow and Keras

| Criteria Difficulty | Exit Criteria |
|---------------------|---------------|
| Required            | Can explain what TensorFlow and Keras are and how they relate. |
| Required            | Can describe a tensor by its rank, shape and dtype and explain elementwise arithmetic, broadcasting and matrix multiplication. |
| Required            | Can explain the difference between tf.constant and tf.Variable and what trainable means. |
| Required            | Can build, compile, fit, evaluate and predict with a Keras Sequential model, and explain the optimizer, loss and metrics passed to compile. |
| Required            | Can read model.summary(): the layers, their output shapes and their parameter counts. |
| Required            | Can choose the output layer's units and activation and the matching loss for binary classification, multi-class classification and regression. |
| Required            | Can save a Keras model to a .keras file, load it and confirm it gives the same predictions. |
| Required            | Can describe how a text classifier is built from TF-IDF features and a Dense network. |
| Required            | Can build a Convolutional Neural Network (CNN) for basic image classification and give a reason for each choice in the model. |
| Required            | Can describe how a neural network is built for tabular data, including missing values, encoding categories and scaling. |
| Preferred           | Can explain eager execution, what tf.function does, and what tracing and retracing mean. |
| Preferred           | Can reduce a tensor along an axis (reduce_sum, reduce_mean, argmax) and explain keepdims. |
| Preferred           | Can build a model with the Functional API and name a model shape Sequential cannot express. |
| Preferred           | Can name the common Keras layers (Dense, Conv2D, MaxPooling2D, Flatten, Dropout, BatchNormalization) and say what each takes in and returns. |
| Preferred           | Can compose a model from smaller models, and freeze a part to reuse it. |
| Preferred           | Can use TensorBoard to compare the training curves of two runs. |
| Preferred           | Can define batch, batch size and epoch and say what fit does on each batch. |
| Preferred           | Can explain what an Embedding layer learns and how it differs from TF-IDF features. |
| Stretch             | Can explain how TensorFlow 1 sessions and placeholders differ from TensorFlow 2, enough to read old code. |
| Stretch             | Can map a model written with the old TFLearn library to its Keras equivalent. |
| Stretch             | Can write a training loop by hand with tf.GradientTape and say when a team writes its own loop. |
| Stretch             | Can diagnose a common Keras error (a shape mismatch, labels in the wrong form for the loss) from its message. |

## Vector Databases (Chroma and Pinecone)

| Criteria Difficulty | Exit Criteria |
|---------------------|---------------|
| Required            | Understands process of vectorizing data |
| Required            | Understands CRUD operations with vector dbs |
| Required            | Demonstrates understanding of vector embeddings and how they represent data in a machine-readable format. |
| Required            | Demonstrates knowledge of embedding models and their role in generating vector representations for text and other data. |
| Required            | Explain the purpose of a vector index and describe how indexing improves the efficiency of vector similarity search. |
| Required            | Describe what a vector database is and explain how it stores and retrieves vector representations for search and retrieval tasks. |
| Required            | Explain the role of vector databases in AI/ML and describe where Chroma DB fits. |
| Required            | Install and configure Chroma DB in a Python environment (a Colab notebook). |
| Required            | Create and manage collections in Chroma DB. |
| Required            | Insert, update, and delete embeddings/documents in collections. |
| Required            | Execute basic similarity search queries using Chroma DB (e.g., nearest neighbor, cosine similarity). |
| Required            | Integrate Chroma DB into a simple Python application for retrieval tasks. |
| Required            | Demonstrates the ability to explain the purpose and core features of Pinecone, including its role in RAG workflows and its benefits over traditional databases. |
| Required            | Can create, manage, and query indices and namespaces using Pinecone's console and SDK. |
| Required            | Describes the concept of namespaces in Pinecone and their use in multi-tenant or segmented data architectures |
| Required            | Demonstrates basic API usage including setting API keys, managing API tokens, and understanding permissions |
| Required            | Successfully implements a semantic search using Pinecone with uploaded vector embeddings and retrieves ranked results |
| Required            | Demonstrates knowledge of data preprocessing, upserting vectors, and querying the database for semantic search, including metadata filtering |
| Required            | Can explain how semantic search differs from keyword search and when each finds the better result. |
| Required            | Can explain what named entity recognition (NER) finds and use it to build metadata for a search index. |
| Preferred           | Ability to describe the concept of vector similarity search |
| Preferred           | Ability to describe and execute vector query with semantic search |
| Preferred           | Applies sentence transformers for creating sentence-level embeddings in vector databases. |
| Preferred           | Connect Chroma DB with an external embedding model (e.g., a Hugging Face sentence-transformers model). |
| Preferred           | Apply metadata filtering in similarity searches. |
| Preferred           | Configure persistence and storage options in Chroma DB (an in-memory client and a persistent client that stores on disk). |
| Preferred           | Explains and selects appropriate distance metrics and vector similarity algorithms for specific use cases. |
| Preferred           | Can describe strategies for performance optimization, including pod types, serverless configurations, and backup/collection best practices. |
| Preferred           | Compares pod-based and serverless Pinecone deployments, evaluating them for cost, latency, and scale |
| Preferred           | Demonstrates ability to clean and normalize raw text data, including handling noisy inputs, duplicates, and formatting issues |
| Preferred           | Can embed a large set of texts in batches and explain why batches are used. |
| Stretch             | Ability to integrate Vector DB with other tools |
| Stretch             | Able to design a warehouse for documents to be vectorized and searched through |
| Stretch             | Explain how Chroma DB is deployed as a server using Docker or a cloud environment, and how a client connects to it. |
| Stretch             | Build a mini semantic search app using Chroma DB. |
| Stretch             | Demonstrates the ability to design and implement advanced metadata structures for efficient filtering and querying in Pinecone, enhancing semantic search results. |
| Stretch             | Describes a backup plan using Pinecone collections and explains versioning or rollback strategy |
