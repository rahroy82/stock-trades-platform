import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

# Adjust this to your actual project path inside the Airflow environment
# For local Docker Airflow, you'll mount your repo into the container
PROJECT_ROOT = os.getenv("STOCK_PROJECT_ROOT", "/mnt/c/Users/rahro/de_project/stock-trades-platform")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="stock_trades_daily_pipeline",
    default_args=default_args,
    description="Daily stock trades pipeline: generate trades -> bars -> ML features",
    schedule_interval="@daily",  # can tweak later
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["stocks", "data-engineering"],
) as dag:

    # 1) Generate raw trades (batch)
    generate_trades = BashOperator(
        task_id="generate_trades",
        bash_command=(
            "cd {{ params.project_root }} && "
            "conda run -n trade-de python ingestion/generate_trades.py "
            "--trades-per-symbol 2000 --minutes-back 600"
        ),
        params={"project_root": PROJECT_ROOT},
    )

    # 2) Build 5-minute OHLCV bars from raw trades
    build_bars = BashOperator(
        task_id="build_bars_5m",
        bash_command=(
            "cd {{ params.project_root }} && "
            "conda run -n trade-de python etl/build_bars_5m.py"
        ),
        params={"project_root": PROJECT_ROOT},
    )

    # 3) Build ML-ready feature & label table from bars
    build_ml_features = BashOperator(
        task_id="build_ml_features",
        bash_command=(
            "cd {{ params.project_root }} && "
            "conda run -n trade-de python etl/build_ml_features.py"
        ),
        params={"project_root": PROJECT_ROOT},
    )

    # Task order: generate -> bars -> features
    generate_trades >> build_bars >> build_ml_features
