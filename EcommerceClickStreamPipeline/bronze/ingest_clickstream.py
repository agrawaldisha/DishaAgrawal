from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime
from google.cloud import storage
import os

# ── 1. Create Spark Session ──────────────────────────────
spark = SparkSession.builder \
    .appName("Bronze_Clickstream_Ingestion") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("✅ Spark Session created successfully")

# ── 2. Define paths ──────────────────────────────────────
INPUT_PATH = "../data/sample_clickstream.csv"
LOCAL_OUTPUT_PATH = "bronze/output/"
GCS_BUCKET = "disha-ecommerce-clickstream-dev"
GCS_BRONZE_PATH = "bronze"
INGESTION_DATE = datetime.now().strftime("%Y-%m-%d")

# ── 3. Read raw data ─────────────────────────────────────
print(f"📥 Reading raw data from {INPUT_PATH}")

df_raw = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(INPUT_PATH)

print(f"✅ Raw records loaded: {df_raw.count()}")

# ── 4. Add metadata columns ──────────────────────────────
df_bronze = df_raw \
    .withColumn("ingestion_date", F.lit(INGESTION_DATE)) \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("source_file", F.lit(INPUT_PATH)) \
    .withColumn("is_processed", F.lit(False))

print("✅ Metadata columns added")

# ── 5. Show schema and sample data ──────────────────────
print("\n📋 Bronze Layer Schema:")
df_bronze.printSchema()

print("\n📊 Sample Bronze Data (5 rows):")
df_bronze.show(5, truncate=False)

# ── 6. Write locally first ───────────────────────────────
spark.conf.set(
    "spark.sql.sources.partitionOverwriteMode",
    "dynamic"
)

print(f"\n💾 Writing Bronze layer locally to {LOCAL_OUTPUT_PATH}")

df_bronze.write \
    .mode("overwrite") \
    .partitionBy("ingestion_date") \
    .parquet(LOCAL_OUTPUT_PATH)

print(f"✅ Bronze layer written locally")

# ── 7. Upload to GCS ─────────────────────────────────────
def upload_to_gcs(local_path, bucket_name, gcs_path):
    """Upload local Parquet files to GCS"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    uploaded = 0
    for root, dirs, files in os.walk(local_path):
        for file in files:
            local_file = os.path.join(root, file)
            relative_path = os.path.relpath(local_file, local_path)
            gcs_file_path = f"{gcs_path}/{relative_path}"

            blob = bucket.blob(gcs_file_path)
            blob.upload_from_filename(local_file)
            print(f"  ☁️  Uploaded: {gcs_file_path}")
            uploaded += 1

    print(f"✅ Total files uploaded: {uploaded}")

print("\n☁️  Uploading Bronze layer to GCS...")

upload_to_gcs(
    local_path=LOCAL_OUTPUT_PATH,
    bucket_name=GCS_BUCKET,
    gcs_path=GCS_BRONZE_PATH
)

print(f"""
🎉 Bronze Layer Complete!
   Local:  {LOCAL_OUTPUT_PATH}
   GCS:    gs://{GCS_BUCKET}/{GCS_BRONZE_PATH}/
   Date:   {INGESTION_DATE}
""")

spark.stop()