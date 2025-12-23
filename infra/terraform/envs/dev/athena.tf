# Athena query results bucket (separate from data lake to keep things clean)
resource "aws_s3_bucket" "athena_results" {
  bucket = "${var.data_lake_bucket_name}-athena-results"
}

resource "aws_s3_bucket_public_access_block" "athena_results_block_public" {
  bucket                  = aws_s3_bucket.athena_results.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Optional: enforce encryption for the bucket (good practice)
resource "aws_s3_bucket_server_side_encryption_configuration" "athena_results_sse" {
  bucket = aws_s3_bucket.athena_results.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Athena Workgroup: forces query results into the results bucket and enables basic cost controls
resource "aws_athena_workgroup" "stock_trades_wg" {
  name        = "${var.project_name}-wg"
  description = "Athena workgroup for Stock Trades platform (query results + cost control)"

  configuration {
    enforce_workgroup_configuration = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/results/"
    }
  }
}

output "athena_workgroup" {
  value = aws_athena_workgroup.stock_trades_wg.name
}

output "athena_results_bucket" {
  value = aws_s3_bucket.athena_results.bucket
}

