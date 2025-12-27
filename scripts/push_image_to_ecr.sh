#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO_URL="${1:-}"

if [[ -z "$ECR_REPO_URL" ]]; then
  echo "Usage: $0 <ECR_REPO_URL>    (example: 123456789012.dkr.ecr.us-east-1.amazonaws.com/stock-trades-platform)"
  exit 1
fi

echo "Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REPO_URL"

echo "Building image..."
docker build -t stock-trades-platform:latest .

echo "Tagging image..."
docker tag stock-trades-platform:latest "$ECR_REPO_URL:latest"

echo "Pushing image..."
docker push "$ECR_REPO_URL:latest"

echo "Done."
