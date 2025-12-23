# Glue Crawlers: create tables for curated datasets (bars_5m, ml_features)

#This crawler targets the curated prefix and will infer tables like bars_5m and ml_features_5m if the 
#folder layout matches. If later partitioned by day= and symbol=, it will also detect partitions.

resource "aws_glue_crawler" "curated_crawler" {
  name          = "${var.project_name}-curated-crawler"
  role          = aws_iam_role.glue_role.arn
  database_name = aws_glue_catalog_database.stock_trades_curated.name

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/stock-trades-platform/curated/"
  }

  # On-demand by default (no schedule). You can run it manually after loading data.
  # schedule = "cron(0 * * * ? *)"  # example hourly
}

