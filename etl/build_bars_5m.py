from pathlib import Path
from datetime import datetime, timezone
import sys

import pandas as pd

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.storage import raw_trades_dir, bars_5m_dir

RAW_DIR = raw_trades_dir()
OUTPUT_DIR = bars_5m_dir()

def load_raw_trades() -> pd.DataFrame:
    """
    Load all Parquet trade files from the raw folder into a single DataFrame.
    """
    files = sorted(RAW_DIR.glob("trades_batch_*.parquet"))
    if not files:
        raise FileNotFoundError(f"No Parquet files found in {RAW_DIR}")

    dfs = [pd.read_parquet(f) for f in files]
    df = pd.concat(dfs, ignore_index=True)

    # Parse timestamps
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)

    return df


def build_5m_bars(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build 5-minute OHLCV bars per symbol from trade-level data.
    """
    # Ensure proper types
    df = df.copy()
    df["price"] = df["price"].astype(float)
    df["size"] = df["size"].astype(float)

    # Set index for resampling
    df = df.set_index("event_time")

    # Group by symbol then resample
    bars = (
        df.groupby("symbol")
        .resample("5min")  # 5-minute frequency
        .agg(
            open_price=("price", "first"),
            high_price=("price", "max"),
            low_price=("price", "min"),
            close_price=("price", "last"),
            volume=("size", "sum"),
            num_trades=("price", "count"),
        )
        .reset_index()
    )

    # Drop empty rows (no trades in that bucket)
    bars = bars.dropna(subset=["open_price", "high_price", "low_price", "close_price"])

    # Add day column (for partitioning later)
    bars["day"] = bars["event_time"].dt.date

    # Rename event_time to bar_start_time
    bars = bars.rename(columns={"event_time": "bar_start_time"})

    # Reorder columns
    cols = [
        "symbol",
        "bar_start_time",
        "day",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "num_trades",
    ]
    bars = bars[cols]

    return bars


def write_bars(bars: pd.DataFrame) -> Path:
    """
    Write bars to a timestamped Parquet file in the curated/bars_5m folder.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    ts_str = now.strftime("%Y%m%dT%H%M%SZ")
    output_path = OUTPUT_DIR / f"bars_5m_{ts_str}.parquet"

    bars.to_parquet(output_path, index=False)
    return output_path


def main():
    print(f"Loading raw trades from {RAW_DIR} ...")
    df = load_raw_trades()
    print(f"Loaded {len(df)} trades.")

    print("Building 5-minute bars ...")
    bars = build_5m_bars(df)
    print(f"Built {len(bars)} bars for {bars['symbol'].nunique()} symbols.")

    output_path = write_bars(bars)
    print(f"Wrote 5-minute bars to {output_path}")


if __name__ == "__main__":
    main()

