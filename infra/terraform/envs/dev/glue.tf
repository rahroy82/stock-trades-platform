# Glue Databases (Catalog)
resource "aws_glue_catalog_database" "stock_trades_raw" {
  name = "stock_trades_raw"
}

resource "aws_glue_catalog_database" "stock_trades_curated" {
  name = "stock_trades_curated"
}

output "glue_db_raw" {
  value = aws_glue_catalog_database.stock_trades_raw.name
}

output "glue_db_curated" {
  value = aws_glue_catalog_database.stock_trades_curated.name
}
