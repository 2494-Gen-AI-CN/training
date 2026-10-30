# w04d1 — Cloud computing concepts

gate: light
verified: 2026-10-30
week: 4 · Data fundamentals, cloud concepts, data warehousing, ETL/ELT
day: 1 · day-1-cloud-computing-concepts

version-stamps:
  - python: 3.15 (verified 2026-10-30)
  - google-cloud-sdk: 591.0 (`gcloud` and `bq`, the trainer machine's installed SDK 591.0.0; learners install the current release over the weekend; gcloud auth list, gcloud config get-value project, bq query --use_legacy_sql=false; no Python import on Monday) (verified 2026-10-30)
  - bigquery-sandbox: free tier, no card; 10 GB storage, 1 TB queries a month, 60-day default table expiration (verified 2026-10-30)   # figures from the Google Cloud docs; the page names them once and tells the reader to check the live pricing page
  - nist-sp-800-145: The NIST Definition of Cloud Computing, September 2011 (five characteristics, three service models, four deployment models) (verified 2026-10-30)

## Claims (≥ metrics.research.claimsMin; each MUST carry a source on a full gate; light gate: source optional but recommended)

- NIST defines cloud computing as a model for on-demand network access to a shared pool of configurable computing resources that can be rapidly provisioned and released with minimal management effort — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
- NIST lists five essential characteristics: on-demand self-service, broad network access, resource pooling, rapid elasticity and measured service — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
- NIST names three service models (SaaS, PaaS, IaaS) and four deployment models (private, community, public, hybrid) — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
- In IaaS the consumer provisions processing, storage and networks and controls the operating system and applications, but not the underlying infrastructure — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
- In SaaS the consumer uses the provider's application running on cloud infrastructure and manages none of the infrastructure or application capabilities beyond limited settings — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
- A Google Cloud region is an independent geographic area made of zones, and a zone is a deployment area within a region; Toronto is `northamerica-northeast2` — [Geography and regions](https://cloud.google.com/docs/geography-and-regions)
- Resources placed in several zones of one region survive the failure of a single zone, which is why managed services spread over zones — [Geography and regions](https://cloud.google.com/docs/geography-and-regions)
- Compute Engine provides virtual machines, which is the IaaS shape of hosting a database yourself — [Compute Engine documentation](https://cloud.google.com/compute/docs)
- Cloud SQL is a managed relational database service for MySQL, PostgreSQL and SQL Server, where Google runs patching, backups and failover — [Cloud SQL documentation](https://cloud.google.com/sql/docs)
- Cloud Storage is object storage, and objects live in buckets — [Cloud Storage documentation](https://cloud.google.com/storage/docs)
- BigQuery is Google's serverless analytics database, queried with GoogleSQL — [BigQuery documentation](https://cloud.google.com/bigquery/docs/introduction)
- BigQuery on-demand pricing charges for bytes processed by queries and for storage, and the console's validator shows an estimate before a query runs ("This query will process ...") — [BigQuery pricing](https://cloud.google.com/bigquery/pricing)
- The BigQuery sandbox needs no billing account, and gives free storage and query allowances with a default 60-day expiration on tables and partitions — [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
- Data leaving a provider's network (egress) is billed separately from compute and storage — [Google Cloud network pricing](https://cloud.google.com/vpc/network-pricing)
- Committed use discounts trade a one- or three-year commitment for a lower price than on-demand — [Committed use discounts](https://cloud.google.com/docs/cuds)
- The AWS shared responsibility model splits security so AWS secures the cloud itself and the customer secures what they put in it — [AWS shared responsibility model](https://aws.amazon.com/compliance/shared-responsibility-model/)
- Amazon S3 is AWS object storage, Azure Blob Storage is Azure's, Cloud Storage is Google's — [Amazon S3](https://docs.aws.amazon.com/s3/), [Azure Blob Storage](https://learn.microsoft.com/azure/storage/blobs/)
- Data warehouse (the matching table's category label): Amazon Redshift, Azure Synapse Analytics, Google BigQuery — [Amazon Redshift](https://docs.aws.amazon.com/redshift/), [Azure Synapse Analytics](https://learn.microsoft.com/azure/synapse-analytics/)

## Notes depth (D-0040; one block per curriculum subtopic, sized for a 4500–7000-word study page; every claim-bearing line carries [title](official url))

### Cloud computing model types
- Interview questions: What are public, private, hybrid and multi-cloud? (qc3.cloud-computing.R03); When would a bank keep its core ledger off the public cloud?; How is hybrid different from multi-cloud?
- Adjacent concept: Data residency and region choice — it is the usual reason a regulated firm keeps data in a named country or on its own premises.
- Trade-off or limit: Hybrid and multi-cloud add integration and skills cost, since every extra environment needs its own tooling and people — [Hybrid and multicloud architecture patterns](https://cloud.google.com/architecture/hybrid-multicloud-patterns)
- Recognise on sight: A diagram with an on-premises box linked by a VPN to a provider box (hybrid), or two provider logos around one app (multi-cloud).
- Claims:
  - Public cloud infrastructure is open to the general public and owned by a provider; private cloud serves a single organisation — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
  - Hybrid cloud is two or more distinct infrastructures bound by technology that allows data and application portability — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
  - Multi-cloud means using services from more than one provider, which is not in the NIST four and is defined by usage, not by ownership — [Hybrid and multicloud architecture patterns](https://cloud.google.com/architecture/hybrid-multicloud-patterns)
  - Bursting runs a steady load on site and sends peak overflow to a public cloud — [Hybrid and multicloud architecture patterns](https://cloud.google.com/architecture/hybrid-multicloud-patterns)

### Cloud computing service types
- Interview questions: What does "as a service" mean?; Which service type fits a team that wants to deploy code but not patch servers?; Where does the line of responsibility sit in each type?
- Adjacent concept: The shared responsibility model — it is how interviewers ask the same question as "what do I still manage".
- Trade-off or limit: The more a provider manages, the less control the customer keeps over versions, tuning and placement — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
- Recognise on sight: A pricing page that bills per VM hour (IaaS), per instance with a managed engine (PaaS) or per user seat (SaaS).
- Claims:
  - Service types stack: IaaS gives machines, PaaS adds a runtime or managed platform, SaaS delivers a finished application — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
  - The desk's MySQL on a VM is IaaS, on Cloud SQL is PaaS-style managed database, and a hosted help-desk product is SaaS — [Cloud SQL documentation](https://cloud.google.com/sql/docs)
  - Serverless services such as Cloud Run and BigQuery hide the servers entirely and bill by use — [Cloud Run documentation](https://cloud.google.com/run/docs)

### Cloud computing definition
- Interview questions: Define cloud computing in one sentence (qc3.cloud-computing.R01); Name the five essential characteristics and give an example of each; What is the difference between a region and a zone? (qc3.cloud-computing.R06)
- Adjacent concept: Virtualisation — it is the technique that lets one physical host serve many tenants, and underlies resource pooling.
- Trade-off or limit: Rapid elasticity does not mean unlimited; quotas and regional capacity still cap what an account can use — [Compute Engine quotas](https://cloud.google.com/compute/resource-usage)
- Recognise on sight: A console page with a "Create instance" button that returns a running resource in a minute (on-demand self-service) and a usage report (measured service).
- Claims:
  - Resource pooling means the provider serves many consumers from a shared pool using a multi-tenant model — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
  - Measured service means usage is metered, monitored and reported, which is what makes pay-per-use possible — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
  - A region contains zones, and zones in a region are separate failure domains linked by low-latency networking — [Geography and regions](https://cloud.google.com/docs/geography-and-regions)
  - AWS names the same idea a Region and Availability Zone; Azure uses region and availability zone — [AWS Regions and Availability Zones](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/)

### IaaS, PaaS, SaaS
- Interview questions: Give one product for each of IaaS, PaaS and SaaS; What benefit does each of IaaS, PaaS and SaaS buy a team? (qc3.cloud-computing.R02); Is BigQuery IaaS, PaaS or SaaS?
- Adjacent concept: Serverless — interviewers ask where it sits relative to PaaS.
- Trade-off or limit: SaaS is fastest to adopt but the customer cannot change the product's data model or hosting — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)
- Recognise on sight: A responsibility-stack table with columns for On-premises, IaaS, PaaS and SaaS and rows for networking, servers, OS, runtime, application, data.
- Claims:
  - IaaS benefit: no hardware purchase and fast provisioning, while the team still patches the OS and runs the database — [Compute Engine documentation](https://cloud.google.com/compute/docs)
  - PaaS benefit: the provider runs patches, backups and failover so the team manages schema and queries only — [Cloud SQL documentation](https://cloud.google.com/sql/docs)
  - SaaS benefit: nothing to install or operate, billed per user, with the vendor shipping updates — [NIST SP 800-145](https://csrc.nist.gov/pubs/sp/800/145/final)

### Challenges
- Interview questions: What are the main challenges of cloud adoption (cost control, security and compliance, vendor lock-in, latency, skills) and how does an organisation plan for each? (qc3.cloud-computing.R04); How does an organisation keep cloud costs under control?; How would you keep data in Canada?
- Adjacent concept: Egress fees and open formats — they are the practical mechanism behind lock-in worries.
- Trade-off or limit: Open formats lower lock-in but managed proprietary features (BigQuery SQL extensions, for instance) are what make the services productive — [BigQuery documentation](https://cloud.google.com/bigquery/docs/introduction)
- Recognise on sight: A budget alert email, or a policy listing allowed regions for resources.
- Claims:
  - Budgets and alerts notify an account owner when spend crosses a threshold; they do not by themselves stop spending — [Cloud Billing budgets](https://cloud.google.com/billing/docs/how-to/budgets)
  - Choosing a dataset location such as Toronto keeps stored data in that region, which supports data-residency rules — [BigQuery locations](https://cloud.google.com/bigquery/docs/locations)
  - Under the shared responsibility model the customer still configures access, so a public bucket is the customer's error — [AWS shared responsibility model](https://aws.amazon.com/compliance/shared-responsibility-model/)
  - Latency grows with distance between user and region, so region choice is a design decision — [Geography and regions](https://cloud.google.com/docs/geography-and-regions)

### Pricing
- Interview questions: How are cloud services priced? (qc3.cloud-computing.R05); What are the four meters?; Estimate the monthly cost of a small workload.
- Adjacent concept: Cost allocation with labels — it is how teams attribute a shared bill to projects.
- Trade-off or limit: Committed use is cheaper per unit but charges whether or not the capacity is used — [Committed use discounts](https://cloud.google.com/docs/cuds)
- Recognise on sight: A BigQuery editor line "This query will process 1.2 GB when run" and a pricing table of dollars per TiB.
- Claims:
  - Pay-as-you-go bills metered usage with no commitment; reserved or committed use trades a term for a discount — [Committed use discounts](https://cloud.google.com/docs/cuds)
  - BigQuery on-demand analysis is billed per TiB of bytes processed, and the first 1 TiB each month is free — [BigQuery pricing](https://cloud.google.com/bigquery/pricing)
  - Storage is billed per GiB a month, with the first 10 GiB a month free — [BigQuery pricing](https://cloud.google.com/bigquery/pricing)
  - Selecting fewer columns reduces bytes processed in BigQuery because storage is columnar; LIMIT does not reduce it — [Estimate and control costs](https://cloud.google.com/bigquery/docs/best-practices-costs)
  - The Free Program has two parts: a 90-day free trial with a one-off credit for new accounts, and the Free Tier, monthly usage allowances on some products (BigQuery's 1 TiB of queries and 10 GiB of storage among them) that do not expire with the trial — [Google Cloud Free Program](https://cloud.google.com/free/docs/free-cloud-features)

### AWS/Azure/GCP data services
- Interview questions: Name the object storage, relational database, NoSQL database, warehouse and pipeline service on each of AWS, Azure and GCP (qc3.cloud-computing.P01); List the common GCP services and say in one line what each is for (Compute Engine, Cloud Storage, Cloud SQL, BigQuery, Cloud Run, Pub/Sub, Dataflow, IAM) (qc3.cloud-computing.R07); What does Cloud Storage do that Cloud SQL does not?; What is Pub/Sub for?
- Adjacent concept: Managed versus serverless services (a Cloud SQL instance billed per hour while it runs, against BigQuery billed per query and per byte stored) — the usual follow-up when matching services across providers.
- Trade-off or limit: Equivalent services differ in pricing unit and features, so a name match is a starting point and not a guarantee — [Google Cloud: compare AWS and Azure services](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
- Recognise on sight: A three-column service-mapping table, one column per provider.
- Claims:
  - Object storage: Amazon S3, Azure Blob Storage, Cloud Storage — [Google Cloud: compare AWS and Azure services](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
  - Relational database: Amazon RDS, Azure SQL Database, Cloud SQL — [Google Cloud: compare AWS and Azure services](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
  - NoSQL database: Amazon DynamoDB, Azure Cosmos DB, Firestore or Bigtable — [Google Cloud: compare AWS and Azure services](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
  - Data warehouse: Amazon Redshift, Azure Synapse Analytics, BigQuery — [Google Cloud: compare AWS and Azure services](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
  - Pipelines: AWS Glue, Azure Data Factory, Dataflow — [Google Cloud: compare AWS and Azure services](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
  - Common GCP services: Compute Engine (VMs), Cloud Storage (objects), Cloud SQL (managed relational), BigQuery (analytics), Cloud Run (containers), Pub/Sub (messaging), Dataflow (pipelines), IAM (access) — [Google Cloud products](https://cloud.google.com/products)

## Sources (official / primary docs preferred; ≥ metrics.research.sourcesMin; full gate: every URL fetched and confirmed)

- NIST SP 800-145, The NIST Definition of Cloud Computing — https://csrc.nist.gov/pubs/sp/800/145/final
- Google Cloud geography and regions — https://cloud.google.com/docs/geography-and-regions
- BigQuery introduction — https://cloud.google.com/bigquery/docs/introduction
- BigQuery pricing — https://cloud.google.com/bigquery/pricing
- BigQuery sandbox — https://cloud.google.com/bigquery/docs/sandbox
- BigQuery locations — https://cloud.google.com/bigquery/docs/locations
- Estimate and control BigQuery costs — https://cloud.google.com/bigquery/docs/best-practices-costs
- Compute Engine documentation — https://cloud.google.com/compute/docs
- Cloud SQL documentation — https://cloud.google.com/sql/docs
- Cloud Storage documentation — https://cloud.google.com/storage/docs
- Cloud Run documentation — https://cloud.google.com/run/docs
- Committed use discounts — https://cloud.google.com/docs/cuds
- Cloud Billing budgets — https://cloud.google.com/billing/docs/how-to/budgets
- Google Cloud service comparison with AWS and Azure — https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison
- Hybrid and multicloud architecture patterns — https://cloud.google.com/architecture/hybrid-multicloud-patterns
- Google Cloud Free Program — https://cloud.google.com/free/docs/free-cloud-features
- AWS shared responsibility model — https://aws.amazon.com/compliance/shared-responsibility-model/
- AWS Regions and Availability Zones — https://aws.amazon.com/about-aws/global-infrastructure/regions_az/

## Glossary terms (3–8; one-sentence plain-language definitions; aka = alternate surface forms)

- cloud computing | Renting computing resources from a provider over a network, on demand and billed by measured use, instead of owning the hardware. | aka: the cloud
- IaaS | Infrastructure as a service: the provider supplies virtual machines, storage and networks, and the customer runs everything above them. | aka: infrastructure as a service
- PaaS | Platform as a service: the provider runs the operating system and runtime or managed engine, and the customer brings code or data. | aka: platform as a service
- SaaS | Software as a service: the provider runs a finished application that users reach through a browser or app. | aka: software as a service
- region | A geographic area in a cloud provider's network, made of several zones, such as Toronto's northamerica-northeast2. | aka: cloud region
- availability zone | An isolated deployment area inside a region with its own power and networking, so one failure does not take down the others. | aka: zones, availability zones
- hybrid cloud | A setup that joins an organisation's own infrastructure to a public cloud so workloads and data can move between them. | aka: hybrid
- multi-cloud | Using services from more than one cloud provider for one organisation's workloads. | aka: multicloud

## Common pitfalls (3–6; feed the runbook "where trainees get stuck" and quiz distractors)

- Mixing up the service types: calling Cloud SQL "IaaS" because it holds a MySQL server, or calling a hosted help-desk product "PaaS"; the test is what the team still manages.
- Treating a region and a zone as the same thing, or saying a zone is a country; a region holds several zones and one region is the unit that data-residency rules name.
- Reading the console's "This query will process" estimate as the price instead of bytes, or thinking `LIMIT` shrinks it; cost follows the columns scanned, not rows returned.
- Assuming the BigQuery sandbox is open-ended: it caps storage and queries, expires tables after 60 days and has no card behind it, so the caps are talking points, not surprises.
- Calling multi-cloud and hybrid the same; hybrid joins on-premises or private infrastructure to a public cloud, multi-cloud uses more than one provider.
- Setup check failures: `gcloud auth login` done but not `gcloud auth application-default login`, or no default project set; `gcloud auth list` and `gcloud config get-value project` show it.

## Demo plan hints (2–4; what must be shown live for this topic to land)

- Draw the five essential characteristics beside the desk: `desk-mysql` on a laptop against a provider-run database, ticking each one, then draw Toronto with its zones.
- Show the same desk hosted three ways on one board (VM running MySQL, Cloud SQL, hosted help-desk SaaS) with a "who manages what" stack filled in by the room.
- In the BigQuery console in each learner's own sandbox, type a query on the public `usa_names` table, read the validator's byte estimate before running, then read Job information after; save nothing.
- Read a live price list and work a small estimate on the board (storage a month plus a day of queries for the desk's warehouse and a 100,000-row dataset), then compare with the console's byte estimate.
