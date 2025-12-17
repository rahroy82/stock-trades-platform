import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd


# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "tickers.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "trades"


def load_tickers():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = json.load(f)
    default = config.get("default_tickers", [])
    extra = config.get("extra_tickers", [])
    tickers = sorted(set(default + extra))
    if not tickers:
        raise ValueError("No tickers configured in tickers.json")
    return tickers


def simulate_trades_for_symbol(symbol: str, start_time: datetime, n_trades: int):
    """
    Very simple price path simulation for a single symbol.
    """
    trades = []
    # Start with some base price per symbol
    base_price_map = {
        "AAPL": 180.0,
        "MSFT": 380.0,
        "GOOGL": 140.0,
        "AMZN": 150.0,
        "TSLA": 250.0,
    }
    price = base_price_map.get(symbol, 100.0)

    current_time = start_time
    for _ in range(n_trades):
        # small random walk
        price_change = random.gauss(0, 0.3)  # mean 0, small std dev
        price = max(1.0, price + price_change)  # don't go below 1

        size = random.choice([10, 25, 50, 100, 250, 500])
        side = random.choice(["BUY", "SELL"])
        venue = "SIM-EX"

        trades.append(
            {
                "event_time": current_time.isoformat(),
                "symbol": symbol,
                "price": round(price, 2),
                "size": size,
                "side": side,
                "venue": venue,
                "source": "simulator",
            }
        )

        # advance time by a few seconds
        current_time += timedelta(seconds=random.randint(1, 15))

    return trades


def generate_batch(n_trades_per_symbol: int = 200, minutes_back: int = 30):
    tickers = load_tickers()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=minutes_back)

    all_trades = []
    for symbol in tickers:
        trades = simulate_trades_for_symbol(symbol, start_time, n_trades_per_symbol)
        all_trades.extend(trades)

    # Shuffle trades to mix symbols
    random.shuffle(all_trades)

    df = pd.DataFrame(all_trades)

    # File name with timestamp
    ts_str = now.strftime("%Y%m%dT%H%M%SZ")
    output_path = OUTPUT_DIR / f"trades_batch_{ts_str}.parquet"

    df.to_parquet(output_path, index=False)
    print(f"Wrote {len(df)} trades for {len(tickers)} symbols to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate simulated stock trades.")
    parser.add_argument(
        "--trades-per-symbol",
        type=int,
        default=200,
        help="Number of trades per symbol.",
    )
    parser.add_argument(
        "--minutes-back",
        type=int,
        default=30,
        help="Length of simulated window in minutes.",
    )
    args = parser.parse_args()

    generate_batch(
        n_trades_per_symbol=args.trades_per_symbol,
        minutes_back=args.minutes_back,
    )


if __name__ == "__main__":
    main()

