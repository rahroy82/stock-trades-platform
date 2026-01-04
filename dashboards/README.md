# Dashboards

## Streamlit (Athena Dashboard)

This dashboard queries Athena to show:
- Latest 5-minute bars per symbol
- Row counts for trades/bars/ml_features
- Label distribution (`target_up`) from ML-ready features

### Prereqs
- AWS region: `us-east-1`
- Athena workgroup: `stock-trades-platform-wg`
- Athena database: `stock_trades_curated`
- Athena results output S3 path (from Terraform output):
  - `athena_results_bucket`

### Run locally

```bash
conda activate trade-de

export AWS_REGION=us-east-1
export ATHENA_WORKGROUP=stock-trades-platform-wg
export ATHENA_DATABASE=stock_trades_curated
export ATHENA_OUTPUT_S3="s3://<athena-results-bucket>/results/"

streamlit run dashboards/streamlit_app.py
