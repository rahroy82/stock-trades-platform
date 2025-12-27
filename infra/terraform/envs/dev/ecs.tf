# ECR repo to store container images
resource "aws_ecr_repository" "app_repo" {
  name = var.ecr_repo_name
}

# ECS cluster (no services, only run-task on demand)
resource "aws_ecs_cluster" "cluster" {
  name = var.ecs_cluster_name
}

# CloudWatch log group for task logs
resource "aws_cloudwatch_log_group" "task_logs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7
}

# IAM role ECS tasks use to pull images and write logs
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "ecs-tasks.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM role the task uses at runtime (access S3 data lake + write results)
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "ecs-tasks.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_s3_policy" {
  name = "${var.project_name}-ecs-task-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:ListBucket"],
        Resource = [aws_s3_bucket.data_lake.arn]
      },
      {
        Effect = "Allow",
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
        Resource = ["${aws_s3_bucket.data_lake.arn}/*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_attach_s3" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_s3_policy.arn
}

# Task Definition (image tag supplied at run time via script; placeholder here)
resource "aws_ecs_task_definition" "pipeline_task" {
  family                   = "${var.project_name}-pipeline"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "pipeline"
      image     = "${aws_ecr_repository.app_repo.repository_url}:latest"
      essential = true
      command   = ["bash", "-lc", "scripts/run_pipeline.sh"]
      environment = [
        { name = "TRADES_PER_SYMBOL", value = "1000" },
        { name = "MINUTES_BACK", value = "300" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.task_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "pipeline"
        }
      }
    }
  ])
}

output "ecr_repo_url" {
  value = aws_ecr_repository.app_repo.repository_url
}

output "ecs_cluster" {
  value = aws_ecs_cluster.cluster.name
}

output "ecs_task_definition_arn" {
  value = aws_ecs_task_definition.pipeline_task.arn
}
