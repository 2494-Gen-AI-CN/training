---
kind: official
project: P0
title: Project 0: from dataset to warehouse
status: draft
handIn: projects/P0/
checkpoints:
- w05d5 Showcase
---

Project 0 takes the dataset your pair analysed with pandas in the data analysis mini-sprint and rebuilds it the way a data team would for a client: a client with a decision to make, a dimensional model, an ETL job that loads the data into a cloud warehouse, and SQL that answers the client's questions from BigQuery. You work in the same pair as the sprint, with the same dataset.

## Goal

Show that you can take raw data all the way into a cloud data warehouse and answer business questions from it. At the showcase, a technical manager sees a star schema, an ETL job, tests and warehouse SQL; a non-technical manager hears who the client is, what they wanted to know and what the data says.

Technologies: Python 3, pandas, Matplotlib and pytest; SQL; Google BigQuery in the free sandbox (no credit card, a Google account is enough) with the `google-cloud-bigquery` client library; dimensional modelling with a star schema and one slowly changing dimension; an ETL job written in Python.

## Scope

In scope: a short business case for a client of your choice; a star schema for your dataset; cleansing and loading the data into BigQuery with Python; one dimension that keeps history; analytical queries in BigQuery SQL; one chart; a README that lets someone else run all of it.

Out of scope: dashboards and BI tools, orchestration tools such as Airflow, streaming, paid Google Cloud services, a web front end, and a MySQL stage. The raw files go straight into BigQuery.

The dataset is the one your pair used in the mini-sprint. The client is yours to invent. An anime viewership dataset can become a streaming publisher planning next season's shows against a revenue target; a New York bike-share dataset can become the City of Toronto improving its own bike-share programme. The client does not need to be real; the questions do need to be ones the data can answer.

## Requirements

- R-01 Open the README with the business case: who the client is, the decision they face, and three to five questions the warehouse must answer for them, in one or two paragraphs that a non-technical manager can read.
- R-02 Design a star schema for the dataset: one fact table at a stated grain chosen for the client's questions and at least three dimension tables, drawn as a diagram saved as an image file, with a short note on why a star schema rather than a snowflake.
- R-03 Write an ETL job in Python that extracts the raw files, transforms them with pandas (data types, the cleansing rules listed in the README, surrogate keys) and loads the fact and dimension tables into a BigQuery dataset in your sandbox project. Running the job twice does not duplicate rows.
- R-04 Cover the transform functions (cleansing, typing, key assignment) with pytest tests. No test connects to BigQuery.
- R-05 Keep one dimension as a slowly changing dimension of type 2, with an effective-from date, an effective-to date and a current-row flag. If nothing in the dataset changes over time, introduce a second version of some dimension rows yourselves and explain in the README what changed and why.
- R-06 Answer at least five analytical questions in BigQuery SQL, each saved as its own `.sql` file and each joining the fact table to one or more dimensions, with one query that uses the history kept by R-05. The questions from R-01 are among them. Each file opens with a comment that states the question and what the answer means for the client.
- R-07 Draw one Matplotlib chart from the results of a BigQuery query and save it as an image file, titled for the client: what the chart tells them, not the column names.
- R-08 Read the BigQuery credentials from an environment variable or from a file outside the repository, never from a file that is committed, and say in the README how to supply them.

## Deliverable

A folder `projects/P0/` in one partner's learner repository holding the README (the business case first, then how to install, how to supply credentials, how to run the ETL job and the tests, which file meets which requirement, and a link to the other partner's repository), the ETL code, the tests, the `.sql` files, the schema diagram, the chart, and the raw data or a link to it when the file is large.

## Checkpoints

The showcase is the one checkpoint: the warehouse is loaded, the queries run and you present. Each topic of the data week adds the piece the next requirement needs, so build the project as the topics arrive instead of in the last few days.

## Rubric

| Area | What a complete project shows |
| --- | --- |
| Business case | A manager can say who the client is, what they wanted to know and what the data told them. |
| Working ETL | From a fresh clone, following the README, the job runs and the rows land in BigQuery. |
| Requirements | R-01 to R-08 are each met and easy to find. |
| Model | The grain is stated, the dimensions are justified and the type 2 dimension keeps history correctly. |
| Queries | Each query is correct, joins the fact table to its dimensions and answers a client question. |
| Tests | `pytest` passes and covers the transform functions. |
| Code quality | Small functions, clear names, no secrets in the repository. |
| Presentation | Both the technical and the non-technical listeners could follow it. |

## Presentation

Fifteen minutes per pair at the showcase, to an audience of technical and non-technical managers. Open with the client and their decision, two minutes and no code. Then show the BigQuery dataset live, run one query and state its answer in the client's terms, show the chart, walk through the ETL code, show the history rows of the type 2 dimension, and take questions. Both partners speak. Everything is run live, not shown as screenshots.
