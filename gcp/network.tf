# Create a custom VPC
resource "google_compute_network" "vpc" {
  name                    = "terraform-${var.environment}-vpc"
  auto_create_subnetworks = false
}

# Create public subnet
resource "google_compute_subnetwork" "public" {
  name          = "terraform-${var.environment}-public"
  ip_cidr_range = "10.0.1.0/24"
  network       = google_compute_network.vpc.id
  region        = var.region

  # Enable flow logs for security
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling       = 0.5
    metadata           = "INCLUDE_ALL_METADATA"
  }
}

# Create private subnet
resource "google_compute_subnetwork" "private" {
  name          = "terraform-${var.environment}-private"
  ip_cidr_range = "10.0.2.0/24"
  network       = google_compute_network.vpc.id
  region        = var.region

  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling       = 0.5
    metadata           = "INCLUDE_ALL_METADATA"
  }
}

# Cloud NAT for private instances
resource "google_compute_router" "router" {
  name    = "terraform-${var.environment}-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "terraform-${var.environment}-nat"
  router                            = google_compute_router.router.name
  region                            = var.region
  nat_ip_allocate_option            = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  
  subnetwork {
    name                    = google_compute_subnetwork.private.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
} 