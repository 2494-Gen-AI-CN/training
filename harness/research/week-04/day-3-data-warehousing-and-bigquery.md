# w04d3 — Data warehousing & BigQuery

gate: light
verified: 2026-10-30
week: 4 · Data fundamentals, cloud concepts, data warehousing, ETL/ELT
day: 3 · data-warehousing-and-bigquery

version-stamps:
  - python: 3.15 (verified 2026-10-30)
  - bigquery-googlesql: current GoogleSQL dialect, no version number (verified 2026-10-30; never legacy SQL)
  - google-cloud-sdk (bq, gcloud): current release installed at home on W3D5 weekend (verified 2026-10-30; the day touches `bq` only and never imports a Google package; the w04d4 brief pins google-cloud-bigquery and its cp315 wheels, D-0058)
  - mysql: 9.7 (verified 2026-10-30; the desk's source, as in week 3)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- OLTP systems run many short read and write transactions on current data; OLAP systems run fewer, larger read-mostly queries that scan and aggregate history — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
- A data warehouse is a subject-oriented, integrated store of historical data built for analysis, fed from operational sources — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
- A data lake keeps raw data in its original format and applies a schema when the data is read; a warehouse applies a schema when the data is loaded — [Data lake vs data warehouse](https://cloud.google.com/discover/data-lake-vs-data-warehouse)
- BigQuery separates storage from compute, so each scales on its own and a query's cost does not depend on the size of a cluster the learner manages — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
- BigQuery stores table data in a columnar format (Capacitor), so a query reads only the columns it names — [Storage overview](https://cloud.google.com/bigquery/docs/storage_overview)
- A slot is BigQuery's unit of computational capacity for running a query; the service schedules the stages of a query over slots — [Slots](https://cloud.google.com/bigquery/docs/slots)
- A dataset is the top-level container that groups tables and views inside a project and carries a location and a default table expiration — [Introduction to datasets](https://cloud.google.com/bigquery/docs/datasets-intro)
- A dataset's location is fixed at creation and cannot be changed afterwards; a query can only join tables whose datasets share a location — [Dataset locations](https://cloud.google.com/bigquery/docs/locations)
- `northamerica-northeast2` is the Toronto region — [BigQuery locations](https://cloud.google.com/bigquery/docs/locations)
- A table's default expiration comes from its dataset unless the table sets its own; the sandbox applies 60 days — [Create datasets](https://cloud.google.com/bigquery/docs/datasets)
- The BigQuery sandbox needs no billing account and gives 10 GB of storage and 1 TB of query processing a month, with a 60-day default table expiration; it does not support DML, streaming inserts or the Data Transfer Service — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
- `bq load` loads a file into a table; `--replace` overwrites the table, `--source_format` names CSV or NEWLINE_DELIMITED_JSON, `--skip_leading_rows` skips a CSV header, and a schema is given inline or as a JSON file — [Loading CSV data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv)
- A load job into a table using `--autodetect` guesses types from a sample of the file and can guess wrongly; a custom schema fixes the types — [Specifying a schema](https://cloud.google.com/bigquery/docs/schemas)
- `bq mk --dataset --location=... --default_table_expiration=<seconds>` creates a dataset; `bq ls`, `bq show --schema` and `bq head -n` inspect it — [bq command-line tool reference](https://cloud.google.com/bigquery/docs/reference/bq-cli-reference)
- Dataset and table access is set with IAM roles such as BigQuery Data Viewer, Data Editor and Data Owner; a BigQuery Data Viewer grant made in the console prints as `READER` (userByEmail) in the `access` list of `bq show --format=prettyjson <dataset>` — [Control access to resources with IAM](https://cloud.google.com/bigquery/docs/control-access-to-resources-iam)
- `QUALIFY` filters on the result of a window function without a subquery; `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` numbers rows within a group — [Query syntax: QUALIFY clause](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#qualify_clause)
- BigQuery supports `WITH RECURSIVE`, which needs an anchor term, `UNION ALL` and a recursive term — [Query syntax: WITH clause](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#with_clause)
- BigQuery encourages denormalised tables with nested (STRUCT) and repeated (ARRAY) columns because they avoid joins at scale — [Nested and repeated fields](https://cloud.google.com/bigquery/docs/best-practices-performance-nested)
- A query dry run reports the bytes it would process without running it, and on-demand pricing bills by bytes processed — [Estimate and control costs](https://cloud.google.com/bigquery/docs/best-practices-costs)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Data warehousing introduction
- Interview questions: What is a data warehouse and why not report straight from the production database? (qc3.data-warehousing.R01); What does "subject-oriented, integrated, time-variant, non-volatile" mean?; Why can a warehouse answer a question that would slow the production system down?
- Adjacent concept: Business intelligence reporting — a dashboard or report is the consumer a warehouse exists to serve.
- Trade-off or limit: a warehouse holds a copy that is only as fresh as its last load, so it is wrong for "what is this ticket's status right now" — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
- Recognise on sight: a nightly job that copies tables into a separate database and a report that reads the copy, never production.
- Claims:
  - A warehouse integrates data from several operational systems into one consistent model — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
  - Warehouse data is mostly appended, not updated in place, so history is kept — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
  - Analytical queries on the transactional database compete with the writes it exists to serve — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)

### Data store vendors
- Interview questions: Name three cloud data warehouses and two on-premises ones; How do cloud and on-premises warehouses compare on scalability, cost and maintenance? (qc3.data-warehousing.P03); What does "serverless" mean for a warehouse?
- Adjacent concept: Managed service versus self-hosted — it decides who patches, scales and backs up the system.
- Trade-off or limit: on-premises means capital cost, fixed capacity and your own maintenance; cloud means pay-per-use, elastic capacity, vendor management and egress and lock-in concerns — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
- Recognise on sight: a connection string host such as `<project>.bigquery`, `*.snowflakecomputing.com`, `*.redshift.amazonaws.com` or `*.sql.azuresynapse.net`; Teradata is another long-standing on-premises warehouse vendor named in the facilitation wording, with no claim resting on it.
- Claims:
  - Cloud data warehouses scale storage and compute on demand and are billed by use with the provider maintaining the system; on-premises warehouses need hardware bought up front, sized for peak load and maintained by the owner — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
  - Cloud warehouses: Snowflake is a cloud data platform delivered as a managed service — [Snowflake key concepts and architecture](https://docs.snowflake.com/en/user-guide/intro-key-concepts); Databricks offers data warehousing on a lakehouse — [What is Databricks](https://docs.databricks.com/aws/en/introduction/); Amazon Redshift is AWS's managed cloud data warehouse — [Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html); Azure Synapse Analytics includes a dedicated SQL pool warehouse — [Azure Synapse Analytics](https://learn.microsoft.com/en-us/azure/synapse-analytics/overview-what-is)
  - On-premises products: Oracle Database is run as a self-managed data warehouse, with its own data warehousing guide — [Oracle Database Data Warehousing Guide 19c](https://docs.oracle.com/en/database/oracle/oracle-database/19/dwhsg/); SQL Server installs on the owner's own Windows or Linux machines (the "boxed product") — [What is SQL Server](https://learn.microsoft.com/en-us/sql/sql-server/what-is-sql-server)
  - BigQuery is serverless: no cluster to size, provision or patch — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)

### OLTP versus OLAP
- Interview questions: Compare OLTP and OLAP by workload, query shape, schema, users and freshness (qc3.data-warehousing.R01); Which one is the desk's MySQL and which is BigQuery?; Why is normalisation good for OLTP and awkward for OLAP?
- Adjacent concept: Row versus column storage — row stores favour single-record work, column stores favour scans over a few columns.
- Trade-off or limit: one system cannot be tuned for both workloads at once, which is why teams copy data to a second store — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
- Recognise on sight: `WHERE ticket_id = 4` (OLTP) next to `GROUP BY priority` over a quarter of rows (OLAP).
- Claims:
  - OLTP: many small transactions, current data, normalised schema, many concurrent application users — [OLTP vs OLAP (AWS)](https://aws.amazon.com/compare/the-difference-between-olap-and-oltp/)
  - OLAP: few large read queries, historical data, denormalised schema, analysts and BI tools — [OLTP vs OLAP (AWS)](https://aws.amazon.com/compare/the-difference-between-olap-and-oltp/)
  - BigQuery is an OLAP system and is not built for high-rate single-row updates — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)

### Data warehouse architecture
- Interview questions: Draw the layers from source to consumer (qc3.data-warehousing.R03); What does the staging layer do?; Where does the extract land, and what moves data from staging into the warehouse?
- Adjacent concept: Metadata and a data catalogue — they describe what each table means so consumers can find it.
- Trade-off or limit: each added layer adds latency and something to maintain, so small teams collapse staging, warehouse and marts into datasets in one system — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
- Recognise on sight: datasets named `raw`, `staging`, `dw`, `mart_*` in one project.
- Claims:
  - Typical flow: sources, extract, staging, warehouse, data marts, consumers (BI, reports, ML) — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
  - Staging holds data as extracted, before cleansing and conforming — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)
  - Datasets are the unit that groups and secures tables inside BigQuery — [Introduction to datasets](https://cloud.google.com/bigquery/docs/datasets-intro)

### Data warehouse versus data lake
- Interview questions: How does a lake differ from a warehouse? (qc3.data-warehousing.R02); What is schema-on-read versus schema-on-write?; What is a data swamp?
- Adjacent concept: Lakehouse — table formats on lake storage that add warehouse features; name it, do not teach it.
- Trade-off or limit: a lake is cheap and flexible but without governance becomes unusable; a warehouse is reliable and fast but needs modelling before load — [Data lake vs data warehouse](https://cloud.google.com/discover/data-lake-vs-data-warehouse)
- Recognise on sight: a bucket full of CSV, JSON and Parquet files with no table definitions (lake) versus typed tables (warehouse).
- Claims:
  - A lake stores structured, semi-structured and unstructured data as files, schema applied on read — [Data lake vs data warehouse](https://cloud.google.com/discover/data-lake-vs-data-warehouse)
  - A warehouse stores structured, modelled data, schema applied on write — [Data lake vs data warehouse](https://cloud.google.com/discover/data-lake-vs-data-warehouse)
  - The raw staging dataset plays a small lake's role beside the modelled warehouse dataset — [Introduction to datasets](https://cloud.google.com/bigquery/docs/datasets-intro)

### Operational data store
- Interview questions: What is an ODS and how does it differ from a warehouse? (qc3.data-warehousing.R03); Why would reports read an ODS rather than production?; Does an ODS keep history?
- Adjacent concept: Replication — an ODS is often fed by change replication from the source.
- Trade-off or limit: an ODS is fresh but short-lived in what it keeps, so it serves today's reports while trend questions go to the warehouse and its marts (the ODS side is the brief author's summary; the AWS page supports only the data-mart side) — [What is a data mart (AWS)](https://aws.amazon.com/what-is/data-mart/)
- Recognise on sight: a read replica or integrated schema refreshed every few minutes that reports query.
- Claims (the ODS definition is the brief author's summary; the AWS page is cited only for the data-mart contrast):
  - An operational data store sits between the sources and the warehouse, holding current, frequently refreshed data for short-lived reporting (author's summary); by contrast a data mart is a subject-focused subset of data serving one team — [What is a data mart (AWS)](https://aws.amazon.com/what-is/data-mart/)
  - Contrast: the warehouse and its marts hold the integrated data used for analysis over time — [What is a data mart (AWS)](https://aws.amazon.com/what-is/data-mart/)

### Data mart
- Interview questions: What is a data mart and how does it relate to the warehouse? (qc3.data-warehousing.R04); When is a dependent mart right and when an independent one?; Why give the support managers a mart?
- Adjacent concept: Access control — marts are also a way to share a subset of data with one team.
- Trade-off or limit: dependent marts keep numbers consistent but wait on the warehouse; independent marts are quick to set up but harder to manage and drift into separate definitions of the same metric — [What is a data mart (AWS)](https://aws.amazon.com/what-is/data-mart/)
- Recognise on sight: a `mart_support` dataset of views or tables built from the warehouse dataset.
- Claims:
  - A data mart is a subject-focused subset of data for one business unit, narrower than the enterprise-wide warehouse — [What is a data mart (AWS)](https://aws.amazon.com/what-is/data-mart/)
  - A dependent mart is filled from a subset of the central warehouse (and fails if it fails); an independent mart reads its own sources with no warehouse; a hybrid mart reads both — [What is a data mart (AWS)](https://aws.amazon.com/what-is/data-mart/)
  - A BigQuery dataset can be shared read-only so one team sees only its mart — [Control access to resources with IAM](https://cloud.google.com/bigquery/docs/control-access-to-resources-iam)

### Data cleansing
- Interview questions: Name the common data quality problems and the fix for each (qc3.data-warehousing.R05); Where in the pipeline do you cleanse?; Who decides what a valid row is?
- Adjacent concept: Data profiling — counting nulls, distinct values and ranges per column before deciding what a valid row is.
- Trade-off or limit: cleansing silently can hide a source bug; dropping rows without a record loses evidence — [Data pipeline quality (Dataplex data quality)](https://cloud.google.com/dataplex/docs/data-quality-overview)
- Recognise on sight: finding queries, not fixes: `QUALIFY ROW_NUMBER() OVER (PARTITION BY ticket_id, kind, created_at ORDER BY event_id) > 1` lists the extra copies, `WHERE kind NOT IN ('open', 'assigned', 'closed')` lists invalid kinds, and a JOIN with `e.created_at < t.opened_at` lists inconsistent timestamps; removing them is named as a fix in prose only, with no SQL shown.
- Claims:
  - Common problems: missing values, duplicates, invalid values, inconsistent formats, inconsistent timestamps — [Dataplex data quality overview](https://cloud.google.com/dataplex/docs/data-quality-overview)
  - Fixes: fill or reject nulls, deduplicate on a business key, validate against allowed values, standardise formats — [Dataplex data quality overview](https://cloud.google.com/dataplex/docs/data-quality-overview)
  - Cleansing happens after extract and before load into the modelled layer — [What is a data warehouse](https://cloud.google.com/learn/what-is-a-data-warehouse)

### BigQuery
- Interview questions: How is BigQuery architected? (qc3.bigquery.R01); What is a slot?; Why is storage separate from compute?; How is a query billed?
- Adjacent concept: Query cost control — dry runs and the bytes estimate.
- Trade-off or limit: on-demand queries bill by bytes read, so `SELECT *` over a wide table costs more than naming columns — [Estimate and control costs](https://cloud.google.com/bigquery/docs/best-practices-costs)
- Recognise on sight: the console's "This query will process X MB" estimate beside the Run button.
- Claims:
  - Storage and compute scale independently — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
  - Dremel executes a query as a tree of stages over slots, reading columnar storage — [Slots](https://cloud.google.com/bigquery/docs/slots)
  - The sandbox caps are 10 GB storage, 1 TB queries per month, 60-day expiration — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)

### Creating datasets
- Interview questions: How do you create a dataset and what must you choose? (qc3.bigquery.R02); Which jobs do you do in the console and which with `bq`, and what are the `bq` equivalents of Create dataset, Upload and Share? (qc3.bigquery.R09); Can you change a location later?; What does default table expiration do?
- Adjacent concept: Project, dataset, table naming `project.dataset.table`.
- Trade-off or limit: location is permanent and cross-location joins fail, so name it once and keep it — [Dataset locations](https://cloud.google.com/bigquery/docs/locations)
- Recognise on sight: `bq mk --dataset --location=northamerica-northeast2 --default_table_expiration=2592000 desk_raw`.
- Claims:
  - A dataset's default expiration is in seconds on the CLI and applies to new tables — [Create datasets](https://cloud.google.com/bigquery/docs/datasets)
  - A table's own expiration overrides the dataset default — [Create datasets](https://cloud.google.com/bigquery/docs/datasets)
  - IAM can be set on a dataset or on a single table — [Control access to resources with IAM](https://cloud.google.com/bigquery/docs/control-access-to-resources-iam)
  - The console and `bq` do the same jobs: Create dataset is `bq mk --dataset`, Upload is `bq load`, the Schema tab is `bq show --schema`, Preview is `bq head`; a share is made in the console and read back with `bq show --format=prettyjson` (its `access` list) — [bq command-line tool reference](https://cloud.google.com/bigquery/docs/reference/bq-cli-reference)

### Create and use tables
- Interview questions: Load a CSV three ways (UI, `bq load`, load job) and say when each fits (qc3.bigquery.R05); Why a custom schema over autodetect? (qc3.bigquery.R05); How do you add a column or change a type? (qc3.bigquery.R04); How do you create a table with a schema, read its structure, and grant a role on the dataset or a single table? (qc3.bigquery.R03)
- Adjacent concept: Load versus insert — loads are batch jobs and are free of the streaming and DML limits in the sandbox.
- Trade-off or limit: autodetect can read `49.00` as FLOAT instead of NUMERIC; only a schema file or inline schema fixes the type — [Specifying a schema](https://cloud.google.com/bigquery/docs/schemas)
- Recognise on sight: `bq load --replace --source_format=CSV --skip_leading_rows=1 desk_raw.t file.csv col:TYPE,...` and `bq show --schema`.
- Claims:
  - Types: INT64, STRING, NUMERIC, DATETIME, TIMESTAMP, with the MySQL counterparts INT, VARCHAR, DECIMAL, DATETIME, TIMESTAMP — [Data types](https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types)
  - `INTEGER` (like `INT`, `SMALLINT`, `BIGINT`, `TINYINT` and `BYTEINT`) is an alias of `INT64`, so a schema file may write `INTEGER` — [Data types](https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types)
  - Adding columns and relaxing a mode are allowed; most other type changes need a copy or `ALTER COLUMN ... SET DATA TYPE` for permitted widenings — [Modifying table schemas](https://cloud.google.com/bigquery/docs/managing-table-schemas)
  - Table expiration is changed with `ALTER TABLE ... SET OPTIONS (expiration_timestamp = ...)` — [Managing tables](https://cloud.google.com/bigquery/docs/managing-tables)
  - A JSON schema file for `bq load` is a list of objects with name, type and mode — [Specifying a schema](https://cloud.google.com/bigquery/docs/schemas)

### BigQuery queries
- Interview questions: Write a query that counts tickets per status (qc3.bigquery.R07); What does the console estimate mean?; How do you run a query from the CLI?
- Adjacent concept: Query cache — an identical query within a day reads cached results at no cost.
- Trade-off or limit: GoogleSQL is not MySQL; `DATETIME` and `TIMESTAMP` differ, and identifiers are case-sensitive for tables — [Query syntax](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- Recognise on sight: `bq query --use_legacy_sql=false "SELECT ..."`.
- Claims:
  - GoogleSQL is the default standard dialect; legacy SQL is avoided — [Query syntax](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
  - `LIMIT` does not reduce the bytes a query reads or bills — [Estimate and control costs](https://cloud.google.com/bigquery/docs/best-practices-costs)
  - Results can be saved to a table, CSV, JSON or Sheets from the console — [Export query results](https://cloud.google.com/bigquery/docs/export-file)

### Advanced queries
- Interview questions: What is a window function and how does it differ from GROUP BY? (qc3.bigquery.S01); Write a CTE; What is a recursive CTE for?; How do you find the duplicate copies?
- Adjacent concept: `ARRAY_AGG(STRUCT(...))` — builds nested rows and leads into denormalisation.
- Trade-off or limit: recursion in BigQuery has an iteration limit and is rarely the right tool for large hierarchies — [Query syntax: WITH clause](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#with_clause)
- Recognise on sight: `QUALIFY ROW_NUMBER() OVER (PARTITION BY ticket_id, kind, created_at ORDER BY event_id) > 1` (the second and later copies of a row).
- Claims:
  - `LAG(x) OVER (PARTITION BY k ORDER BY t)` reads the previous row's value in each group — [Navigation functions](https://cloud.google.com/bigquery/docs/reference/standard-sql/navigation_functions)
  - `DATETIME_DIFF(a, b, HOUR)` returns the number of whole HOUR part boundaries crossed between two DATETIMEs — [Datetime functions](https://cloud.google.com/bigquery/docs/reference/standard-sql/datetime_functions)
  - A non-recursive `WITH` names a subquery for the statement; `WITH RECURSIVE` repeats until no rows are added — [Query syntax: WITH clause](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#with_clause)

### Denormalization
- Interview questions: What is denormalisation and why do analytical stores do it? (qc3.data-warehousing.P07); What is the trade-off in storage, query speed and update cost?; What are nested and repeated fields?
- Adjacent concept: Materialised views — a stored, refreshed query result is another way to pay storage for read speed; name it only.
- Trade-off or limit: copies of a value take more storage and a change must be made in every copy, but queries avoid joins — [Nested and repeated fields](https://cloud.google.com/bigquery/docs/best-practices-performance-nested)
- Recognise on sight: one wide `board` query joining ticket, customer and agent into a single row, or a STRUCT column holding an address.
- Claims:
  - Denormalising trades storage and update cost for fewer joins and faster scans — [Nested and repeated fields](https://cloud.google.com/bigquery/docs/best-practices-performance-nested)
  - A STRUCT groups named fields in a column; an ARRAY repeats a value, and together they model one-to-many without a join — [Nested and repeated fields](https://cloud.google.com/bigquery/docs/best-practices-performance-nested)
  - Normalisation suits OLTP because each fact is stored once, so an update touches one place — [OLTP vs OLAP (AWS)](https://aws.amazon.com/compare/the-difference-between-olap-and-oltp/)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- BigQuery overview — https://cloud.google.com/bigquery/docs/introduction
- Introduction to datasets — https://cloud.google.com/bigquery/docs/datasets-intro
- Create datasets — https://cloud.google.com/bigquery/docs/datasets
- Dataset locations — https://cloud.google.com/bigquery/docs/locations
- BigQuery sandbox — https://cloud.google.com/bigquery/docs/sandbox
- Specifying a schema — https://cloud.google.com/bigquery/docs/schemas
- Modifying table schemas — https://cloud.google.com/bigquery/docs/managing-table-schemas
- Loading CSV data — https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv
- bq command-line tool reference — https://cloud.google.com/bigquery/docs/reference/bq-cli-reference
- Control access to resources with IAM — https://cloud.google.com/bigquery/docs/control-access-to-resources-iam
- Query syntax (GoogleSQL) — https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
- Slots — https://cloud.google.com/bigquery/docs/slots
- Nested and repeated fields — https://cloud.google.com/bigquery/docs/best-practices-performance-nested
- Estimate and control costs — https://cloud.google.com/bigquery/docs/best-practices-costs
- What is a data warehouse — https://cloud.google.com/learn/what-is-a-data-warehouse
- Data lake vs data warehouse — https://cloud.google.com/discover/data-lake-vs-data-warehouse
- Dataplex data quality overview — https://cloud.google.com/dataplex/docs/data-quality-overview
- OLTP vs OLAP (AWS) — https://aws.amazon.com/compare/the-difference-between-olap-and-oltp/
- Amazon Redshift — https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html
- Azure Synapse Analytics — https://learn.microsoft.com/en-us/azure/synapse-analytics/overview-what-is
- Snowflake key concepts and architecture — https://docs.snowflake.com/en/user-guide/intro-key-concepts
- What is Databricks — https://docs.databricks.com/aws/en/introduction/
- Oracle Database Data Warehousing Guide 19c — https://docs.oracle.com/en/database/oracle/oracle-database/19/dwhsg/
- What is SQL Server — https://learn.microsoft.com/en-us/sql/sql-server/what-is-sql-server
- What is a data mart (AWS) — https://aws.amazon.com/what-is/data-mart/

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- schema-on-write | Checking and typing data against a fixed table schema at the moment it is loaded, as a warehouse does, instead of when it is read. | aka: schema on write
- data mart | A subject-focused slice of warehouse data built for one team, such as support managers. | aka: data marts, dependent data mart, independent data mart
- operational data store | A short-history, frequently refreshed copy that integrates current data from operational systems for day-to-day reports. | aka: ODS
- denormalization | Deliberately storing copies of values or nesting related rows together so analytical queries need fewer joins. | aka: denormalisation, denormalize, denormalise, denormalized
- data cleansing | The steps that fix or reject missing, duplicate, invalid and inconsistently formatted rows before they are loaded into a warehouse. | aka: data cleaning, data quality
- slot | BigQuery's unit of computing capacity, which a query's stages are scheduled over. | aka: slots, slot usage
- dataset | The BigQuery container that groups tables and views in a project and carries a location and a default table expiration. | aka: datasets, BigQuery dataset
- staging table | A table that holds extracted data exactly as it arrived, before cleansing and modelling. | aka: staging tables, raw staging

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Console signed in as a work or other Google account instead of the sandbox's own account: every dataset page reads `Access Denied: ... bigquery.datasets.get`; switch accounts (URL gains `authuser=N`).
- Creating a dataset or loading with a different location, then a join or query fails with a "not found in location" error; the location is permanent and must match.
- Trusting `--autodetect`: `monthly_fee` 49.00 arrives as FLOAT and dates as STRING, so types differ from the MySQL schema; use the custom schema.
- Forgetting `--skip_leading_rows=1` on CSV loads, so the header row loads as data or fails the type check; and forgetting that `--default_table_expiration` is in seconds, not days.
- Treating a warehouse like OLTP: expecting INSERT/UPDATE/DELETE to work in the sandbox (DML is unsupported) or expecting normalised designs to be faster; mixing up OLTP/OLAP columns in the comparison table.
- Reading cleansing as "delete bad rows": the day only finds the three bad events; removing or rejecting them belongs to Thursday and Friday.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- 01-desk-extract (AM, 60, a Python block): open `feature/desk-staging`, fetch `sql/history.sql` with `curl -fsSL -o` (never typed), run the week's one rebuild (`cat sql/schema.sql sql/seed.sql sql/routines.sql sql/history.sql` into `docker exec -i desk-mysql mysql`), then `python extract.py` writes `exports/priorities.csv`, `customers.csv`, `agents.csv`, `tickets.csv` and `ticket_events.jsonl` (14 events, three bad on purpose) with `exports/` ignored by git; stop point: after the five counts print and `head` shows `exports/tickets.csv`, paste the `write_jsonl` test (26 tests green) and commit.
- 02-raw-staging, datasets: read the sandbox banner and name the caps once; create `desk_raw` in the console's Create dataset dialog (`northamerica-northeast2`, 30-day default expiration; replay stand-in `bq mk --dataset --location=northamerica-northeast2 --default_table_expiration=2592000 desk_raw`), read it with `bq show desk_raw`, then create `desk_dw` with `bq mk --dataset --location=northamerica-northeast2 --default_table_expiration=5184000 desk_dw` (60 days).
- 02-raw-staging, loads: the console UI upload of `exports/customers.csv` with Auto detect, its Schema tab showing `monthly_fee` as FLOAT; then `warehouse/schemas/ticket_events.json` and `bash warehouse/load_raw.sh` (five `bq load --replace` lines with custom schemas) replace it, `bq ls desk_raw` lists five tables and `bq show --schema` prints NUMERIC; the break comes here.
- 02-raw-staging, queries and share: `warehouse/explore.sql` pasted query by query finds the three bad events (the `ROW_NUMBER() ... QUALIFY copy > 1` duplicate, the `closd` kind with `NOT IN`, ticket 6's event before it opened) and removes none, and its `board, denormalised` query shows the nested `ARRAY_AGG(STRUCT(...))` history; both IAM shares, never cut: the dataset share of `desk_dw` with BigQuery Data Viewer to a second account, after which `bq show --format=prettyjson desk_dw` lists five `access` entries with the new `READER` userByEmail, and the table share of `desk_raw.tickets`, before which `bq get-iam-policy desk_raw.tickets` prints only an `etag` and after which it prints a `bindings` list with `roles/bigquery.dataViewer` (both Checks are recorded from the trainer's console rehearsal of 2026-10-30; a replay proves only the `bq` lines; after a hard stop the shares resume at 05-external-data Step 1), then the merge into `main` and `git push origin main`.
