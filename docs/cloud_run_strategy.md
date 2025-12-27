# Cloud Run Strategy (Low Cost AWS)

Goal: Run the stock-trades platform on AWS with minimal cost while keeping it demo-ready for userX.

## Core Services
- S3: data lake storage (raw/curated/ml_features)
- Glue: catalog + crawler (on-demand)
- Athena: query layer (pay per query scanned; optimized via Parquet + partitions)
- IAM + STS: userX time-limited, read-only demo access

## Orchestration (Cost-Efficient)
We avoid always-on Airflow in iteration 1.

Preferred options:
1) ECS Fargate RunTask (on-demand): runs the existing Python scripts in a container
2) AWS Lambda (only if pipeline logic stays small/lightweight)

Chosen approach (iteration 1): TBD

## Demo Flow (userX)
- Deploy infra (Terraform apply)
- Load data + run pipeline on-demand
- userX assumes demo role (STS) and views/query results
- Destroy infra (Terraform destroy) to stop ongoing costs

## Cost Controls
- Partition by day (Athena scans less)
- Parquet for storage + query efficiency
- Run crawlers only when needed
- No always-on compute

