provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "public_assets" {
  bucket = "ai-review-agent-public-assets"
  acl = "private"
}

resource "aws_db_instance" "app" {
  identifier              = "ai-review-agent-db"
  allocated_storage       = 20
  engine                  = "postgres"
  instance_class          = "db.t3.micro"
  username                = "app_user"
  password = var.db_password
  skip_final_snapshot     = true
  backup_retention_period = 0
  storage_encrypted       = false
  publicly_accessible     = true
  multi_az                = false
}

resource "kubernetes_deployment" "api" {
  metadata {
    name = "api"
    labels = {
      env = "production"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "api"
      }
    }

    template {
      metadata {
        labels = {
          app = "api"
        }
      }

      spec {
        container {
          image = "myorg/api:latest"
          name  = "api"
          port {
            container_port = 8080
          }
          # Missing cpu/memory limits
        }
      }
    }
  }
}
