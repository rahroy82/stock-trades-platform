# Cloud Mapping: S3 + Glue + Athena

This document describes how the existing local `data/` layout for the Stock Trades Data Engineering Platform maps to an AWS S3-based data lake with Glue Data Catalog and Athena.

The goal is: keep the same conceptual structure you already use locally, but deploy it on S3 so that Glue and Athena can query it, and dashboards/ML can use it.

---

## S3 Layout

**Example bucket name:** `stock-trades-de-prod`  
**Prefix:** `stock-trades-platform/`

The S3 layout mirrors the local `data/` folder:

```text
s3://stock-trades-de-prod/stock-trades-platform/
  raw/
    trades/
      day=YYYY-MM-DD/
        symbol=SYMBOL/
          trades_batch_*.parquet

  curated/
    bars_5m/
      day=YYYY-MM-DD/
        symbol=SYMBOL/
          bars_5m_*.parquet

    ml_features/
      day=YYYY-MM-DD/
        symbol=SYMBOL/
          ml_features_5m_*.parquet

    signals/   # future (for trade signals)
      ...

