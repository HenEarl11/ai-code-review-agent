# Application tier running on ECS Fargate.

resource "aws_ecs_cluster" "main" {
  name = "acme-webapp-${var.environment}"
}

resource "aws_iam_role" "task" {
  name = "acme-webapp-task-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Task role policy — far too broad for an app that only reads one bucket.
resource "aws_iam_role_policy" "task" {
  name = "acme-webapp-task-${var.environment}"
  role = aws_iam_role.task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}

resource "aws_ecs_task_definition" "web" {
  family                   = "acme-webapp-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name  = "web"
    image = "acme/webapp:latest"
    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]
    environment = [
      { name = "DATABASE_URL", value = "postgres://admin:Sup3rS3cretPassw0rd!@${aws_db_instance.main.address}/webapp" },
      { name = "PAYMENTS_API_KEY", value = "pay-live-DEMO-FAKE-KEY-0123456789abcdef" },
      { name = "LOG_LEVEL", value = "debug" },
    ]
  }])
}

resource "aws_ecs_service" "web" {
  name            = "acme-webapp-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.web.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = [aws_subnet.public_a.id, aws_subnet.public_b.id]
    security_groups  = [aws_security_group.web.id]
    assign_public_ip = true
  }
}
