import json
from pathlib import Path

import streamlit as st

# Local config path for Step 2 (we'll swap to S3 later)
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "tickers.json"


def load_config():
    default_config = {
        "default_tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
        "extra_tickers": [],
    }

    try:
        if CONFIG_PATH.exists():
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return default_config
    except json.JSONDecodeError:
        # Fallback if file is invalid JSON
        st.warning(
            "Config file is corrupted or invalid JSON. "
            "Reverting to default configuration."
        )
        return default_config



def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


st.set_page_config(page_title="Stock Ticker Config", page_icon="📈")

st.title("📈 Stock Ticker Configuration")
st.write(
    "Manage which stock tickers are tracked by the data pipeline. "
    "Defaults are always included; you can add or remove extra tickers."
)

config = load_config()
default_tickers = config.get("default_tickers", [])
extra_tickers = config.get("extra_tickers", [])

# --- Default tickers (read-only) ---
st.subheader("Default Tickers (always tracked)")
if default_tickers:
    st.write(", ".join(sorted(default_tickers)))
else:
    st.write("_No default tickers defined._")

st.markdown("---")

# --- Current extra tickers + removal ---
st.subheader("User-Configured Tickers")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("Currently tracked (user-added):")
    if extra_tickers:
        st.write(", ".join(sorted(extra_tickers)))
    else:
        st.write("_No extra tickers added yet._")

with col2:
    if extra_tickers:
        remove_selection = st.multiselect(
            "Select tickers to remove:",
            options=sorted(extra_tickers),
            key="remove_multiselect",
        )
        if st.button("Remove Selected"):
            updated = [t for t in extra_tickers if t not in remove_selection]
            config["extra_tickers"] = updated
            save_config(config)
            st.success("Selected tickers removed.")
            st.rerun()

st.markdown("---")

# --- Add new tickers ---
st.subheader("Add New Tickers")

new_tickers_input = st.text_input(
    "Enter one or more tickers (comma-separated):",
    placeholder="e.g. NVDA, META, AMD",
)

if st.button("Add Tickers"):
    if new_tickers_input.strip():
        raw_tickers = [t.strip().upper() for t in new_tickers_input.split(",")]
        raw_tickers = [t for t in raw_tickers if t]  # drop empties

        merged = set(extra_tickers)
        merged.update(raw_tickers)
        config["extra_tickers"] = sorted(merged)

        save_config(config)
        st.success("Tickers added.")
        st.rerun()
    else:
        st.warning("Please enter at least one ticker symbol.")
