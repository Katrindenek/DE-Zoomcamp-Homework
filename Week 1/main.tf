terraform {
  required_providers {
    # We recommend pinning to the specific version of the Docker Provider you're using
    # since new versions are released frequently
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.1"
    }
  }
}

# Configure the docker provider
provider "docker" {
}

resource "docker_network" "private_network" {
  name = "pgnetwork"
}

resource "docker_container" "pgdatabase" {
  name = "pgdatabase"
  image = "postgres:13"
  network_mode = "bridge"

  env = [
    "POSTGRES_USER=root",
    "POSTGRES_PASSWORD=root",
    "POSTGRES_DB=ny_taxi",
  ]

  ports {
    internal = 5432
    external = 5432
  }

  volumes {
    host_path = "/home/katrine/Zoomcamp/2_docker_sql/ny_taxi_postgres_data"
    container_path = "/var/lib/postgresql/data"
    read_only = false
  }

  networks_advanced {
    name = "${docker_network.private_network.name}"
  }
}

resource "docker_container" "pgadmin" {
  name = "pgadmin"
  image = "dpage/pgadmin4"
  network_mode = "bridge"

  env = [
    "PGADMIN_DEFAULT_EMAIL=admin@admin.com",
    "PGADMIN_DEFAULT_PASSWORD=root",
  ]

  ports {
    internal = 80
    external = 8080
  }

  volumes {
    host_path = "/home/katrine/Zoomcamp/2_docker_sql/data_pgadmin"
    container_path = "/var/lib/pgadmin"
  }

  networks_advanced {
    name = "${docker_network.private_network.name}"
  }
}
