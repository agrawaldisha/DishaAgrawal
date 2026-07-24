from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType
from datetime import datetime

# ── 1. Create Spark Session ──────────────────────────────
spark = SparkSession.builder \
    .appName("Silver_Clickstream_Transform") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("✅ Spark Session created")

# ── 2. Read Bronze layer ─────────────────────────────────
BRONZE_PATH = "bronze/output/"
SILVER_PATH = "silver/output/"

print(f"📥 Reading Bronze layer from {BRONZE_PATH}")

df_bronze = spark.read.parquet(BRONZE_PATH)

print(f"✅ Bronze records loaded: {df_bronze.count()}")


# Null checks 

null_counts = df_bronze.select ([
    F.count(F.when(F.col(c).isNull(), c)).alias(c)
    for c in df_bronze.columns
])

null_counts.show()

# Drop rows where critical columns are null
critical_columns = ["event_id", "user_id", "event_type", "event_timestamp"]

df_not_null = df_bronze.dropna(subset=critical_columns)

dropped_nulls = df_bronze.count() - df_not_null.count()
print(f"✅ Null records dropped: {dropped_nulls}")

# ── 4. DEDUPLICATION ─────────────────────────────────────
print("\n🔍 Removing duplicates...")

df_deduped = df_not_null.dropDuplicates(["event_id"])

dropped_dupes = df_not_null.count() - df_deduped.count()
print(f"✅ Duplicate records dropped: {dropped_dupes}")
# ── 5. STANDARDIZATION ───────────────────────────────────
print("\n🔧 Standardizing columns...")

df_standardized = df_deduped \
    .withColumn("device_type", 
        F.lower(F.trim(F.col("device_type")))) \
    .withColumn("traffic_source", 
        F.lower(F.trim(F.col("traffic_source")))) \
    .withColumn("event_type", 
        F.lower(F.trim(F.col("event_type"))))

print("✅ Columns standardized to lowercase")

# ── 6. DATA TYPE ENFORCEMENT ─────────────────────────────
print("\n🔧 Enforcing data types...")

df_typed = df_standardized \
    .withColumn("event_timestamp", 
        F.col("event_timestamp").cast(TimestampType())) \
    .withColumn("amount", 
        F.col("amount").cast("double")) \
    .withColumn("event_id", 
        F.col("event_id").cast("integer"))

print("✅ Data types enforced")


valid_event_types = ["page_view", "add_to_cart", "purchase", "wishlist"]
# ── QUARANTINE LAYER ─────────────────────────────────────
print("\n🔧 Writing rejected records to quarantine...")

QUARANTINE_PATH = "silver/quarantine/"

# Capture invalid records
df_rejected = df_typed.filter(
    (F.col("amount") < 0) |
    (F.col("event_timestamp") > F.current_timestamp()) |
    (~F.col("event_type").isin(valid_event_types))
).withColumn("rejection_reason",
    F.when(F.col("amount") < 0, "negative_amount")
     .when(F.col("event_timestamp") > F.current_timestamp(), "future_timestamp")
     .otherwise("invalid_event_type")
).withColumn("rejected_at", F.current_timestamp())

rejected_count = df_rejected.count()
print(f"⚠️ Quarantined records: {rejected_count}")

if rejected_count > 0:
    df_rejected.write \
        .mode("overwrite") \
        .parquet(QUARANTINE_PATH)
    print(f"✅ Rejected records saved to {QUARANTINE_PATH}")

# ── 7. BUSINESS RULES VALIDATION ─────────────────────────
print("\n🔧 Applying business rules...")

# Rule 1: amount cannot be negative
df_valid = df_typed.filter(F.col("amount") >= 0)

# Rule 2: event_timestamp cannot be in the future
df_valid = df_valid.filter(
    F.col("event_timestamp") <= F.current_timestamp()
)

# Rule 3: valid event types only

df_valid = df_valid.filter(
    F.col("event_type").isin(valid_event_types)
)

invalid_records = df_typed.count() - df_valid.count()
print(f"✅ Invalid records removed: {invalid_records}")

# ── 8. ADD SILVER METADATA ───────────────────────────────
print("\n🔧 Adding Silver metadata...")

df_silver = df_valid \
    .withColumn("silver_processed_at", F.current_timestamp()) \
    .withColumn("silver_version", F.lit("1.0")) \
    .drop("is_processed") \
    .drop("source_file")

# ── 9. SHOW RESULTS ──────────────────────────────────────
print("\n📋 Silver Layer Schema:")
df_silver.printSchema()

print(f"\n📊 Silver record count: {df_silver.count()}")
print("\n📊 Sample Silver Data:")
df_silver.show(5, truncate=False)

# ── 10. WRITE SILVER LAYER ───────────────────────────────
spark.conf.set(
    "spark.sql.sources.partitionOverwriteMode",
    "dynamic"
)

print(f"\n💾 Writing Silver layer to {SILVER_PATH}")

df_silver.write \
    .mode("overwrite") \
    .partitionBy("ingestion_date") \
    .parquet(SILVER_PATH)

print("✅ Silver layer written successfully!")
print(f"📁 Output: {SILVER_PATH}")



# ── WRITE TO BIGQUERY ────────────────────────────────────
from google.cloud import bigquery
import pandas as pd

print("\n☁️ Writing Silver layer to BigQuery...")

PROJECT_ID = "project-9491f28f-49e8-436b-958"
DATASET_ID = "silver_clickstream"
TABLE_ID = "clickstream_events"
TABLE_REF = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Convert Spark DF to Pandas for BQ upload
print("Converting to Pandas...")
df_silver_pandas = df_silver \
    .drop("ingestion_timestamp") \
    .drop("processed_file") \
    .toPandas()

print(f"✅ Converted: {len(df_silver_pandas)} rows")

# Upload to BigQuery
client = bigquery.Client(project=PROJECT_ID)

job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE",
    autodetect=True,
)

job = client.load_table_from_dataframe(
    df_silver_pandas,
    TABLE_REF,
    job_config=job_config
)

job.result()  # Wait for job to complete

table = client.get_table(TABLE_REF)
print(f"""
🎉 Silver Layer → BigQuery Complete!
   Table:   {TABLE_REF}
   Rows:    {table.num_rows}
   Schema:  {len(table.schema)} columns
""")