# Create storage bucket with versioning
resource "google_storage_bucket" "data" {
  name          = "terraform-${var.environment}-${var.project_id}-data"
  location      = "US"
  force_destroy = true

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.bucket_key.id
  }

  # Add explicit dependency on the IAM binding
  depends_on = [
    google_kms_crypto_key_iam_member.crypto_key
  ]
}

# KMS key for bucket encryption
resource "google_kms_key_ring" "bucket_keyring" {
  name     = "terraform-${var.environment}-bucket-keyring"
  location = "us"
}

resource "google_kms_crypto_key" "bucket_key" {
  name     = "terraform-${var.environment}-bucket-key"
  key_ring = google_kms_key_ring.bucket_keyring.id
  
  # Remove or modify the lifecycle block if you're sure it's safe to allow destruction
  # lifecycle {
  #   prevent_destroy = true
  # }
}

# Grant Cloud Storage service account access to use the KMS key
resource "google_kms_crypto_key_iam_member" "crypto_key" {
  crypto_key_id = google_kms_crypto_key.bucket_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:service-${data.google_project.current.number}@gs-project-accounts.iam.gserviceaccount.com"
}

# Get current project details
data "google_project" "current" {
} 