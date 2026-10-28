---
kind: official
project: P0
title: Project 0: from dataset to warehouse
status: draft
handIn: projects/P0/
checkpoints:
- w05d5 Showcase
---

Project 0 takes the dataset your pair analysed with pandas in the data analysis mini-sprint and rebuilds it the way a data team would for a client. It has three parts. Part 1 ingests the raw files: a configurable Python job validates and cleans the records, keeps the rejects, and loads the good rows into staging tables in a cloud warehouse. Part 2 models the data as a star schema in the warehouse, with one dimension that keeps history. Part 3 analyses it and tells the story: SQL and charts that answer a client's questions, and a presentation built around a business case. You work in the same pair as the sprint, with the same dataset.

## Goal

Show that you can take raw data all the way into a cloud data warehouse and turn it into findings a client can act on. The repository holds the proof for a technical reader: a configurable ingestion job with validation and rejects, a star schema, tests and warehouse SQL. The showcase is for the client: who they are, what they wanted to know, what the data says and what they should do about it.

Technologies: Python 3, pandas, Matplotlib and pytest (NumPy, Seaborn and any other Python package you find useful are allowed); SQL; Google BigQuery in the free sandbox (no credit card, a Google account is enough) with the `google-cloud-bigquery` client library; dimensional modelling with a star schema and one slowly changing dimension; an ETL job written in Python and driven by a configuration file.

## Scope

In scope: a short business case for a client of your choice; an ingestion job that reads CSV or JSON files named in a configuration file, validates and cleans them, stores the rejects and logs each load; staging tables, a star schema and one history-keeping dimension in BigQuery; analytical queries in BigQuery SQL; feature engineering, one correlation and at least three charts; a slide deck and a README that lets someone else run all of it.

Out of scope: dashboards and BI tools, orchestration tools such as Airflow, streaming, paid Google Cloud services, a web front end, and a separate MySQL or PostgreSQL stage. The raw files go straight into BigQuery staging tables.

The dataset is the one your pair used in the mini-sprint: real, non-sensitive, 100,000 rows or more. The client is yours to invent. An anime viewership dataset can become a streaming publisher planning next season's shows against a revenue target; a New York bike-share dataset can become the City of Toronto improving its own bike-share programme. The client does not need to be real; the questions do need to be ones the data can answer.

## Requirements

Part 1, ingestion.

- R-01 Open the README with the business case as a hook: who the client is, the decision they face, and three to five questions the warehouse must answer for them, in one or two paragraphs that a non-technical manager can read. Everything else in the project serves these questions.
- R-02 Drive the ingestion job from a configuration file (YAML, JSON or `.env`): the raw files, their format (CSV or JSON), the cleansing rules that have settings, and the BigQuery project and dataset. Adding another source file is a configuration change, not a code change.
- R-03 Validate every record against the expected columns and types, apply the cleansing rules listed in the README (missing values, wrong values, formats) and remove duplicates. A record that fails validation goes to a rejects table with the reason it was rejected; the job carries on with the valid records and never stops on one bad row.
- R-04 Load the valid records into staging tables in your BigQuery sandbox, one `stg_` table per source, and write a load log for every run: when it ran, rows read, rows loaded, rows rejected. Running the job twice does not duplicate rows in any table.
- R-05 Read the BigQuery credentials from an environment variable or from a file outside the repository, never from a file that is committed, and say in the README how to supply them. Any SQL that takes a value from Python uses query parameters, not string formatting, and every client or connection is closed when the job ends.
- R-06 Cover the ingestion and transform code (validation, cleansing, typing, key assignment) with pytest tests at 80 percent line coverage or more, measured with `pytest --cov`. No test connects to BigQuery.

Part 2, the warehouse.

- R-07 Design a star schema for the dataset: one fact table at a stated grain chosen for the client's questions and at least three dimension tables, drawn as a diagram saved as an image file, with a short note on why a star schema rather than a snowflake. Build the fact and dimension tables in BigQuery from the staging tables, with surrogate keys assigned in Python.
- R-08 Keep one dimension as a slowly changing dimension of type 2, with an effective-from date, an effective-to date and a current-row flag. If nothing in the dataset changes over time, introduce a second version of some dimension rows yourselves and explain in the README what changed and why.

Part 3, analysis and the story.

- R-09 Answer at least five analytical questions in BigQuery SQL, each saved as its own `.sql` file and each joining the fact table to one or more dimensions, with one query that uses the history kept by R-08. The questions from R-01 are among them. Each file opens with a comment that states the question and what the answer means for the client.
- R-10 Engineer at least two features that the raw data does not have (a rate, a bucket, a flag, a rolling figure, a derived date part) in the transform step or in the analysis, and say in the README which question each one serves.
- R-11 Find at least one correlation in the data and state it in the client's terms, with the size of the effect and a sentence on why it may not be a cause.
- R-12 Draw at least three Matplotlib charts from the results of BigQuery queries, saved as image files and titled for the client: what each chart tells them, not the column names. One of them shows the correlation from R-11.
- R-13 Make a slide deck for the showcase that opens with the hook from R-01, presents the findings question by question with the charts, and closes with what the client should do. Commit it to the project folder as a `.pptx` or `.pdf`.

## Deliverable

A folder `projects/P0/` in one partner's learner repository holding the README (the business case first, then how to install, how to supply credentials, how to run the ingestion job, the tests and the coverage report, the cleansing rules, which file meets which requirement, and a link to the other partner's repository), the configuration file with placeholders for anything private, the ingestion and transform code, the tests, the `.sql` files, the schema diagram, the charts, the slide deck, a sample load log and a sample of the rejects, and the raw data or a link to it when the file is large.

## Checkpoints

The showcase is the one checkpoint: the warehouse is loaded, the queries run and you present. Each topic of the data week adds the piece the next requirement needs, so build the project as the topics arrive instead of in the last few days. Part 1 can start on day one with the files you already have.

## Rubric

| Area | What a complete project shows |
| --- | --- |
| Business case | A manager can say who the client is, what they wanted to know, what the data told them and what they should do. |
| Ingestion | From a fresh clone, following the README, the job reads the files named in the configuration, rejects the bad records with reasons, logs the load and lands the rows in BigQuery. |
| Requirements | R-01 to R-13 are each met and easy to find. |
| Model | The grain is stated, the dimensions are justified and the type 2 dimension keeps history correctly. |
| Queries | Each query is correct, joins the fact table to its dimensions and answers a client question. |
| Analysis | The features, the correlation and the charts each change what the client would decide. |
| Tests | `pytest` passes, coverage is 80 percent or more, and no test touches BigQuery. |
| Code quality | Small modules and functions, clear names, parameterized queries, connections closed, no secrets in the repository, a readable commit history. |
| Presentation | A non-technical listener leaves knowing what the data says and what the client should do; the warehouse appears as evidence, not as the story. |

## Presentation

Fifteen minutes per pair at the showcase, to an audience of technical and non-technical managers who care about what the data says, not how it was stored. Present from the slide deck. Open with the client and the decision they face, two minutes and no code. Spend most of the time on the findings: take the client's questions one at a time, run the query live in BigQuery, read the answer in the client's terms, show the chart when its question comes up, and close with what you would tell the client to do. Keep the technical side to two or three minutes of evidence near the end: the load log, the loaded dataset and one row of the history your type 2 dimension keeps. Do not walk through the code; the README and the rubric cover it. Both partners speak. The queries are run live, not shown as screenshots.
