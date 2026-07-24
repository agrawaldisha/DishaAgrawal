from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ── 1. Create Spark Session ──────────────────────────────
spark = SparkSession.builder \
    .appName("Gold_Clickstream_Aggregations") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("✅ Spark Session created")

# ── 2. Read Silver Layer ─────────────────────────────────
SILVER_PATH = "silver/output/"
GOLD_PATH = "gold/output/"

df_silver = spark.read.parquet(SILVER_PATH)
print(f"✅ Silver records loaded: {df_silver.count()}")

# ── 3. GOLD TABLE 1 — User Behaviour Summary ─────────────
print("\n🥇 Building Gold Table 1: User Behaviour...")

gold_user = df_silver \
    .groupBy("user_id") \
    .agg(
        F.count("event_id").alias("total_events"),
        F.countDistinct("session_id").alias("total_sessions"),
        F.sum(F.when(F.col("event_type") == "purchase", 
            F.col("amount")).otherwise(0)
        ).alias("total_spend"),
        F.sum(F.when(F.col("event_type") == "purchase", 
            1).otherwise(0)
        ).alias("total_purchases"),
        F.sum(F.when(F.col("event_type") == "add_to_cart", 
            1).otherwise(0)
        ).alias("total_cart_additions"),
        F.max("event_timestamp").alias("last_seen_at")
    )

print("📊 User Behaviour Sample:")
gold_user.show(5, truncate=False)

# ── 4. GOLD TABLE 2 — Product Performance ────────────────
print("\n🥇 Building Gold Table 2: Product Performance...")

gold_product = df_silver \
    .groupBy("product_id") \
    .agg(
        F.count(F.when(F.col("event_type") == "page_view",
            1)).alias("total_views"),
        F.count(F.when(F.col("event_type") == "add_to_cart",
            1)).alias("total_cart_adds"),
        F.count(F.when(F.col("event_type") == "purchase",
            1)).alias("total_purchases"),
        F.sum(F.when(F.col("event_type") == "purchase",
            F.col("amount")).otherwise(0)
        ).alias("total_revenue"),
        F.round(
            F.count(F.when(F.col("event_type") == "purchase", 1)) /
            F.nullif(F.count(F.when(
                F.col("event_type") == "page_view", 1)), F.lit(0)
            ) * 100, 2
        ).alias("conversion_rate_pct")
    )

print("📊 Product Performance Sample:")
gold_product.show(5, truncate=False)

# ── 5. GOLD TABLE 3 — Cart Abandonment ───────────────────
print("\n🥇 Building Gold Table 3: Cart Abandonment...")

# Users who added to cart
users_carted = df_silver \
    .filter(F.col("event_type") == "add_to_cart") \
    .select("user_id") \
    .distinct()

# Users who purchased
users_purchased = df_silver \
    .filter(F.col("event_type") == "purchase") \
    .select("user_id") \
    .distinct()

# Users who abandoned = carted but NOT purchased
users_abandoned = users_carted.join(
    users_purchased,
    on="user_id",
    how="left_anti"
)

total_carted = users_carted.count()
total_abandoned = users_abandoned.count()
abandonment_rate = round((total_abandoned / total_carted) * 100, 2) \
    if total_carted > 0 else 0

gold_abandonment = df_silver \
    .filter(F.col("event_type") == "add_to_cart") \
    .groupBy("device_type", "traffic_source") \
    .agg(
        F.countDistinct("user_id").alias("users_who_carted"),
    ).withColumn("abandonment_rate_pct", F.lit(abandonment_rate))

print(f"⚠️ Overall Cart Abandonment Rate: {abandonment_rate}%")
print("📊 Abandonment by Device + Traffic Source:")
gold_abandonment.show(5, truncate=False)

# ── 6. GOLD TABLE 4 — Traffic Source Performance ─────────
print("\n🥇 Building Gold Table 4: Traffic Source...")

gold_traffic = df_silver \
    .groupBy("traffic_source", "device_type") \
    .agg(
        F.countDistinct("user_id").alias("unique_users"),
        F.countDistinct("session_id").alias("total_sessions"),
        F.sum(F.when(F.col("event_type") == "purchase",
            F.col("amount")).otherwise(0)
        ).alias("total_revenue"),
        F.count(F.when(F.col("event_type") == "purchase",
            1)).alias("total_purchases")
    ) \
    .withColumn("revenue_per_user",
        F.round(F.col("total_revenue") / F.col("unique_users"), 2)
    )

print("📊 Traffic Source Performance:")
gold_traffic.show(5, truncate=False)

# ── 7. WRITE ALL GOLD TABLES ─────────────────────────────
spark.conf.set(
    "spark.sql.sources.partitionOverwriteMode",
    "dynamic"
)

print("\n💾 Writing Gold tables...")

gold_user.write.mode("overwrite") \
    .parquet(f"{GOLD_PATH}user_behaviour/")

gold_product.write.mode("overwrite") \
    .parquet(f"{GOLD_PATH}product_performance/")

gold_abandonment.write.mode("overwrite") \
    .parquet(f"{GOLD_PATH}cart_abandonment/")

gold_traffic.write.mode("overwrite") \
    .parquet(f"{GOLD_PATH}traffic_source/")

print("✅ All Gold tables written successfully!")
print(f"""
📁 Gold Layer Output:
   ├── user_behaviour/
   ├── product_performance/
   ├── cart_abandonment/
   └── traffic_source/
""")