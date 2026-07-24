from airflow import DAG 
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import subprocess
import logging 

# Define default arguments for the DAG
default_args = {
    'owner': 'disha_agrawal',
    'depends_on_past': False,
    'email': ['agrawaldisha294@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2026,7,10),
}

# Define DAG 

dag= DAG(
    dag_id='ecommerce_clickstream_pipeline',
    default_args=default_args,
    description='Bronze -> Silver -> Gold Clickstream Data Pipeline',
    schedule='0 2 * * *',
    catchup=False,
    tags=['clickstream', 'bronze', 'silver', 'gold']
)

# Define task functions 

def run_bronze_layer():
    logging.info("Starting Bronze Layer Ingestion...")
    result=subprocess.run(
        ["python", "bronze/ingest_clickstream.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0 :
        raise Exception (f" Bronze layer failed: {result.stderr}")
    logging.info("Bronze Layer Ingestion completed successfully.")
    logging.info(f"Output: {result.stdout}")

def run_silver_layer():
    logging.info("Starting Silver Layer Transformation...")
    result=subprocess.run(
        ["python", "silver/transform_clickstream.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0 :
        raise Exception (f" Silver layer failed: {result.stderr}")
    logging.info("Silver Layer Transformation completed successfully.")
    logging.info(f"Output: {result.stdout}")

def run_gold_layer():
    logging.info("Starting Gold Layer Aggregation...")
    result=subprocess.run(
        ["python", "gold/build_gold.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0 :
        raise Exception (f" Gold layer failed: {result.stderr}")
    logging.info("Gold Layer Aggregation completed successfully.")
    logging.info(f"Output: {result.stdout}")

def run_data_quality_checks():
    logging.info("Starting Data Quality Checks...")
    
    from pyspark.sql import SparkSession

    spark= SparkSession.builder \
        .appName("Data_Quality_Checks") \
        .master("local[*]") \
        .getOrCreate()
    
    # check 1 - silver record count >0 
    silver_df = spark.read.parquet("silver/output/")
    silver_count = silver_df.count()
    assert silver_count >0 , f"Silver layer empty ! count : {silver_count}"
    logging.info(f"Silver layer record count check passed: {silver_count} records found.")

    # check 2 - NO nulls in critical columns

    from pyspark.sql import functions as F 
    null_count = silver_df.filter(
    F.col("event_id").isNull() | F.col("user_id").isNull() | F.col("event_type").isNull() | F.col("event_timestamp").isNull()
    )
    assert null_count.count() == 0, f"Null values found in critical columns!"
    logging.info("Data Quality Checks completed successfully.")

     # Check 3 — Gold tables exist and not empty
    gold_tables = [
        "user_behaviour",
        "product_performance", 
        "cart_abandonment",
        "traffic_source"
    ]
    for table in gold_tables:
        df = spark.read.parquet(f"gold/output/{table}/")
        count = df.count()
        assert count > 0, f"❌ Gold table {table} is empty!"
        logging.info(f"✅ Check 3 passed: {table} has {count} records")
    
    logging.info("✅ All data quality checks passed!")
    spark.stop()


# Define tasks

task_bronze = PythonOperator(
    task_id='bronze_layer_ingestion',
    python_callable=run_bronze_layer,
    dag=dag
)

task_silver = PythonOperator(
    task_id='silver_layer_transformation',
    python_callable=run_silver_layer,
    dag=dag
)

task_gold = PythonOperator(
    task_id='gold_layer_aggregation',
    python_callable=run_gold_layer,
    dag=dag
)

task_quality_checks = PythonOperator(
    task_id='data_quality_checks',
    python_callable=run_data_quality_checks,
    dag=dag
)

# Define task dependencies
task_bronze >> task_silver >> task_gold >> task_quality_checks

