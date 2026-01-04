aws ecs describe-tasks \
  --region us-east-1 \
  --cluster stock-trades-platform-cluster \
  --tasks arn:aws:ecs:us-east-1:402205012123:task/stock-trades-platform-cluster/7c3d2193e24145ec9f510a99acbdf1f1 \
  --query "tasks[0].{lastStatus:lastStatus,desiredStatus:desiredStatus,stoppedReason:stoppedReason,exit:containers[0].exitCode}" \
  --output table


cd infra/terraform/envs/dev
terraform apply -var "data_lake_bucket_name=stock-trades-platform-rahroy82-dev-$(date +%s)"

# Athena (Querying the Data Lake)

## Prereqs
- AWS region: `us-east-1`
- Athena workgroup: `stock-trades-platform-wg`
- S3 data lake bucket: `stock-trades-platform-rahroy82-dev-1766886891`
- Glue databases (created by Terraform):
  - `stock_trades_raw`
  - `stock_trades_curated`

## Create External Tables (Parquet)

### 1) RAW trades
Run in Athena with database set to `stock_trades_raw`:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS stock_trades_raw.trades (
  symbol string,
  trade_time timestamp,
  price double,
  size double
)
STORED AS PARQUET
LOCATION 's3://stock-trades-platform-rahroy82-dev-1766886891/stock-trades-platform/raw/trades/';

###################### Sanity Check:

SELECT COUNT(*) AS n_trades FROM stock_trades_raw.trades;


##################################################

CREATE EXTERNAL TABLE IF NOT EXISTS stock_trades_curated.bars_5m (
  symbol string,
  bar_start_time timestamp,
  day string,
  open_price double,
  high_price double,
  low_price double,
  close_price double,
  volume double,
  num_trades bigint
)
STORED AS PARQUET
LOCATION 's3://stock-trades-platform-rahroy82-dev-1766886891/stock-trades-platform/curated/bars_5m/';

################### Sanity Check: 

SELECT symbol, COUNT(*) AS n_bars
FROM stock_trades_curated.bars_5m
GROUP BY symbol
ORDER BY n_bars DESC;


######################################

CREATE EXTERNAL TABLE IF NOT EXISTS stock_trades_curated.ml_features_5m (
  symbol string,
  bar_start_time timestamp,
  day string,
  open_price double,
  high_price double,
  low_price double,
  close_price double,
  volume double,
  num_trades bigint,
  return_1 double,
  return_3 double,
  return_6 double,
  vol_6 double,
  sma_6 double,
  sma_12 double,
  target_up bigint
)
STORED AS PARQUET
LOCATION 's3://stock-trades-platform-rahroy82-dev-1766886891/stock-trades-platform/curated/ml_features/';

############################# Sanity Check:

SELECT target_up, COUNT(*) AS n_rows
FROM stock_trades_curated.ml_features_5m
GROUP BY target_up
ORDER BY target_up;
