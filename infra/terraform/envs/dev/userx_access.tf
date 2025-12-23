# userX demo role: read-only access to curated data + Athena workgroup usage
resource "aws_iam_role" "userx_demo_role" {
  name = "${var.project_name}-userx-demo-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

# Policy: read-only curated data + allow Athena queries in the project workgroup
resource "aws_iam_policy" "userx_demo_policy" {
  name = "${var.project_name}-userx-demo-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # S3: list bucket
      {
        Effect = "Allow",
        Action = ["s3:ListBucket"],
        Resource = [aws_s3_bucket.data_lake.arn],
        Condition = {
          StringLike = {
            "s3:prefix" = [
              "stock-trades-platform/curated/*",
              "stock-trades-platform/raw/*"
            ]
          }
        }
      },
      # S3: read objects (curated + raw read for transparency; can tighten to curated only)
      {
        Effect = "Allow",
        Action = ["s3:GetObject"],
        Resource = [
          "${aws_s3_bucket.data_lake.arn}/stock-trades-platform/curated/*",
          "${aws_s3_bucket.data_lake.arn}/stock-trades-platform/raw/*"
        ]
      },
      # Athena: allow running queries in the workgroup
      {
        Effect = "Allow",
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:ListWorkGroups",
          "athena:GetWorkGroup"
        ],
        Resource = "*"
      },
      # S3: allow Athena to write query results ONLY to the Athena results bucket
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ],
        Resource = [aws_s3_bucket.athena_results.arn]
      },
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ],
        Resource = ["${aws_s3_bucket.athena_results.arn}/results/*"]
      },
      # Glue: read catalog metadata (needed for Athena UX)
      {
        Effect = "Allow",
        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "userx_attach_policy" {
  role       = aws_iam_role.userx_demo_role.name
  policy_arn = aws_iam_policy.userx_demo_policy.arn
}

output "userx_demo_role_arn" {
  value = aws_iam_role.userx_demo_role.arn
}

