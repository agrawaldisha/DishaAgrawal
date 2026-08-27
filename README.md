# Disha Agrawal

**Data & AI Engineer** · Learning in public

A working repository, not a portfolio. It holds two kinds of things: pipelines and applications I've actually built and run, and the study notes and reference guides I wrote while learning the stack around them. Both are here because the notes are what made the projects possible.

---

## Quick navigation

| | Folder | What it is |
|---|---|---|
| 🔧 | [`EcommerceClickStreamPipeline/`](EcommerceClickStreamPipeline/) | Medallion clickstream pipeline — PySpark, Airflow, Terraform |
| 🔧 | [`python/`](python/) | PaySync — FastAPI + PostgreSQL payment gateway, and a full FastAPI guide |
| 🔧 | [`Claude/`](Claude/) | Building with Claude — API, Claude Code, MCP servers, subagents |
| 📘 | [`SQL/`](SQL/) | SQL patterns reference, zero to advanced |
| 📘 | [`Snowflake/`](Snowflake/) | SnowPro Core course work, theory, and a streaming demo |
| 📘 | [`DataBricks/`](DataBricks/) | Apache Spark notebooks — basics through optimization |
| 📘 | [`GenAI/`](GenAI/) | Generative AI course guides and Vertex AI scripts |
| 📘 | [`Google Cloud/`](Google%20Cloud/) | GCP certification question banks |

🔧 built · 📘 studied

---

## Projects

### `EcommerceClickStreamPipeline/`

An end-to-end clickstream pipeline built on the medallion architecture.

- **Bronze** — `ingest_clickstream.py` lands raw events as date-partitioned Parquet
- **Silver** — `transform_clickstream.py` cleans, types, and deduplicates
- **Gold** — `build_gold.py` produces four analytical tables: user behaviour, product performance, traffic source, and cart abandonment
- **Orchestration** — an Airflow DAG (`dags/clickstream_pipeline_dag.py`) chains the three layers on a 2 AM daily schedule with retries and failure alerts
- **Infrastructure** — Terraform provisions the GCS data lake with lifecycle rules for tiering old partitions to cheaper storage

Runs locally against `local[*]` Spark with the sample data in `data/`.

### `python/` — PaySync

A multi-tenant payment gateway built with FastAPI and PostgreSQL, plus the guide written alongside it.

- `readme.md` — a complete FastAPI reference: Pydantic validation, SQLAlchemy, psycopg2, the request lifecycle, OpenAPI, and concurrency vs. parallelism, all framed around building PaySync
- `pydanticValidation.ipynb` — validation patterns worked through interactively
- `paysync.tar.gz`, `FastAPI - CRUD (Postgres).zip` — the source archives

### `Claude/`

Building with Claude, from first API call to multi-agent orchestration — Messages API features (streaming, tool use, multi-turn), project-level Claude Code configuration with hooks and custom skills, MCP server construction, and subagent design. See the [folder README](Claude/README.md) for the breakdown.

---

## Study material

### `SQL/`

`Readme.md` is the centrepiece — a pattern-by-pattern SQL reference that works up from `SELECT` and filtering to window functions, each pattern with a "when to use" and a worked example. Alongside it: window-function deep-dive PDFs and solved query files (`GoldMedalCount.sql`, custom sorting).

### `Snowflake/`

- `SnowCoreContent-Udemy/` — SnowPro Core course work as runnable SQL across six days: access control and row/column security, virtual warehouses and resource monitors, stages and `COPY INTO`, query profiling and caching, clustering and micro-partition pruning, UDFs and stored procedures, secure data sharing, time travel, and cloning
- `Comparison.md` — 16 real-world pain points across traditional, modern cloud, and Snowflake warehouses, framed for a fintech audience
- `snowpipe-streaming.md` — a real-time ride-sharing analytics design using Snowpipe Streaming and Kafka
- `Theory/` — notes on stages, with sample order data

### `DataBricks/`

Four Apache Spark notebooks — `SparkBasics`, `spark_sql`, `SparkAdvance`, and `SparkOptimizations` — moving from DataFrames and Spark SQL through to partitioning, joins, and tuning.

### `GenAI/`

- `CourseGuides/` — foundational concepts, moving beyond chatbots, and navigating the GenAI landscape
- `Scripts/` — generating text embeddings with Vertex AI, and loading GCS data into BigQuery from the CLI

### `Google Cloud/`

Certification question banks with answers: Professional Data Engineer (304 questions), Data Practitioner (91), and GenAI Leader, plus notes on client-server architecture.

---

## Also here

`Generative AI Weekly Recap - 7 Pages.pptx` — a slide summary of a week's GenAI reading.

---

## Stack

**Processing** PySpark · Spark SQL · Databricks
**Warehousing** Snowflake · BigQuery
**Orchestration** Airflow
**Infrastructure** Terraform · Google Cloud Storage
**Application** Python · FastAPI · PostgreSQL · Pydantic
**AI** Claude API · Claude Code · MCP · Vertex AI

---

## A note on what's here

Commits reflect genuine progress rather than finished products — some folders are deep, others are a starting point, and the READMEs say which is which. If something here is useful to you, take it. If you spot something worth improving, open an issue.
