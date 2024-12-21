# Configure the Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "containerregistry.googleapis.com"
  ])
  service = each.key
  disable_on_destroy = false
}

# Create Cloud SQL instance
resource "google_sql_database_instance" "instance" {
  name             = "demo-db-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_13"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled = true
      start_time = "03:00"  # 3 AM UTC
    }

    ip_configuration {
      ipv4_enabled = true
      # Only allow private IP in production
      authorized_networks {
        name  = "allow-cloud-run"
        value = "0.0.0.0/0"  # Replace with actual Cloud Run IP in production
      }
    }
  }

  deletion_protection = false  # Set to true in production
}

# Create database
resource "google_sql_database" "database" {
  name     = "demo-db"
  instance = google_sql_database_instance.instance.name
}

# Create database user
resource "google_sql_user" "users" {
  name     = "demo-user"
  instance = google_sql_database_instance.instance.name
  password = random_password.db_password.result
}

# Random suffix for unique DB instance names
resource "random_id" "db_name_suffix" {
  byte_length = 4
}

# Generate random DB password
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Cloud Run service
resource "google_cloud_run_service" "service" {
  name     = "demo-service"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/demo-app:latest"
        
        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.users.name}:${random_password.db_password.result}@${google_sql_database_instance.instance.connection_name}/demo-db"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Make the service public
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_service.service.name
  location = google_cloud_run_service.service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
