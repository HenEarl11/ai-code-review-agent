# Static assets bucket for the web app.

resource "aws_s3_bucket" "assets" {
  bucket = "acme-webapp-assets-${var.environment}"

  tags = {
    Environment = var.environment
    Team        = "platform"
  }
}

resource "aws_s3_bucket_acl" "assets" {
  bucket = aws_s3_bucket.assets.id
  acl    = "public-read"
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id

  versioning_configuration {
    status = "Suspended"
  }
}

# Access logs bucket — no lifecycle rule, logs grow forever.
resource "aws_s3_bucket" "logs" {
  bucket = "acme-webapp-logs-${var.environment}"
}
