import json
from pathlib import Path
from typing import Literal

BACKEND_TYPE = Literal["local", "s3"]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "storage.json"


def load_storage_config() -> dict:
    if not CONFIG_PATH.exists():
        # Sensible defaults if file missing
        return {
            "backend": "local",
            "local_data_root": "data",
            "s3_bucket": None,
            "s3_prefix": "stock-trades-platform",
        }
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


_cfg = load_storage_config()
_BACKEND: BACKEND_TYPE = _cfg.get("backend", "local")  # type: ignore
_LOCAL_ROOT = PROJECT_ROOT / _cfg.get("local_data_root", "data")
_S3_BUCKET = _cfg.get("s3_bucket")
_S3_PREFIX = _cfg.get("s3_prefix", "stock-trades-platform")


def get_backend() -> BACKEND_TYPE:
    return _BACKEND


# ---------- Local path helpers (current mode) ----------

def raw_trades_dir() -> Path:
    return _LOCAL_ROOT / "raw" / "trades"


def bars_5m_dir() -> Path:
    return _LOCAL_ROOT / "curated" / "bars_5m"


def ml_features_dir() -> Path:
    return _LOCAL_ROOT / "curated" / "ml_features"


# ---------- Future S3 helpers (stubs for now) ----------

def s3_raw_trades_uri() -> str:
    if not _S3_BUCKET:
        raise ValueError("s3_bucket is not configured in storage.json")
    return f"s3://{_S3_BUCKET}/{_S3_PREFIX}/raw/trades"


def s3_bars_5m_uri() -> str:
    if not _S3_BUCKET:
        raise ValueError("s3_bucket is not configured in storage.json")
    return f"s3://{_S3_BUCKET}/{_S3_PREFIX}/curated/bars_5m"


def s3_ml_features_uri() -> str:
    if not _S3_BUCKET:
        raise ValueError("s3_bucket is not configured in storage.json")
    return f"s3://{_S3_BUCKET}/{_S3_PREFIX}/curated/ml_features"

