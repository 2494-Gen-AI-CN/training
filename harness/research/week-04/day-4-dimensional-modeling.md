# w04d4 — Dimensional modeling

gate: light
verified: 2026-10-30
week: 4 · Data fundamentals, cloud concepts, data warehousing, ETL/ELT
day: 4 · dimensional-modeling

version-stamps:
  - python: 3.15 (verified 2026-10-30)
  - google-cloud-bigquery: 3.47.0 google_cloud_bigquery-3.47.0-py3-none-any.whl (verified 2026-10-30)
  - db-dtypes: 1.9.0 db_dtypes-1.9.0-py3-none-any.whl (verified 2026-10-30)
  - pyarrow: 26.0.0 pyarrow-26.0.0-cp315-cp315-win_amd64.whl (verified 2026-10-30)
  - BigQuery GoogleSQL: current (managed service, no version) (verified 2026-10-30)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- A star schema has one central fact table of events or measurements whose dimension tables form the points of the star, joined on keys — [Dimensional modeling in Microsoft Fabric Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-overview)
- The dimension key values set a fact table's granularity (grain), and a fact table must load at one consistent grain — [Modeling fact tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-fact-tables)
- BigQuery supports both star and snowflake schemas, though its native representation is nested and repeated fields — [Schema and data transfer overview](https://cloud.google.com/bigquery/docs/migration/schema-data-overview)
- BigQuery performs best when data is denormalised, because joining large tables on every query is resource intensive — [Specify nested and repeated columns](https://cloud.google.com/bigquery/docs/nested-repeated)
- A partitioned table is divided into segments by a time-unit column (DATE, DATETIME, TIMESTAMP), by ingestion time or by an integer range — [Introduction to partitioned tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
- Filtering on the partition column prunes partitions, so the query scans and bills fewer bytes and runs faster — [Optimize query computation](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)
- Clustering sorts a table's storage by up to four columns, and filters on them reduce the bytes scanned; the gain grows with table size — [Introduction to clustered tables](https://cloud.google.com/bigquery/docs/clustered-tables)
- Query results are cached for about 24 hours per user and project when the query text and tables are unchanged, and a cached result bills no bytes — [Using cached query results](https://cloud.google.com/bigquery/docs/cached-results)
- Cached results are not used when the query calls non-deterministic functions such as CURRENT_TIMESTAMP, or when a referenced table changed — [Using cached query results](https://cloud.google.com/bigquery/docs/cached-results)
- A dry run (`bq query --dry_run`) reports the bytes a query would process without running it — [Estimate and control costs](https://cloud.google.com/bigquery/docs/best-practices-costs)
- The BigQuery sandbox applies a 60-day default expiration to tables and partitions and allows no DML — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
- `CREATE TABLE ... PARTITION BY ... CLUSTER BY ... AS SELECT` creates a partitioned and clustered table from a query — [CREATE TABLE statement](https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#create_table_statement)
- `QUALIFY` filters on window-function results after they are computed — [Query syntax](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#qualify_clause)
- `bigquery.Client.query(sql).result()` waits for a job and returns rows; `to_dataframe()` needs db-dtypes for DATE and TIME columns — [BigQuery Python client library](https://cloud.google.com/python/docs/reference/bigquery/latest)
- Application Default Credentials let client libraries find credentials written by `gcloud auth application-default login` — [Set up ADC](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- Python `datetime.date` compares with `<` and `>=`, which is how an effective-date range picks a row — [datetime](https://docs.python.org/3/library/datetime.html)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Modeling
- Interview questions: What is a data model and what is it for in a warehouse? (qc3.data-warehousing.R06); How does a business requirement become a table? (qc3.data-warehousing.R07); Why model before loading a warehouse?
- Adjacent concept: Business questions as the starting point — the word "by" in "events by agent, by month" names the dimensions the model needs.
- Trade-off or limit: A warehouse should be designed to adapt as requirements evolve, so a model built for today's questions grows new columns and tables later — [Dimensional modeling in Microsoft Fabric Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-overview)
- Recognise on sight: a whiteboard of boxes (ticket, customer, agent) with lines between them before any CREATE TABLE.
- Claims:
  - A data model is a blueprint of what data an organisation collects, how the datasets relate and how they are stored and analysed — [What is data modeling? (AWS)](https://aws.amazon.com/what-is/data-modeling/) · [What is data modeling? (IBM)](https://www.ibm.com/think/topics/data-modeling)
  - Business rules are captured first, the conceptual model bridges them to the database, and the logical and physical models add types, keys and platform details until tables can be built — [What is data modeling? (AWS)](https://aws.amazon.com/what-is/data-modeling/)
  - A good dimension design starts by asking users what they analyse: "sales by salesperson, by month" names the dimensions and attributes — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)
  - A warehouse model is read many times and loaded in batches, the opposite of a transactional one — [BigQuery overview](https://cloud.google.com/bigquery/docs/introduction)

### Conceptual/logical/physical
- Interview questions: Define conceptual, logical and physical models (qc3.data-warehousing.P02); Which one do business stakeholders read?; Name the warehouse design best practices applied to the desk: schema design, data quality and performance (qc3.data-warehousing.P01); What partitioning strategies does BigQuery offer, and how does filtering on the partition column change bytes billed and speed? (qc3.bigquery.R10); How do partitioning, clustering and the query cache each cut cost on the desk's fact table? (qc3.bigquery.P01)
- Adjacent concept: Data types per engine (MySQL DECIMAL against BigQuery NUMERIC) — the logical model survives an engine change, the physical one does not.
- Trade-off or limit: The physical model is tied to one engine's features and prices, and in the sandbox a partition older than 60 days expires, so partitioning by an old date empties the table — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
- Recognise on sight: an ER sketch with names only (conceptual), the same with keys and attributes (logical), a DDL file with types, PARTITION BY and CLUSTER BY (physical).
- Claims:
  - Conceptual models give the big picture (entities, business rules) in a simple diagram that business stakeholders and analysts can agree on — [What is data modeling? (AWS)](https://aws.amazon.com/what-is/data-modeling/) · [What is data modeling? (IBM)](https://www.ibm.com/think/topics/data-modeling)
  - Logical models add data types, relationships and key fields and stay technology-agnostic; physical models map them to one DBMS with field types and tuning — [What is data modeling? (AWS)](https://aws.amazon.com/what-is/data-modeling/) · [What is data modeling? (IBM)](https://www.ibm.com/think/topics/data-modeling)
  - BigQuery partitions by a time-unit column, by ingestion time or by an integer range, and filtering on the partition column prunes partitions, which reduces bytes billed and improves query performance — [Introduction to partitioned tables](https://cloud.google.com/bigquery/docs/partitioned-tables) · [Optimize query computation](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)
  - Clustering orders storage by up to four columns so filters on them read fewer blocks — [Introduction to clustered tables](https://cloud.google.com/bigquery/docs/clustered-tables)
  - A rerun of an identical query over unchanged tables reads the cached result and bills no bytes — [Using cached query results](https://cloud.google.com/bigquery/docs/cached-results)
  - Data-quality best practice: the load tests integrity between related tables and uses special member rows (such as key 0 for missing) instead of null keys — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)

### Dimension modeling
- Interview questions: What are facts, dimensions and measures? (qc3.data-warehousing.R08); What is grain and why state it first?; What is dimensional modeling for, and how does it differ from ER modeling? (qc3.data-warehousing.R09)
- Adjacent concept: Additive, semi-additive and non-additive measures — which can be summed across which dimensions.
- Trade-off or limit: Dimensional models accept repeated descriptive data for query speed, while relational and ER models reduce duplication to keep writes safe — [What is data modeling? (AWS)](https://aws.amazon.com/what-is/data-modeling/) · [Dimensional modeling techniques (Kimball Group)](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- Recognise on sight: table names prefixed `fact_` and `dim_`, a `date_key` column, and `event_count` or `amount` measures.
- Claims:
  - Fact tables hold dimension keys and numeric measures; dimension tables hold descriptive attributes used to filter and group — [Modeling fact tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-fact-tables) · [Dimensional modeling techniques (Kimball Group)](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
  - An additive measure sums across every dimension, a semi-additive one across some, a non-additive one (a rate, a temperature) across none — [Modeling fact tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-fact-tables)
  - A fact table must load at a consistent grain; mixing grains in one table gives wrong sums — [Understand star schema (Power BI)](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
  - A date dimension stores one row per date with year, month and weekday, and its key is the date as a YYYYMMDD integer — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)
  - Surrogate keys insulate the warehouse from source ids and make type 2 history possible — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)

### Star schema
- Interview questions: Describe a star schema and state the grain of the desk's fact table (qc3.data-warehousing.R11); Design a star for an order or ticket process: fact, dimensions and measures (qc3.data-warehousing.S03); Write a star query that joins the fact to dim_agent, filters on kind and counts events per agent (qc3.bigquery.R08)
- Adjacent concept: Conformed dimensions — one `dim_date` shared by several fact tables.
- Trade-off or limit: A star repeats dimension attributes, so a change to a descriptive value needs a rule (see slowly changing dimensions) — [Understand star schema (Power BI)](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- Recognise on sight: a fact query with `JOIN dim_x AS x ON x.key = f.x_key` and `GROUP BY x.name`.
- Claims:
  - A star schema suits analytic queries, which filter and group by dimensions and summarise the fact — [Dimensional modeling in Microsoft Fabric Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-overview)
  - A star query joins the fact to each needed dimension, then filters with WHERE, groups with GROUP BY and aggregates with COUNT or SUM — [Query syntax](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
  - `GENERATE_DATE_ARRAY` with `UNNEST` builds a date dimension in one statement — [Array functions](https://cloud.google.com/bigquery/docs/reference/standard-sql/array_functions)
  - `ROW_NUMBER() OVER (...)` can make a surrogate key — [Numbering functions](https://cloud.google.com/bigquery/docs/reference/standard-sql/numbering_functions)
  - `FORMAT_DATE('%Y%m%d', d)` cast to INT64 yields a YYYYMMDD key — [Date functions](https://cloud.google.com/bigquery/docs/reference/standard-sql/date_functions)

### Snowflake schema
- Interview questions: How does a snowflake schema differ from a star, and when is the extra normalization worth its joins? (qc3.data-warehousing.R12); Compare star, snowflake and nested designs and name a use case for each (qc3.data-warehousing.R10); Which suits BigQuery?
- Adjacent concept: Normalization from week 3 — a snowflake normalises the dimensions only, never the fact.
- Trade-off or limit: Snowflaking stores less repeated text but adds joins, and BigQuery performs best on denormalised data — [Specify nested and repeated columns](https://cloud.google.com/bigquery/docs/nested-repeated)
- Recognise on sight: `dim_ticket` joined to `dim_priority` joined to the fact; a dimension holding a foreign key to another dimension.
- Claims:
  - A snowflake schema is a star whose dimension tables are normalised; BigQuery supports both — [Schema and data transfer overview](https://cloud.google.com/bigquery/docs/migration/schema-data-overview)
  - Splitting `dim_priority` from `dim_ticket` is the snowflaked form; folding `sla_hours` into `dim_ticket` is the star form — [Understand star schema (Power BI)](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
  - A snowflake dimension pays when the dimension is very large and storage outweighs query speed, when a fact sits at a higher grain (such as subcategory), or when history is tracked at a higher level — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)
  - Nested and repeated fields are BigQuery's third way: they keep related rows together without a join on every query — [Specify nested and repeated columns](https://cloud.google.com/bigquery/docs/nested-repeated)

### Slowly changing dimensions
- Interview questions: What is a slowly changing dimension?; A customer changes plan: what should last month's report say?; How do you choose an SCD type from how the data changes and what reports need? (qc3.data-warehousing.P04); Walk through SCD types 0 to 6 and what each keeps (qc3.data-warehousing.S02)
- Adjacent concept: Effective dates and a current flag — the columns that make history queryable.
- Trade-off or limit: Type 2 keeps history at the cost of more rows and a date-range join; type 1 is simple but rolls the past up under the new value — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)
- Recognise on sight: `effective_from`, `effective_to`, `is_current` columns on a dimension.
- Claims:
  - An SCD manages dimension values that change slowly and unpredictably, such as a customer's email or plan — [Understand star schema (Power BI)](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
  - Use type 1 for attributes where no history matters and type 2 only where reports must show the value in force at event time — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)
  - An attribute that changes often belongs in the fact table rather than in a type 2 dimension — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)
  - A date dimension suits type 0 because a date's attributes never change — [Dimensional modeling techniques (Kimball Group)](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
  - Facts join to a type 2 dimension with a time-based lookup on the event date — [Understand star schema (Power BI)](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)

### SCD types
- Interview questions: Name types 0 to 6 and what each keeps (qc3.data-warehousing.S02); Which type keeps full history, and which keeps one previous value?; Why pick type 2 for the desk's customers and type 1 for tickets? (qc3.data-warehousing.P04)
- Adjacent concept: Type 2 in code: closing the old row and appending a new one is a pure function, testable without a database.
- Trade-off or limit: Type 3 keeps limited history in a previous-value column and is rarely used; types 5 and 6 combine approaches and are harder to maintain — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables) · [Dimensional modeling techniques (Kimball Group)](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- Recognise on sight: a function taking current rows, source rows and `as_of`, returning updated rows; `9999-12-31` as the open end.
- Claims:
  - Type 1 overwrites, type 2 inserts a versioned row, type 3 tracks limited history in attributes — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)
  - Type 0 retains the original, type 4 moves changing attributes to a mini-dimension or history table, and types 5 and 6 are hybrids (6 = 1 + 2 + 3) — [Dimensional modeling techniques (Kimball Group)](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
  - A type 2 change sets the old row's end date and current flag to false, then adds a new current row whose start date is that end date — [Modeling dimension tables](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables)
  - Python `Decimal` compares exactly where float may not, which matters for a tracked fee — [decimal](https://docs.python.org/3/library/decimal.html)
  - Loading with the table's own schema avoids autodetect guessing types — [BigQuery Python client library](https://cloud.google.com/python/docs/reference/bigquery/latest)
  - Without DML in the sandbox, a type 2 change is a whole-table load with WRITE_TRUNCATE — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- Schema and data transfer overview (BigQuery) — https://cloud.google.com/bigquery/docs/migration/schema-data-overview
- Specify nested and repeated columns (BigQuery) — https://cloud.google.com/bigquery/docs/nested-repeated
- Optimize query computation (BigQuery) — https://cloud.google.com/bigquery/docs/best-practices-performance-compute
- Introduction to partitioned tables — https://cloud.google.com/bigquery/docs/partitioned-tables
- Introduction to clustered tables — https://cloud.google.com/bigquery/docs/clustered-tables
- Using cached query results — https://cloud.google.com/bigquery/docs/cached-results
- BigQuery sandbox — https://cloud.google.com/bigquery/docs/sandbox
- Estimate and control costs — https://cloud.google.com/bigquery/docs/best-practices-costs
- Query syntax — https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
- BigQuery Python client library — https://cloud.google.com/python/docs/reference/bigquery/latest
- Set up ADC — https://cloud.google.com/docs/authentication/provide-credentials-adc
- Dimensional modeling in Microsoft Fabric Warehouse — https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-overview
- Modeling dimension tables (Microsoft Fabric) — https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables
- Modeling fact tables (Microsoft Fabric) — https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-fact-tables
- Understand star schema (Power BI) — https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
- What is data modeling? (AWS) — https://aws.amazon.com/what-is/data-modeling/
- What is data modeling? (IBM) — https://www.ibm.com/think/topics/data-modeling
- Dimensional modeling techniques (Kimball Group; the only source for SCD types 0, 4, 5 and 6) — https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/
- datetime — https://docs.python.org/3/library/datetime.html
- decimal — https://docs.python.org/3/library/decimal.html

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- fact table | The central table of a dimensional model, with one row per event or measurement at a stated grain, holding keys to dimensions and numeric measures. | aka: fact tables, fact
- dimension table | A table of descriptive attributes (who, what, where, when) that a fact table points to and that queries filter and group by. | aka: dimension tables, dimension, dimensions
- grain | What exactly one row of a fact table represents, such as one ticket event, stated before any column is chosen. | aka: granularity, fact grain
- star schema | A dimensional model with one fact table joined directly to denormalised dimension tables, drawn like a star. | aka: star schemas, star
- snowflake schema | A star whose dimensions are further normalised into linked lookup tables, trading extra joins for less repetition. | aka: snowflake, snowflaked
- slowly changing dimension | A dimension whose attribute values change rarely, with a rule (type 0 to 6) for what happens to the old value. | aka: SCD, SCDs, SCD type 2
- partition pruning | A warehouse skipping the partitions a filter on the partition column rules out, so fewer bytes are scanned and billed. | aka: pruning, pruned partitions
- clustered table | A table whose storage is sorted by up to four chosen columns, so a filter on them reads fewer blocks. | aka: clustering, cluster columns

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Choosing columns before stating the grain, then mixing event-level and ticket-level numbers in one fact table and double counting.
- Joining a type 2 dimension on the business key only, so each event matches every historical version and counts multiply; the effective-date range is missing.
- Rerunning `CREATE OR REPLACE` on a history-keeping dimension wipes the history; it must be `IF NOT EXISTS`.
- Expecting a filter on a non-partition column to cut bytes billed, or forgetting the sandbox's 60-day partition expiry empties a table of old dates.
- Treating a cached rerun as proof a query is cheap, when non-deterministic functions or a changed table turn the cache off.
- Treating an exclusive `effective_to` as inclusive (`<=`), so an event on the change date matches two versions.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- 03-star-schema (AM, 80): the grain ("one row per ticket event") is stated on the whiteboard in Facilitation: Dimension modeling and repeated as the walkthrough's talking point before the first CREATE TABLE, never typed into `star.sql`, so the file and its tally stay as the plan lists them; open `feature/desk-star`, type the five dimension statements, break, type the fact, run `star.sql` once and show `bq ls desk_dw` listing six tables.
- 03-star-schema: in `questions.sql` show a star query (fact joined to `dim_agent`, filtered on `kind`, counted per agent) beside its snowflake counterpart through `dim_ticket` and `dim_priority`; compare the bytes estimate with and without the `event_date` filter, then the cached rerun (first on the cut list), and name the 60-day partition expiry while `bq show` prints it.
- 04-customer-history (PM, 85): build `dw.py` and `apply_scd2` with its tests and pause at `pytest` showing 29 passed (the break); then type the `star.sql` history lines and `sql/changes.sql`, and in the REPL run Dana's change with `as_of = date(2026, 11, 5)` and read her two `dim_customer` rows (49.00 closed, 199.00 current).
- 04-customer-history: close the block by merging `feature/desk-star` into `main` and running `git push origin main`, so `main` holds Thursday's two commits and `origin/main` matches it (the ladder guarantee); after a hard stop the merge and push slide to 05-external-data Step 1.
