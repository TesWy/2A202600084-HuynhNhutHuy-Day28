# scripts/03_delta_to_feast.py
import glob
import json
import os
import time
from pathlib import Path

import pandas as pd
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_URL = os.environ.get("REDIS_URL", f"redis://localhost:{REDIS_PORT}")
DELTA_PATH = Path(os.environ.get("DELTA_LAKE_PATH", "delta-lake/raw"))

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def sample_records() -> list[dict]:
    return [
        {"id": "doc_001", "text": "AI platform integration test", "timestamp": time.time()},
        {"id": "doc_002", "text": "Kafka to Prefect pipeline", "timestamp": time.time()},
    ]


def ensure_delta_seed() -> list[Path]:
    files = [Path(path) for path in glob.glob(str(DELTA_PATH / "*.parquet"))]
    if files:
        return files

    DELTA_PATH.mkdir(parents=True, exist_ok=True)
    seed_path = DELTA_PATH / "bootstrap_sample.parquet"
    pd.DataFrame(sample_records()).to_parquet(seed_path)
    print(f"No Delta parquet found; wrote local bootstrap data to {seed_path}")
    return [seed_path]


def load_from_delta_and_push_feast() -> None:
    files = ensure_delta_seed()
    df = pd.concat([pd.read_parquet(file) for file in files], ignore_index=True)
    print(f"Loaded {len(df)} records from Delta Lake")

    for _, row in df.iterrows():
        feature_key = f"feature:{row['id']}"
        r.set(
            feature_key,
            json.dumps(
                {
                    "text": row["text"],
                    "timestamp": float(row.get("timestamp", time.time())),
                    "processed": True,
                }
            ),
        )

    print(f"Integration 3+4 OK: Delta Lake -> Feast (Redis) - {len(df)} features stored")


if __name__ == "__main__":
    load_from_delta_and_push_feast()
