output "data_lake_bucket_name" {
  description = "GCS Data Lake bucket name"
  value       = google_storage_bucket.data_lake.name
}

output "data_lake_bucket_url" {
  description = "GCS Data Lake bucket URL"
  value       = "gs://${google_storage_bucket.data_lake.name}"
}

output "bronze_dataset_id" {
  description = "BigQuery Bronze dataset ID"
  value       = google_bigquery_dataset.bronze.dataset_id
}

output "silver_dataset_id" {
  description = "BigQuery Silver dataset ID"
  value       = google_bigquery_dataset.silver.dataset_id
}

output "gold_dataset_id" {
  description = "BigQuery Gold dataset ID"
  value       = google_bigquery_dataset.gold.dataset_id
}

output "pipeline_service_account" {
  description = "Pipeline service account email"
  value       = google_service_account.pipeline_sa.email
}