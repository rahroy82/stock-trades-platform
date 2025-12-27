data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "ecs_tasks_sg" {
  name   = "${var.project_name}-ecs-tasks-sg"
  vpc_id = data.aws_vpc.default.id

  # Outbound only (tasks can reach AWS APIs / internet if needed)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "ecs_subnets" {
  value = data.aws_subnets.default.ids
}

output "ecs_security_group" {
  value = aws_security_group.ecs_tasks_sg.id
}
