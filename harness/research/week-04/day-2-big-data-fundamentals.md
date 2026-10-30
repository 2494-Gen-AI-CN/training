# w04d2 — Big data fundamentals

gate: light
verified: 2026-10-30
week: 4 · Data fundamentals, cloud concepts, data warehousing, ETL/ELT
day: 2 · big-data-fundamentals

version-stamps:
  - python: 3.15 (verified 2026-10-30)
  - apache-avro (specification): 1.12 (verified 2026-10-30; no Python import today, formats are written on the board)
  - apache-parquet (format): 2.x (verified 2026-10-30; no Python import today)
  - apache-orc (format): 2.x (verified 2026-10-30; no Python import today)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- Big data is commonly characterised by volume, velocity and variety (the three V's), extended with veracity and value to give five. — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
- Volume is the amount of data, velocity the speed at which it arrives and must be processed, and variety the mix of formats and sources. — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
- A data platform on Google Cloud is described as a lifecycle of stages: ingest, store, process and analyse, then explore and visualise, with a Google Cloud service named for each. — [Google Cloud Architecture Center: Data lifecycle on Google Cloud](https://cloud.google.com/architecture/data-lifecycle-cloud-platform)
- Batch processing handles a bounded set of data collected over a period; stream processing handles an unbounded sequence of events as they arrive. — [Apache Beam programming guide](https://beam.apache.org/documentation/programming-guide/)
- Pub/Sub is Google Cloud's messaging service for ingesting event streams: a publisher sends each message to a topic and subscribers receive it. — [Pub/Sub overview](https://cloud.google.com/pubsub/docs/overview)
- Dataflow is a managed service that runs Apache Beam pipelines for both batch and streaming data. — [Dataflow overview](https://cloud.google.com/dataflow/docs/overview)
- Cloud Storage holds objects (files) in buckets and is the usual landing place for raw files in a Google Cloud data platform. — [Cloud Storage documentation](https://cloud.google.com/storage/docs/introduction)
- BigQuery is a serverless analytics data warehouse that separates storage from compute. — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
- BigQuery stores table data in a columnar format, so a query reads only the columns it names. — [BigQuery storage overview](https://cloud.google.com/bigquery/docs/storage_overview)
- Distributed systems split data across many machines so storage and processing scale out instead of up, and tolerate one machine failing. — [Apache Hadoop: HDFS architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- Structured data fits a fixed schema of rows and columns (SQL tables); semi-structured data carries its own structure through tags or keys (JSON, XML); unstructured data has no predefined model (images, free text, audio). — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
- BigQuery can load and query JSON, and supports nested and repeated fields, so semi-structured data can be queried without flattening first. — [BigQuery: Loading JSON data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json)
- CSV is a plain-text row format with no embedded types, so a loader has to detect or be told each column's type. — [BigQuery: Loading CSV data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv)
- Parquet is a columnar file format with per-column compression and an embedded schema, suited to analytical reads. — [Apache Parquet documentation](https://parquet.apache.org/docs/)
- ORC is a columnar file format with built-in indexes and compression, from the Hadoop ecosystem. — [Apache ORC specification](https://orc.apache.org/specification/)
- Avro is a row-based format whose schema (written in JSON) travels in the file header, and it supports schema evolution. — [Apache Avro specification](https://avro.apache.org/docs/current/specification/)
- BigQuery loads CSV, JSON lines, Avro, Parquet and ORC files, and the format choice changes how the schema is obtained. — [BigQuery: Introduction to loading data](https://cloud.google.com/bigquery/docs/loading-data)
- JSON lines (newline-delimited JSON) holds one complete JSON object per line, so a file can be split and read a line at a time. — [BigQuery: Loading JSON data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json)
- Personal data such as an email address falls under privacy law; Canada's PIPEDA sets rules for collecting, using and keeping it. — [Office of the Privacy Commissioner of Canada: PIPEDA](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/)
- BigQuery dataset locations decide where data is stored, which matters for data residency. — [BigQuery locations](https://cloud.google.com/bigquery/docs/locations)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Big data fundamentals
- Interview questions: Explain the five V's of big data and how each one shapes a data warehouse design (qc3.big-data.R01); How would a high-velocity source change the design compared with a nightly file?; Which V is hardest to fix with more hardware, and why?
- Adjacent concept: What counts as "big" for a given team — the answer is "when one machine and one ordinary database stop coping", not a byte count — it frames why the V's are design pressures rather than definitions.
- Trade-off or limit: The V's describe pressures on a system rather than a size threshold: volume, velocity and variety are measured against what a team's storage and processing can handle — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
- Recognise on sight: A design doc with a "Data profile" table: rows per day, arrivals per second, number of sources, known error rate, the business question (the six-ticket desk scores low on every row, a SaaS company with ten thousand customers high on several).
- Claims:
  - Volume pushes toward storage that scales out and a low cost per byte — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
  - Velocity pushes toward a streaming path next to the batch one — [Dataflow overview](https://cloud.google.com/dataflow/docs/overview)
  - Variety pushes toward formats that carry or tolerate different shapes — [BigQuery: Introduction to loading data](https://cloud.google.com/bigquery/docs/loading-data)
  - Veracity pushes toward cleansing before analysis — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
  - Value is the reason to pay for any of it: a stated business question comes first — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)

### Components of big data
- Interview questions: Name the components of a big data system and the role of each (qc3.big-data.R02); Where would a ticket form's data enter, and where would a manager's chart read it?; What changes if ingestion is a message queue rather than a file drop?
- Adjacent concept: Orchestration (something runs the stages in order and on schedule) — interviewers ask who triggers each stage; it is named, not taught in depth.
- Trade-off or limit: Each stage maps to its own managed service (Pub/Sub, Cloud Storage, Dataflow, BigQuery, Looker Studio), which gives choice per stage and adds the work of connecting them — [Google Cloud Architecture Center: Data lifecycle on Google Cloud](https://cloud.google.com/architecture/data-lifecycle-cloud-platform)
- Recognise on sight: An architecture diagram with boxes labelled Pub/Sub, Cloud Storage, Dataflow, BigQuery and a dashboard tool, arrows left to right.
- Claims:
  - Ingestion: Pub/Sub receives events as messages on a topic; batches arrive as files — [Pub/Sub overview](https://cloud.google.com/pubsub/docs/overview)
  - Storage: Cloud Storage holds raw files as objects in buckets — [Cloud Storage documentation](https://cloud.google.com/storage/docs/introduction)
  - Processing: Dataflow runs pipelines that transform data in batch or streaming mode — [Dataflow overview](https://cloud.google.com/dataflow/docs/overview)
  - Analysis: SQL queries run over stored tables in BigQuery — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
  - Visualisation: Looker Studio reads BigQuery tables to draw charts and dashboards — [Looker Studio help](https://docs.cloud.google.com/data-studio)

### Architecture
- Interview questions: Describe a typical big data architecture with a batch path and a streaming path, and explain why storage and processing are distributed (qc3.big-data.R03); When is batch good enough?; Why can one machine not be scaled forever, and what does a distributed system split up?
- Adjacent concept: Latency versus throughput — interviewers ask which a design optimises; a nightly batch has high throughput and high latency.
- Trade-off or limit: Streaming gives fresh results at higher cost and complexity (ordering, late events, duplicates); batch is simpler and cheaper but stale until the next run — [Apache Beam programming guide](https://beam.apache.org/documentation/programming-guide/)
- Recognise on sight: Two parallel arrows from one source: "nightly extract -> files -> batch job" and "event -> topic -> streaming job".
- Claims:
  - A batch job processes a bounded input and then ends — [Apache Beam programming guide](https://beam.apache.org/documentation/programming-guide/)
  - A streaming job processes an unbounded input and keeps running — [Apache Beam programming guide](https://beam.apache.org/documentation/programming-guide/)
  - Scaling up (a bigger machine) hits a hardware ceiling; scaling out adds ordinary machines to a cluster, the model HDFS is built for — [Apache Hadoop: HDFS architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
  - Distributed storage replicates blocks across machines so a failed node loses no data — [Apache Hadoop: HDFS architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
  - Distributed processing splits a job into work that runs on many workers at once — [Dataflow overview](https://cloud.google.com/dataflow/docs/overview)

### Benefits
- Interview questions: Explain the benefits of big data for an organisation (better decisions, new products, operational efficiency) with one example of each (qc3.big-data.R04); How would you show a manager the value of a data project, for example staffing the desk by the hour tickets arrive?; What would you measure to prove it?
- Adjacent concept: Return on investment — the benefit only counts against the cost named in the next subtopic.
- Trade-off or limit: Benefits are weighed against cost: BigQuery bills the bytes stored and the bytes each query scans, so data nobody analyses still costs storage — [BigQuery pricing](https://cloud.google.com/bigquery/pricing)
- Recognise on sight: A project pitch with "Today / With data / Expected change" columns, such as staffing by the hour (a decision), a self-service ticket status page (a product) or routing tickets by tag (efficiency).
- Claims:
  - Big data supports better decisions, new products and services, and more efficient operations — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
  - Better decisions come from analysing patterns across more records than a person could read — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
  - New products and services can be built from data an organisation already collects about its customers — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
  - Operational efficiency comes from finding delays and waste in a process through its own records — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)

### Challenges
- Interview questions: Describe the challenges of big data: data quality, integration of sources, storage and processing cost, privacy and governance, and skills (qc3.big-data.R05); Why is integration of sources hard?; Which desk column is personal data and what follows from that?
- Adjacent concept: Data governance (who owns, may see and must delete data) — interviewers pair it with privacy.
- Trade-off or limit: Keeping everything "in case" raises storage cost and privacy exposure together; BigQuery bills storage and bytes scanned — [BigQuery pricing](https://cloud.google.com/bigquery/pricing)
- Recognise on sight: A column named `email` or `phone` with no note about retention or access.
- Claims:
  - Data quality: duplicates, misspellings and impossible dates arrive from real systems — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
  - Integration: sources disagree on keys, types and time zones — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)
  - Cost: storage and scanned bytes are billed — [BigQuery pricing](https://cloud.google.com/bigquery/pricing)
  - Privacy: Canadian personal-data rules apply to customer emails — [PIPEDA overview](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/)
  - Residency: a dataset's location is fixed when created — [BigQuery locations](https://cloud.google.com/bigquery/docs/locations)

### Data lifecycle stages
- Interview questions: List the eight lifecycle stages in order and say what happens to a ticket at each (qc3.big-data.R06); What happens to a ticket at the archival stage and why not delete it at once?; What triggers deletion?
- Adjacent concept: Retention policy — a rule stating how long data is kept; it decides when archival turns into deletion.
- Trade-off or limit: Different sources list different stage counts (Google's architecture guide uses four: ingest, store, process and analyse, explore and visualise); the course uses eight (generation, collection, storage, processing, analysis, sharing, archival, deletion) — [Google Cloud Architecture Center: Data lifecycle on Google Cloud](https://cloud.google.com/architecture/data-lifecycle-cloud-platform)
- Recognise on sight: A table expiration setting or a bucket lifecycle rule that deletes objects after N days; one ticket followed from the form, through the insert, the MySQL row, the extract, the report and the share with a manager, to archival and deletion.
- Claims:
  - Data is generated by applications, devices and people, then collected (ingested) into storage — [Google Cloud Architecture Center: Data lifecycle on Google Cloud](https://cloud.google.com/architecture/data-lifecycle-cloud-platform)
  - A relational database stores collected records as rows in tables — [MySQL reference manual](https://dev.mysql.com/doc/refman/9.0/en/)
  - Archival can move cold data to cheaper storage classes — [Cloud Storage: Storage classes](https://cloud.google.com/storage/docs/storage-classes)
  - Deletion can be automatic through bucket lifecycle rules — [Cloud Storage: Object Lifecycle Management](https://cloud.google.com/storage/docs/lifecycle)
  - BigQuery tables can carry an expiration time — [BigQuery: Managing tables](https://cloud.google.com/bigquery/docs/managing-tables)

### Types of data: structured, semi-structured, unstructured
- Interview questions: Distinguish structured, semi-structured and unstructured data, give an example of each and say how each is stored and queried (qc3.big-data.R07); Is JSON structured?; Where would a screenshot attached to a ticket be stored?
- Adjacent concept: Nested and repeated fields (a JSON array or object inside one row) — interviewers ask how a loader flattens such a field into extra rows or keeps it as a nested column; it is the first question once JSON meets a table.
- Trade-off or limit: Semi-structured data is flexible to write and costly to query reliably because fields may be missing or change type — [BigQuery: Loading JSON data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json)
- Recognise on sight: `{"id": 4, "tags": ["billing"], "note": null}` next to a sibling object with no `tags` key.
- Claims:
  - Structured: rows and columns under a fixed schema, queried with SQL — [MySQL reference manual](https://dev.mysql.com/doc/refman/9.0/en/)
  - Semi-structured: JSON and XML carry their own keys or tags — [BigQuery: Loading JSON data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json)
  - Nested and repeated JSON fields load as RECORD and REPEATED columns rather than being flattened — [BigQuery: Loading JSON data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json)
  - Unstructured: images and email bodies are stored as objects — [Cloud Storage documentation](https://cloud.google.com/storage/docs/introduction)
  - Unstructured data is queried by first extracting structure or metadata from it — [Google Cloud: What is big data?](https://cloud.google.com/learn/what-is-big-data)

### File types
- Interview questions: Compare CSV, JSON, XML, Parquet, Avro and ORC by structure, schema handling, compression and typical use, and choose a format for a given workload (qc3.big-data.R08); Which format would you choose for a nightly analytical extract, and why?; What does columnar mean and when does it hurt?
- Adjacent concept: Splittable files and compression codecs — interviewers ask why analytics prefers columnar; it is named here as a reason, not taught.
- Trade-off or limit: Columnar files read fast for a few columns and are slower to write and awkward to append row by row; row formats suit streaming writes — [Apache Parquet documentation](https://parquet.apache.org/docs/)
- Recognise on sight: A file extension (`.csv`, `.jsonl`, `.xml`, `.parquet`, `.avro`, `.orc`) in a load command or a bucket listing.
- Claims:
  - CSV: row text, no types, human readable, large — [BigQuery: Loading CSV data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv)
  - JSON lines: one object per line, nested fields allowed — [BigQuery: Loading JSON data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json)
  - Parquet: columnar, typed, compressed per column — [Apache Parquet documentation](https://parquet.apache.org/docs/)
  - ORC: columnar with indexes, strong in Hive — [Apache ORC specification](https://orc.apache.org/specification/)
  - Avro: row-based with the schema in the header, favoured for streams — [Apache Avro specification](https://avro.apache.org/docs/current/specification/)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Google Cloud: What is big data? — https://cloud.google.com/learn/what-is-big-data
- Google Cloud Architecture Center: Data lifecycle on Google Cloud — https://cloud.google.com/architecture/data-lifecycle-cloud-platform
- BigQuery overview — https://cloud.google.com/bigquery/docs/introduction
- BigQuery storage overview — https://cloud.google.com/bigquery/docs/storage_overview
- BigQuery: Introduction to loading data — https://cloud.google.com/bigquery/docs/loading-data
- BigQuery: Loading CSV data — https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv
- BigQuery: Loading JSON data — https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json
- BigQuery: Managing tables — https://cloud.google.com/bigquery/docs/managing-tables
- BigQuery locations — https://cloud.google.com/bigquery/docs/locations
- BigQuery pricing — https://cloud.google.com/bigquery/pricing
- Pub/Sub overview — https://cloud.google.com/pubsub/docs/overview
- Dataflow overview — https://cloud.google.com/dataflow/docs/overview
- Cloud Storage documentation — https://cloud.google.com/storage/docs/introduction
- Cloud Storage: Storage classes — https://cloud.google.com/storage/docs/storage-classes
- Cloud Storage: Object Lifecycle Management — https://cloud.google.com/storage/docs/lifecycle
- Looker Studio help — https://docs.cloud.google.com/data-studio
- Apache Beam programming guide — https://beam.apache.org/documentation/programming-guide/
- Apache Hadoop: HDFS architecture — https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html
- Apache Parquet documentation — https://parquet.apache.org/docs/
- Apache ORC specification — https://orc.apache.org/specification/
- Apache Avro specification — https://avro.apache.org/docs/current/specification/
- MySQL reference manual — https://dev.mysql.com/doc/refman/9.0/en/
- PIPEDA overview (Office of the Privacy Commissioner of Canada) — https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- big data | Data whose volume, velocity or variety is too great for one machine and an ordinary database to store and process well. | aka: big-data, five V's
- batch processing | Processing a bounded set of data collected over a period in one scheduled run that then ends. | aka: batch job, batch jobs
- stream processing | Processing an unbounded flow of events continuously as each one arrives. | aka: streaming pipeline, streaming pipelines
- distributed storage | Keeping data split and copied across many machines so capacity grows by adding machines and one failure loses nothing. | aka: distributed file system
- semi-structured data | Data that carries its own structure through keys or tags, such as JSON or XML, without a fixed table schema. | aka: semi structured, semistructured
- columnar format | A file or table layout that stores each column's values together so a query reads only the columns it needs. | aka: column-oriented, columnar file
- data lifecycle | The stages data passes through from generation to deletion: collection, storage, processing, analysis, sharing and archival between. | aka: data life cycle, lifecycle stages
- JSON lines | A text file holding one complete JSON object per line. | aka: newline-delimited JSON, NDJSON, JSONL

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Treating "big data" as a size threshold, then calling the six-ticket desk big; the V's are pressures, and the desk shows none.
- Calling JSON structured because it looks tidy; it is semi-structured, since each object may carry different keys.
- Mixing up JSON (one document, usually one array) with JSON lines (one object per line); only the latter can be read a line at a time.
- Assuming columnar means better for everything; row writes, single-row lookups and streaming appends favour row formats such as Avro or the MySQL table itself.
- Confusing batch with "slow" and streaming with "better"; the choice follows how fresh the answer must be and what it costs.
- Listing lifecycle stages from memory in the wrong order, or skipping sharing and archival; deletion comes last and follows a retention period.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Draw the batch path (nightly extract of `ticket_events`) and the streaming path (each event published as it happens) side by side on the board, with a GCP service named at each stage.
- Write the same six tickets on the board as CSV, JSON, JSON lines and XML, then point at where each format states types and where it does not.
- Follow one ticket through all eight lifecycle stages on the board, naming what the desk stores at each.
- Pairs choose a format for four workloads, one being Wednesday's extract, and defend the choice by structure, schema, compression and use.
