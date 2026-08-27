# E-commerce Clickstream Pipeline

A medallion-architecture data pipeline that turns raw clickstream events into
four analytical tables, orchestrated with Airflow and running on
Terraform-provisioned Google Cloud infrastructure.

Built to run end to end on a laptop with local Spark, then push its output to
GCS and BigQuery.

---

## Architecture

```
sample_clickstream.csv
        │
        ▼
   ┌──────────┐   raw events + ingestion metadata
   │  BRONZE  │   partitioned by ingestion_date  ──►  GCS gs://…/bronze/
   └────┬─────┘
        │
        ▼
   ┌──────────┐   null checks · dedupe · standardize · type cast
   │  SILVER  │   business rules  ──►  quarantine/  (rejected rows)
   └────┬─────┘                   ──►  BigQuery silver_clickstream
        │
        ▼
   ┌──────────┐   user_behaviour · product_performance
   │   GOLD   │   cart_abandonment · traffic_source
   └────┬─────┘
        │
        ▼
   data quality checks
```

Airflow runs the four stages in sequence:

```
bronze_layer_ingestion → silver_layer_transformation
    → gold_layer_aggregation → data_quality_checks
```

---

## The layers

### Bronze — `bronze/ingest_clickstream.py`

Reads the raw CSV with schema inference and stamps every row with the
metadata needed to trace it later: `ingestion_date`, `ingestion_timestamp`,
`source_file`, and an `is_processed` flag. Writes Parquet partitioned by
`ingestion_date` using dynamic partition overwrite, so re-running a single
day replaces only that day. The local output is then mirrored to GCS.

Nothing is filtered here — bronze keeps the raw record exactly as it arrived.

### Silver — `silver/transform_clickstream.py`

Where the data is actually made trustworthy, in stages:

1. **Null handling** — counts nulls per column, then drops rows missing any of
   `event_id`, `user_id`, `event_type`, or `event_timestamp`
2. **Deduplication** — `dropDuplicates` on `event_id`
3. **Standardization** — `device_type`, `traffic_source`, and `event_type`
   lowercased and trimmed
4. **Type enforcement** — `event_timestamp` to timestamp, `amount` to double,
   `event_id` to integer
5. **Quarantine** — rows failing a business rule are written to
   `silver/quarantine/` with a `rejection_reason` and `rejected_at`, rather
   than being silently dropped
6. **Business rules** — no negative `amount`, no future `event_timestamp`,
   and `event_type` restricted to `page_view`, `add_to_cart`, `purchase`,
   `wishlist`
7. **Lineage** — adds `silver_processed_at` and `silver_version`

Clean output lands as partitioned Parquet and is loaded into BigQuery
(`silver_clickstream.clickstream_events`, `WRITE_TRUNCATE`).

The quarantine step is the part worth stealing: a rejected row keeps its
reason, so bad data becomes something you can investigate instead of
something that vanishes.

### Gold — `gold/build_gold.py`

Four aggregate tables, each written to its own directory:

| Table | Grain | Measures |
|---|---|---|
| `user_behaviour` | user | events, sessions, total spend, purchases, cart adds, last seen |
| `product_performance` | product | views, cart adds, purchases, revenue, conversion rate % |
| `cart_abandonment` | device × traffic source | users who carted, abandonment rate % |
| `traffic_source` | traffic source × device | unique users, sessions, revenue, purchases, revenue per user |

Abandonment is computed with a left-anti join — users who added to cart minus
users who purchased — which is cheaper and clearer than a NOT IN subquery.
Conversion rate guards its denominator with `nullif` so products with zero
views yield null rather than a divide-by-zero.

---

## Orchestration — `dags/clickstream_pipeline_dag.py`

DAG `ecommerce_clickstream_pipeline`, daily at 02:00, `catchup=False`, two
retries five minutes apart, email on failure.

Each layer runs as a `PythonOperator` shelling out to its script and raising
on a non-zero exit code so the task fails loudly. The final task runs three
assertions:

1. Silver is not empty
2. No nulls in the critical columns
3. All four gold tables exist and have rows

---

## Infrastructure — `terraform/`

Provisions the Google Cloud side:

- **GCS data lake** with uniform bucket-level access, versioning, and
  lifecycle rules that tier objects to Nearline at 30 days, Coldline at 90,
  and Archive at 365
- **Layer prefixes** — `bronze/`, `silver/`, `gold/`, `quarantine/`
- **Three BigQuery datasets** — one per medallion layer, labelled by layer
  and environment
- **A pipeline service account** granted `storage.objectAdmin`,
  `bigquery.dataEditor`, and `dataproc.worker`

Region defaults to `asia-south1`; `project_id` and `gcs_bucket_name` are
required variables. The GCS remote backend is stubbed in `main.tf`, commented
out until a state bucket exists.

---

## Sample data

`data/sample_clickstream.csv` — nine events covering the full funnel
(`page_view` → `add_to_cart` → `purchase`) across mobile and desktop, organic
and paid, so every gold table produces rows on a first run.

| Column | Type |
|---|---|
| `event_id` | integer |
| `user_id`, `session_id`, `product_id` | string |
| `event_type` | one of page_view, add_to_cart, purchase, wishlist |
| `device_type`, `traffic_source` | string |
| `event_timestamp` | timestamp |
| `amount` | double |

---

## Running it

```bash
pip install -r requirements.txt
```

Then, from this directory:

```bash
python bronze/ingest_clickstream.py
python silver/transform_clickstream.py
python gold/build_gold.py
```

Or place `dags/clickstream_pipeline_dag.py` in your Airflow DAGs folder and
trigger `ecommerce_clickstream_pipeline`.

**Before the cloud steps will work**, set your own values — the scripts
currently carry the project and bucket they were developed against:

- `GCS_BUCKET` in `bronze/ingest_clickstream.py`
- `PROJECT_ID` in `silver/transform_clickstream.py`
- `project_id` and `gcs_bucket_name` for Terraform

Authenticate with `gcloud auth application-default login` first. To run
purely locally, comment out the GCS upload and BigQuery load blocks at the
end of the bronze and silver scripts.

Layer outputs are written to `bronze/output/`, `silver/output/`, and
`gold/output/` and are not tracked in git — they are regenerated on every run.
