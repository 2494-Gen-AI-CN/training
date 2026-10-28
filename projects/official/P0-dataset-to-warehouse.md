---
kind: official
project: P0
title: Project 0: Data Warehouse and Analytics for a Client
status: draft
handIn: projects/P0/
checkpoints:
- w05d5 Showcase
---

Working in the same pair and with the same dataset as the data analysis mini-sprint, rebuild that dataset the way a data team would for a client: load it into a cloud warehouse, model it, and answer the client's questions from there. Two weeks, from Monday 2 November to the showcase on Friday 13 November 2026.

## Dataset

- The dataset your pair analysed in the mini-sprint: 100,000 rows or more, real, non-sensitive.
- The client is yours to invent, with something they want to learn from the data. An anime viewership dataset can become a streaming publisher planning next season against a revenue target; a New York bike-share dataset can become the City of Toronto improving its own programme.
- The client does not need to be real. The questions do need to be ones your data can answer.

## Build

Ingest.

- A Python job, driven by a configuration file (YAML, JSON or `.env`) that names the raw files, their format (CSV or JSON) and the BigQuery project and dataset. Adding a source file is a configuration change, not a code change.
- The job validates and cleans every record with pandas: expected columns and types, the cleansing rules you list in the README, duplicates removed. A row that fails goes to a rejects table with the reason; the job carries on with the rest.
- Every run writes a load log: when it ran, rows read, rows loaded, rows rejected. Running the job twice adds nothing.

Warehouse.

- The raw files go straight into staging tables in your free BigQuery sandbox (a Google account is enough, no credit card). No MySQL or PostgreSQL stage in between.
- From staging, build a star schema: one fact table at a grain you state, three or more dimension tables, drawn as a diagram saved as an image.
- One dimension is a slowly changing dimension of type 2: effective-from, effective-to and a current-row flag. If nothing in your data changes over time, introduce a change yourselves and say in the README what changed.

Analyse and tell.

- Five or more BigQuery SQL files, each joining the fact table to its dimensions and answering one of the client's questions. One of them uses the history the type 2 dimension keeps. Each file opens with a comment: the question, and what the answer means for the client.
- Two engineered features the raw data does not have (a rate, a bucket, a flag, a rolling figure) and one correlation, stated in the client's terms with a line on why it may not be a cause.
- Three or more Matplotlib charts drawn from BigQuery results, titled for the client: what the chart tells them, not the column names.
- A slide deck that opens with the client and what they asked, answers the questions one by one with the charts, and closes with what you recommend.

## Rules

- The README opens with the business case: who the client is, what they want to know, and three to five questions, in one or two paragraphs a non-technical manager can read. Everything else serves those questions.
- BigQuery credentials come from an environment variable or a file outside the repository, never from a committed file. The README says how to supply them.
- The transform and cleansing functions have pytest tests. No test connects to BigQuery.
- The README lets someone else run all of it from a fresh clone: install, credentials, the job, the tests, the queries.

## Presentation

- When: Friday 13 November 2026, in class.
- Length: 15 minutes per pair.
- Audience: technical and non-technical managers who care about what the data says, not how it was stored.
- Format: your slide deck, with the queries run live in BigQuery, not screenshots.
- Shape: the client and what they asked first, two minutes and no code. Then the findings, one question at a time, each answer in the client's terms with its chart, and what you recommend. Two or three minutes of evidence near the end: the load log, the loaded dataset, one history row from the type 2 dimension. No code walkthrough.
- Both partners speak.

## Hand-in

Push to `projects/P0/` in one partner's learner repository before the showcase: the README, the configuration file with placeholders for anything private, the ingestion code and its tests, the `.sql` files, the schema diagram, the charts, the slide deck, a sample load log and a sample of the rejects, and a link to the dataset (not the data file itself when it is large). The README names the other partner's repository.

## What we look for

- The story lands: a non-technical listener leaves knowing what the data says and what you recommend.
- The warehouse is real: from a fresh clone, following the README, the job runs, the rows land in BigQuery and the queries answer.
- The analysis matters: the features, the correlation and the charts each tell the client something they can act on.
