#!/usr/bin/env bash
set -euo pipefail

# Runs the pipeline steps in order.
# Works locally (python) or inside a container (same commands).

TRADES_PER_SYMBOL="${TRADES_PER_SYMBOL:-1000}"
MINUTES_BACK="${MINUTES_BACK:-300}"

echo "Generating trades..."
python ingestion/generate_trades.py --trades-per-symbol "$TRADES_PER_SYMBOL" --minutes-back "$MINUTES_BACK"

echo "Building 5-minute bars..."
python etl/build_bars_5m.py

echo "Building ML features (ML-ready only; no model training)..."
python etl/build_ml_features.py

echo "Pipeline complete."
