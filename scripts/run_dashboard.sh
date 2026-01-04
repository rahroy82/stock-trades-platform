
## 16.4.3 Add a helper script (optional but nice)
Create:

`scripts/run_dashboard.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${ATHENA_OUTPUT_S3:?Set ATHENA_OUTPUT_S3 to s3://<athena-results-bucket>/results/}"

export AWS_REGION="${AWS_REGION:-us-east-1}"
export ATHENA_WORKGROUP="${ATHENA_WORKGROUP:-stock-trades-platform-wg}"
export ATHENA_DATABASE="${ATHENA_DATABASE:-stock_trades_curated}"

python -m streamlit run dashboards/streamlit_app.py
