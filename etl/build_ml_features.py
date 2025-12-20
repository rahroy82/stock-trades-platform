from pathlib import Path
from datetime import datetime, timezone
import sys

import numpy as np
import pandas as pd

# Ensure project root is on sys.path so `utils` can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.storage import bars_5m_dir, ml_features_dir


BARS_DIR = bars_5m_dir()
OUTPUT_DIR = ml_features_dir()


def load_bars() -> pd.DataFrame:
    files = sorted(BARS_DIR.glob("bars_5m_*.parquet"))
    if not files:
        raise FileNotFoundError(f"No bars_5m parquet files found in {BARS_DIR}")

    dfs = [pd.read_parquet(f) for f in files]
    df = pd.concat(dfs, ignore_index=True)

    df["bar_start_time"] = pd.to_datetime(df["bar_start_time"], utc=True)
    return df


def build_features_and_labels(bars: pd.DataFrame) -> pd.DataFrame:
    """
    Build ML features and targets from 5-minute bars.
    One row = one (symbol, bar_start_time).
    """
    df = bars.copy()
    df = df.sort_values(["symbol", "bar_start_time"])

    grouped = df.groupby("symbol", group_keys=False)

    # 1-bar returns (current bar vs previous bar)
    df["return_1"] = grouped["close_price"].apply(lambda x: x.pct_change())

    # Rolling volatility (std of returns)
    df["rolling_vol_5"] = grouped["return_1"].apply(
        lambda x: x.rolling(window=5, min_periods=3).std()
    )
    df["rolling_vol_20"] = grouped["return_1"].apply(
        lambda x: x.rolling(window=20, min_periods=5).std()
    )

    # Rolling volume
    df["rolling_volume_5"] = grouped["volume"].apply(
        lambda x: x.rolling(window=5, min_periods=1).sum()
    )

    # Moving averages
    df["ma_5"] = grouped["close_price"].apply(
        lambda x: x.rolling(window=5, min_periods=3).mean()
    )
    df["ma_20"] = grouped["close_price"].apply(
        lambda x: x.rolling(window=20, min_periods=5).mean()
    )

    # Targets: next-bar return and direction
    df["target_return_1_ahead"] = grouped["close_price"].apply(
        lambda x: x.shift(-1) / x - 1.0
    )
    df["target_direction_1_ahead"] = (df["target_return_1_ahead"] > 0).astype("Int64")

    # Clean infinities
    df = df.replace([np.inf, -np.inf], np.nan)

    # Only require "core" features + targets to be present
    required_cols = [
        "return_1",
        "rolling_vol_5",
        "rolling_volume_5",
        "ma_5",
        "target_return_1_ahead",
        "target_direction_1_ahead",
    ]
    df = df.dropna(subset=required_cols)

    # Final column order
    cols = [
        "symbol",
        "bar_start_time",
        "day",
        "close_price",
        "volume",
        "num_trades",
        "return_1",
        "rolling_vol_5",
        "rolling_vol_20",
        "rolling_volume_5",
        "ma_5",
        "ma_20",
        "target_return_1_ahead",
        "target_direction_1_ahead",
    ]

    df = df[cols].reset_index(drop=True)
    return df


def write_features(df: pd.DataFrame) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    ts_str = now.strftime("%Y%m%dT%H%M%SZ")
    output_path = OUTPUT_DIR / f"ml_features_5m_{ts_str}.parquet"
    df.to_parquet(output_path, index=False)
    return output_path


def main():
    print(f"Loading 5-minute bars from {BARS_DIR} ...")
    bars = load_bars()
    print(f"Loaded {len(bars)} bars for {bars['symbol'].nunique()} symbols.")

    print("Building ML features and labels ...")
    ml_df = build_features_and_labels(bars)
    print(
        f"Built {len(ml_df)} ML rows for {ml_df['symbol'].nunique()} symbols "
        f"with targets."
    )

    output_path = write_features(ml_df)
    print(f"Wrote ML feature table to {output_path}")


if __name__ == "__main__":
    main()

