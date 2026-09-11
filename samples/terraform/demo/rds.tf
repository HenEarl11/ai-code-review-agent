# Primary Postgres database for the web app.

resource "aws_db_subnet_group" "main" {
  name       = "acme-webapp-${var.environment}"
  subnet_ids = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

resource "aws_db_instance" "main" {
  identifier     = "acme-webapp-${var.environment}"
  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t3.medium"

  allocated_storage = 50
  storage_type      = "gp3"
  storage_encrypted = false

  db_name  = "webapp"
  username = "admin"
  password = "Sup3rS3cretPassw0rd!"

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  publicly_accessible     = true
  multi_az                = false
  backup_retention_period = 0
  skip_final_snapshot     = true
  deletion_protection     = false

  tags = {
    Environment = var.environment
  }
}
