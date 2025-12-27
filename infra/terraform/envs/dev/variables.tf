variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "stock-trades-platform"
}

variable "data_lake_bucket_name" {
  type        = string
  description = "Globally-unique S3 bucket name for the data lake"
}

variable "ecr_repo_name" {
  type    = string
  default = "stock-trades-platform"
}

variable "ecs_cluster_name" {
  type    = string
  default = "stock-trades-platform-cluster"
}
