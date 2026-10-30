# w04d5 — ETL & ELT pipelines

gate: light
verified: 2026-10-30
week: 4 · Data fundamentals, cloud concepts, data warehousing, ETL/ELT
day: 5 · etl-and-elt-pipelines

version-stamps:
  - python: 3.15 (verified 2026-10-30)
  - google-cloud-bigquery: 3.47.0 (verified 2026-10-30) — google_cloud_bigquery-3.47.0-py3-none-any.whl
  - db-dtypes: 1.9.0 (verified 2026-10-30) — db_dtypes-1.9.0-py3-none-any.whl
  - pyarrow: 26.0.0 (verified 2026-10-30) — pyarrow-26.0.0-cp315-cp315-win_amd64.whl
  - pandas: 3.1.0 (verified 2026-10-30) — pandas-3.1.0-cp315-cp315-win_amd64.whl
  - pytest: 9.2.0 (verified 2026-10-30) — pytest-9.2.0-py3-none-any.whl
  - BigQuery GoogleSQL: current service (verified 2026-10-30)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- ETL extracts data from sources, transforms it on a separate processing system, and loads the result into the warehouse; in ELT the raw data is loaded first and transformed inside the warehouse with SQL — [Introduction to loading data](https://cloud.google.com/bigquery/docs/loading-data)
- BigQuery separates storage from compute, which is why transforming inside the warehouse (ELT) is practical there — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
- A load job writes with a write disposition: WRITE_TRUNCATE replaces the table, WRITE_APPEND adds rows, WRITE_EMPTY fails if the table has data — [Batch loading data](https://cloud.google.com/bigquery/docs/batch-loading-data)
- `load_table_from_file` and `load_table_from_dataframe` take a `LoadJobConfig` whose `schema` and `write_disposition` control the load; `.result()` waits for the job and raises on failure — [Python client library](https://cloud.google.com/python/docs/reference/bigquery/latest)
- `to_dataframe()` on a query result needs `db-dtypes` (and `pyarrow`) so BigQuery DATE and TIME types map to pandas dtypes — [db-dtypes on PyPI](https://pypi.org/project/db-dtypes/)
- An external table reads data that stays in Google Drive (Sheets) or Cloud Storage; BigQuery stores only the table definition, so each query reads the current source — [Introduction to external tables](https://cloud.google.com/bigquery/docs/external-tables)
- Querying a Google Sheet through an external table needs Drive access on the credentials, which the console grants but `bq` and ADC without a Drive scope do not — [Create Google Drive external tables](https://cloud.google.com/bigquery/docs/external-data-drive)
- A federated query reaches an external database (Cloud SQL, Spanner, AlloyDB) through `EXTERNAL_QUERY` and a connection resource; a BigQuery connection stores the access details — [Introduction to connections](https://cloud.google.com/bigquery/docs/connections-api-intro)
- The BigQuery Data Transfer Service schedules recurring loads from sources such as Cloud Storage, Amazon S3 and SaaS apps; the sandbox does not offer it — [What is the BigQuery Data Transfer Service?](https://cloud.google.com/bigquery/docs/dts-introduction)
- Query parameters (`@name`) send values separately from the SQL text, so a value cannot change the statement's structure; `bq query --parameter=name:TYPE:value` supplies them and an empty type means STRING — [Running parameterized queries](https://cloud.google.com/bigquery/docs/parameterized-queries)
- Saving query results from the console writes them to Google Sheets, Google Drive (CSV or JSONL), a local CSV or JSON download, or a BigQuery table; the Sheets save has a size limit — [Writing query results](https://cloud.google.com/bigquery/docs/writing-results)
- An extract job exports a table to Cloud Storage as CSV, JSON (newline delimited), Avro or Parquet; the sandbox has no bucket, so the course names this path without running it — [Export table data to Cloud Storage](https://cloud.google.com/bigquery/docs/exporting-data)
- The sandbox gives 10 GB of storage and 1 TB of queries a month, applies a 60-day default expiration, and does not support DML, streaming or the Data Transfer Service — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
- Application Default Credentials are found by client libraries from `gcloud auth application-default login` without a key file — [Set up ADC](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- `DataFrame.duplicated()` marks every repeat after the first by default (`keep="first"`), so row order decides which copy survives — [pandas.DataFrame.duplicated](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html)
- pytest fixtures supply test inputs; tests of pure transform functions need no database — [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### ETL overview
- Interview questions: What do the letters ETL stand for, what does each step do and what role does ETL play in a data warehouse? (qc3.data-warehousing.R13); Compare ETL and ELT: where does the transform run in each, why do cloud warehouses favour ELT, and what are the steps of a pipeline that loads a source into a warehouse? (qc3.data-warehousing.R14); How does a pipeline handle a bad record, a rerun and a load of only the new rows, so a run can be repeated without duplicating or losing data? (qc3.data-warehousing.P08); What does a staging area buy a large pipeline? (qc3.data-warehousing.P05); Follow-up (a level beyond): at scale, why would a job extract from an ODS rather than the production database, and what does that save? (qc3.data-warehousing.P06)
- Adjacent concept: Change data capture (CDC) versus batch extraction — after "what is ETL" an interviewer asks how a job picks up changes at all: a scheduled batch extract re-reads the source on a timer, while CDC streams each insert, update and delete from the database's change log as it happens; notes steps 1 to 3 (ETL and ELT, the pipeline steps with staging, ODS, rejects and the load log, then reruns and incremental loads) all sit under this subtopic, so P08 is answered here first and built in 06-etl-job.
- Trade-off or limit: ELT lands raw data first, so unvalidated and sensitive columns sit in the warehouse until transformed; ETL cleans before loading but needs its own compute — [Introduction to loading data](https://cloud.google.com/bigquery/docs/loading-data)
- Recognise on sight: a job file with `extract()`, `transform()`, `load()` functions called in order from `main()`; or a SQL file of `CREATE OR REPLACE TABLE ... AS SELECT` run after a load step (ELT).
- Claims:
  - ETL transforms on a separate engine before loading; ELT transforms in the warehouse after loading — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
  - Separated storage and compute make holding raw data and transforming it with SQL near the data affordable — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
  - A load into a warehouse should be safe to repeat; that is a design choice of the job (write disposition, watermark), not a default of the tool — [Batch loading data](https://cloud.google.com/bigquery/docs/batch-loading-data)
  - Design statement: an ODS or a replica is the copy a job extracts from so the extract's reads never compete with production; Cloud SQL read replicas exist to offload read and analytics traffic from the primary instance — [About replication in Cloud SQL](https://cloud.google.com/sql/docs/mysql/replication)
  - Design statement: landing raw extracts in staging tables first lets a job re-run its transform and validation without extracting from the source again; a load job writes a staging table with its own write disposition — [Batch loading data](https://cloud.google.com/bigquery/docs/batch-loading-data)

### BigQuery connections
- Interview questions: How do you export query results to and import data from Google Sheets and Cloud Storage, and in which file formats? (qc3.bigquery.R06); What is an external table, how does it differ from a loaded one, and what is a federated query to Cloud Storage or Cloud SQL? (qc3.bigquery.P04); What does a BigQuery connection hold, and which sources (Cloud Storage, Cloud SQL, AWS S3) need one? (qc3.bigquery.P05); How would you automate a recurring load from S3 or a SaaS source? (the Data Transfer Service) (qc3.bigquery.P03); Why use a named parameter such as @kind, and how do you pass one with `bq query --parameter`? (qc3.bigquery.P02); Follow-up (a level beyond): a Sheet-backed external table is joined to a partitioned fact every hour. What does each query cost and read, when would you switch to the native copy, and why can `bq` and ADC not read the Sheet at all? (qc3.bigquery.P04)
- Adjacent concept: Native copy versus external table — once a federated source is read often, a `CREATE TABLE ... AS SELECT` import trades freshness for speed and cost; the interviewer's next question after "what is an external table".
- Trade-off or limit: an external table is always current but slower and has fewer optimisations than a native table; import it when it is read often — [Introduction to external tables](https://cloud.google.com/bigquery/docs/external-tables)
- Recognise on sight: `CREATE OR REPLACE EXTERNAL TABLE ... OPTIONS (format = 'GOOGLE_SHEETS', uris = [...])`; `SELECT * FROM EXTERNAL_QUERY('connection_id', 'SELECT ...')`; `WHERE kind = @kind`.
- Claims:
  - External tables over Sheets and Cloud Storage keep the data at the source — [Introduction to external tables](https://cloud.google.com/bigquery/docs/external-tables)
  - Connections exist for Cloud SQL, Spanner, AlloyDB, Cloud Storage and AWS/Azure (BigQuery Omni) sources — [Introduction to connections](https://cloud.google.com/bigquery/docs/connections-api-intro)
  - The sandbox has no Data Transfer Service and no Cloud Storage bucket, so the course's external source is a Sheet — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
  - Query results save to Google Sheets, Google Drive, a local CSV or JSON file, or a table — [Writing query results](https://cloud.google.com/bigquery/docs/writing-results)
  - A table exports to Cloud Storage as CSV, JSON, Avro or Parquet through an extract job — [Export table data to Cloud Storage](https://cloud.google.com/bigquery/docs/exporting-data)
  - A parameterized query keeps values out of the SQL text, the BigQuery counterpart of week 3's `%s` placeholders — [Running parameterized queries](https://cloud.google.com/bigquery/docs/parameterized-queries)

### Building ETL/ELT processes
- Interview questions: How would you make a pipeline safe to run twice? What do you do with a record that fails validation? How do you load only what is new? (qc3.data-warehousing.P08); Follow-up (a level beyond): your watermark is MAX(event_id). What does it miss when a source row is updated after loading, or when ids arrive out of order, and what would you use instead (an updated-at timestamp, change data capture, or a periodic full reload)? (qc3.data-warehousing.P08, qc3.data-warehousing.R14)
- Adjacent concept: Testing transforms — a transform that is a pure function of its inputs is testable without a database, which is why the job keeps `transform.py` apart from `dw.py`.
- Trade-off or limit: an incremental load by `MAX(id)` watermark misses rows that change after loading and rows that arrive with lower ids; a full replace is simpler but costs more at scale — [Batch loading data](https://cloud.google.com/bigquery/docs/batch-loading-data)
- Recognise on sight: `WRITE_TRUNCATE` versus `WRITE_APPEND` in a `LoadJobConfig`; `SELECT MAX(event_id)` at the top of a job; a rejects table with a `reason` column; a one-row-per-run log table.
- Claims:
  - `WRITE_TRUNCATE` replaces a table, so repeating the same load leaves the same data — [Batch loading data](https://cloud.google.com/bigquery/docs/batch-loading-data)
  - `WRITE_APPEND` repeated with the same rows duplicates them, which is why append loads need a watermark — [Batch loading data](https://cloud.google.com/bigquery/docs/batch-loading-data)
  - Passing `schema=bq.get_table(table).schema` keeps the destination's types instead of a guess — [Python client library](https://cloud.google.com/python/docs/reference/bigquery/latest)
  - `datetime.now(timezone.utc)` gives a timezone-aware timestamp that loads into a TIMESTAMP column — [datetime](https://docs.python.org/3/library/datetime.html)
  - `DataFrame.merge` joins two frames on a column, like a SQL join — [pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
  - Design statement: a load job can skip invalid rows up to `max_bad_records` and report them only as job errors, so a job that must keep each bad row and its reason writes it to a rejects table itself — [Loading CSV data from Cloud Storage](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv)

### Review
- Interview questions: Walk me through how data gets from an operational database to a report. Why a star schema and not the source tables? Where would you put cleansing, and why? Compare two warehouse architectures for a given business. (qc3.data-warehousing.S01); Follow-up (a level beyond): the desk grows to millions of events a day, with a second source arriving as Parquet files. Would you keep ETL in Python or move to ELT in SQL, and what would change in staging, the watermark and the rejects table? (qc3.data-warehousing.S01)
- Adjacent concept: Architecture trade-offs — warehouse with ETL versus lake with ELT, and what size, latency and skills point to.
- Trade-off or limit: cleansing in Python is testable and keeps reasons but moves data out of the warehouse; cleansing in SQL runs next to the data but is harder to unit test — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)
- Recognise on sight: a README section naming grain, dimensions, the SCD choice and where cleansing runs.
- Claims:
  - A partitioned fact table limits the data a query scans — [Introduction to partitioned tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
  - Sandbox tables expire after 60 days unless the expiration is changed — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
  - ADC from one `gcloud auth application-default login` serves every Python run without a key file — [Set up ADC](https://cloud.google.com/docs/authentication/provide-credentials-adc)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Introduction to loading data — https://cloud.google.com/bigquery/docs/loading-data
- Batch loading data — https://cloud.google.com/bigquery/docs/batch-loading-data
- BigQuery overview — https://cloud.google.com/bigquery/docs/introduction
- Introduction to external tables — https://cloud.google.com/bigquery/docs/external-tables
- Create Google Drive external tables — https://cloud.google.com/bigquery/docs/external-data-drive
- Introduction to connections — https://cloud.google.com/bigquery/docs/connections-api-intro
- What is the BigQuery Data Transfer Service? — https://cloud.google.com/bigquery/docs/dts-introduction
- Running parameterized queries — https://cloud.google.com/bigquery/docs/parameterized-queries
- Writing query results — https://cloud.google.com/bigquery/docs/writing-results
- Export table data to Cloud Storage — https://cloud.google.com/bigquery/docs/exporting-data
- BigQuery sandbox — https://cloud.google.com/bigquery/docs/sandbox
- Introduction to partitioned tables — https://cloud.google.com/bigquery/docs/partitioned-tables
- Set up Application Default Credentials — https://cloud.google.com/docs/authentication/provide-credentials-adc
- pandas.DataFrame.duplicated — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html
- pytest fixtures — https://docs.pytest.org/en/stable/how-to/fixtures.html
- datetime — https://docs.python.org/3/library/datetime.html
- About replication in Cloud SQL — https://cloud.google.com/sql/docs/mysql/replication
- Loading CSV data from Cloud Storage — https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- watermark | The highest id or timestamp a job has already loaded, read at the start of a run so it extracts only newer rows. | aka: high-water mark, load watermark
- incremental load | A run that extracts and loads only the rows added since the last run instead of the whole source. | aka: delta load, incremental extract
- idempotent | Describes a job whose repeated run leaves the data exactly as one run did. | aka: idempotency, safe to rerun
- reject | A record that fails a validation rule and is saved in a separate table with the reason instead of being loaded or silently dropped. | aka: rejects, rejected row, reject table
- external table | A BigQuery table whose data stays in a source such as a Google Sheet or Cloud Storage and is read at query time. | aka: external data source
- federated query | A query that BigQuery sends to an outside database through a connection and joins with its own tables. | aka: federated queries, EXTERNAL_QUERY
- query parameter | A named placeholder such as @kind in SQL whose value is sent separately from the statement text. | aka: parameterized query, named parameter, bind variable
- load log | A table with one row per job run recording when it ran and how many rows were read, loaded and rejected. | aka: run log, audit table

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Using `WRITE_APPEND` on a table the job refills each run, so a second run doubles the rows; the table must be replaced or guarded by a watermark.
- Letting BigQuery return rows in no fixed order and marking duplicates by frame order, so a different copy is kept on different runs; sort by the key first.
- Dropping bad records silently so counts disagree with the source and nobody can say why; a reject needs a reason and a table.
- Forgetting `DESK_GCP_PROJECT` in a new terminal (`KeyError`), or trying to read the Sheet-backed external table from `bq` or Python, which carry no Drive scope.
- Pasting a value into SQL text instead of using `@kind`, or forgetting that `--parameter=kind::value` with an empty type means STRING.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- 05-external-data (AM, 50): create `desk_raw.agent_teams` as an external table over the public "Desk agent teams" Sheet from the console, join it to the star for events per team, save the result to a Google Sheet and as a CSV file, edit one Sheet cell and rerun the same query to see new totals with no load, then `bq show desk_raw.agent_teams` printing Type EXTERNAL; the block stops there with the four native-copy lines pasted into `warehouse/external.sql` and `warehouse/kind_report.sql` and committed. Per the block's resumeAt, the native copy runs in the console in the first 10 minutes of Facilitation: Review, with `bq show desk_raw.agent_teams_copy` printing Type TABLE beside the EXTERNAL one.
- 05-external-data, resumeAt (opening Facilitation: Review, right after the native copy): three runs of `bq query --use_legacy_sql=false --parameter=kind::<value> < warehouse/kind_report.sql` with the same file, two with different kinds to show the value travels beside the SQL text and never inside it (the empty type between the colons means STRING), then the injection attempt as a value, which is on the cut-first list (the two kind runs stay).
- 06-etl-job (PM, 110): run `pytest` to 32 passed with no BigQuery and no environment variable before `etl.py` exists, to show the transforms are testable alone; the break follows this run.
- 06-etl-job, stop point: the first `python etl.py` prints its load-log row (rows_read 1, rows_loaded 12, rows_rejected 3) and the commit is made there; per the block's resumeAt, the second run (rows_read 0, every table but `desk_dw.load_log` unchanged), the REPL reads and `pylint` open the sprint / project work slot rather than running inside the block, and the merge of `feature/desk-etl` into `main` with its push is never left for week 5.
