# Athena SQL (Examples)

These are example queries to explore curated datasets once Glue + Athena are enabled.

## Bars: daily rollups

```sql
SELECT
  symbol,
  day,
  AVG(close_price) AS avg_close,
  MAX(high_price) AS daily_high,
  MIN(low_price)  AS daily_low,
  SUM(volume)     AS total_volume
FROM stock_trades_curated.bars_5m
WHERE day BETWEEN '2025-12-15' AND '2025-12-17'
GROUP BY symbol, day
ORDER BY day, symbol;


## ML Features: label distribution

SELECT
  symbol,
  target_direction_1_ahead AS direction,
  COUNT(*) AS n
FROM stock_trades_curated.ml_features_5m
GROUP BY symbol, target_direction_1_ahead
ORDER BY symbol, direction;



### 12.1.3 Add dashboard plan doc

Paste into `docs/dashboard_plan.md`:

```markdown
# Dashboard Plan (Low-Cost)

Goal: build dashboards over curated data with minimal always-on cost.

## Preferred approach (low-cost)

- Use Athena as the query layer.
- Use a dashboard tool that can connect to Athena:
  - Open source options: Apache Superset or Metabase
  - Commercial: Power BI / Tableau (via Athena connector)

## Demo approach for userX

- Deploy infra on demand (Terraform apply).
- Provide userX time-limited credentials (STS) + a dashboard URL.
- Tear down infra after the demo (Terraform destroy).

## Candidate dashboards

1) Market Overview
- Latest close per symbol
- Daily volume
- Intraday volatility proxy (rolling_vol_5)

2) Symbol Drilldown
- 5-min OHLC chart
- Volume + trade count

3) Data Quality
- Row counts per day/symbol
- Missing values (where applicable)

## Notes

- For small datasets, Python/pandas is enough.
- Spark becomes useful when curated data grows large or when using AWS Glue jobs for distributed ETL.
  PySpark will be the default Spark implementation; Scala Spark versions can be added later for Spark-only parts.

