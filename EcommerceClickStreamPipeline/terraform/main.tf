terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  # Remote backend — uncomment when you have GCP project
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "ecommerce-clickstream/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── GCS BUCKET — DATA LAKE ───────────────────────────────
resource "google_storage_bucket" "data_lake" {
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true

  # Lifecycle rules — move old data to cheaper storage
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }

  versioning {
    enabled = true
  }

  labels = {
    environment = var.environment
    project     = "ecommerce-clickstream"
    owner       = "disha-agrawal"
  }
}

# ── GCS FOLDERS — MEDALLION LAYERS ──────────────────────
resource "google_storage_bucket_object" "bronze_folder" {
  name    = "bronze/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

resource "google_storage_bucket_object" "silver_folder" {
  name    = "silver/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

resource "google_storage_bucket_object" "gold_folder" {
  name    = "gold/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

resource "google_storage_bucket_object" "quarantine_folder" {
  name    = "quarantine/"
  content = " "
  bucket  = google_storage_bucket.data_lake.name
}

# ── BIGQUERY DATASET — BRONZE ────────────────────────────
resource "google_bigquery_dataset" "bronze" {
  dataset_id    = "bronze_clickstream"
  friendly_name = "Bronze Layer — Raw Clickstream Data"
  description   = "Raw ingested clickstream events"
  location      = var.region

  labels = {
    environment = var.environment
    layer       = "bronze"
  }

  delete_contents_on_destroy = false
}

# ── BIGQUERY DATASET — SILVER ────────────────────────────
resource "google_bigquery_dataset" "silver" {
  dataset_id    = "silver_clickstream"
  friendly_name = "Silver Layer — Cleaned Clickstream Data"
  description   = "Validated and standardized clickstream events"
  location      = var.region

  labels = {
    environment = var.environment
    layer       = "silver"
  }

  delete_contents_on_destroy = false
}

# ── BIGQUERY DATASET — GOLD ──────────────────────────────
resource "google_bigquery_dataset" "gold" {
  dataset_id    = "gold_clickstream"
  friendly_name = "Gold Layer — Business Aggregations"
  description   = "Pre-aggregated business metrics"
  location      = var.region

  labels = {
    environment = var.environment
    layer       = "gold"
  }

  delete_contents_on_destroy = false
}

# ── SERVICE ACCOUNT ──────────────────────────────────────
resource "google_service_account" "pipeline_sa" {
  account_id   = "clickstream-pipeline-sa"
  display_name = "Clickstream Pipeline Service Account"
  description  = "SA for ecommerce clickstream pipeline"
}

# ── IAM ROLES FOR SERVICE ACCOUNT ───────────────────────
resource "google_project_iam_member" "pipeline_sa_gcs" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "pipeline_sa_bq" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "pipeline_sa_dataproc" {
  project = var.project_id
  role    = "roles/dataproc.worker"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}