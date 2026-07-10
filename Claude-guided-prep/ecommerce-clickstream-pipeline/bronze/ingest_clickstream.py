from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime 

import os

# Create spark session 

spark = SparkSession.builder \
    .appName("Bronze_Clickstream Ingestion") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("Spark Session created successfully.")

# Define Paths 

input_path = "data/sample_clickstream.csv"
output_path = "bronze/output/"
ingestion_date = datetime.now().strftime("%Y-%m-%d")

# Read the CSV file into a DataFrame

df_raw = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(input_path)
print("Raw DataFrame read successfully.")

# Add metadata columns 

df_bronze =df_raw \
    .withColumn("ingestion_date", F.lit(ingestion_date)) \
    .withColumn("ingestion_timestamp",F.current_timestamp()) \
    .withColumn("source_file",F.lit(input_path)) \
    .withColumn("processed_file",F.lit(False)) 

print("Metadata columns added")

# show schema and sample data 

print("Bronze DataFrame Schema:")
df_bronze.printSchema()

print("Sample bronze data")
df_bronze.show(5,truncate=False)

# write to bronze output 
print("Writing to Bronze output path...")

# Mode can be "overwrite" or "append" ,"ignore" or "error"
df_bronze.write \
    .mode("overwrite") \
    .partitionBy("ingestion_date") \
    .parquet(output_path) 

print("Bronze data written successfully to:", output_path)

