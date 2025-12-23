#!/usr/bin/env bash
set -euo pipefail

ROLE_ARN="${1:-}"
DURATION_SECONDS="${2:-3600}" # default 1 hour

if [[ -z "$ROLE_ARN" ]]; then
  echo "Usage: $0 <ROLE_ARN> [DURATION_SECONDS]"
  exit 1
fi

echo "Assuming role: $ROLE_ARN"
echo "Duration (seconds): $DURATION_SECONDS"

CREDS_JSON=$(aws sts assume-role \
  --role-arn "$ROLE_ARN" \
  --role-session-name "userx-demo-session" \
  --duration-seconds "$DURATION_SECONDS")

ACCESS_KEY=$(echo "$CREDS_JSON" | python -c "import sys, json; print(json.load(sys.stdin)['Credentials']['AccessKeyId'])")
SECRET_KEY=$(echo "$CREDS_JSON" | python -c "import sys, json; print(json.load(sys.stdin)['Credentials']['SecretAccessKey'])")
SESSION_TOKEN=$(echo "$CREDS_JSON" | python -c "import sys, json; print(json.load(sys.stdin)['Credentials']['SessionToken'])")
EXPIRATION=$(echo "$CREDS_JSON" | python -c "import sys, json; print(json.load(sys.stdin)['Credentials']['Expiration'])")

echo ""
echo "Temporary credentials for userX (expires at): $EXPIRATION"
echo ""
echo "export AWS_ACCESS_KEY_ID=$ACCESS_KEY"
echo "export AWS_SECRET_ACCESS_KEY=$SECRET_KEY"
echo "export AWS_SESSION_TOKEN=$SESSION_TOKEN"
echo ""
echo "UserX can run read-only Athena/S3 operations during this window."

