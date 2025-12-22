# Recruiter Demo Access (Time-Limited)

This project is designed to be deployed temporarily for demo purposes and then torn down to reduce cost.

## Approach

- Deploy AWS resources using Terraform (`infra/terraform/envs/dev`).
- Create a dedicated IAM role for recruiter/demo access:
  - Read-only access to curated S3 prefixes (and later: dashboards/UI).
  - No delete/modify permissions.
- Issue temporary credentials using AWS STS AssumeRole:
  - Time-limited (e.g., 1 hour).
  - Can be reissued as needed.

## Intended Demo Flow

1. I run: `terraform apply` to deploy the demo environment.
2. I provide the recruiter with:
   - A read-only dashboard URL (later step)
   - A temporary access method (STS credentials)
3. Recruiter can view:
   - Curated datasets (Athena queries later step)
   - Dashboards (Metabase/Superset later step)
4. I run: `terraform destroy` to remove infrastructure and stop costs.

## Notes

- For security, the demo role is least-privilege.
- Access is always time-scoped and can optionally be IP-restricted.

