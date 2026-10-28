# QC - 3

## Cloud Computing

| Criteria Difficulty | Exit Criteria |
|---------------------|---------------|
| Required            | Can define cloud computing and describe its essential characteristics (on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service). |
| Required            | Explain the benefits of using "the cloud" in terms of each cloud service model (IaaS, PaaS, SaaS) |
| Required            | Can describe the public, private, hybrid and multi-cloud deployment models and name a situation that suits each. |
| Required            | Can describe the main challenges of adopting cloud computing (cost control, security and compliance, vendor lock-in, latency, skills) and how an organisation plans for them. |
| Required            | Can explain how cloud services are priced (pay-as-you-go, reserved and committed use, free tiers, charges for compute, storage, queries and data egress) and estimate the cost of a small workload. |
| Required            | Know the difference between a Region and Availability Zone |
| Required            | Can list and explain common GCP services |
| Preferred           | Can name the main data services of AWS, Azure and GCP (object storage, relational and NoSQL databases, data warehouse, data pipeline) and match a service on one provider to its equivalent on the other two. |

## Big Data

| Criteria Difficulty | Exit Criteria |
|---------------------|---------------|
| Required            | Can explain the 5 V's of Big Data and describe how they influence data warehouse design. |
| Required            | Can describe the components of a big data system (ingestion, storage, processing, analysis, visualisation) and the role of each. |
| Required            | Can describe a typical big data architecture, including batch and streaming paths, and explain why distributed storage and processing are needed. |
| Required            | Can explain the benefits of big data for an organisation (better decisions, new products, operational efficiency) with an example of each. |
| Required            | Can describe the challenges of big data (data quality, integration of sources, storage and processing cost, privacy and governance, skills). |
| Required            | Can describe the stages of the data lifecycle (generation, collection, storage, processing, analysis, sharing, archival, deletion) and what happens to data at each stage. |
| Required            | Can distinguish structured, semi-structured and unstructured data, give examples of each, and explain how each type is stored and queried. |
| Required            | Can compare common data file formats (CSV, JSON, XML, Parquet, Avro, ORC) by structure, schema handling, compression and typical use, and choose a format for a given workload. |

## Data Warehousing

| Criteria Difficulty | Exit Criteria |
|---------------------|---------------|
| Required            | Can explain the differences between OLTP and OLAP, including their respective use cases. |
| Required            | Can distinguish between Data Warehouses and Data Lakes, and describe the key differences in their architecture and use cases. |
| Required            | Can describe common components of data warehouse architecture and how they interact. |
| Required            | Can define a data mart, explain how it relates to a data warehouse, and describe when a dependent or independent data mart is appropriate. |
| Required            | Can describe common data quality problems (missing values, duplicates, inconsistent formats, invalid values) and the cleansing steps that fix them before data is loaded into a warehouse. |
| Required            | Can define what a data model is and explain its role in organizing, storing, and retrieving data in a data warehouse. |
| Required            | Can explain what data modeling is for and how a model moves from business requirements to tables. |
| Required            | Can explain dimensional modeling concepts, including fact tables, dimension tables, and measures, to create basic data models. |
| Required            | Can explain the purpose and benefits of dimensional modeling in data warehouse design, and differentiate it from entity-relationship modeling. |
| Required            | Can compare different schema designs and identify suitable use cases for each. |
| Required            | Can describe a star schema (a fact table surrounded by dimension tables), identify the grain of the fact table, and design one for a given business process. |
| Required            | Can describe a snowflake schema, explain how it differs from a star schema, and state when the extra normalization is worth its join cost. |
| Required            | Can describe the ETL (Extract, Transform, Load) process and its role in data warehousing. |
| Required            | Can compare ETL and ELT, explain where the transformation runs in each and why cloud warehouses favour ELT, and describe the steps of a pipeline that loads a source into a warehouse (extract, stage, transform, load, validate, log). |
| Preferred           | Can explain and apply key best practices in data warehouse design, including schema design, data quality, and performance optimization. |
| Preferred           | Define and distinguish between conceptual, logical, and physical data models. |
| Preferred           | Understands different data storage and data warehouse vendors, and can compare cloud-based versus on-premises data warehouse solutions in terms of scalability, cost, and maintenance. |
| Preferred           | Can explain how to choose the appropriate Slowly Changing Dimension (SCD) type based on how the data changes and business reporting needs. |
| Preferred           | Can explain the impact of using staging areas in large-scale ETL pipelines. |
| Preferred           | Can explain the impact of using an Operation Data Store (ODS) in large-scale ETL pipelines. |
| Preferred           | Can explain what denormalization is, why analytical stores denormalize where transactional databases normalize, and the trade-off in storage, query speed and update cost. |
| Preferred           | Can explain how a pipeline handles bad records, reruns and incremental loads so that a run can be repeated without duplicating or losing data. |
| Stretch             | Can evaluate trade-offs between different data warehouse architectures and propose an appropriate design for a given business scenario. |
| Stretch             | Can elaborate on all types (0-6) of slowly changing dimensions |
| Stretch             | Can apply dimensional modeling concepts to create basic data models, including designing fact tables, dimension tables, and measures. |

## BigQuery

| Criteria Difficulty | Exit Criteria |
|---------------------|---------------|
| Required            | Understands BigQuery architecture, including the separation of storage and compute, slot usage, and how queries are executed. |
| Required            | Can create a dataset in a cloud data warehouse, explain how datasets group tables, and set its location and default table expiration. |
| Required            | Can create tables, managing schema, and understanding table structures within BigQuery, and set IAM roles and permissions for datasets and tables. |
| Required            | Can create, modify, and manage table schemas, including adding columns, updating data types, and setting table expiration. |
| Required            | Can load data into BigQuery using multiple methods (UI, CLI, and load jobs), including using custom schemas. |
| Required            | Exports and imports data to and from BigQuery, using various file formats, and destination/source (Google Cloud Storage and Google Sheets) |
| Required            | Able to write and execute basic SQL queries in BigQuery to retrieve and analyze data. |
| Required            | Performs basic data transformations within BigQuery, such as aggregations, joins, and filtering. |
| Required            | Use BigQuery UI and the bq command-line tool effectively. |
| Required            | Understands common table partitioning strategies and can explain how partitioning affects cost and performance. |
| Preferred           | Uses partitioning and clustering to optimize data storage and retrieval and optimize complex queries using query caching |
| Preferred           | Can use parameterized queries for better reusability and security. |
| Preferred           | Uses BigQuery Data Transfer Services to automate the transfer of data from external sources. |
| Preferred           | Query external data sources like Cloud Storage or Cloud SQL using federated queries |
| Preferred           | Creates and manages BigQuery Connections (GCS, Cloud SQL, AWS S3) to enable federated or external querying. |
| Stretch             | Implements advanced data transformations, including window functions and recursive queries. |
