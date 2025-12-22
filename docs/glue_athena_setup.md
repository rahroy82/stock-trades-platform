# Glue + Athena Setup (Planned Implementation)

This document describes how the Stock Trades Data Platform will register S3 datasets in the Glue Data Catalog and query them using Athena.

## Glue Databases

We will create two Glue databases:

- `stock_trades_raw`
- `stock_trades_curated`

## Tables (Targets)

### 1) Raw Trades

- Database: `stock_trades_raw`
- Table: `trades`
- S3 location:
  - `s3://<bucket>/stock-trades-platform/raw/trades/`
- Format: Parquet
- Partitions:
  - `day` (string)
  - optionally `symbol` (string)

### 2) 5-minute Bars

- Database: `stock_trades_curated`
- Table: `bars_5m`
- S3 location:
  - `s3://<bucket>/stock-trades-platform/curated/bars_5m/`
- Format: Parquet
- Partitions:
  - `day` (string)
  - optionally `symbol` (string)

### 3) ML Features (5-minute)

- Database: `stock_trades_curated`
- Table: `ml_features_5m`
- S3 location:
  - `s3://<bucket>/stock-trades-platform/curated/ml_features/`
- Format: Parquet
- Partitions:
  - `day` (string)
  - optionally `symbol` (string)

## How Tables Will Be Created

Two supported approaches:

### Approach A: Glue Crawler (fastest)
- Point a crawler at each top-level dataset prefix
- Configure crawler to create tables in the correct database
- Run crawler on schedule or on-demand after ETL writes

Pros:
- Minimal setup
Cons:
- Less control over schema evolution

### Approach B: Explicit Glue Table Definitions (best practice for production)
- Define Glue tables via Terraform:
  - Database resources
  - Table resources (schema + partitions + location)

Pros:
- Strong schema control
Cons:
- More up-front work

## Athena Query Layer

Athena will query the Glue tables directly. These queries can power:
- Exploratory analysis
- Dashboards (e.g., Superset/Metabase, or BI tools via Athena connectors)

## Notes on Cost Control

- Partition by `day` (and optionally `symbol`) to reduce scanned data.
- Use Parquet to reduce storage and query cost.
- Keep demo environments temporary (deploy/teardown with Terraform).
- Provide limited access to userX via time-bound STS credentials (read-only).

