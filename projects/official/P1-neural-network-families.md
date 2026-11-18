---
kind: official
project: P1
title: Project 1: Neural Network Families
status: published
handIn: projects/P1/
checkpoints:
- w08d5 Showcase
---

Working on your own, pick a real dataset and take it through the whole machine learning workflow with a neural network built in TensorFlow / Keras: problem, dataset, preprocessing, model, training, evaluation, improvement, presentation. The work runs to the showcase on Friday 4 December 2026.

## Goals and objectives

Goal: show a neural network trained, measured and explained from start to finish, by you.

By the showcase you can:

- Frame a prediction problem and say who would use the model.
- Prepare data so a network can read it.
- Choose an architecture and give a reason for its layers, activations, output layer, loss and optimizer.
- Read the training and validation curves and say whether the model is overfitting.
- Evaluate with the metrics that fit the problem, and look at the examples the model gets wrong.
- Make one change, measure it, and say whether it helped.
- Say plainly what the model cannot do.

## Choose one

| Option | Model | What to report |
| --- | --- | --- |
| Tabular classification or regression (customer churn, loan default, house prices, medical risk) | A Dense network | Classification: accuracy, precision, recall, F1 and a confusion matrix. Regression: MSE and MAE, a predicted-against-actual plot and the rows with the largest errors. |
| Image classification (clothing, letters, plants, product defects) | A Dense network on flattened pixels, or a CNN built from `Conv2D`, `MaxPooling2D`, `Flatten` and `Dense` | Accuracy, a confusion matrix and a grid of misclassified images. |
| Autoencoder (image denoising, unusual transactions, sensor faults) | A Dense autoencoder | Originals beside their reconstructions, the reconstruction error, and how you chose the anomaly threshold if you use one. |
| Text classification (spam, review sentiment, news topics, support tickets) | TF-IDF features into a Dense network | Accuracy, precision, recall, F1, a confusion matrix, and examples of false positives and false negatives. |

Optional stretch for text: build the same classifier a second time with a `TextVectorization` layer and an `Embedding` layer, and compare it with the TF-IDF model. The Keras documentation covers both layers.

## Dataset

- Real or realistic, with a clear problem behind it and a target to predict. An autoencoder needs no target.
- It loads in Colab from code, with no manual upload: a Keras built-in dataset, a scikit-learn `fetch_` loader, TensorFlow Datasets, or a public CSV that pandas reads from a URL.
- Small enough that one training run finishes in a few minutes on a CPU runtime. A sample of a large dataset is fine; say how you took it.
- Not one the course notebooks have already used: no MNIST digits, no breast cancer set, no 8 by 8 digits.

## Build

One notebook that runs from top to bottom, with a markdown cell before each part saying what it does and what you found.

- Problem statement: what you predict or classify, why it matters, who would use the model.
- Dataset: the source and a link, the number of examples, what the columns or classes are, and a few sample records, images or texts.
- Preprocessing: for tabular data, missing values, encoding of categories, scaling and the split; for images, normalisation and the shape the model reads; for text, how it is vectorised and the vocabulary size.
- Model: `model.summary()`, and a reason for the kind of network, the number and type of layers, the activations, the output layer, the loss and the optimizer.
- Training: epochs, batch size, the validation split, any callback, and the training and validation curves on one chart.
- Evaluation: the metrics for your option from the table above, and an error analysis: which examples the model gets wrong and what they have in common.
- One improvement attempt: change one thing (layers or units, the learning rate, dropout, batch normalization, early stopping, the preprocessing, the threshold, or a second architecture), and show before and after on the same validation data with a sentence on why it did or did not help.
- Limitations and next steps: what the model does well, where it struggles, whether the dataset is biased or too small, and what you would do with more time or data.

## Rules

- TensorFlow / Keras, in Google Colab on a CPU runtime.
- Hold out a test set at the start and use it once, at the end. Every choice along the way is made on the validation data.
- The notebook runs with Runtime > Run all in a fresh runtime, without edits.
- Every number on a slide comes from a cell in the notebook.
- Set the random seeds so a rerun lands close to the numbers you present.
- The work is your own. Talking a problem through with someone is fine; sharing a notebook is not.

## Presentation

- When: Friday 4 December 2026, on the call.
- Length: 5 to 7 minutes each, questions included.
- Format: a slide deck, with the notebook open in another tab for questions.
- Slide flow: title, problem statement, dataset, preprocessing, model architecture, results and metrics, error analysis, improvement attempt, limitations and next steps, questions.

## Hand-in

Push to `projects/P1/` in your learner repository before the showcase: the notebook with its outputs kept, a README (the problem, a link to the dataset, how to run the notebook, a table of your results), the slide deck, and the saved `.keras` model if it is a few megabytes or less.

## What we look for

- The workflow is complete: every part of the build is in the notebook, and it reruns.
- You can explain it: each choice has a reason, and you can say what the curves and the wrong predictions tell you.
- The improvement is measured honestly, including when it did not help.
