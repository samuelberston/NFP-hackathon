# Public instance
resource "google_compute_instance" "public" {
  name         = "terraform-${var.environment}-public"
  machine_type = "e2-micro"
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.public.id
    access_config {
      // Ephemeral public IP
    }
  }

  tags = ["public", "web"]

  metadata = {
    environment = var.environment
  }
}

# Private instance
resource "google_compute_instance" "private" {
  name         = "terraform-${var.environment}-private"
  machine_type = "e2-micro"
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.private.id
  }

  tags = ["private"]

  metadata = {
    environment = var.environment
  }
} 